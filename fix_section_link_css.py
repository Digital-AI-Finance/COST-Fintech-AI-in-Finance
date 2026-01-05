"""
Fix .sl-section-link CSS - Add display: block
This fixes the issue where clicking category names doesn't navigate to landing pages.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

def fix_css_in_file(filepath: Path) -> tuple[bool, str]:
    """Add display: block to .sl-section-link CSS."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Read error: {e}"

    # Check if file has the CSS to fix
    if '.sl-section-link {' not in content:
        return False, "No sl-section-link CSS"

    # Check if already fixed
    if 'display: block' in content and '.sl-section-link' in content:
        # More specific check
        section = re.search(r'\.sl-section-link \{[^}]+\}', content)
        if section and 'display: block' in section.group():
            return True, "Already fixed"

    original = content

    # Replace the CSS rule to add display: block
    # Match: .sl-section-link { ... flex: 1; ... }
    pattern = r'(\.sl-section-link \{[^}]*flex: 1;)([^}]*\})'
    replacement = r'\1\n            display: block;\2'
    content = re.sub(pattern, replacement, content)

    if content == original:
        return False, "Pattern not matched"

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "Fixed"
    except Exception as e:
        return False, f"Write error: {e}"


def main():
    print("Fixing .sl-section-link CSS (adding display: block)...\n")

    # Find all HTML files
    root_files = list(BASE_DIR.glob('*.html'))
    financial_files = list((BASE_DIR / 'financial-reports').glob('*.html'))
    budget_files = list((BASE_DIR / 'work-budget-plans').glob('*.html'))

    all_files = root_files + financial_files + budget_files

    print(f"Found {len(all_files)} HTML files to check\n")
    print("-" * 60)

    fixed = 0
    skipped = 0
    no_css = 0
    errors = 0

    for filepath in all_files:
        success, message = fix_css_in_file(filepath)
        rel_path = filepath.relative_to(BASE_DIR)

        if message == "No sl-section-link CSS":
            no_css += 1
        elif message == "Already fixed":
            skipped += 1
            print(f"[SKIP] {rel_path}")
        elif success:
            fixed += 1
            print(f"[OK]   {rel_path}")
        else:
            errors += 1
            print(f"[ERR]  {rel_path} - {message}")

    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Fixed:   {fixed}")
    print(f"  Skipped: {skipped}")
    print(f"  No CSS:  {no_css}")
    print(f"  Errors:  {errors}")


if __name__ == '__main__':
    main()
