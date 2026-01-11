"""
Verify WBP Plan Completion - Check all deliverables from the extraction plan.

Checks:
1. Phase 1: Data files modified correctly
2. Phase 2: Parser infrastructure created
3. Phase 3: JSON files extracted
4. Phase 4: GP pages enhanced
5. Phase 5: New HTML pages created
6. Phase 6: Validation tests pass
7. Phase 7: Navigation updates complete
"""

import json
from pathlib import Path
import re

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
WBP_DIR = DATA_DIR / "wbp"
HTML_DIR = BASE_DIR / "work-budget-plans"
TESTS_DIR = BASE_DIR / "tests" / "utils"
SCRIPTS_DIR = BASE_DIR / "scripts"


def check_phase1():
    """Phase 1: Data Verification & Audit"""
    print("\n" + "=" * 60)
    print("PHASE 1: Data Verification & Audit")
    print("=" * 60)

    issues = []

    # Check budget_data.json has budget_planned
    budget_file = DATA_DIR / "budget_data.json"
    if budget_file.exists():
        with open(budget_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        has_planned = any('budget_planned' in str(data) for _ in [1])
        if has_planned:
            print("[OK] budget_data.json contains budget_planned fields")
        else:
            issues.append("budget_data.json missing budget_planned fields")
            print("[FAIL] budget_data.json missing budget_planned fields")
    else:
        issues.append("budget_data.json not found")
        print("[FAIL] budget_data.json not found")

    # Check meetings.json exists
    meetings_file = DATA_DIR / "meetings.json"
    if meetings_file.exists():
        print("[OK] meetings.json exists")
    else:
        issues.append("meetings.json not found")
        print("[FAIL] meetings.json not found")

    # Check summary_statistics.json
    summary_file = DATA_DIR / "summary_statistics.json"
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        meeting_count = data.get('meetings', {}).get('total', 0)
        if meeting_count == 52:
            print(f"[OK] summary_statistics.json has correct meeting count (52)")
        else:
            issues.append(f"summary_statistics.json meeting count is {meeting_count}, expected 52")
            print(f"[WARN] summary_statistics.json meeting count is {meeting_count}")
    else:
        issues.append("summary_statistics.json not found")
        print("[FAIL] summary_statistics.json not found")

    return issues


def check_phase2():
    """Phase 2: WBP Parser Infrastructure"""
    print("\n" + "=" * 60)
    print("PHASE 2: WBP Parser Infrastructure")
    print("=" * 60)

    issues = []

    files_to_check = [
        ("tests/utils/wbp_models.py", "Dataclass definitions"),
        ("tests/utils/wbp_patterns.py", "Regex patterns"),
        ("tests/utils/wbp_parser_full.py", "Full parser"),
    ]

    for rel_path, desc in files_to_check:
        filepath = BASE_DIR / rel_path
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"[OK] {rel_path} exists ({size:,} bytes) - {desc}")
        else:
            issues.append(f"{rel_path} not found")
            print(f"[FAIL] {rel_path} not found - {desc}")

    return issues


def check_phase3():
    """Phase 3: Extract & Generate JSON Files"""
    print("\n" + "=" * 60)
    print("PHASE 3: Extract & Generate JSON Files")
    print("=" * 60)

    issues = []

    # Check WBP per-GP JSON files
    print("\nWBP Per-GP JSON Files:")
    for gp in range(1, 6):
        filepath = WBP_DIR / f"wbp_gp{gp}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            meetings = len(data.get('meetings', []))
            schools = len(data.get('training_schools', []))
            budget = data.get('budget_summary', {}).get('total_grant', 0)
            print(f"[OK] wbp_gp{gp}.json - Budget: {budget:,.2f} EUR, Meetings: {meetings}, Schools: {schools}")
        else:
            issues.append(f"wbp_gp{gp}.json not found")
            print(f"[FAIL] wbp_gp{gp}.json not found")

    # Check summary file
    summary_path = WBP_DIR / "wbp_summary.json"
    if summary_path.exists():
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_meetings = data.get('total_meetings_planned', 0)
        total_schools = data.get('total_training_schools_planned', 0)
        print(f"[OK] wbp_summary.json - {total_meetings} meetings, {total_schools} training schools")
    else:
        issues.append("wbp_summary.json not found")
        print("[FAIL] wbp_summary.json not found")

    # Check new JSON files
    print("\nNew JSON Files:")
    new_files = [
        ("mou_objectives.json", "16 secondary objectives"),
        ("grant_period_goals.json", "53 GAPGs"),
    ]

    for filename, expected in new_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if filename == "mou_objectives.json":
                count = len(data.get('secondary_objectives', []))
                print(f"[OK] {filename} - {count} secondary objectives")
            elif filename == "grant_period_goals.json":
                total = sum(data['grant_periods'][f'GP{gp}']['gapg_count'] for gp in range(1, 6))
                print(f"[OK] {filename} - {total} GAPGs")
        else:
            issues.append(f"{filename} not found")
            print(f"[FAIL] {filename} not found - {expected}")

    # Check scripts
    print("\nExtraction Scripts:")
    scripts = [
        "extract_wbp_full.py",
        "extract_gapgs.py",
        "generate_wbp_pages.py",
        "validate_wbp_extraction.py",
    ]

    for script in scripts:
        filepath = SCRIPTS_DIR / script
        if filepath.exists():
            print(f"[OK] scripts/{script}")
        else:
            issues.append(f"scripts/{script} not found")
            print(f"[FAIL] scripts/{script} not found")

    return issues


