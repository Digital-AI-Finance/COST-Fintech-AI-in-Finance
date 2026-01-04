"""
Sync FFR Source Files to JSON Data Files.

This script reads the FFR (Final Financial Report) source text files and
regenerates the JSON data files with correct values.

Usage:
    python scripts/sync_ffr_to_json.py

Source: extracted_text/AGA-CA19130-[1-5]-FFR_ID*.txt (ground truth)
Output: data/budget_data.json, data/summary_statistics.json
"""

import sys
from pathlib import Path
from decimal import Decimal
import json

# Add tests directory to path for importing ffr_parser
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'tests'))

from utils.ffr_parser import FFRParser

# Source data location
FFR_SOURCE_DIR = REPO_ROOT.parent / 'extracted_text'
DATA_OUTPUT_DIR = REPO_ROOT / 'data'


def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def sync_budget_data():
    """
    Regenerate budget_data.json from FFR source files.

    Returns:
        dict: The generated budget data structure
    """
    parser = FFRParser(str(FFR_SOURCE_DIR))
    all_data = parser.parse_all()

    # GP date ranges
    gp_dates = {
        1: ("2020-11-01", "2021-10-31"),
        2: ("2021-11-01", "2022-05-31"),
        3: ("2022-06-01", "2022-10-31"),
        4: ("2022-11-01", "2023-10-31"),
        5: ("2023-11-01", "2024-09-13"),
    }

    budget_data = {
        "grant_periods": [],
        "totals": {
            "total_budget": Decimal("0.00"),
            "total_actual": Decimal("0.00"),
            "by_category": {}
        }
    }

    # Category totals accumulator
    category_totals = {}

    for gp in sorted(all_data.keys()):
        data = all_data[gp]
        cats = data.categories

        # Get budget from total_eligible category
        budget = cats.get('total_eligible', type('', (), {'budget': Decimal("0")})()).budget
        actual = data.total_eligible

        # Build breakdown
        breakdown = {}

        # Meetings
        if 'meetings' in cats:
            breakdown['meetings'] = cats['meetings'].actuals
            category_totals['meetings'] = category_totals.get('meetings', Decimal("0")) + cats['meetings'].actuals

        # Training Schools
        if 'training_schools' in cats:
            breakdown['training_schools'] = cats['training_schools'].actuals
            category_totals['training_schools'] = category_totals.get('training_schools', Decimal("0")) + cats['training_schools'].actuals

        # STSM
        if 'stsm' in cats:
            breakdown['stsm'] = cats['stsm'].actuals
            category_totals['stsm'] = category_totals.get('stsm', Decimal("0")) + cats['stsm'].actuals

        # Virtual Mobility / Virtual Networking
        vm_total = Decimal("0")
        if 'virtual_mobility' in cats:
            vm_total += cats['virtual_mobility'].actuals
        if 'virtual_networking_support' in cats:
            vm_total += cats['virtual_networking_support'].actuals
        if vm_total > 0:
            # Use appropriate key name based on GP
            vm_key = 'virtual_networking' if gp <= 2 else 'virtual_mobility'
            breakdown[vm_key] = vm_total
            category_totals['virtual_mobility'] = category_totals.get('virtual_mobility', Decimal("0")) + vm_total

        # ITC Conference Grants
        if 'itc_conference' in cats:
            breakdown['itc_grants'] = cats['itc_conference'].actuals
            category_totals['itc_grants'] = category_totals.get('itc_grants', Decimal("0")) + cats['itc_conference'].actuals

        # Dissemination
        diss_total = Decimal("0")
        if 'dissemination' in cats:
            diss_total += cats['dissemination'].actuals
        if 'dissemination_conference' in cats:
            diss_total += cats['dissemination_conference'].actuals
        if diss_total > 0:
            breakdown['dissemination'] = diss_total
            category_totals['dissemination'] = category_totals.get('dissemination', Decimal("0")) + diss_total

        # OERSA
        if 'oersa' in cats:
            breakdown['oersa'] = cats['oersa'].actuals
            category_totals['oersa'] = category_totals.get('oersa', Decimal("0")) + cats['oersa'].actuals

        # FSAC
        if 'fsac' in cats:
            breakdown['fsac'] = cats['fsac'].actuals
            category_totals['fsac'] = category_totals.get('fsac', Decimal("0")) + cats['fsac'].actuals

        # Build GP entry
        start_date, end_date = gp_dates[gp]
        gp_entry = {
            "id": f"GP{gp}",
            "name": f"Grant Period {gp}",
            "start": start_date,
            "end": end_date,
            "budget": budget,
            "actual": actual,
            "breakdown": breakdown
        }

        budget_data["grant_periods"].append(gp_entry)
        budget_data["totals"]["total_budget"] += budget
        budget_data["totals"]["total_actual"] += actual

    # Add category totals
    budget_data["totals"]["by_category"] = category_totals

    return budget_data


