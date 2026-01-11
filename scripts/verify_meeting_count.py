"""
Verify meeting count against FFR source files.
Counts actual meetings from FFR documents to determine correct count.
"""

import re
from pathlib import Path
from collections import defaultdict

FFR_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}


def count_ffr_meetings(gp: int) -> tuple:
    """
    Count meetings from FFR file.
    Returns (count, meeting_list) where meeting_list contains (location, type, cost).
    """
    filepath = FFR_DIR / FFR_FILES[gp]
    content = filepath.read_text(encoding="utf-8")

    meetings = []

    # Find Meetings Expenditure section
    start = content.find("Meetings Expenditure")
    if start == -1:
        return 0, []

    # Find the overview section (ends at "Meeting 1" details)
    details_start = content.find("Meeting 1\nStart date", start)
    if details_start == -1:
        details_start = start + 3000

    overview = content[start:details_start]

    # Method 1: Count numbered entries in overview table
    # Pattern: number location / country type cost
    lines = overview.split("\n")
    for line in lines:
        line = line.strip()
        # Match: starts with number, has location/country
        match = re.match(r'^(\d+)\s+(.+?)\s*/\s*([A-Za-z\s]+)', line)
        if match:
            num = int(match.group(1))
            location = match.group(2).strip()
            country = match.group(3).strip()
            meetings.append({
                "num": num,
                "location": location,
                "country": country
            })

    return len(meetings), meetings


def main():
    print("=" * 80)
    print("FFR MEETING COUNT VERIFICATION")
    print("=" * 80)
    print()

    total_meetings = 0
    gp_counts = {}

    for gp in range(1, 6):
        count, meetings = count_ffr_meetings(gp)
        gp_counts[gp] = count
        total_meetings += count

        print(f"GP{gp}: {count} meetings in FFR")
        print("-" * 40)
        for m in meetings:
            print(f"  {m['num']:>2}. {m['location'][:30]:<30} / {m['country']}")
        print()

    print("=" * 80)
    print(f"TOTAL FFR MEETINGS: {total_meetings}")
    print("=" * 80)
    print()

    print("Summary by GP:")
    for gp in range(1, 6):
        print(f"  GP{gp}: {gp_counts[gp]} meetings")
    print(f"  Total: {total_meetings} meetings")
    print()

    # Compare with summary_statistics.json
    import json
    ss_path = Path(__file__).parent.parent / "data" / "summary_statistics.json"
    with open(ss_path, "r", encoding="utf-8") as f:
        ss = json.load(f)

    current_count = ss["by_category"]["meetings"]["count"]
    print(f"Current summary_statistics.json count: {current_count}")
    print(f"FFR verified count: {total_meetings}")

    if current_count != total_meetings:
        print(f"RECOMMENDATION: Update count from {current_count} to {total_meetings}")
    else:
        print("Count is correct - no update needed")


if __name__ == "__main__":
    main()
