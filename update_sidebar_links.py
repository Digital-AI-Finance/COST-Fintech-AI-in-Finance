"""
Update Sidebar Links - Make section headers link to landing pages
Created: 2026-01-05

Changes sidebar from:
    <div class="sl-section-header" onclick="slToggleSection(this)">IMPACT <span class="toggle">&#9660;</span></div>
To:
    <div class="sl-section-header"><a href="impact.html" class="sl-section-link">IMPACT</a> <span class="toggle" onclick="slToggleSection(this.parentNode)">&#9660;</span></div>
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Categories and their landing pages
CATEGORIES = {
    'IMPACT': 'impact.html',
    'NETWORK': 'network.html',
    'RESEARCH': 'research.html',
    'ACTIVITIES': 'activities.html',
    'ARCHIVE': 'archive.html',
}

# CSS to add for section links
SECTION_LINK_CSS = '''
        .sl-section-link {
            color: inherit;
            text-decoration: none;
            flex: 1;
        }
        .sl-section-link:hover {
            color: #E87722;
        }
'''

def update_sidebar_in_file(filepath: Path, is_subdir: bool = False) -> tuple[bool, str]:
    """Update sidebar section headers to include links.

    Returns (success, message)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Read error: {e}"

    # Check if file has sidebar
    if 'sl-sidebar' not in content:
        return False, "No sidebar found"

    # Check if already correctly updated (has sl-section-link AND toggle onclick AND CSS)
    has_structure = ('sl-section-link' in content and 'onclick="slToggleSection(this.parentNode)"' in content)
    has_css = '.sl-section-link {' in content or '.sl-section-link{' in content

    if has_structure and has_css:
        return True, "Already updated"

    original_content = content
    prefix = '../' if is_subdir else ''

    # Update each category
    for category, landing_page in CATEGORIES.items():
        new_html = (
            f'<div class="sl-section-header">'
            f'<a href="{prefix}{landing_page}" class="sl-section-link">{category}</a> '
            f'<span class="toggle" onclick="slToggleSection(this.parentNode)">&#9660;</span></div>'
        )

        # Pattern 1: <div class="sl-section-header" onclick="slToggleSection(this)">CATEGORY <span class="toggle">&#9660;</span></div>
        # (used in most pages)
        pattern1 = (
            rf'<div class="sl-section-header" onclick="slToggleSection\(this\)">'
            rf'{category} <span class="toggle">&#9660;</span></div>'
        )
        content = re.sub(pattern1, new_html, content)

        # Pattern 2: <a href="X.html" class="sl-section-header">CATEGORY <span class="toggle">&#9660;</span></a>
        # (used in landing pages - impact.html, network.html, etc.)
        pattern2 = (
            rf'<a href="[^"]*" class="sl-section-header">'
            rf'{category} <span class="toggle">&#9660;</span></a>'
        )
        content = re.sub(pattern2, new_html, content)

    # Add CSS if not present (insert after sidebar-home styles)
    if SECTION_LINK_CSS.strip() not in content:
        # Try pattern 1: after .sl-sidebar-home.current (used in most pages)
        css_insert_pattern = r'(\.sl-sidebar-home\.current \{[^}]+\})'
        if re.search(css_insert_pattern, content):
            content = re.sub(
                css_insert_pattern,
                r'\1\n' + SECTION_LINK_CSS,
                content,
                count=1
            )
        else:
            # Try pattern 2: after .sl-sidebar-home:hover (used in landing pages)
            css_insert_pattern2 = r'(\.sl-sidebar-home:hover \{[^}]+\})'
            if re.search(css_insert_pattern2, content):
                content = re.sub(
                    css_insert_pattern2,
                    r'\1\n' + SECTION_LINK_CSS,
                    content,
                    count=1
                )

    if content == original_content:
        return False, "No changes made"

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, "Updated"
    except Exception as e:
        return False, f"Write error: {e}"


def main():
    """Find and update all HTML files with sidebars."""
    print("Updating sidebar section headers to include links...\n")

    # Find all HTML files
    root_files = list(BASE_DIR.glob('*.html'))
    financial_files = list((BASE_DIR / 'financial-reports').glob('*.html'))
    budget_files = list((BASE_DIR / 'work-budget-plans').glob('*.html'))

    all_files = []
    for f in root_files:
        all_files.append((f, False))  # Not in subdir
    for f in financial_files:
        all_files.append((f, True))   # In subdir
    for f in budget_files:
        all_files.append((f, True))   # In subdir

    print(f"Found {len(all_files)} HTML files to check\n")
    print("-" * 60)

    updated = 0
    skipped = 0
    no_sidebar = 0
    errors = 0

    for filepath, is_subdir in all_files:
        success, message = update_sidebar_in_file(filepath, is_subdir)

        rel_path = filepath.relative_to(BASE_DIR)

        if message == "No sidebar found":
            no_sidebar += 1
        elif message == "Already updated":
            skipped += 1
            print(f"[SKIP] {rel_path} - Already has section links")
        elif success:
            updated += 1
            print(f"[OK]   {rel_path} - {message}")
        else:
            errors += 1
            print(f"[ERR]  {rel_path} - {message}")

    print("-" * 60)
    print(f"\nSummary:")
    print(f"  Updated:    {updated}")
    print(f"  Skipped:    {skipped}")
    print(f"  No sidebar: {no_sidebar}")
    print(f"  Errors:     {errors}")
    print(f"\nDone!")


if __name__ == '__main__':
    main()
