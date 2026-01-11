"""
Enhance GP Pages - Add GAPGs, planned meetings, and training schools.

Updates gp1-5.html with rich content from WBP extraction.
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
WBP_DIR = DATA_DIR / "wbp"
HTML_DIR = Path(__file__).parent.parent / "work-budget-plans"


def load_gapgs() -> dict:
    """Load GAPGs data."""
    with open(DATA_DIR / "grant_period_goals.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def load_wbp_data(gp: int) -> dict:
    """Load WBP data for a grant period."""
    filepath = WBP_DIR / f"wbp_gp{gp}.json"
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_gapg_section(gp: int, gapgs_data: dict) -> str:
    """Generate HTML for Grant Period Goals section."""
    gp_gapgs = gapgs_data['grant_periods'][f'GP{gp}']
    count = gp_gapgs['gapg_count']
    gapgs = gp_gapgs['gapgs']

    html = f'''
        <h2>Grant Period Goals</h2>
        <div class="card">
            <p style="margin-bottom: 1rem; color: var(--gray);">{count} GAPGs defined for Grant Period {gp}</p>
'''

    for g in gapgs:
        # Format MoU objectives
        mou_refs = []
        if g.get('relates_to_primary_objective'):
            mou_refs.append('Primary')
        for obj_num in g.get('mou_objectives', []):
            mou_refs.append(f'Obj {obj_num}')
        mou_text = ', '.join(mou_refs) if mou_refs else ''

        # Truncate title if too long
        title = g['description']
        if len(title) > 120:
            title = title[:117] + '...'

        html += f'''
            <div style="display: flex; gap: 1rem; padding: 0.75rem; border-bottom: 1px solid var(--border); align-items: flex-start;">
                <div style="background: var(--cost-purple); color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-weight: 600; font-size: 0.8rem; min-width: 40px; text-align: center;">G{g['gapg_number']}</div>
                <div style="flex: 1;">
                    <div style="font-size: 0.9rem; color: var(--dark);">{title}</div>
                    {f'<div style="font-size: 0.75rem; color: var(--gray); margin-top: 0.25rem;">MoU: {mou_text}</div>' if mou_text else ''}
                </div>
            </div>
'''

    html += '''
            <p style="margin-top: 1rem; font-size: 0.85rem;"><a href="gapg.html" style="color: var(--cost-purple);">View all GAPGs across all grant periods</a></p>
        </div>
'''
    return html


def generate_meetings_section(gp: int, wbp_data: dict) -> str:
    """Generate HTML for Planned Meetings section."""
    meetings = wbp_data.get('meetings', [])

    if not meetings:
        return ''

    html = f'''
        <h2>Planned Meetings (WBP)</h2>
        <div class="card">
            <p style="margin-bottom: 1rem; color: var(--gray);">{len(meetings)} meeting(s) planned in Work & Budget Plan</p>
            <table>
                <thead>
                    <tr><th>#</th><th>Title</th><th>Dates</th><th>Location</th></tr>
                </thead>
                <tbody>
'''

    for m in meetings:
        title = m.get('title', 'Unknown')
        if len(title) > 60:
            title = title[:57] + '...'

        start = m.get('start_date', '')
        end = m.get('end_date', '')
        if start and end:
            dates = f"{start} to {end}"
        elif start:
            dates = start
        else:
            dates = 'TBD'

        location = m.get('location', '')
        country = m.get('country', '')
        loc_str = f"{location}, {country}" if location and country else location or country or 'TBD'

        html += f'''
                    <tr>
                        <td>{m.get('meeting_number', '')}</td>
                        <td>{title}</td>
                        <td>{dates}</td>
                        <td>{loc_str}</td>
                    </tr>
'''

    html += '''
                </tbody>
            </table>
        </div>
'''
    return html


def generate_training_schools_section(gp: int, wbp_data: dict) -> str:
    """Generate HTML for Training Schools section (GP4, GP5 only)."""
    schools = wbp_data.get('training_schools', [])

    if not schools:
        return ''

    html = f'''
        <h2>Planned Training Schools (WBP)</h2>
        <div class="card">
            <p style="margin-bottom: 1rem; color: var(--gray);">{len(schools)} training school(s) planned</p>
            <table>
                <thead>
                    <tr><th>#</th><th>Title</th><th>Dates</th><th>Location</th></tr>
                </thead>
                <tbody>
'''

    for i, ts in enumerate(schools, 1):
        title = ts.get('title', 'Training School')
        if len(title) > 60:
            title = title[:57] + '...'

        start = ts.get('start_date', '')
        end = ts.get('end_date', '')
        if start and end:
            dates = f"{start} to {end}"
        elif start:
            dates = start
        else:
            dates = 'TBD'

        location = ts.get('location', '')
        country = ts.get('country', '')
        loc_str = f"{location}, {country}" if location and country else location or country or 'TBD'

        html += f'''
                    <tr>
                        <td>{i}</td>
                        <td>{title}</td>
                        <td>{dates}</td>
                        <td>{loc_str}</td>
                    </tr>
'''

    html += '''
                </tbody>
            </table>
            <p style="margin-top: 1rem; font-size: 0.85rem;"><a href="../financial-reports/training-schools.html" style="color: var(--cost-purple);">View all training schools with details</a></p>
        </div>
'''
    return html


def enhance_gp_page(gp: int, gapgs_data: dict):
    """Enhance a single GP page."""
    print(f"\nEnhancing GP{gp} page...")

    filepath = HTML_DIR / f"gp{gp}.html"
    content = filepath.read_text(encoding='utf-8')

    # Check if already enhanced
    if 'Grant Period Goals</h2>' in content:
        print(f"  GP{gp} already enhanced - skipping")
        return False

    # Load WBP data
    wbp_data = load_wbp_data(gp)

    # Generate new sections
    gapg_html = generate_gapg_section(gp, gapgs_data)
    meetings_html = generate_meetings_section(gp, wbp_data)
    training_html = generate_training_schools_section(gp, wbp_data)

    # Combine new content
    new_sections = gapg_html + meetings_html + training_html

    # Find insertion point - after the Context card, before </section>
    # Look for the pattern: </div>\s*</section>
    # The Context card ends with </div> and then </section> follows

    # Find the Context section
    context_pattern = r'(<h2>Context</h2>\s*<div class="card">.*?</div>)'
    context_match = re.search(context_pattern, content, re.DOTALL)

    if context_match:
        # Insert after Context section
        insert_pos = context_match.end()
        new_content = content[:insert_pos] + new_sections + content[insert_pos:]

        filepath.write_text(new_content, encoding='utf-8')
        print(f"  Added: GAPGs ({gapgs_data['grant_periods'][f'GP{gp}']['gapg_count']}), Meetings ({len(wbp_data.get('meetings', []))}), Training Schools ({len(wbp_data.get('training_schools', []))})")
        return True
    else:
        # Fallback: insert before </section>
        section_end = content.rfind('</section>')
        if section_end != -1:
            new_content = content[:section_end] + new_sections + content[section_end:]
            filepath.write_text(new_content, encoding='utf-8')
            print(f"  Added (fallback): GAPGs, Meetings, Training Schools")
            return True
        else:
            print(f"  WARNING: Could not find insertion point in GP{gp}")
            return False


def main():
    print("=" * 60)
    print("Enhancing GP Pages with WBP Data")
    print("=" * 60)

    # Load GAPGs data
    gapgs_data = load_gapgs()

    enhanced = 0
    for gp in range(1, 6):
        if enhance_gp_page(gp, gapgs_data):
            enhanced += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Pages enhanced: {enhanced}/5")

    print("\nNew content added:")
    for gp in range(1, 6):
        count = gapgs_data['grant_periods'][f'GP{gp}']['gapg_count']
        print(f"  GP{gp}: {count} GAPGs")


if __name__ == "__main__":
    main()
