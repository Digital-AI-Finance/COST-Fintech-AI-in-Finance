"""
Validate WBP Extraction - Comprehensive validation of extracted WBP data.

Checks:
1. JSON files exist and have expected structure
2. Budget totals match known values
3. Meeting and training school counts
4. HTML pages were generated
5. Cross-references between files
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
WBP_DIR = DATA_DIR / "wbp"
HTML_DIR = Path(__file__).parent.parent / "work-budget-plans"


def check_json_files():
    """Verify all required JSON files exist and have expected structure."""
    print("\n1. Checking JSON Files")
    print("-" * 40)

    errors = []

    # Check WBP per-GP files
    for gp in range(1, 6):
        filepath = WBP_DIR / f"wbp_gp{gp}.json"
        if not filepath.exists():
            errors.append(f"Missing: {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check required fields
        required = ['grant_period', 'budget_summary', 'meetings', 'training_schools']
        for field in required:
            if field not in data:
                errors.append(f"GP{gp}: Missing field '{field}'")

        print(f"  GP{gp}: OK - {len(data.get('meetings', []))} meetings, {len(data.get('training_schools', []))} training schools")

    # Check summary file
    summary_path = WBP_DIR / "wbp_summary.json"
    if not summary_path.exists():
        errors.append(f"Missing: {summary_path}")
    else:
        print(f"  wbp_summary.json: OK")

    # Check MoU objectives file
    mou_path = DATA_DIR / "mou_objectives.json"
    if not mou_path.exists():
        errors.append(f"Missing: {mou_path}")
    else:
        with open(mou_path, 'r', encoding='utf-8') as f:
            mou = json.load(f)
        obj_count = len(mou.get('secondary_objectives', []))
        print(f"  mou_objectives.json: OK - {obj_count} secondary objectives")

    # Check GAPGs file
    gapg_path = DATA_DIR / "grant_period_goals.json"
    if not gapg_path.exists():
        errors.append(f"Missing: {gapg_path}")
    else:
        with open(gapg_path, 'r', encoding='utf-8') as f:
            gapgs = json.load(f)
        total = sum(gapgs['grant_periods'][f'GP{gp}']['gapg_count'] for gp in range(1, 6))
        print(f"  grant_period_goals.json: OK - {total} GAPGs")

    return errors


def check_budget_totals():
    """Verify budget totals match known values."""
    print("\n2. Checking Budget Totals")
    print("-" * 40)

    errors = []

    # Known Total Grant values from WBP documents
    KNOWN_TOTALS = {
        1: 62985.50,
        2: 202607.00,
        3: 169820.50,
        4: 257925.91,
        5: 270315.26,
    }

    total_calculated = 0

    for gp in range(1, 6):
        filepath = WBP_DIR / f"wbp_gp{gp}.json"
        if not filepath.exists():
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        extracted = data['budget_summary']['total_grant']
        expected = KNOWN_TOTALS[gp]
        total_calculated += extracted

        if abs(extracted - expected) > 0.01:
            errors.append(f"GP{gp}: Total Grant mismatch - {extracted:,.2f} vs expected {expected:,.2f}")
            print(f"  GP{gp}: FAIL - {extracted:,.2f} (expected {expected:,.2f})")
        else:
            print(f"  GP{gp}: OK - {extracted:,.2f} EUR")

    # Check grand total
    expected_total = sum(KNOWN_TOTALS.values())
    if abs(total_calculated - expected_total) > 0.01:
        errors.append(f"Grand total mismatch: {total_calculated:,.2f} vs {expected_total:,.2f}")
    else:
        print(f"  Total: OK - {total_calculated:,.2f} EUR")

    return errors


def check_html_pages():
    """Verify HTML pages were generated."""
    print("\n3. Checking HTML Pages")
    print("-" * 40)

    errors = []

    required_pages = [
        "objectives.html",
        "gapg.html",
    ]

    for page in required_pages:
        filepath = HTML_DIR / page
        if not filepath.exists():
            errors.append(f"Missing HTML: {filepath}")
            print(f"  {page}: MISSING")
        else:
            size = filepath.stat().st_size
            print(f"  {page}: OK ({size:,} bytes)")

    return errors


def check_data_integrity():
    """Cross-check data between files."""
    print("\n4. Checking Data Integrity")
    print("-" * 40)

    errors = []

    # Load summary
    summary_path = WBP_DIR / "wbp_summary.json"
    if not summary_path.exists():
        return ["Summary file missing - skipping integrity check"]

    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    # Verify meeting counts
    total_meetings = 0
    for gp in range(1, 6):
        filepath = WBP_DIR / f"wbp_gp{gp}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            total_meetings += len(data.get('meetings', []))

    if total_meetings == summary['total_meetings_planned']:
        print(f"  Meeting count: OK ({total_meetings})")
    else:
        errors.append(f"Meeting count mismatch: {total_meetings} vs {summary['total_meetings_planned']}")

    # Verify training school counts
    total_schools = 0
    for gp in range(1, 6):
        filepath = WBP_DIR / f"wbp_gp{gp}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            total_schools += len(data.get('training_schools', []))

    if total_schools == summary['total_training_schools_planned']:
        print(f"  Training school count: OK ({total_schools})")
    else:
        errors.append(f"Training school count mismatch: {total_schools} vs {summary['total_training_schools_planned']}")

    # Verify GAPG counts per GP
    gapg_path = DATA_DIR / "grant_period_goals.json"
    if gapg_path.exists():
        with open(gapg_path, 'r', encoding='utf-8') as f:
            gapgs = json.load(f)

        for gp in range(1, 6):
            count = gapgs['grant_periods'][f'GP{gp}']['gapg_count']
            actual = len(gapgs['grant_periods'][f'GP{gp}']['gapgs'])
            if count != actual:
                errors.append(f"GP{gp} GAPG count mismatch: {count} vs {actual}")

        print(f"  GAPG counts: OK")

    return errors


def main():
    print("=" * 60)
    print("WBP EXTRACTION VALIDATION")
    print("=" * 60)

    all_errors = []

    all_errors.extend(check_json_files())
    all_errors.extend(check_budget_totals())
    all_errors.extend(check_html_pages())
    all_errors.extend(check_data_integrity())

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if all_errors:
        print(f"\nFOUND {len(all_errors)} ERROR(S):")
        for e in all_errors:
            print(f"  - {e}")
        return False
    else:
        print("\nALL VALIDATIONS PASSED!")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