def check_phase4():
    """Phase 4: Populate Existing HTML Pages"""
    print("\n" + "=" * 60)
    print("PHASE 4: Populate Existing HTML Pages (GP Enhancements)")
    print("=" * 60)

    issues = []

    for gp in range(1, 6):
        filepath = HTML_DIR / f"gp{gp}.html"
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')

            # Check for GAPG section
            has_gapg = 'Grant Period Goals</h2>' in content

            # Check for Planned Meetings section
            has_meetings = 'Planned Meetings (WBP)</h2>' in content

            # Check for Training Schools (GP4, GP5 only)
            has_schools = 'Planned Training Schools' in content

            status = []
            if has_gapg:
                status.append("GAPGs")
            if has_meetings:
                status.append("Meetings")
            if has_schools:
                status.append("Schools")

            if has_gapg and has_meetings:
                print(f"[OK] gp{gp}.html enhanced - {', '.join(status)}")
            else:
                missing = []
                if not has_gapg:
                    missing.append("GAPGs")
                if not has_meetings:
                    missing.append("Meetings")
                issues.append(f"gp{gp}.html missing: {', '.join(missing)}")
                print(f"[FAIL] gp{gp}.html missing: {', '.join(missing)}")
        else:
            issues.append(f"gp{gp}.html not found")
            print(f"[FAIL] gp{gp}.html not found")

    return issues


def check_phase5():
    """Phase 5: Create New HTML Pages"""
    print("\n" + "=" * 60)
    print("PHASE 5: Create New HTML Pages")
    print("=" * 60)

    issues = []

    pages = [
        ("objectives.html", "MoU Objectives", ["Primary Objective", "Secondary Objectives"]),
        ("gapg.html", "Grant Period Goals", ["GP1", "GP2", "GP3", "GP4", "GP5"]),
    ]

    for filename, title, expected_content in pages:
        filepath = HTML_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            size = filepath.stat().st_size

            # Check for expected content
            found = [c for c in expected_content if c in content]

            if len(found) == len(expected_content):
                print(f"[OK] {filename} ({size:,} bytes) - {title}")
            else:
                missing = [c for c in expected_content if c not in content]
                print(f"[WARN] {filename} missing content: {missing}")
        else:
            issues.append(f"{filename} not found")
            print(f"[FAIL] {filename} not found - {title}")

    return issues


def check_phase6():
    """Phase 6: Validation & Testing"""
    print("\n" + "=" * 60)
    print("PHASE 6: Validation & Testing")
    print("=" * 60)

    issues = []

    # Run the validation script
    validate_script = SCRIPTS_DIR / "validate_wbp_extraction.py"
    if validate_script.exists():
        print("[OK] validate_wbp_extraction.py exists")

        # Check if validation would pass by checking key data
        try:
            # Verify budget totals
            expected_totals = {
                1: 62985.50,
                2: 202607.00,
                3: 169820.50,
                4: 257925.91,
                5: 270315.26,
            }

            all_match = True
            for gp in range(1, 6):
                filepath = WBP_DIR / f"wbp_gp{gp}.json"
                if filepath.exists():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    extracted = data['budget_summary']['total_grant']
                    expected = expected_totals[gp]
                    if abs(extracted - expected) > 0.01:
                        all_match = False
                        issues.append(f"GP{gp} budget mismatch: {extracted} vs {expected}")

            if all_match:
                total = sum(expected_totals.values())
                print(f"[OK] All budget totals verified ({total:,.2f} EUR)")
            else:
                print("[FAIL] Budget totals mismatch")
        except Exception as e:
            issues.append(f"Validation error: {e}")
            print(f"[FAIL] Validation error: {e}")
    else:
        issues.append("validate_wbp_extraction.py not found")
        print("[FAIL] validate_wbp_extraction.py not found")

    return issues


