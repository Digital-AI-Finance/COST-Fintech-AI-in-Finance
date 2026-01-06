"""
Apply Phase 1 Additional Compaction (beyond Option B).
Adds narrower sidebar, thinner topbar, minimal hero, dense tables, smaller charts.
Estimated: Additional 15-20% reduction on top of Option B.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Phase 1: Additional CSS compaction
PHASE1_CSS = """
        /* === Phase 1: Additional Compaction === */
        /* 1A: Narrower Sidebar (160px -> 120px) */
        :root {
            --sl-sidebar-width: 120px !important;
            --sl-topbar-height: 32px !important;
        }
        .sl-sidebar { width: 120px !important; }
        .sl-section-header { font-size: 0.6rem !important; }
        .sl-links a { font-size: 0.65rem !important; padding: 0.3rem 0.5rem !important; }
        .sl-main { margin-left: 120px !important; }

        /* 1B: Thinner Topbar (36px -> 32px) */
        .sl-topbar { height: 32px !important; }
        .sl-topbar-tab { padding: 0.35rem 0.5rem !important; font-size: 0.6rem !important; }

        /* 2A: Minimal Hero (2rem -> 1rem) */
        .hero { padding: 1rem 0 !important; }
        .hero h1 { font-size: 1.75rem !important; margin-bottom: 0.25rem !important; }
        .hero .subtitle { font-size: 1rem !important; }
        .hero .action-id { font-size: 0.85rem !important; }

        /* 3B: Dense Table Typography */
        table { font-size: 0.8rem !important; }
        th { font-size: 0.75rem !important; padding: 0.375rem 0.5rem !important; }
        td { padding: 0.35rem 0.5rem !important; }

        /* 6B: Tighter Headings */
        h2 { font-size: 1.5rem !important; margin: 0.75rem 0 0.5rem !important; }
        h3 { font-size: 1.2rem !important; margin: 0.5rem 0 0.4rem !important; }
        h4 { font-size: 1rem !important; margin: 0.4rem 0 0.3rem !important; }

        /* 6C: Condensed Lists */
        ul, ol { margin: 0.25rem 0 !important; }
        li { margin-bottom: 0.15rem !important; }

        /* 7A: Smaller Icons */
        .objective-card .icon { width: 32px !important; height: 32px !important; }

        /* 7B: Smaller Charts (200px -> 150px) */
        .chart-wrapper { height: 150px !important; }
        .chart-container { padding: 0.5rem !important; }

        /* 8A: Compact Stats */
        .stats-banner { padding: 0.75rem !important; gap: 1rem !important; }
        .stat-number { font-size: 1.75rem !important; }
        .stat-label { font-size: 0.7rem !important; }

        /* Main content adjust for narrower sidebar */
        @media (min-width: 901px) {
            .sl-main { margin-left: 120px !important; }
        }
        /* === End Phase 1 === */
"""

def add_phase1_styles(content):
    """Add Phase 1 styles before closing </style> tag."""
    # Check if already has Phase 1 styles
    if '/* === Phase 1: Additional Compaction ===' in content:
        print("    [SKIP] Already has Phase 1 styles")
        return content, False

    # Find the first </style> tag and insert before it
    pattern = r'(</style>)'
    matches = list(re.finditer(pattern, content))

    if not matches:
        print("    [WARN] No </style> tag found")
        return content, False

    # Insert before the first </style> tag
    first_match = matches[0]
    insert_pos = first_match.start()

    new_content = content[:insert_pos] + PHASE1_CSS + content[insert_pos:]
    return new_content, True

def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip files without sidebar layout
        if 'sl-sidebar' not in content and 'hero' not in content:
            return False

        new_content, changed = add_phase1_styles(content)

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

    print("Applying Phase 1: Additional Compaction (+15-20%)")
    print("=" * 60)
    print("Changes: narrower sidebar, thinner topbar, minimal hero,")
    print("         dense tables, smaller charts, compact stats")
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
            if process_file(f):
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
            if process_file(f):
                print(" [UPDATED]")
                updated_count += 1
            else:
                print(" [skipped]")
                skipped_count += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: Updated {updated_count} files, skipped {skipped_count}")
    print("Total compaction now: ~35-45% (Option B + Phase 1)")

if __name__ == '__main__':
    main()
