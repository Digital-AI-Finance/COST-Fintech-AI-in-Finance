#!/usr/bin/env python3
"""
Extract detailed training school participant data from FFR source files.
Fixes the thousands separator parsing issue.
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
FFR_SOURCE_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# FFR file mapping
FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}

# ITC Countries
ITC_COUNTRIES = {'AL', 'BA', 'BG', 'HR', 'CY', 'CZ', 'EE', 'EL', 'HU', 'LV',
                 'LT', 'MT', 'MD', 'ME', 'MK', 'PL', 'PT', 'RO', 'RS', 'SK',
                 'SI', 'TR', 'UA', 'KV'}


def parse_eur_amount(text: str) -> float:
    """Parse EUR amount from FFR text (handles formats like '1 194.72')"""
    if not text:
        return 0.0
    text = text.strip().replace(" ", "").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def get_ffr_ts_category_total(content: str, gp: int) -> float:
    """Extract the training schools category total from FFR expenditure table"""

    # Find the expenditure section
    expenditure_section = re.search(
        r"EUR\s+EUR\s+EUR\s+EUR\s+EUR(.*?)(?:Total Networking|Eligible Networking)",
        content, re.DOTALL
    )

    if not expenditure_section:
        return 0.0

    section = expenditure_section.group(1)

    # Pattern for Training Schools line
    patterns = [
        r"Training Schools\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})",
        r"Total Schools\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, section)
        if match:
            return parse_eur_amount(match.group(2))  # Actuals column

    return 0.0


def extract_training_schools_from_ffr(content: str, gp: int) -> List[Dict]:
    """Extract all training schools with participant details from FFR content"""
    schools = []

    # Split content into training school blocks
    ts_blocks = re.split(r'\nTraining School (\d+)\n', content)

    for i in range(1, len(ts_blocks), 2):
        if i + 1 >= len(ts_blocks):
            break

        ts_num = int(ts_blocks[i])
        ts_content = ts_blocks[i + 1]

        # Stop at next major section
        for section_marker in ['Short-Term Scientific Mission', 'STSM', 'Virtual Mobility', 'ITC Conference']:
            if section_marker in ts_content:
                match = re.search(rf'{section_marker}', ts_content)
                if match:
                    ts_content = ts_content[:match.start()]
                    break

        school = extract_single_training_school(ts_content, ts_num, gp)
        if school:
            schools.append(school)

    return schools


def extract_single_training_school(content: str, ts_num: int, gp: int) -> Dict:
    """Extract details for a single training school"""
    school = {
        "id": f"GP{gp}_TS{ts_num}",
        "grant_period": gp,
        "school_number": ts_num,
        "start_date": None,
        "end_date": None,
        "duration_days": 0,
        "location": None,
        "city": None,
        "country": None,
        "title": None,
        "participants": [],
        "trainers": [],
        "participant_subtotal": 0.0,
        "los_grant": 0.0,
        "total_expenditure": 0.0
    }

    # Extract metadata
    start_match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', content)
    if start_match:
        school["start_date"] = start_match.group(1)

    end_match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', content)
    if end_match:
        school["end_date"] = end_match.group(1)

    duration_match = re.search(r'Training School duration \(days\)\s+(\d+)', content)
    if duration_match:
        school["duration_days"] = int(duration_match.group(1))

    location_match = re.search(r'Training School location\s+(.+?)(?:\n|$)', content)
    if location_match:
        location = location_match.group(1).strip()
        school["location"] = location
        if ' / ' in location:
            parts = location.split(' / ')
            school["city"] = parts[-2].strip() if len(parts) > 1 else parts[0].strip()
            school["country"] = parts[-1].strip() if len(parts) > 1 else None

    title_match = re.search(r'Training School title\s+(.+?)(?:\n|$)', content)
    if title_match:
        school["title"] = title_match.group(1).strip()

    # Extract participants - pattern with thousands separators
    num_pattern = r'(-?[\d\s]*\d+\.\d{2})'
    participant_pattern = re.compile(
        rf'^(\d+)\s+([A-Za-zÀ-ÿ\s\-\(\),\.\']+?)\s+([A-Z]{{2}})\s+{num_pattern}\s+{num_pattern}\s+{num_pattern}\s+{num_pattern}$',
        re.MULTILINE
    )

    for match in participant_pattern.finditer(content):
        name = match.group(2).strip()
        if 'participant' in name.lower() or 'name' in name.lower():
            continue

        country = match.group(3)
        travel = parse_eur_amount(match.group(4))
        daily = parse_eur_amount(match.group(5))
        other = parse_eur_amount(match.group(6))
        total = parse_eur_amount(match.group(7))

        participant = {
            "index": int(match.group(1)),
            "name": name,
            "country": country,
            "is_itc": country in ITC_COUNTRIES,
            "travel_allowance": travel,
            "daily_allowance": daily,
            "other_expenses": other,
            "total": total
        }
        school["participants"].append(participant)

    # Extract sub-total
    subtotal_match = re.search(r'Sub-total actual amounts - Paid\s+([\d\s\.,]+)', content)
    if subtotal_match:
        school["participant_subtotal"] = parse_eur_amount(subtotal_match.group(1))

    # Extract LOS grant
    los_section = re.search(
        r'Local Organiser Support \(LOS\) Grant\s*\n.*?Sub-total actual amounts - Paid\s+([\d\s\.,]+)',
        content, re.DOTALL
    )
    if los_section:
        school["los_grant"] = parse_eur_amount(los_section.group(1))

    # Calculate total
    school["total_expenditure"] = school["participant_subtotal"] + school["los_grant"]

    return school


def main():
    print("=" * 70)
    print("Extracting Training School Data from FFR Sources")
    print("=" * 70)

    all_schools = []
    verification_results = []

    for gp, filename in FFR_FILES.items():
        filepath = FFR_SOURCE_DIR / filename
        if not filepath.exists():
            print(f"Warning: FFR{gp} file not found")
            continue

        print(f"\nProcessing GP{gp}: {filename}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Get FFR category total
        ffr_total = get_ffr_ts_category_total(content, gp)
        print(f"  FFR Training Schools Total: {ffr_total:,.2f} EUR")

        # Extract schools
        schools = extract_training_schools_from_ffr(content, gp)
        print(f"  Extracted {len(schools)} training schools")

        # Calculate extracted total
        extracted_total = sum(s["total_expenditure"] for s in schools)
        participant_count = sum(len(s["participants"]) for s in schools)
        print(f"  Extracted Total: {extracted_total:,.2f} EUR")
        print(f"  Total Participants: {participant_count}")

        # Verify
        diff = abs(ffr_total - extracted_total)
        status = "PASS" if diff < 1.0 else "FAIL"
        print(f"  Verification: {status} (diff: {diff:.2f} EUR)")

        verification_results.append({
            "grant_period": gp,
            "ffr_total": ffr_total,
            "extracted_total": extracted_total,
            "difference": diff,
            "status": status,
            "school_count": len(schools),
            "participant_count": participant_count
        })

        # Print school details
        for s in schools:
            print(f"    TS{s['school_number']}: {s['city'] or 'Unknown'} - "
                  f"{len(s['participants'])} participants - {s['total_expenditure']:,.2f} EUR")

        all_schools.extend(schools)

    # Save to JSON
    output_path = DATA_DIR / "training_schools_detailed.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_schools, f, indent=2, ensure_ascii=False)
    print(f"\nTraining schools data saved to: {output_path}")

    # Also update the old file for compatibility
    # Convert to old format
    old_format = []
    for s in all_schools:
        old_school = {
            "id": s["id"],
            "grant_period": s["grant_period"],
            "school_number": s["school_number"],
            "start_date": s["start_date"],
            "end_date": s["end_date"],
            "duration_days": s["duration_days"],
            "location": s["location"],
            "city": s["city"],
            "country": s["country"],
            "title": s["title"],
            "participants": s["participants"],
            "participant_count": len(s["participants"]),
            "los_grant": s["los_grant"],
            "total_reimbursed": s["participant_subtotal"]
        }
        old_format.append(old_school)

    old_output_path = DATA_DIR / "training_school_attendees.json"
    with open(old_output_path, 'w', encoding='utf-8') as f:
        json.dump(old_format, f, indent=2, ensure_ascii=False)
    print(f"Updated training_school_attendees.json")

    # Summary
    grand_total = sum(s["total_expenditure"] for s in all_schools)
    total_participants = sum(len(s["participants"]) for s in all_schools)

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total Training Schools: {len(all_schools)}")
    print(f"Total Participants: {total_participants}")
    print(f"Grand Total Expenditure: {grand_total:,.2f} EUR")

    print(f"\n{'=' * 70}")
    print("VERIFICATION BY GRANT PERIOD")
    print(f"{'=' * 70}")

    all_pass = True
    for v in verification_results:
        if v["ffr_total"] > 0 or v["extracted_total"] > 0:
            status = "PASS" if v["status"] == "PASS" else "FAIL"
            if v["status"] != "PASS":
                all_pass = False
            print(f"GP{v['grant_period']}: FFR={v['ffr_total']:>12,.2f} | "
                  f"Extracted={v['extracted_total']:>12,.2f} | "
                  f"Diff={v['difference']:>8,.2f} | {status}")

    print(f"\nAll Training Schools Verified: {'YES' if all_pass else 'NO'}")

    return all_schools, verification_results


if __name__ == "__main__":
    main()
