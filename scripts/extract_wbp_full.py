"""
Extract WBP Full Data - Generate comprehensive JSON files from WBP documents.

This script:
1. Parses all WBP text files (GP1-GP5)
2. Extracts budget, meetings, training schools, and more
3. Generates per-GP JSON files in data/wbp/
4. Creates summary statistics for verification
"""

import json
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal
from dataclasses import asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from tests.utils.wbp_parser_full import WBPParserFull, WBP_FILES, GP_DATES


OUTPUT_DIR = Path(__file__).parent.parent / "data" / "wbp"


class WBPJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for WBP dataclasses."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def extract_gp_to_json(gp: int) -> dict:
    """
    Extract all data from a single WBP and return as dictionary.

    Args:
        gp: Grant period number (1-5)

    Returns:
        Dictionary with all extracted WBP data
    """
    parser = WBPParserFull(gp)
    extraction = parser.parse_full()

    # Convert dataclass to dict
    data = asdict(extraction)

    # Add metadata
    data['_metadata'] = {
        'source_file': WBP_FILES[gp],
        'extraction_date': date.today().isoformat(),
        'parser_version': '1.0.0',
    }

    return data


def generate_all_json_files():
    """Generate JSON files for all grant periods."""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_budgets = {}
    all_meetings = []
    all_training_schools = []

    for gp in range(1, 6):
        print(f"\n{'='*60}")
        print(f"Extracting WBP GP{gp}")
        print(f"{'='*60}")

        data = extract_gp_to_json(gp)

        # Save per-GP JSON file
        output_file = OUTPUT_DIR / f"wbp_gp{gp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, cls=WBPJSONEncoder, indent=2, ensure_ascii=False)

        print(f"Saved: {output_file}")

        # Collect summary data
        budget = data['budget_summary']
        all_budgets[gp] = budget

        meetings = data.get('meetings', [])
        all_meetings.extend(meetings)

        schools = data.get('training_schools', [])
        all_training_schools.extend(schools)

        # Print summary
        print(f"\nBudget Summary:")
        print(f"  Total Grant: {budget['total_grant']:,.2f}")
        print(f"  Meetings: {budget['meetings']:,.2f}")
        print(f"  Training Schools: {budget['training_schools']:,.2f}")
        print(f"  Mobility: {budget['mobility']:,.2f}")
        print(f"  FSAC: {budget['fsac']:,.2f}")
        print(f"\nMeetings: {len(meetings)}")
        print(f"Training Schools: {len(schools)}")

    # Generate combined summary
    print(f"\n{'='*60}")
    print("COMBINED SUMMARY")
    print(f"{'='*60}")

    summary = {
        'total_meetings_planned': len(all_meetings),
        'total_training_schools_planned': len(all_training_schools),
        'budgets_by_gp': {
            f"GP{gp}": {
                'total_grant': all_budgets[gp]['total_grant'],
                'meetings': all_budgets[gp]['meetings'],
                'training_schools': all_budgets[gp]['training_schools'],
                'mobility': all_budgets[gp]['mobility'],
                'fsac': all_budgets[gp]['fsac'],
            }
            for gp in range(1, 6)
        },
        'totals': {
            'total_grant': sum(all_budgets[gp]['total_grant'] for gp in range(1, 6)),
            'meetings': sum(all_budgets[gp]['meetings'] for gp in range(1, 6)),
            'training_schools': sum(all_budgets[gp]['training_schools'] for gp in range(1, 6)),
            'mobility': sum(all_budgets[gp]['mobility'] for gp in range(1, 6)),
            'fsac': sum(all_budgets[gp]['fsac'] for gp in range(1, 6)),
        }
    }

    # Save summary
    summary_file = OUTPUT_DIR / "wbp_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, cls=WBPJSONEncoder, indent=2)

    print(f"\nSaved summary: {summary_file}")
    print(f"\nTotal Meetings Planned: {summary['total_meetings_planned']}")
    print(f"Total Training Schools Planned: {summary['total_training_schools_planned']}")
    print(f"\nTotal Grant (all GPs): {summary['totals']['total_grant']:,.2f}")

    return summary


def verify_extraction():
    """Verify extracted data against known values."""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)

    # Known Total Grant values from verified WBP documents
    # These are the WBP planned budgets (not FFR actuals)
    KNOWN_TOTAL_GRANTS = {
        1: 62985.50,
        2: 202607.00,
        3: 169820.50,
        4: 257925.91,
        5: 270315.26,
    }

    errors = []

    for gp in range(1, 6):
        json_file = OUTPUT_DIR / f"wbp_gp{gp}.json"
        if not json_file.exists():
            errors.append(f"GP{gp}: JSON file not found")
            continue

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        extracted = data['budget_summary']['total_grant']
        expected = KNOWN_TOTAL_GRANTS[gp]

        if abs(extracted - expected) > 0.01:
            errors.append(f"GP{gp}: Total Grant mismatch - extracted {extracted:,.2f}, expected {expected:,.2f}")
        else:
            print(f"GP{gp}: Total Grant {extracted:,.2f} - VERIFIED")

    if errors:
        print("\nERRORS FOUND:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("\nAll extractions verified successfully!")
        return True


if __name__ == "__main__":
    summary = generate_all_json_files()
    verify_extraction()
