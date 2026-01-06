"""
Apply site-wide compact styling (Option B: Moderate Compaction).
Reduces vertical spacing by 20-25% while maintaining readability.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Option B: Moderate Compaction CSS overrides
COMPACT_CSS = """
        /* === Site-Wide Compaction (Option B: Moderate) === */
        /* Hero: reduced padding */
        .hero {
            padding: 2rem 0 !important;
        }
        .hero h1 {
            font-size: 2rem !important;
        }

        /* Content sections: tighter padding */
        .content-section {
            padding: 1.25rem !important;
        }

        /* Cards: reduced padding */
        .stat-card {
            padding: 0.875rem !important;
        }

        /* Grid gaps: tightened */
        .stats-grid, .features-grid, .sections-grid {
            gap: 0.75rem !important;
        }

        /* Sidebar: tighter spacing */
        .sl-sidebar {
            padding: 0.5rem !important;
        }
        .sl-links a {
            padding: 0.35rem 0.75rem !important;
        }
        .sl-section-header {
            padding: 0.5rem 0.75rem !important;
        }

        /* Tables: tighter */
        th, td {
            padding: 0.5rem 0.75rem !important;
        }

        /* Reduce margins on headings */
        h2, h3, h4 {
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }

        /* Tighter list spacing */
        ul, ol {
            margin: 0.5rem 0 !important;
        }
        li {
            margin-bottom: 0.25rem !important;
        }
        /* === End Compaction === */
"""

def add_compact_styles(content):
    """Add compact styles before closing </style> tag."""
    # Check if already has compaction styles
    if '/* === Site-Wide Compaction' in content:
        print("    [SKIP] Already has compact styles")
        return content, False

    # Find the last </style> tag and insert before it
    # We want to add it to the main inline styles, not external

    # Look for </style> that's not inside a template
    pattern = r'(</style>)'
    matches = list(re.finditer(pattern, content))

    if not matches:
        print("    [WARN] No </style> tag found")
        return content, False

    # Insert before the first </style> tag (main styles)
    first_match = matches[0]
    insert_pos = first_match.start()

    new_content = content[:insert_pos] + COMPACT_CSS + content[insert_pos:]
    return new_content, True

def process_file(filepath, is_subdir=False):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip files without sidebar layout (our target pages)
        if 'sl-sidebar' not in content and 'hero' not in content:
            return False

        new_content, changed = add_compact_styles(content)

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
    skipped_count = 0

    print("Applying Option B: Moderate Compaction (20-25% reduction)")
    print("=" * 60)

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
            skipped_count += 1

    # Financial reports
    subdir = BASE_DIR / 'financial-reports'
    if subdir.exists():
        print("\n[FINANCIAL REPORTS]")
        for f in sorted(subdir.glob('*.html')):
            print(f"  {f.name}...", end='')
            if process_file(f, is_subdir=True):
                print(" [UPDATED]")
                updated_count += 1
            else:
                print(" [skipped]")
                skipped_count += 1

    # Work budget plans
    subdir = BASE_DIR / 'work-budget-plans'
    if subdir.exists():
        print("\n[WORK BUDGET PLANS]")
        for f in sorted(subdir.glob('*.html')):
            print(f"  {f.name}...", end='')
            if process_file(f, is_subdir=True):
                print(" [UPDATED]")
                updated_count += 1
            else:
                print(" [skipped]")
                skipped_count += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: Updated {updated_count} files, skipped {skipped_count}")
    print("Compaction applied: ~20-25% vertical space reduction")

if __name__ == '__main__':
    main()
