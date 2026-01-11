"""
Extract Virtual Mobility grant data from FFR source files.
Parses the "List of paid Virtual Mobility" section from each FFR text file.
"""

import re
import sys
from pathlib import Path
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def parse_amount(amount_str: str) -> float:
    """Parse EUR amount with space-separated thousands."""
    cleaned = amount_str.replace(' ', '').replace(',', '')
    return float(cleaned)


def extract_vm_grants_from_ffr(ffr_text: str, gp_number: int) -> list:
    """Extract VM grants from FFR text content."""
    vm_grants = []

    # Find the VM section
    vm_section_pattern = r"List of paid Virtual Mobility\s*(.*?)(?:Sub-total actual amounts|No Virtual Mobility still to be reimbursed|Virtual Networking Support|Dissemination|OERSA|$)"
    match = re.search(vm_section_pattern, ffr_text, re.DOTALL | re.IGNORECASE)

    if not match:
        return vm_grants

    vm_section = match.group(1)

    # Two different patterns depending on grant period:
    # GP2/GP3/GP4: Number Name VM Country StartDate EndDate Amount
    #   Example: 1 Alessandra Tanda VM IT 15/07/2022 15/09/2022 1 310.00
    #   Example: 3 Wolfgang Härdle VM DE 27/07/2022 26/10/2022 1 500.00
    # GP5: Number Name YRI Title Country StartDate EndDate Amount
    #   Example: 1 Maria Iannario NO Explainable AI IT 01/02/2024 01/07/2024 1 500.00

    # Unicode-aware name pattern (handles ö, ä, ü, ę, ó, ś, etc.)
    # Extended to include Latin Extended-A (U+0100-U+017F) for Polish chars
    name_pattern = r'[A-Za-zÀ-ÿĀ-ſ][A-Za-zÀ-ÿĀ-ſ\s\-\']+'

    # Pattern for GP2/GP3/GP4 format (Name VM Country)
    pattern_vm = rf'^(\d+)\s+({name_pattern}?)\s+VM\s+.*?([A-Z]{{2}})\s+(\d{{2}}/\d{{2}}/\d{{4}})\s+(\d{{2}}/\d{{2}}/\d{{4}})\s+([\d\s]+\.\d{{2}})'

    # Pattern for GP5 format (Name YRI ... Country)
    pattern_yri = rf'^(\d+)\s+({name_pattern}?)\s+(YES|NO)\s+.*?([A-Z]{{2}})\s+(\d{{2}}/\d{{2}}/\d{{4}})\s+(\d{{2}}/\d{{2}}/\d{{4}})\s+([\d\s]+\.\d{{2}})'

    for line in vm_section.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Skip page markers and headers
        if 'of 20' in line or 'of 26' in line or 'of 17' in line or 'of 15' in line:
            continue
        if line.startswith('Page') or 'Grantee name' in line:
            continue

        # Try GP5 pattern first (has YES/NO)
        m = re.match(pattern_yri, line)
        if m:
            entry_num = int(m.group(1))
            name = m.group(2).strip()
            yri = m.group(3).upper() == 'YES'
            country = m.group(4)
            start_date = m.group(5)
            end_date = m.group(6)
            amount = parse_amount(m.group(7))

            vm_grants.append({
                'id': f'GP{gp_number}_VM{entry_num}',
                'grant_period': gp_number,
                'entry_number': entry_num,
                'name': name,
                'yri': yri,
                'country': country,
                'start_date': start_date,
                'end_date': end_date,
                'amount': amount
            })
            continue

        # Try GP2/GP3/GP4 pattern (has VM type)
        m = re.match(pattern_vm, line)
        if m:
            entry_num = int(m.group(1))
            name = m.group(2).strip()
            country = m.group(3)
            start_date = m.group(4)
            end_date = m.group(5)
            amount = parse_amount(m.group(6))

            vm_grants.append({
                'id': f'GP{gp_number}_VM{entry_num}',
                'grant_period': gp_number,
                'entry_number': entry_num,
                'name': name,
                'yri': False,  # Not tracked in GP2/3/4
                'country': country,
                'start_date': start_date,
                'end_date': end_date,
                'amount': amount
            })

    return vm_grants


def main():
    """Extract VM grants from all FFR files and report counts."""
    base_dir = Path(__file__).parent.parent.parent
    extracted_text_dir = base_dir / 'extracted_text'

    ffr_files = {
        1: 'AGA-CA19130-1-FFR_ID2193.txt',
        2: 'AGA-CA19130-2-FFR_ID2346.txt',
        3: 'AGA-CA19130-3-FFR_ID2998.txt',
        4: 'AGA-CA19130-4-FFR_ID3993.txt',
        5: 'AGA-CA19130-5-FFR_ID4828.txt',
    }

    all_grants = []
    counts_by_gp = {}
    amounts_by_gp = {}

    print("=" * 70)
    print("VIRTUAL MOBILITY GRANT EXTRACTION FROM FFR SOURCE FILES")
    print("=" * 70)
    print()

    for gp, filename in ffr_files.items():
        filepath = extracted_text_dir / filename

        if not filepath.exists():
            print(f"GP{gp}: File not found - {filepath}")
            counts_by_gp[gp] = 0
            amounts_by_gp[gp] = 0.0
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        grants = extract_vm_grants_from_ffr(content, gp)
        all_grants.extend(grants)

        count = len(grants)
        total_amount = sum(g['amount'] for g in grants)

        counts_by_gp[gp] = count
        amounts_by_gp[gp] = total_amount

        print(f"GP{gp}: {count} VM grants, Total: {total_amount:,.2f} EUR")
        for g in grants:
            print(f"     {g['entry_number']:2d}. {g['name']:<30} {g['country']} {g['amount']:>10,.2f} EUR")
        print()

    total_count = sum(counts_by_gp.values())
    total_amount = sum(amounts_by_gp.values())

    print("-" * 70)
    print(f"TOTAL: {total_count} VM grants, {total_amount:,.2f} EUR")
    print("-" * 70)

    # Compare with JSON
    json_path = Path(__file__).parent.parent / 'data' / 'virtual_mobility_full.json'
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        json_count = len(json_data)
        json_amount = sum(g.get('amount', 0) for g in json_data)

        print()
        print("COMPARISON WITH virtual_mobility_full.json:")
        print(f"  FFR Count:  {total_count}")
        print(f"  JSON Count: {json_count}")
        print(f"  FFR Amount:  {total_amount:,.2f} EUR")
        print(f"  JSON Amount: {json_amount:,.2f} EUR")

        if total_count != json_count:
            print(f"  [MISMATCH] Count differs by {abs(total_count - json_count)}")
        else:
            print(f"  [OK] Counts match")

        if abs(total_amount - json_amount) > 0.01:
            print(f"  [MISMATCH] Amount differs by {abs(total_amount - json_amount):,.2f} EUR")
        else:
            print(f"  [OK] Amounts match")

    # Output summary
    result = {
        'counts_by_gp': counts_by_gp,
        'amounts_by_gp': amounts_by_gp,
        'total_count': total_count,
        'total_amount': total_amount,
        'grants': all_grants
    }

    return result


if __name__ == '__main__':
    main()
