"""
Apply simple typography changes:
- Font size: 0.75rem (12px) - 25% smaller
- Line height: 1.0 (true single-spaced)
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

TYPOGRAPHY_CSS = """
        /* === Typography: 25% smaller, single-spaced === */
        body {
            font-size: 0.75rem !important;
            line-height: 1.0 !important;
        }
        /* === End Typography === */
"""

def add_typography_styles(content):
    """Add typography styles before closing </style> tag."""
    if '/* === Typography: 25% smaller' in content:
        print("    [SKIP] Already has typography styles")
        return content, False

    pattern = r'(</style>)'
    matches = list(re.finditer(pattern, content))

    if not matches:
        print("    [WARN] No </style> tag found")
        return content, False

    first_match = matches[0]
    insert_pos = first_match.start()

    new_content = content[:insert_pos] + TYPOGRAPHY_CSS + content[insert_pos:]
    return new_content, True

def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'sl-sidebar' not in content and 'hero' not in content:
            return False

        new_content, changed = add_typography_styles(content)

        if changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

def main():
    updated_count = 0

    print("Applying Typography Changes")
    print("=" * 50)
    print("Font size: 0.75rem (12px) - 25% smaller")
    print("Line height: 1.0 (single-spaced)")
    print("=" * 50)

    # Root HTML files
    print("\n[ROOT PAGES]")
    for f in sorted(BASE_DIR.glob('*.html')):
        if f.name.startswith('test-'):
            continue
        print(f"  {f.name}...", end='')
        if process_file(f):
            print(" [UPDATED]")
            updated_count += 1
        else:
            print(" [skipped]")

    # Financial reports
    subdir = BASE_DIR / 'financial-reports'
    if subdir.exists():
        print("\n[FINANCIAL REPORTS]")
        for f in sorted(subdir.glob('*.html')):
            print(f"  {f.name}...", end='')
            if process_file(f):
                print(" [UPDATED]")
                updated_count += 1
            else:
                print(" [skipped]")

    # Work budget plans
    subdir = BASE_DIR / 'work-budget-plans'
    if subdir.exists():
        print("\n[WORK BUDGET PLANS]")
        for f in sorted(subdir.glob('*.html')):
            print(f"  {f.name}...", end='')
            if process_file(f):
                print(" [UPDATED]")
                updated_count += 1
            else:
                print(" [skipped]")

    print("\n" + "=" * 50)
    print(f"SUMMARY: Updated {updated_count} files")

if __name__ == '__main__':
    main()
