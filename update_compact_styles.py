"""
COST CA19130 Compact Styles Update Script
Applies aggressive (30-40%) spacing reduction to all HTML files
Created: 2026-01-03
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# CSS replacements for compact styling (old_value -> new_value)
CSS_REPLACEMENTS = [
    # Section and page-level spacing
    (r'padding:\s*4rem\s+2rem', 'padding: 2rem 2rem'),
    (r'padding:\s*3rem\s+2rem', 'padding: 1.5rem 2rem'),
    (r'padding:\s*5rem\s+2rem', 'padding: 2.5rem 2rem'),

    # Hero sections
    (r'padding:\s*8rem\s+2rem\s+4rem', 'padding: 4.5rem 2rem 2rem'),
    (r'padding:\s*6rem\s+2rem\s+3rem', 'padding: 4rem 2rem 2rem'),

    # Card padding
    (r'padding:\s*2rem;', 'padding: 1rem;'),
    (r'padding:\s*1\.5rem;', 'padding: 1rem;'),

    # Grid gaps
    (r'gap:\s*2rem;', 'gap: 1rem;'),
    (r'gap:\s*1\.5rem;', 'gap: 1rem;'),
    (r'gap:\s*4rem;', 'gap: 2rem;'),

    # Margins
    (r'margin-top:\s*2rem;', 'margin-top: 0.75rem;'),
    (r'margin-top:\s*3rem;', 'margin-top: 1.5rem;'),
    (r'margin-top:\s*4rem;', 'margin-top: 1.5rem;'),
    (r'margin-bottom:\s*2rem;', 'margin-bottom: 1rem;'),
    (r'margin-bottom:\s*1\.5rem;', 'margin-bottom: 0.75rem;'),
    (r'margin-bottom:\s*3rem;', 'margin-bottom: 1.5rem;'),

    # Table cell padding
    (r'padding:\s*1rem\s+1\.5rem', 'padding: 0.5rem 0.75rem'),
    (r'padding:\s*0\.75rem\s+1rem', 'padding: 0.4rem 0.6rem'),

    # Border radius (slightly smaller)
    (r'border-radius:\s*12px', 'border-radius: 10px'),

    # Chart heights
    (r'height:\s*280px', 'height: 200px'),
    (r'height:\s*300px', 'height: 220px'),
    (r'height:\s*250px', 'height: 180px'),
]

# Files to skip (already updated or special handling)
SKIP_FILES = [
    'index.html',  # Already manually updated
]


def apply_compact_styles(file_path):
    """Apply compact CSS replacements to a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        for pattern, replacement in CSS_REPLACEMENTS:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                changes_made.append(f"{pattern} -> {replacement} ({len(matches)}x)")

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes_made

        return False, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []


def main():
    """Update all HTML files with compact styles"""
    html_files = []

    # Root level files
    for f in BASE_DIR.glob('*.html'):
        if f.name not in SKIP_FILES:
            html_files.append(f)

    # Subdirectory files
    for subdir in ['financial-reports', 'work-budget-plans']:
        subdir_path = BASE_DIR / subdir
        if subdir_path.exists():
            for f in subdir_path.glob('*.html'):
                html_files.append(f)

    print(f"Found {len(html_files)} HTML files to update")
    print(f"Skipping: {SKIP_FILES}")
    print("-" * 60)

    updated_count = 0

    for file_path in sorted(html_files):
        rel_path = file_path.relative_to(BASE_DIR)
        updated, changes = apply_compact_styles(file_path)

        if updated:
            updated_count += 1
            print(f"[OK] {rel_path}")
            for change in changes[:3]:  # Show first 3 changes
                print(f"     {change}")
            if len(changes) > 3:
                print(f"     ... and {len(changes) - 3} more")
        else:
            print(f"[--] {rel_path} - No changes needed")

    print("-" * 60)
    print(f"Summary: {updated_count}/{len(html_files)} files updated")


if __name__ == '__main__':
    main()
