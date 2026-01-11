"""
Extract Grant Agreement Period Goals (GAPGs) from all WBP documents.
"""

import re
import json
from pathlib import Path

WBP_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")
OUTPUT_DIR = Path(__file__).parent.parent / "data"

WBP_FILES = {
    1: "WBP-AGA-CA19130-1_13682.txt",
    2: "WBP-AGA-CA19130-2_14713.txt",
    3: "WBP-AGA-CA19130-3_14714.txt",
    4: "WBP-AGA-CA19130-4_15816.txt",
    5: "WBP-AGA-CA19130-5_16959.txt",
}


def extract_gapgs(gp: int) -> list:
    """Extract GAPGs from a single WBP file."""
    filepath = WBP_DIR / WBP_FILES[gp]
    content = filepath.read_text(encoding="utf-8")

    gapgs = []

    # Find the Grant Agreement Period Goals section
    gapg_start = content.find("Grant Agreement Period Goals")
    if gapg_start == -1:
        return gapgs

    # Find end of GAPG section (usually at "Work and Budget Plan Summary" or next major section)
    gapg_end = content.find("Work and Budget Plan Summary", gapg_start)
    if gapg_end == -1:
        gapg_end = content.find("PAGE 7", gapg_start)
    if gapg_end == -1:
        gapg_end = gapg_start + 10000

    gapg_section = content[gapg_start:gapg_end]

    # Pattern to match GAPG entries
    # Format: GAPG N <description> Secondary objective X / Challenge
    pattern = re.compile(
        r'GAPG\s+(\d+)\s+(.+?)(?=GAPG\s+\d+|\Z|^\d+$)',
        re.DOTALL | re.MULTILINE
    )

    matches = pattern.findall(gapg_section)

    for num_str, content_block in matches:
        num = int(num_str)

        # Extract MoU objectives from the content
        obj_pattern = re.compile(r'Secondary objective\s+(\d+)', re.IGNORECASE)
        objectives = [int(m) for m in obj_pattern.findall(content_block)]

        # Check if it relates to "Challenge" (primary objective)
        relates_to_challenge = 'Challenge' in content_block

        # Clean up description - remove objective references
        desc = content_block
        desc = re.sub(r'Secondary objective\s+\d+', '', desc)
        desc = re.sub(r'Challenge', '', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()

        # Remove trailing numbers (page numbers)
        desc = re.sub(r'\s+\d+\s*$', '', desc)

        if desc:
            gapgs.append({
                "gapg_number": num,
                "grant_period": gp,
                "title": desc[:100] + ("..." if len(desc) > 100 else ""),
                "description": desc,
                "mou_objectives": objectives,
                "relates_to_primary_objective": relates_to_challenge
            })

    return gapgs


def main():
    all_gapgs = {
        "action_code": "CA19130",
        "grant_periods": {}
    }

    for gp in range(1, 6):
        print(f"\nExtracting GAPGs from GP{gp}...")
        gapgs = extract_gapgs(gp)
        all_gapgs["grant_periods"][f"GP{gp}"] = {
            "gapg_count": len(gapgs),
            "gapgs": gapgs
        }
        print(f"  Found {len(gapgs)} GAPGs")
        for g in gapgs[:3]:
            print(f"    GAPG {g['gapg_number']}: {g['title'][:50]}...")

    # Save to JSON
    output_file = OUTPUT_DIR / "grant_period_goals.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_gapgs, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("GAPG SUMMARY")
    print("="*60)
    total = 0
    for gp in range(1, 6):
        count = all_gapgs["grant_periods"][f"GP{gp}"]["gapg_count"]
        total += count
        print(f"GP{gp}: {count} GAPGs")
    print(f"Total: {total} GAPGs")


if __name__ == "__main__":
    main()
