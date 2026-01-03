#!/usr/bin/env python3
"""
Extract detailed meeting participant data from FFR source files.
Creates comprehensive JSON with per-person, per-event reimbursements.
Verifies totals match FFR category totals.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
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
    """Parse EUR amount from FFR text (handles formats like '10 300.30')"""
    if not text:
        return 0.0
    text = text.strip().replace(" ", "").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_meetings_from_ffr(content: str, gp: int) -> List[Dict]:
    """Extract all meetings with participant details from FFR content"""
    meetings = []

    # Split content into meeting blocks
    # Pattern: "Meeting N" followed by meeting details until next "Meeting N" or end of meetings section
    meeting_blocks = re.split(r'\nMeeting (\d+)\n', content)

    # First element is before any meeting, skip it
    # Then pairs of (meeting_number, meeting_content)
    for i in range(1, len(meeting_blocks), 2):
        if i + 1 >= len(meeting_blocks):
            break

        meeting_num = int(meeting_blocks[i])
        meeting_content = meeting_blocks[i + 1]

        # Stop if we hit Training Schools or STSM section
        if re.search(r'Training Schools Expenditure|Short[- ]?Term Scientific Mission|STSM', meeting_content):
            # Truncate content at that point
            match = re.search(r'(Training Schools Expenditure|Short[- ]?Term Scientific Mission|STSM)', meeting_content)
            if match:
                meeting_content = meeting_content[:match.start()]

        meeting = extract_single_meeting(meeting_content, meeting_num, gp)
        if meeting:
            meetings.append(meeting)

    return meetings


def extract_single_meeting(content: str, meeting_num: int, gp: int) -> Dict:
    """Extract details for a single meeting"""
    meeting = {
        "grant_period": gp,
        "meeting_number": meeting_num,
        "start_date": None,
        "end_date": None,
        "duration_days": 0,
        "location": None,
        "city": None,
        "country": None,
        "title": None,
        "meeting_type": None,
        "total_participants": 0,
        "reimbursed_participants": 0,
        "participants": [],
        "participant_subtotal": 0.0,
        "los_grant": 0.0,
        "total_expenditure": 0.0
    }

    # Extract meeting metadata
    start_match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', content)
    if start_match:
        meeting["start_date"] = start_match.group(1)

    end_match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', content)
    if end_match:
        meeting["end_date"] = end_match.group(1)

    duration_match = re.search(r'Meeting duration \(days\)\s+(\d+)', content)
    if duration_match:
        meeting["duration_days"] = int(duration_match.group(1))

    location_match = re.search(r'Meeting location\s+(.+?)(?:\n|$)', content)
    if location_match:
        location = location_match.group(1).strip()
        meeting["location"] = location
        # Parse city / country
        if ' / ' in location:
            parts = location.split(' / ')
            meeting["city"] = parts[0].strip()
            if len(parts) > 1:
                meeting["country"] = parts[1].strip()

    title_match = re.search(r'Meeting title\s+(.+?)(?:\n|$)', content)
    if title_match:
        meeting["title"] = title_match.group(1).strip()

    type_match = re.search(r'Meeting type\s+(.+?)(?:\n|$)', content)
    if type_match:
        meeting["meeting_type"] = type_match.group(1).strip()

    total_part_match = re.search(r'Total number of participants\s+(\d+)', content)
    if total_part_match:
        meeting["total_participants"] = int(total_part_match.group(1))

    reimb_part_match = re.search(r'Total number of reimbursed participants\s+(\d+)', content)
    if reimb_part_match:
        meeting["reimbursed_participants"] = int(reimb_part_match.group(1))

    # Extract participants
    # Pattern: "# Name Country travel daily other total"
    # Numbers can have spaces as thousand separators (e.g., "1 286.30")
    # Each number: optional digits, optional space, digits, dot, 2 decimals
    num_pattern = r'(-?[\d\s]*\d+\.\d{2})'
    participant_pattern = re.compile(
        rf'^(\d+)\s+([A-Za-zÀ-ÿ\s\-\(\),\.\']+?)\s+([A-Z]{{2}})\s+{num_pattern}\s+{num_pattern}\s+{num_pattern}\s+{num_pattern}$',
        re.MULTILINE
    )

    for match in participant_pattern.finditer(content):
        # Skip if this looks like a header line
        name = match.group(2).strip()
        if 'participant' in name.lower() or 'name' in name.lower():
            continue

        country = match.group(3)
        travel = parse_eur_amount(match.group(4))
        daily = parse_eur_amount(match.group(5))
        other = parse_eur_amount(match.group(6))
        total = parse_eur_amount(match.group(7))

        # Validate: total should roughly equal travel + daily + other
        calculated_total = travel + daily + other
        # Sometimes "other" column is 0.00 or 1.0 (flag) and actual other expenses are in "total"
        # Use the parsed total as the authoritative value

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
        meeting["participants"].append(participant)

    # Extract sub-totals
    subtotal_match = re.search(r'Sub-total actual amounts - Paid\s+([\d\s\.,]+)', content)
    if subtotal_match:
        meeting["participant_subtotal"] = parse_eur_amount(subtotal_match.group(1))

    # Extract LOS grant (appears after "Local Organiser Support (LOS) Grant")
    los_section = re.search(r'Local Organiser Support \(LOS\) Grant\s*\n.*?Sub-total actual amounts - Paid\s+([\d\s\.,]+)', content, re.DOTALL)
    if los_section:
        meeting["los_grant"] = parse_eur_amount(los_section.group(1))

    # Calculate total expenditure
    meeting["total_expenditure"] = meeting["participant_subtotal"] + meeting["los_grant"]

    # Generate unique ID
    meeting["id"] = f"GP{gp}_M{meeting_num}"

    return meeting


def extract_meeting_summary_totals(content: str, gp: int) -> Dict[str, float]:
    """Extract meeting summary totals from the expenditure table"""
    totals = {}

    # Find the meetings summary section
    # Format: "# Location / Country Type Amount 0.00 Amount"
    summary_pattern = re.compile(
        r'^(\d+)\s+([A-Za-zÀ-ÿ\s\-]+)\s*/\s*([A-Za-zÀ-ÿ\s]+)\s+(?:Core Group|Workshop|Conference|Management|Working)[^\d]*([\d\s\.,]+)\s+[\d\s\.,]+\s+([\d\s\.,]+)',
        re.MULTILINE
    )

    for match in summary_pattern.finditer(content):
        location = match.group(2).strip()
        country = match.group(3).strip()
        total = parse_eur_amount(match.group(5))
        key = f"{location}/{country}"
        totals[key] = total

    return totals


def verify_meeting_totals(meetings: List[Dict], ffr_category_total: float, gp: int) -> Dict:
    """Verify extracted meeting data against FFR category total"""

    # Sum up all meeting expenditures
    extracted_total = sum(m["total_expenditure"] for m in meetings)

    # Sum participant totals
    participant_total = sum(
        sum(p["total"] for p in m["participants"])
        for m in meetings
    )

    # Sum LOS grants
    los_total = sum(m["los_grant"] for m in meetings)

    verification = {
        "grant_period": gp,
        "ffr_category_total": ffr_category_total,
        "extracted_total": extracted_total,
        "participant_total": participant_total,
        "los_total": los_total,
        "difference": abs(ffr_category_total - extracted_total),
        "status": "MATCH" if abs(ffr_category_total - extracted_total) < 1.0 else "MISMATCH",
        "meeting_count": len(meetings),
        "total_participants": sum(len(m["participants"]) for m in meetings)
    }

    return verification


def get_ffr_meetings_category_total(content: str, gp: int) -> float:
    """Extract the meetings category total from FFR expenditure table"""

    # Find the expenditure section first
    expenditure_section = re.search(
        r"EUR\s+EUR\s+EUR\s+EUR\s+EUR(.*?)(?:Total Networking|Eligible Networking)",
        content, re.DOTALL
    )

    if not expenditure_section:
        return 0.0

    section = expenditure_section.group(1)

    # Try different patterns for different GP formats
    # Format: Category Budget Actuals Accruals Total Delta
    # Numbers have spaces as thousand separators
    patterns = [
        # GP3-5 format: "Meetings" followed by 5 numbers
        r"Meetings\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})",
        # GP1-2 format: "Total Meetings" followed by 5 numbers
        r"Total Meetings\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})\s+(-?[\d\s]+\.\d{2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, section)
        if match:
            # Return the Actuals column (group 2)
            return parse_eur_amount(match.group(2))

    return 0.0


def main():
    print("=" * 70)
    print("Extracting Detailed Meeting Data from FFR Sources")
    print("=" * 70)

    all_meetings = []
    verification_results = []

    for gp, filename in FFR_FILES.items():
        filepath = FFR_SOURCE_DIR / filename
        if not filepath.exists():
            print(f"Warning: FFR{gp} file not found: {filepath}")
            continue

        print(f"\nProcessing GP{gp}: {filename}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Get FFR category total
        ffr_total = get_ffr_meetings_category_total(content, gp)
        print(f"  FFR Meetings Total: {ffr_total:,.2f} EUR")

        # Extract meetings
        meetings = extract_meetings_from_ffr(content, gp)
        print(f"  Extracted {len(meetings)} meetings")

        # Calculate extracted totals
        extracted_total = sum(m["total_expenditure"] for m in meetings)
        participant_count = sum(len(m["participants"]) for m in meetings)
        print(f"  Extracted Total: {extracted_total:,.2f} EUR")
        print(f"  Total Participants: {participant_count}")

        # Verify
        verification = verify_meeting_totals(meetings, ffr_total, gp)
        verification_results.append(verification)

        status = "OK" if verification["status"] == "MATCH" else "MISMATCH"
        print(f"  Verification: {status} (diff: {verification['difference']:.2f} EUR)")

        # Add to all meetings
        all_meetings.extend(meetings)

        # Print meeting details
        for m in meetings:
            if m["total_expenditure"] > 0:
                print(f"    Meeting {m['meeting_number']}: {m['city'] or 'Unknown'} - "
                      f"{len(m['participants'])} participants - {m['total_expenditure']:,.2f} EUR")

    # Save meetings JSON
    output_path = DATA_DIR / "meetings_detailed.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_meetings, f, indent=2, ensure_ascii=False)
    print(f"\nMeetings data saved to: {output_path}")

    # Calculate grand totals
    grand_total = sum(m["total_expenditure"] for m in all_meetings)
    total_participants = sum(len(m["participants"]) for m in all_meetings)
    total_meetings_with_costs = len([m for m in all_meetings if m["total_expenditure"] > 0])

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total Meetings: {len(all_meetings)}")
    print(f"Meetings with Costs: {total_meetings_with_costs}")
    print(f"Total Participants Reimbursed: {total_participants}")
    print(f"Grand Total Expenditure: {grand_total:,.2f} EUR")

    # Verification summary
    print(f"\n{'=' * 70}")
    print("VERIFICATION BY GRANT PERIOD")
    print(f"{'=' * 70}")

    all_match = True
    for v in verification_results:
        status = "PASS" if v["status"] == "MATCH" else "FAIL"
        if v["status"] != "MATCH":
            all_match = False
        print(f"GP{v['grant_period']}: FFR={v['ffr_category_total']:>12,.2f} | "
              f"Extracted={v['extracted_total']:>12,.2f} | "
              f"Diff={v['difference']:>8,.2f} | {status}")

    # Save verification report
    report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_meetings": len(all_meetings),
            "meetings_with_costs": total_meetings_with_costs,
            "total_participants": total_participants,
            "grand_total": grand_total,
            "all_verified": all_match
        },
        "by_grant_period": verification_results,
        "per_meeting_totals": [
            {
                "id": m["id"],
                "grant_period": m["grant_period"],
                "city": m["city"],
                "country": m["country"],
                "title": m["title"],
                "date": m["start_date"],
                "participants": len(m["participants"]),
                "participant_subtotal": m["participant_subtotal"],
                "los_grant": m["los_grant"],
                "total": m["total_expenditure"]
            }
            for m in all_meetings if m["total_expenditure"] > 0
        ]
    }

    report_path = REPORTS_DIR / "meetings_verification.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nVerification report saved to: {report_path}")

    # Print participant verification sample
    print(f"\n{'=' * 70}")
    print("SAMPLE PARTICIPANT VERIFICATION (First 10 participants from GP5)")
    print(f"{'=' * 70}")

    gp5_meetings = [m for m in all_meetings if m["grant_period"] == 5]
    count = 0
    for m in gp5_meetings:
        for p in m["participants"]:
            if count >= 10:
                break
            print(f"{p['name']:<35} {p['country']} {p['total']:>10,.2f} EUR  ({m['city']})")
            count += 1
        if count >= 10:
            break

    return all_meetings, verification_results


if __name__ == "__main__":
    main()
