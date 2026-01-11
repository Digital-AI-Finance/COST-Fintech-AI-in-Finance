"""
Update WBP Navigation - Add links to new objectives.html and gapg.html pages.

Updates:
1. work-budget-plans/index.html - Add nav-cards
2. All 9 work-budget-plans/*.html - Add sidebar links
"""

import re
from pathlib import Path

WBP_DIR = Path(__file__).parent.parent / "work-budget-plans"

# Files to update
FILES_TO_UPDATE = [
    "index.html",
    "overview.html",
    "gp1.html",
    "gp2.html",
    "gp3.html",
    "gp4.html",
    "gp5.html",
    "deliverables.html",
    "working-groups.html",
]

# New nav-cards to add to index.html
NEW_NAV_CARDS = '''            <a href="objectives.html" class="nav-card">
                <h3>MoU Objectives</h3>
                <p>Primary objective and 16 secondary objectives from the Memorandum of Understanding.</p>
                <span class="arrow">View Objectives -></span>
            </a>
            <a href="gapg.html" class="nav-card">
                <h3>Grant Period Goals</h3>
                <p>53 GAPGs defining specific objectives for each grant period with MoU mappings.</p>
                <span class="arrow">View GAPGs -></span>
            </a>
'''

# New sidebar links to add to IMPACT section
NEW_SIDEBAR_LINKS = '''                <a href="objectives.html">MoU Objectives</a>
                <a href="gapg.html">Grant Period Goals</a>'''


def update_index_nav_cards(content: str) -> str:
    """Add nav-cards for objectives and gapg to index.html."""
    # Find the Working Groups nav-card and add new cards after it
    pattern = r'(<a href="working-groups\.html" class="nav-card">.*?</a>)'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        # Check if objectives.html card already exists
        if 'href="objectives.html"' in content:
            print("  Nav-cards already exist in index.html")
            return content

        # Insert new cards after Working Groups card
        insert_pos = match.end()
        new_content = content[:insert_pos] + "\n" + NEW_NAV_CARDS + content[insert_pos:]
        print("  Added nav-cards for objectives.html and gapg.html")
        return new_content
    else:
        print("  WARNING: Could not find Working Groups nav-card in index.html")
        return content


def update_sidebar_links(content: str, filepath: Path) -> str:
    """Add sidebar links for objectives and gapg to IMPACT section."""
    # Check if links already exist
    if 'href="objectives.html">MoU Objectives' in content or 'href="../work-budget-plans/objectives.html"' in content:
        print(f"  Sidebar links already exist in {filepath.name}")
        return content

    # Find the IMPACT section's sl-links div
    # Pattern: <div class="sl-links"> followed by deliverables link
    # We need to add after the deliverables link in the IMPACT section

    # Look for the pattern where deliverables is listed
    pattern = r'(<a href="[^"]*deliverables\.html">Deliverables[^<]*</a>)'

    def replace_deliverables(match):
        deliverables_link = match.group(1)
        # Determine if we're in work-budget-plans folder or parent
        if filepath.parent.name == "work-budget-plans":
            # Same folder - use relative paths
            new_links = '''
                <a href="objectives.html">MoU Objectives</a>
                <a href="gapg.html">Grant Period Goals</a>'''
        else:
            # Parent folder - use work-budget-plans/ prefix
            new_links = '''
                <a href="../work-budget-plans/objectives.html">MoU Objectives</a>
                <a href="../work-budget-plans/gapg.html">Grant Period Goals</a>'''
        return deliverables_link + new_links

    new_content, count = re.subn(pattern, replace_deliverables, content)

    if count > 0:
        print(f"  Added {count} sidebar link(s) for objectives.html and gapg.html")
        return new_content
    else:
        print(f"  WARNING: Could not find deliverables link in {filepath.name}")
        return content


def process_file(filepath: Path) -> bool:
    """Process a single HTML file to update navigation."""
    print(f"\nProcessing: {filepath.name}")

    content = filepath.read_text(encoding='utf-8')
    original_content = content

    # Update sidebar links for all files
    content = update_sidebar_links(content, filepath)

    # Add nav-cards only to index.html
    if filepath.name == "index.html":
        content = update_index_nav_cards(content)

    # Save if changed
    if content != original_content:
        filepath.write_text(content, encoding='utf-8')
        print(f"  Saved: {filepath}")
        return True
    else:
        print(f"  No changes needed")
        return False


def main():
    print("=" * 60)
    print("Updating WBP Navigation")
    print("=" * 60)

    updated_count = 0

    for filename in FILES_TO_UPDATE:
        filepath = WBP_DIR / filename
        if filepath.exists():
            if process_file(filepath):
                updated_count += 1
        else:
            print(f"\nWARNING: File not found: {filepath}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files processed: {len(FILES_TO_UPDATE)}")
    print(f"Files updated: {updated_count}")
    print(f"\nNew pages linked:")
    print(f"  - objectives.html (MoU Objectives)")
    print(f"  - gapg.html (Grant Period Goals)")


if __name__ == "__main__":
    main()
