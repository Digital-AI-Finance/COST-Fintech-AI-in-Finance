"""
Verify meetings.json against WBP source files.
Compares planned meetings from WBP with current JSON data.
"""

import json
import re
from pathlib import Path
from decimal import Decimal
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXTRACTED_TEXT_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

# WBP files by grant period
WBP_FILES = {
    1: "WBP-AGA-CA19130-1_13682.txt",
    2: "WBP-AGA-CA19130-2_14713.txt",
    3: "WBP-AGA-CA19130-3_14714.txt",
    4: "WBP-AGA-CA19130-4_15816.txt",
    5: "WBP-AGA-CA19130-5_16959.txt",
}


def parse_eur_amount(text: str) -> Decimal:
    """Parse EUR amount from text, handling various formats."""
    # Remove spaces (used as thousands separator in some cases)
    clean = text.replace(" ", "").replace(",", "")
    try:
        return Decimal(clean)
    except:
        return Decimal("0.00")


def extract_wbp_meetings_total(content: str) -> Decimal:
    """Extract total meetings cost from WBP content."""
    # Look for the Meetings overview section total
    # Pattern: "Total" followed by amount at end of meetings section
    meetings_section = re.search(
        r'Meetings\s*\nOverview.*?Total\s+([\d,\.]+)',
        content, re.DOTALL | re.IGNORECASE
    )
    if meetings_section:
        return parse_eur_amount(meetings_section.group(1))
    return Decimal("0.00")


def extract_wbp_meeting_count(content: str) -> int:
    """Count meetings from WBP overview table."""
    # Find meetings overview section
    meetings_start = content.find("Meetings\nOverview")
    if meetings_start == -1:
        meetings_start = content.find("Meetings")
    if meetings_start == -1:
        return 0

    # Find end of overview (Details or Total)
    meetings_end = content.find("Details", meetings_start)
    if meetings_end == -1:
        meetings_end = content.find("Short Term", meetings_start)
    if meetings_end == -1:
        meetings_end = len(content)

    section = content[meetings_start:meetings_end]

    # Count lines that look like meeting entries (contain dates like 24/04/2024)
    date_pattern = r'\d{2}/\d{2}/\d{4}'
    matches = re.findall(date_pattern, section)
    # Each meeting has 1-2 dates, so divide by 1.5 approx
    return len(matches) // 2 if matches else 0


def load_meetings_json():
    """Load current meetings.json."""
    with open(DATA_DIR / "meetings.json", "r") as f:
        return json.load(f)


def analyze_meetings_by_gp():
    """Analyze meetings per grant period from both sources."""
    # Load current JSON
    meetings_data = load_meetings_json()
    meetings_list = meetings_data.get("meetings", [])

    # Count JSON meetings by GP
    json_by_gp = defaultdict(lambda: {"count": 0, "total_cost": Decimal("0")})
    for m in meetings_list:
        gp = int(m["gp"].replace("GP", ""))
        json_by_gp[gp]["count"] += 1
        json_by_gp[gp]["total_cost"] += Decimal(str(m.get("cost", 0)))

    # Extract WBP data
    wbp_by_gp = {}
    for gp, filename in WBP_FILES.items():
        filepath = EXTRACTED_TEXT_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            wbp_by_gp[gp] = {
                "total_cost": extract_wbp_meetings_total(content),
                "count": extract_wbp_meeting_count(content)
            }
        else:
            wbp_by_gp[gp] = {"total_cost": Decimal("0"), "count": 0}

    # Print comparison
    print("=" * 80)
    print("MEETING DATA COMPARISON: meetings.json vs WBP Source Files")
    print("=" * 80)
    print()
    print(f"{'GP':<5} {'JSON Count':<12} {'WBP Count':<12} {'JSON Cost':>15} {'WBP Planned':>15} {'Diff':>12}")
    print("-" * 80)

    total_json_count = 0
    total_json_cost = Decimal("0")
    total_wbp_cost = Decimal("0")

    for gp in range(1, 6):
        json_count = json_by_gp[gp]["count"]
        json_cost = json_by_gp[gp]["total_cost"]
        wbp_total = wbp_by_gp[gp]["total_cost"]
        wbp_count = wbp_by_gp[gp]["count"]
        diff = json_cost - wbp_total

        total_json_count += json_count
        total_json_cost += json_cost
        total_wbp_cost += wbp_total

        print(f"GP{gp:<3} {json_count:<12} {wbp_count:<12} {float(json_cost):>15,.2f} {float(wbp_total):>15,.2f} {float(diff):>12,.2f}")

    print("-" * 80)
    print(f"{'Total':<5} {total_json_count:<12} {'':<12} {float(total_json_cost):>15,.2f} {float(total_wbp_cost):>15,.2f} {float(total_json_cost - total_wbp_cost):>12,.2f}")
    print()

    # Note about the data
    print("NOTES:")
    print("- JSON Cost = actual expenditure from FFR")
    print("- WBP Planned = budgeted amount from Work & Budget Plan")
    print("- Difference = Actual - Planned (negative = under budget)")
    print()

    return json_by_gp, wbp_by_gp


def list_gp5_meetings():
    """List GP5 meetings from both sources for detailed comparison."""
    # Load JSON meetings for GP5
    meetings_data = load_meetings_json()
    gp5_meetings = [m for m in meetings_data["meetings"] if m["gp"] == "GP5"]

    print("=" * 80)
    print("GP5 MEETINGS COMPARISON")
    print("=" * 80)
    print()
    print("FROM meetings.json:")
    print("-" * 40)
    for m in gp5_meetings:
        print(f"  {m['id']:>2}. {m['title'][:35]:<35} {m['location']:<15} {m['cost']:>10,.2f}")

    # Load WBP5
    wbp5_path = EXTRACTED_TEXT_DIR / WBP_FILES[5]
    content = wbp5_path.read_text(encoding="utf-8")

    print()
    print("FROM WBP5 Overview Table:")
    print("-" * 40)

    # Extract meeting lines from WBP5
    # Pattern: Title + Meeting Type + Dates + Location + ITC + Cost
    meeting_pattern = r'([A-Za-z][\w\s\-,\.]+?)\s+((?:Core Group|Working Group|Management Committee|Workshops/Conferences)[^0-9]*)\s+(\d{2}/\d{2}/\d{4})\s*-?\s*(\d{2}/\d{2}/\d{4})?\s+([A-Za-z\s\(\)]+?)\s+(Yes|No)\s+([\d,\.]+)'

    # Find meetings section
    meetings_start = content.find("Meetings\nOverview")
    if meetings_start != -1:
        meetings_end = content.find("Details", meetings_start)
        if meetings_end == -1:
            meetings_end = meetings_start + 3000
        section = content[meetings_start:meetings_end]

        # More flexible extraction - look for costs at end of lines
        lines = section.split('\n')
        i = 0
        meeting_num = 0
        while i < len(lines):
            line = lines[i].strip()
            # Look for lines ending with cost pattern
            cost_match = re.search(r'([\d,\.]+)\s*$', line)
            if cost_match:
                try:
                    cost = float(cost_match.group(1).replace(",", ""))
                    if cost > 100:  # Likely a meeting cost
                        meeting_num += 1
                        # Get meeting title from previous lines
                        title = lines[i-1].strip() if i > 0 else "Unknown"
                        print(f"  {meeting_num:>2}. {title[:35]:<35} {cost:>10,.2f}")
                except:
                    pass
            i += 1


if __name__ == "__main__":
    analyze_meetings_by_gp()
    print()
    list_gp5_meetings()
