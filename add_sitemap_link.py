"""
Add Sitemap link to sidebar navigation in all HTML files.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

def add_sitemap_link(content, is_subdir=False):
    """Add sitemap link to ARCHIVE section of sidebar."""
    prefix = "../" if is_subdir else ""

    # Pattern to find ARCHIVE section's sl-links div
    # Look for: Financial Overview link followed by </div> (end of sl-links)
    patterns = [
        # Pattern for root pages
        (r'(<a href="financial-reports/overview\.html">Financial Overview</a>)(\s*</div>\s*</div>\s*</aside>)',
         r'\1\n                <a href="sitemap.html">Site Map</a>\2'),
        # Pattern for subdirectory pages
        (r'(<a href="\.\./financial-reports/overview\.html">Financial Overview</a>)(\s*</div>\s*</div>\s*</aside>)',
         r'\1\n                <a href="../sitemap.html">Site Map</a>\2'),
    ]

    # Check if sitemap link already exists
    if 'sitemap.html">Site Map</a>' in content:
        return content, False

    # Try each pattern
    for pattern, replacement in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            return content, True

    return content, False

def main():
    updated_count = 0

    # Root HTML files
    for f in sorted(BASE_DIR.glob('*.html')):
        if f.name.startswith('test-'):
            continue

        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()

        new_content, changed = add_sitemap_link(content, is_subdir=False)

        if changed:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"[OK] {f.name}")
            updated_count += 1
        elif 'sl-sidebar' in content:
            print(f"[--] {f.name} (already has sitemap or no match)")

    # Subdirectory HTML files
    for subdir in ['financial-reports', 'work-budget-plans']:
        subdir_path = BASE_DIR / subdir
        if not subdir_path.exists():
            continue

        for f in sorted(subdir_path.glob('*.html')):
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()

            new_content, changed = add_sitemap_link(content, is_subdir=True)

            if changed:
                with open(f, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"[OK] {subdir}/{f.name}")
                updated_count += 1
            elif 'sl-sidebar' in content:
                print(f"[--] {subdir}/{f.name} (already has sitemap or no match)")

    print(f"\nUpdated {updated_count} files")

if __name__ == '__main__':
    main()
