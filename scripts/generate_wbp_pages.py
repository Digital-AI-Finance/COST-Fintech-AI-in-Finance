"""
Generate WBP HTML pages from extracted JSON data.

Creates:
- work-budget-plans/objectives.html - MoU Objectives page
- work-budget-plans/gapg.html - Grant Period Goals page
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "work-budget-plans"
TEMPLATE_FILE = OUTPUT_DIR / "deliverables.html"


def load_json(filename: str) -> dict:
    """Load JSON data from data directory."""
    with open(DATA_DIR / filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_template_parts(template_path: Path) -> tuple:
    """
    Extract header and footer from template file.
    Returns (header_html, footer_html).
    """
    content = template_path.read_text(encoding='utf-8')

    # Find the breadcrumb div - content starts after the sidebar layout stuff
    breadcrumb_start = content.find('<div class="breadcrumb">')
    if breadcrumb_start == -1:
        raise ValueError("Could not find breadcrumb in template")

    # Find footer
    footer_start = content.find('<footer')
    if footer_start == -1:
        footer_start = content.find('<!-- Legacy Footer -->')

    header = content[:breadcrumb_start]
    footer = content[footer_start:] if footer_start != -1 else "</body></html>"

    return header, footer


def generate_objectives_page():
    """Generate the MoU Objectives HTML page."""
    print("Generating objectives.html...")

    mou = load_json("mou_objectives.json")
    header, footer = get_template_parts(TEMPLATE_FILE)

    # Update title in header
    header = header.replace(
        '<title>Deliverables - Work &amp; Budget Plans - COST CA19130</title>',
        '<title>MoU Objectives - Work &amp; Budget Plans - COST CA19130</title>'
    )
    header = header.replace(
        '<title>Deliverables - Work & Budget Plans - COST CA19130</title>',
        '<title>MoU Objectives - Work & Budget Plans - COST CA19130</title>'
    )

    # Build content
    content = f'''
    <div class="breadcrumb">
        <a href="../index.html">Home</a> / <a href="index.html">Work & Budget Plans</a> / <span>MoU Objectives</span>
    </div>

    <div class="hero-small">
        <h1>MoU Objectives</h1>
        <p>Memorandum of Understanding objectives for COST Action CA19130</p>
    </div>

    <section>
        <div class="stats">
            <div class="stat-box"><div class="num">1</div><div class="label">Primary Objective</div></div>
            <div class="stat-box"><div class="num">16</div><div class="label">Secondary Objectives</div></div>
            <div class="stat-box"><div class="num">100%</div><div class="label">Achievement Rate</div></div>
        </div>

        <h2>Primary Objective (Aim)</h2>
        <div class="card" style="background: linear-gradient(135deg, rgba(91, 45, 138, 0.1), rgba(43, 95, 158, 0.1)); border-left: 4px solid var(--cost-purple);">
            <p style="font-size: 1rem; line-height: 1.8;">{mou['primary_objective']['description']}</p>
        </div>

        <h2>Secondary Objectives</h2>
'''

    # Group objectives by category
    categories = {}
    for obj in mou['secondary_objectives']:
        cat = obj.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(obj)

    category_names = {
        'research': 'Research Objectives',
        'capacity_building': 'Capacity Building',
        'dissemination': 'Dissemination & Outreach'
    }

    for cat, cat_name in category_names.items():
        if cat in categories:
            content += f'''
        <h3 style="color: var(--cost-teal); margin: 1.5rem 0 1rem; font-size: 1.1rem;">{cat_name}</h3>
'''
            for obj in categories[cat]:
                content += f'''
        <div class="deliverable-card">
            <div class="d-num">{obj['number']}</div>
            <div class="d-content">
                <h3>{obj['title']}</h3>
                <p class="d-desc">{obj['description']}</p>
            </div>
        </div>
'''

    content += '''
        <div class="nav-buttons" style="display: flex; justify-content: space-between; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border);">
            <a href="deliverables.html" style="color: var(--cost-purple); text-decoration: none; font-weight: 500;">View Deliverables</a>
            <a href="gapg.html" style="color: var(--cost-purple); text-decoration: none; font-weight: 500;">View Grant Period Goals</a>
        </div>
    </section>
'''

    # Write file
    output_path = OUTPUT_DIR / "objectives.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + content + footer)

    print(f"  Saved: {output_path}")


def generate_gapg_page():
    """Generate the Grant Period Goals HTML page."""
    print("Generating gapg.html...")

    gapgs = load_json("grant_period_goals.json")
    header, footer = get_template_parts(TEMPLATE_FILE)

    # Update title in header
    header = header.replace(
        '<title>Deliverables - Work &amp; Budget Plans - COST CA19130</title>',
        '<title>Grant Period Goals - Work &amp; Budget Plans - COST CA19130</title>'
    )
    header = header.replace(
        '<title>Deliverables - Work & Budget Plans - COST CA19130</title>',
        '<title>Grant Period Goals - Work & Budget Plans - COST CA19130</title>'
    )

    # Count totals
    total_gapgs = sum(gapgs['grant_periods'][f'GP{gp}']['gapg_count'] for gp in range(1, 6))

    # Build content
    content = f'''
    <div class="breadcrumb">
        <a href="../index.html">Home</a> / <a href="index.html">Work & Budget Plans</a> / <span>Grant Period Goals</span>
    </div>

    <div class="hero-small">
        <h1>Grant Period Goals</h1>
        <p>GAPGs define specific objectives for each grant period</p>
    </div>

    <section>
        <div class="stats">
            <div class="stat-box"><div class="num">{total_gapgs}</div><div class="label">Total GAPGs</div></div>
            <div class="stat-box"><div class="num">5</div><div class="label">Grant Periods</div></div>
            <div class="stat-box"><div class="num">100%</div><div class="label">Achieved</div></div>
        </div>

        <div class="gp-nav" style="display: flex; justify-content: center; gap: 1rem; margin: 1.5rem 0; flex-wrap: wrap;">
            <a href="#gp1" style="padding: 0.5rem 1rem; background: white; border-radius: 8px; text-decoration: none; color: var(--cost-purple); box-shadow: 0 2px 10px rgba(0,0,0,0.08); font-weight: 500;">GP1</a>
            <a href="#gp2" style="padding: 0.5rem 1rem; background: white; border-radius: 8px; text-decoration: none; color: var(--cost-purple); box-shadow: 0 2px 10px rgba(0,0,0,0.08); font-weight: 500;">GP2</a>
            <a href="#gp3" style="padding: 0.5rem 1rem; background: white; border-radius: 8px; text-decoration: none; color: var(--cost-purple); box-shadow: 0 2px 10px rgba(0,0,0,0.08); font-weight: 500;">GP3</a>
            <a href="#gp4" style="padding: 0.5rem 1rem; background: white; border-radius: 8px; text-decoration: none; color: var(--cost-purple); box-shadow: 0 2px 10px rgba(0,0,0,0.08); font-weight: 500;">GP4</a>
            <a href="#gp5" style="padding: 0.5rem 1rem; background: white; border-radius: 8px; text-decoration: none; color: var(--cost-purple); box-shadow: 0 2px 10px rgba(0,0,0,0.08); font-weight: 500;">GP5</a>
        </div>
'''

    gp_periods = {
        1: "Nov 2020 - Oct 2021",
        2: "Nov 2021 - May 2022",
        3: "Jun 2022 - Oct 2022",
        4: "Nov 2022 - Oct 2023",
        5: "Nov 2023 - Sep 2024"
    }

    for gp in range(1, 6):
        gp_data = gapgs['grant_periods'][f'GP{gp}']
        count = gp_data['gapg_count']

        content += f'''
        <h2 id="gp{gp}">Grant Period {gp} <span style="font-size: 0.9rem; color: var(--gray); font-weight: normal;">({gp_periods[gp]})</span></h2>
        <p style="margin-bottom: 1rem; color: var(--gray);">{count} Grant Period Goals</p>
'''
        for g in gp_data['gapgs']:
            # Format MoU objectives
            mou_refs = ', '.join([f'Obj {n}' for n in g.get('mou_objectives', [])])
            if g.get('relates_to_primary_objective'):
                if mou_refs:
                    mou_refs = 'Primary, ' + mou_refs
                else:
                    mou_refs = 'Primary Objective'

            content += f'''
        <div class="deliverable-card">
            <div class="d-num">{g['gapg_number']}</div>
            <div class="d-content">
                <h3>{g['title']}</h3>
                <div class="d-meta">
                    <span>GP{gp}</span>
                    {f'<span>MoU: {mou_refs}</span>' if mou_refs else ''}
                </div>
            </div>
        </div>
'''

    content += '''
        <div class="nav-buttons" style="display: flex; justify-content: space-between; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border);">
            <a href="objectives.html" style="color: var(--cost-purple); text-decoration: none; font-weight: 500;">View MoU Objectives</a>
            <a href="deliverables.html" style="color: var(--cost-purple); text-decoration: none; font-weight: 500;">View Deliverables</a>
        </div>
    </section>
'''

    # Write file
    output_path = OUTPUT_DIR / "gapg.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + content + footer)

    print(f"  Saved: {output_path}")


def main():
    print("="*60)
    print("Generating WBP HTML Pages")
    print("="*60)

    generate_objectives_page()
    generate_gapg_page()

    print("\nDone!")
    print(f"Files created in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