def sync_summary_statistics():
    """
    Regenerate summary_statistics.json from FFR source files.

    Returns:
        dict: The generated summary statistics
    """
    parser = FFRParser(str(FFR_SOURCE_DIR))
    all_data = parser.parse_all()

    # Calculate statistics
    total_meetings = sum(
        d.categories.get('meetings', type('', (), {'actuals': Decimal("0")})()).actuals
        for d in all_data.values()
    )
    total_stsm = sum(
        d.categories.get('stsm', type('', (), {'actuals': Decimal("0")})()).actuals
        for d in all_data.values()
    )
    total_vm = sum(
        d.categories.get('virtual_mobility', type('', (), {'actuals': Decimal("0")})()).actuals +
        d.categories.get('virtual_networking_support', type('', (), {'actuals': Decimal("0")})()).actuals
        for d in all_data.values()
    )
    total_ts = sum(
        d.categories.get('training_schools', type('', (), {'actuals': Decimal("0")})()).actuals
        for d in all_data.values()
    )
    total_fsac = sum(
        d.categories.get('fsac', type('', (), {'actuals': Decimal("0")})()).actuals
        for d in all_data.values()
    )
    total_budget = sum(d.categories.get('total_eligible', type('', (), {'budget': Decimal("0")})()).budget for d in all_data.values())
    total_actual = sum(d.total_eligible for d in all_data.values())

    # Count items
    total_stsm_count = sum(len(d.stsms) for d in all_data.values())
    total_meeting_count = sum(len(d.meetings) for d in all_data.values())
    total_vm_count = sum(len(d.virtual_mobility) for d in all_data.values())

    summary = {
        "totals": {
            "budget": total_budget,
            "actual": total_actual,
            "utilization_rate": float(total_actual / total_budget * 100) if total_budget > 0 else 0
        },
        "by_category": {
            "meetings": {
                "total": total_meetings,
                "count": total_meeting_count
            },
            "stsm": {
                "total": total_stsm,
                "count": total_stsm_count
            },
            "virtual_mobility": {
                "total": total_vm,
                "count": total_vm_count
            },
            "training_schools": {
                "total": total_ts,
                "count": 7  # Known from FFR data
            },
            "fsac": {
                "total": total_fsac
            }
        },
        "by_grant_period": {}
    }

    # Add per-GP summary
    for gp, data in sorted(all_data.items()):
        summary["by_grant_period"][f"GP{gp}"] = {
            "budget": data.categories.get('total_eligible', type('', (), {'budget': Decimal("0")})()).budget,
            "actual": data.total_eligible,
            "utilization": float(data.total_eligible / data.categories.get('total_eligible', type('', (), {'budget': Decimal("1")})()).budget * 100) if data.categories.get('total_eligible', type('', (), {'budget': Decimal("1")})()).budget > 0 else 0
        }

    return summary


def main():
    """Main entry point."""
    print("=" * 60)
    print("COST Action CA19130 - FFR to JSON Sync")
    print("=" * 60)

    # Ensure source directory exists
    if not FFR_SOURCE_DIR.exists():
        print(f"ERROR: FFR source directory not found: {FFR_SOURCE_DIR}")
        sys.exit(1)

    # Ensure output directory exists
    DATA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Sync budget_data.json
    print("\n[1/2] Syncing budget_data.json...")
    budget_data = sync_budget_data()

    budget_data_path = DATA_OUTPUT_DIR / 'budget_data.json'
    with open(budget_data_path, 'w') as f:
        json.dump(budget_data, f, indent=2, default=decimal_to_float)
    print(f"  Written: {budget_data_path}")

    # Print summary
    print("\n  Budget Summary (from FFR source):")
    for gp in budget_data["grant_periods"]:
        print(f"    {gp['id']}: Budget={gp['budget']:,.2f}, Actual={gp['actual']:,.2f}")

    # Sync summary_statistics.json
    print("\n[2/2] Syncing summary_statistics.json...")
    summary = sync_summary_statistics()

    summary_path = DATA_OUTPUT_DIR / 'summary_statistics.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=decimal_to_float)
    print(f"  Written: {summary_path}")

    print("\n" + "=" * 60)
    print("JSON sync complete!")
    print("=" * 60)

    # Return success
    return 0


if __name__ == "__main__":
    sys.exit(main())
