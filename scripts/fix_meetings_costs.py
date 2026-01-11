"""
Fix meetings.json costs using actual FFR data.
This script compares meetings.json with FFR source files and updates costs.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
FFR_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}


def extract_ffr_meeting_costs(gp: int) -> list:
    """Extract meeting costs from FFR text file."""
    filepath = FFR_DIR / FFR_FILES[gp]
    content = filepath.read_text(encoding="utf-8")

    meetings = []

    # Find meetings expenditure section
    meetings_start = content.find("Meetings Expenditure")
    if meetings_start == -1:
        return meetings

    # Find the overview table - ends at "Meeting 1" or similar
    overview_end = content.find("Meeting 1", meetings_start)
    if overview_end == -1:
        overview_end = content.find("Meeting details", meetings_start)
    if overview_end == -1:
        overview_end = meetings_start + 3000

    overview_section = content[meetings_start:overview_end]

    # Pattern to match: number location / country type cost
    # Example: "1 Berlin / Germany Workshop/Conference, Working Group, 3 927.98 0.00 3 927.98"
    lines = overview_section.split("\n")

    for line in lines:
        line = line.strip()
        # Match: starts with number, has location/country, ends with 3 decimal amounts
        # Allow any characters in country name (for Türkiye etc.)
        match = re.match(
            r'^(\d+)\s+'  # Meeting number
            r'([^/]+?)\s*/\s*(.+?)\s+'  # Location / Country (allow any chars)
            r'([^0-9]*?)\s+'  # Meeting type (optional)
            r'([\d,\s]+\.\d{2})\s+'  # Actuals
            r'([\d,\s]+\.\d{2})\s+'  # Accruals
            r'([\d,\s]+\.\d{2})$',  # Total
            line
        )
        if match:
            num = int(match.group(1))
            location = match.group(2).strip()
            country = match.group(3).strip()
            total = float(match.group(7).replace(",", "").replace(" ", ""))
            meetings.append({
                "num": num,
                "location": location,
                "country": country,
                "cost": total
            })

    return meetings


def normalize_location(loc: str) -> str:
    """Normalize location name for matching."""
    loc = loc.lower().strip()
    # Remove common suffixes
    loc = re.sub(r'\s*/\s*\w+$', '', loc)  # Remove /country
    loc = re.sub(r'\s+', ' ', loc)
    # Common normalizations
    normalizations = {
        'cluj napoca': 'cluj-napoca',
        'horta faial azores': 'horta faial azores',
        'reykjavík': 'reykjavik',
        'türkiye': 'turkey',
    }
    for old, new in normalizations.items():
        if old in loc:
            loc = loc.replace(old, new)
    return loc


def main():
    # Load current meetings.json
    with open(DATA_DIR / "meetings.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    meetings = data["meetings"]

    print("=" * 90)
    print("MEETINGS.JSON COST CORRECTION ANALYSIS")
    print("=" * 90)
    print()

    changes = []

    for gp in range(1, 6):
        print(f"\nGP{gp}:")
        print("-" * 90)

        # Get FFR meetings for this GP
        ffr_meetings = extract_ffr_meeting_costs(gp)

        # Get meetings.json entries for this GP
        json_meetings = [m for m in meetings if m["gp"] == f"GP{gp}"]

        # Match by location
        for jm in json_meetings:
            jm_loc = normalize_location(jm["location"])
            old_cost = jm["cost"]

            # Find matching FFR meeting
            matched = None
            for fm in ffr_meetings:
                fm_loc = normalize_location(fm["location"])
                if jm_loc in fm_loc or fm_loc in jm_loc:
                    matched = fm
                    break

            if matched:
                new_cost = matched["cost"]
                diff = new_cost - old_cost
                if abs(diff) > 0.01:
                    status = "CHANGE"
                    changes.append({
                        "id": jm["id"],
                        "gp": gp,
                        "title": jm["title"],
                        "location": jm["location"],
                        "old_cost": old_cost,
                        "new_cost": new_cost,
                        "diff": diff
                    })
                else:
                    status = "OK"
                print(f"  {jm['id']:>2}. {jm['title'][:30]:<30} {jm['location']:<15} "
                      f"Old: {old_cost:>10,.2f} -> FFR: {new_cost:>10,.2f} ({status})")
            else:
                print(f"  {jm['id']:>2}. {jm['title'][:30]:<30} {jm['location']:<15} "
                      f"Cost: {old_cost:>10,.2f} (NO FFR MATCH)")

    print()
    print("=" * 90)
    print("PROPOSED CHANGES:")
    print("=" * 90)

    if changes:
        total_diff = 0
        for c in changes:
            print(f"  Meeting {c['id']:>2} ({c['title'][:25]:<25}): "
                  f"{c['old_cost']:>10,.2f} -> {c['new_cost']:>10,.2f} (diff: {c['diff']:+,.2f})")
            total_diff += c["diff"]
        print()
        print(f"Total difference: {total_diff:+,.2f} EUR")
        print(f"Number of changes: {len(changes)}")
    else:
        print("  No changes needed.")

    return changes


if __name__ == "__main__":
    main()