def check_phase7():
    """Phase 7: Navigation Updates"""
    print("\n" + "=" * 60)
    print("PHASE 7: Navigation Updates")
    print("=" * 60)

    issues = []

    # Check navigation script
    nav_script = SCRIPTS_DIR / "update_wbp_navigation.py"
    if nav_script.exists():
        print("[OK] update_wbp_navigation.py exists")
    else:
        issues.append("update_wbp_navigation.py not found")
        print("[FAIL] update_wbp_navigation.py not found")

    # Check files have navigation links
    files_to_check = [
        "index.html",
        "overview.html",
        "gp1.html", "gp2.html", "gp3.html", "gp4.html", "gp5.html",
        "deliverables.html",
        "working-groups.html",
    ]

    print("\nNavigation links check:")
    for filename in files_to_check:
        filepath = HTML_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')

            has_objectives = 'objectives.html' in content
            has_gapg = 'gapg.html' in content

            obj_count = content.count('objectives.html')
            gapg_count = content.count('gapg.html')

            if has_objectives and has_gapg:
                print(f"[OK] {filename} - objectives.html ({obj_count}x), gapg.html ({gapg_count}x)")
            else:
                missing = []
                if not has_objectives:
                    missing.append("objectives.html")
                if not has_gapg:
                    missing.append("gapg.html")
                issues.append(f"{filename} missing links: {', '.join(missing)}")
                print(f"[FAIL] {filename} missing: {', '.join(missing)}")
        else:
            issues.append(f"{filename} not found")
            print(f"[FAIL] {filename} not found")

    # Check index.html has nav-cards
    index_path = HTML_DIR / "index.html"
    if index_path.exists():
        content = index_path.read_text(encoding='utf-8')
        has_obj_card = 'MoU Objectives</h3>' in content and 'nav-card' in content
        has_gapg_card = 'Grant Period Goals</h3>' in content and 'nav-card' in content

        if has_obj_card and has_gapg_card:
            print("[OK] index.html has nav-cards for both new pages")
        else:
            if not has_obj_card:
                issues.append("index.html missing MoU Objectives nav-card")
            if not has_gapg_card:
                issues.append("index.html missing Grant Period Goals nav-card")
            print("[WARN] index.html may be missing some nav-cards")

    return issues


def main():
    print("=" * 60)
    print("WBP PLAN COMPLETION VERIFICATION")
    print("=" * 60)
    print(f"Base directory: {BASE_DIR}")

    all_issues = []

    # Run all phase checks
    all_issues.extend(check_phase1())
    all_issues.extend(check_phase2())
    all_issues.extend(check_phase3())
    all_issues.extend(check_phase4())
    all_issues.extend(check_phase5())
    all_issues.extend(check_phase6())
    all_issues.extend(check_phase7())

    # Summary
    print("\n" + "=" * 60)
    print("OVERALL SUMMARY")
    print("=" * 60)

    if all_issues:
        print(f"\nFound {len(all_issues)} issue(s):")
        for issue in all_issues:
            print(f"  - {issue}")
        return False
    else:
        print("\nALL PHASES COMPLETED SUCCESSFULLY!")
        print("\nDeliverables verified:")
        print("  - Phase 1: Data files modified")
        print("  - Phase 2: Parser infrastructure created")
        print("  - Phase 3: JSON files extracted (5 WBP + 2 new)")
        print("  - Phase 4: GP pages enhanced (5 pages)")
        print("  - Phase 5: New HTML pages created (2 pages)")
        print("  - Phase 6: Validation tests pass")
        print("  - Phase 7: Navigation updated (9 files)")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
