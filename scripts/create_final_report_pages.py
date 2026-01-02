"""
Create Final Report HTML pages and Mid-Term vs Final comparison page.
Reads text extractions and generates styled GitHub Pages HTML.
"""

import re
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
FINAL_TXT = BASE_DIR / "FinalReport_in_progress" / "CA19130_FA_ActionChairReport_2026-01-02.txt"
MIDTERM_TXT = BASE_DIR / "MidTermReport" / "CA19130_PR2_ActionChairReport_2024-06-27 (1).txt"
OUTPUT_FINAL = BASE_DIR / "final-action-chair-report.html"
OUTPUT_COMPARISON = BASE_DIR / "comparison-action-chair.html"


def read_file(filepath):
    """Read file content."""
    return Path(filepath).read_text(encoding='utf-8')


def extract_key_metrics(text, is_final=False):
    """Extract key metrics from report text."""
    metrics = {
        'researchers': 0,
        'countries': 0,
        'cost_countries': 0,
        'wg1_members': 0,
        'wg2_members': 0,
        'wg3_members': 0,
        'conferences': 0,
        'participants': 0,
        'citations': 0,
        'website': '',
        'period': '',
        'title': ''
    }

    # Extract researchers count
    match = re.search(r'(\d+)\s+interdisciplinary researchers', text)
    if match:
        metrics['researchers'] = int(match.group(1))

    # Extract countries
    match = re.search(r'from\s+(\d+)\s+countries', text)
    if match:
        metrics['countries'] = int(match.group(1))

    # Extract COST countries
    match = re.search(r'(\d+)\s+of those countries being European COST countries', text)
    if match:
        metrics['cost_countries'] = int(match.group(1))

    # Extract WG membership from specific pattern
    wg_pattern = r'Transparency in FinTech\s+(\d+)'
    match = re.search(wg_pattern, text)
    if match:
        metrics['wg1_members'] = int(match.group(1))

    wg2_pattern = r'Transparent versus Black Box.*?(\d+)\s+Prof Petre Lameski'
    match = re.search(wg2_pattern, text, re.DOTALL)
    if match:
        metrics['wg2_members'] = int(match.group(1))

    wg3_pattern = r'Transparency into Investment.*?(\d+)\s+Prof Peter Schwendner'
    match = re.search(wg3_pattern, text, re.DOTALL)
    if match:
        metrics['wg3_members'] = int(match.group(1))

    # Extract conferences
    match = re.search(r'organized\s+(\d+)\s+research\s+conferences', text)
    if match:
        metrics['conferences'] = int(match.group(1))

    # Extract participants
    match = re.search(r'more than\s+([\d,]+)\s+participants', text)
    if match:
        metrics['participants'] = int(match.group(1).replace(',', ''))

    # Extract citations
    match = re.search(r'cited more than\s+([\d,]+)\s+times', text)
    if match:
        metrics['citations'] = int(match.group(1).replace(',', ''))

    # Extract website
    match = re.search(r'Action website\s+(https?://[^\s]+)', text)
    if match:
        metrics['website'] = match.group(1)

    # Extract period
    if is_final:
        match = re.search(r'\(14/09/2020 to 13/09/2024\)', text)
        if match:
            metrics['period'] = '14/09/2020 - 13/09/2024 (48 months)'
            metrics['title'] = 'Final Achievement Report'
    else:
        match = re.search(r'\(14/09/2020 to 14/09/2022\)', text)
        if match:
            metrics['period'] = '14/09/2020 - 14/09/2022 (24 months)'
            metrics['title'] = 'Progress Report at 24 months'

    return metrics


def extract_objectives(text):
    """Extract MoU objectives with achievement levels."""
    objectives = []

    # Pattern to find objectives
    obj_pattern = r'Mou objective\s+(.*?)Type of objective\s+(.*?)Level of (?:achievement|progress).*?(\d+\s*-\s*\d+%)'
    matches = re.findall(obj_pattern, text, re.DOTALL)

    for i, (desc, obj_type, level) in enumerate(matches, 1):
        objectives.append({
            'num': i,
            'description': desc.strip()[:200] + '...' if len(desc.strip()) > 200 else desc.strip(),
            'type': obj_type.strip()[:100] + '...' if len(obj_type.strip()) > 100 else obj_type.strip(),
            'level': level.strip()
        })

    return objectives


def extract_deliverables(text):
    """Extract deliverables with status."""
    deliverables = []

    # Pattern to find deliverables
    del_pattern = r'Deliverable\s+(.*?)Level of achievement.*?(Delivered|Not delivered|Expected)'
    matches = re.findall(del_pattern, text, re.DOTALL | re.IGNORECASE)

    for i, (desc, status) in enumerate(matches, 1):
        deliverables.append({
            'num': i,
            'description': desc.strip()[:150] + '...' if len(desc.strip()) > 150 else desc.strip(),
            'status': status.strip()
        })

    return deliverables


def extract_countries_list(text):
    """Extract list of participating countries."""
    countries = []
    country_codes = {
        'AL': 'Albania', 'AM': 'Armenia', 'AT': 'Austria', 'BE': 'Belgium',
        'BA': 'Bosnia and Herzegovina', 'BG': 'Bulgaria', 'HR': 'Croatia',
        'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DK': 'Denmark', 'EE': 'Estonia',
        'FI': 'Finland', 'FR': 'France', 'GE': 'Georgia', 'DE': 'Germany',
        'EL': 'Greece', 'HU': 'Hungary', 'IS': 'Iceland', 'IE': 'Ireland',
        'IL': 'Israel', 'IT': 'Italy', 'LV': 'Latvia', 'LT': 'Lithuania',
        'LU': 'Luxembourg', 'MT': 'Malta', 'MD': 'Moldova', 'ME': 'Montenegro',
        'NL': 'Netherlands', 'MK': 'North Macedonia', 'NO': 'Norway', 'PL': 'Poland',
        'PT': 'Portugal', 'RO': 'Romania', 'RS': 'Serbia', 'SK': 'Slovakia',
        'SI': 'Slovenia', 'ZA': 'South Africa', 'ES': 'Spain', 'SE': 'Sweden',
        'CH': 'Switzerland', 'TR': 'Turkey', 'UA': 'Ukraine', 'UK': 'United Kingdom'
    }

    for code, name in country_codes.items():
        if re.search(rf'\b{code}\b\s+\d{{2}}/\d{{2}}/\d{{4}}', text):
            countries.append(name)

    return sorted(countries)


def get_html_template():
    """Return base HTML template with COST styling."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - COST Action CA19130</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --cost-purple: #5B2D8A;
            --cost-blue: #2B5F9E;
            --cost-teal: #00A0B0;
            --cost-orange: #E87722;
            --cost-green: #7AB800;
            --cost-red: #DC3545;
            --dark: #1a1a2e;
            --light: #f8f9fa;
            --gray: #6c757d;
            --border: #dee2e6;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #333;
            background: var(--light);
        }}

        nav {{
            background: linear-gradient(135deg, var(--cost-purple) 0%, var(--cost-blue) 100%);
            padding: 1rem 2rem;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .nav-content {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            color: white;
            font-size: 1.4rem;
            font-weight: 700;
            text-decoration: none;
        }}

        .logo span {{ color: var(--cost-orange); }}

        .nav-links {{
            display: flex;
            gap: 1.5rem;
        }}

        .nav-links a {{
            color: white;
            text-decoration: none;
            font-size: 0.9rem;
            opacity: 0.9;
            transition: opacity 0.3s;
        }}

        .nav-links a:hover {{ opacity: 1; }}

        .hero {{
            background: linear-gradient(135deg, var(--cost-purple) 0%, var(--cost-blue) 100%);
            color: white;
            padding: 7rem 2rem 3rem;
            text-align: center;
        }}

        .hero h1 {{
            font-size: 2.2rem;
            margin-bottom: 0.5rem;
        }}

        .hero p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-top: 1rem;
        }}

        .badge-draft {{
            background: var(--cost-orange);
            color: white;
        }}

        .badge-internal {{
            background: rgba(255,255,255,0.2);
            color: white;
        }}

        .breadcrumb {{
            background: white;
            padding: 1rem 2rem;
            font-size: 0.85rem;
            border-bottom: 1px solid var(--border);
        }}

        .breadcrumb a {{
            color: var(--cost-purple);
            text-decoration: none;
        }}

        section {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        h2 {{
            color: var(--cost-purple);
            font-size: 1.6rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid var(--cost-orange);
        }}

        h3 {{
            color: var(--dark);
            font-size: 1.2rem;
            margin: 1.5rem 0 1rem;
        }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-box {{
            background: linear-gradient(135deg, var(--cost-purple) 0%, var(--cost-blue) 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
        }}

        .stat-box .value {{
            font-size: 2rem;
            font-weight: 700;
        }}

        .stat-box .label {{
            font-size: 0.8rem;
            opacity: 0.9;
        }}

        .objective-item {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--cost-purple);
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .objective-item h4 {{
            color: var(--cost-purple);
            margin-bottom: 0.5rem;
        }}

        .objective-item p {{
            color: var(--gray);
            font-size: 0.9rem;
        }}

        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 8px;
            margin-top: 0.5rem;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--cost-green) 0%, var(--cost-teal) 100%);
        }}

        .deliverable-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}

        .deliverable-table th {{
            background: var(--cost-purple);
            color: white;
            padding: 0.8rem;
            text-align: left;
            font-size: 0.85rem;
        }}

        .deliverable-table td {{
            padding: 0.8rem;
            border-bottom: 1px solid var(--border);
            font-size: 0.85rem;
        }}

        .deliverable-table tr:hover {{
            background: rgba(91,45,138,0.03);
        }}

        .status-badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .status-delivered {{
            background: rgba(122,184,0,0.15);
            color: #5a8a00;
        }}

        .status-expected {{
            background: rgba(232,119,34,0.15);
            color: #c66000;
        }}

        .country-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        .country-tag {{
            background: rgba(91,45,138,0.1);
            color: var(--cost-purple);
            padding: 0.3rem 0.6rem;
            border-radius: 15px;
            font-size: 0.75rem;
        }}

        /* Comparison specific styles */
        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }}

        .comparison-column {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }}

        .column-midterm {{
            border-top: 4px solid var(--cost-blue);
        }}

        .column-final {{
            border-top: 4px solid var(--cost-green);
        }}

        .column-header {{
            text-align: center;
            padding: 1rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }}

        .column-header h3 {{
            margin: 0;
            color: var(--dark);
        }}

        .column-header .period {{
            font-size: 0.85rem;
            color: var(--gray);
        }}

        .growth-indicator {{
            color: var(--cost-green);
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .growth-arrow {{
            font-size: 1.2rem;
        }}

        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.8rem 0;
            border-bottom: 1px solid var(--border);
        }}

        .metric-label {{
            font-weight: 500;
            color: var(--dark);
        }}

        .metric-value {{
            font-weight: 600;
        }}

        .new-badge {{
            background: var(--cost-green);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 10px;
            font-size: 0.7rem;
            margin-left: 0.5rem;
        }}

        .changed-badge {{
            background: var(--cost-orange);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 10px;
            font-size: 0.7rem;
            margin-left: 0.5rem;
        }}

        footer {{
            background: var(--dark);
            color: white;
            padding: 2rem;
            text-align: center;
        }}

        footer a {{
            color: var(--cost-orange);
            text-decoration: none;
            margin: 0 0.5rem;
        }}

        @media (max-width: 768px) {{
            .nav-links {{ display: none; }}
            .hero h1 {{ font-size: 1.6rem; }}
            .comparison-grid {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
{content}
</body>
</html>'''


def generate_final_report_html(text, metrics, objectives, deliverables, countries):
    """Generate the final report HTML page."""

    # Build stats grid
    stats_html = f'''
    <div class="stats-grid">
        <div class="stat-box">
            <div class="value">{metrics['researchers']}</div>
            <div class="label">Researchers</div>
        </div>
        <div class="stat-box">
            <div class="value">{metrics['countries']}</div>
            <div class="label">Countries</div>
        </div>
        <div class="stat-box">
            <div class="value">{metrics['conferences']}</div>
            <div class="label">Conferences</div>
        </div>
        <div class="stat-box">
            <div class="value">{metrics['participants']:,}</div>
            <div class="label">Participants</div>
        </div>
        <div class="stat-box">
            <div class="value">{metrics['citations']:,}+</div>
            <div class="label">Citations</div>
        </div>
        <div class="stat-box">
            <div class="value">{metrics['wg1_members'] + metrics['wg2_members'] + metrics['wg3_members']}</div>
            <div class="label">WG Members</div>
        </div>
    </div>'''

    # Build objectives section
    objectives_html = ''
    for obj in objectives[:16]:
        objectives_html += f'''
        <div class="objective-item">
            <h4>Objective {obj['num']}</h4>
            <p>{obj['description']}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 90%;"></div>
            </div>
            <small style="color: var(--gray);">Achievement: {obj['level']}</small>
        </div>'''

    # Build deliverables table
    deliverables_html = '''
    <table class="deliverable-table">
        <thead>
            <tr>
                <th>#</th>
                <th>Deliverable</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>'''

    for d in deliverables[:15]:
        status_class = 'status-delivered' if 'delivered' in d['status'].lower() else 'status-expected'
        deliverables_html += f'''
            <tr>
                <td>{d['num']}</td>
                <td>{d['description']}</td>
                <td><span class="status-badge {status_class}">{d['status']}</span></td>
            </tr>'''

    deliverables_html += '''
        </tbody>
    </table>'''

    # Build countries grid
    countries_html = '<div class="country-grid">'
    for country in countries:
        countries_html += f'<span class="country-tag">{country}</span>'
    countries_html += '</div>'

    # Working groups section
    wg_html = f'''
    <div class="card">
        <h3>Working Groups</h3>
        <div class="stats-grid">
            <div class="stat-box" style="background: linear-gradient(135deg, #6B3D9A 0%, #4A2870 100%);">
                <div class="value">{metrics['wg1_members']}</div>
                <div class="label">WG1: Transparency in FinTech</div>
            </div>
            <div class="stat-box" style="background: linear-gradient(135deg, #3B6FAE 0%, #2B5F9E 100%);">
                <div class="value">{metrics['wg2_members']}</div>
                <div class="label">WG2: Black Box Models</div>
            </div>
            <div class="stat-box" style="background: linear-gradient(135deg, #00B0C0 0%, #00A0B0 100%);">
                <div class="value">{metrics['wg3_members']}</div>
                <div class="label">WG3: Investment Performance</div>
            </div>
        </div>
    </div>'''

    content = f'''
    <nav>
        <div class="nav-content">
            <a href="index.html" class="logo">COST <span>CA19130</span></a>
            <div class="nav-links">
                <a href="index.html">Home</a>
                <a href="midterm-report.html">Mid-Term Report</a>
                <a href="comparison-action-chair.html">Comparison</a>
                <a href="leadership.html">Leadership</a>
                <a href="publications.html">Publications</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <h1>Final Achievement Report</h1>
        <p>COST Action CA19130: Fintech and Artificial Intelligence in Finance</p>
        <p style="opacity: 0.8; margin-top: 0.5rem;">Period: {metrics['period']}</p>
        <span class="badge badge-draft">DRAFT</span>
        <span class="badge badge-internal">Internal Document</span>
    </header>

    <div class="breadcrumb">
        <a href="index.html">Home</a> / <a href="midterm-report.html">Reports</a> / <span>Final Achievement Report</span>
    </div>

    <section>
        <h2>Executive Summary</h2>
        {stats_html}

        <div class="card">
            <h3>Main Objective</h3>
            <p>Establish a large and interconnected community across academia, public institutions and industry focusing on Financial Technology and Artificial Intelligence, improving transparency in financial services, especially in and through FinTech, in financial modelling and investment performance evaluation.</p>
        </div>

        <div class="card">
            <h3>Key Achievement</h3>
            <p>The COST Action on Fintech and AI in Finance has brought together an incredibly diverse network of <strong>{metrics['researchers']} interdisciplinary researchers</strong> from <strong>{metrics['countries']} countries</strong>, with {metrics['cost_countries']} European COST countries, becoming one of the largest and most active COST Actions in Europe.</p>
        </div>
    </section>

    <section>
        <h2>Leadership & Working Groups</h2>

        <div class="card">
            <h3>Action Leadership</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <div>
                    <strong>Chair:</strong> Prof Jorg Osterrieder<br>
                    <small style="color: var(--gray);">Netherlands</small>
                </div>
                <div>
                    <strong>Vice-Chair:</strong> Prof Valerio Poti<br>
                    <small style="color: var(--gray);">Ireland</small>
                </div>
                <div>
                    <strong>Science Communication:</strong> Dr Ioana Coita<br>
                    <small style="color: var(--gray);">Romania</small>
                </div>
                <div>
                    <strong>GH Scientific Rep:</strong> Branka Hadji Misheva<br>
                    <small style="color: var(--gray);">Switzerland</small>
                </div>
            </div>
        </div>

        {wg_html}
    </section>

    <section>
        <h2>Participating Countries ({len(countries)})</h2>
        <div class="card">
            {countries_html}
        </div>
    </section>

    <section>
        <h2>MoU Objectives ({len(objectives[:16])})</h2>
        {objectives_html}
    </section>

    <section>
        <h2>Deliverables</h2>
        <div class="card">
            {deliverables_html}
        </div>
    </section>

    <section>
        <h2>Knowledge Exchange Platforms</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
            <div class="card" style="border-top: 3px solid var(--cost-teal);">
                <h4>Quantlet.com</h4>
                <p style="font-size: 0.85rem; color: var(--gray);">Repository of reproducible code pieces for academic research in finance and data science.</p>
            </div>
            <div class="card" style="border-top: 3px solid var(--cost-teal);">
                <h4>Quantinar.com</h4>
                <p style="font-size: 0.85rem; color: var(--gray);">Training and dissemination platform with fundamentals of FinTech and cutting-edge research.</p>
            </div>
            <div class="card" style="border-top: 3px solid var(--cost-teal);">
                <h4>ExplainableAIforFinance.com</h4>
                <p style="font-size: 0.85rem; color: var(--gray);">Extensive platform on XAI with use cases, papers, code repositories, and interactive apps.</p>
            </div>
            <div class="card" style="border-top: 3px solid var(--cost-teal);">
                <h4>Blockchain Research Center</h4>
                <p style="font-size: 0.85rem; color: var(--gray);">Datasets and resources for blockchain and cryptocurrency research.</p>
            </div>
        </div>
    </section>

    <footer>
        <p>COST Action CA19130 - Fintech and Artificial Intelligence in Finance</p>
        <div>
            <a href="{metrics['website']}" target="_blank">Action Website</a>
            <a href="https://www.cost.eu/actions/CA19130/" target="_blank">COST Website</a>
            <a href="comparison-action-chair.html">Compare with Mid-Term</a>
        </div>
        <p style="margin-top: 1rem; opacity: 0.7; font-size: 0.85rem;">Final Achievement Report (DRAFT) | Generated: {datetime.now().strftime('%Y-%m-%d')}</p>
    </footer>'''

    template = get_html_template()
    return template.format(title='Final Achievement Report (DRAFT)', content=content)


def generate_comparison_html(midterm_metrics, final_metrics, midterm_objectives, final_objectives):
    """Generate the comparison HTML page."""

    def calc_growth(final_val, midterm_val):
        diff = final_val - midterm_val
        if diff > 0:
            return f'<span class="growth-indicator"><span class="growth-arrow">+</span>{diff}</span>'
        elif diff < 0:
            return f'<span style="color: var(--cost-red);">{diff}</span>'
        return '<span style="color: var(--gray);">-</span>'

    # Key metrics comparison
    metrics_comparison = f'''
    <div class="comparison-grid">
        <div class="comparison-column column-midterm">
            <div class="column-header">
                <h3>Mid-Term Report</h3>
                <p class="period">{midterm_metrics['period']}</p>
            </div>
            <div class="metric-row">
                <span class="metric-label">Researchers</span>
                <span class="metric-value">{midterm_metrics['researchers']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Countries</span>
                <span class="metric-value">{midterm_metrics['countries']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">WG1 Members</span>
                <span class="metric-value">{midterm_metrics['wg1_members']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">WG2 Members</span>
                <span class="metric-value">{midterm_metrics['wg2_members']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">WG3 Members</span>
                <span class="metric-value">{midterm_metrics['wg3_members']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Conferences</span>
                <span class="metric-value">{midterm_metrics['conferences']}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Website</span>
                <span class="metric-value" style="font-size: 0.8rem;">fin-ai.eu</span>
            </div>
        </div>

        <div class="comparison-column column-final">
            <div class="column-header">
                <h3>Final Report</h3>
                <p class="period">{final_metrics['period']}</p>
                <span class="badge badge-draft" style="font-size: 0.7rem;">DRAFT</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Researchers</span>
                <span class="metric-value">{final_metrics['researchers']} {calc_growth(final_metrics['researchers'], midterm_metrics['researchers'])}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Countries</span>
                <span class="metric-value">{final_metrics['countries']} {calc_growth(final_metrics['countries'], midterm_metrics['countries'])}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">WG1 Members</span>
                <span class="metric-value">{final_metrics['wg1_members']} {calc_growth(final_metrics['wg1_members'], midterm_metrics['wg1_members'])}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">WG2 Members</span>
                <span class="metric-value">{final_metrics['wg2_members']} {calc_growth(final_metrics['wg2_members'], midterm_metrics['wg2_members'])}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">WG3 Members</span>
                <span class="metric-value">{final_metrics['wg3_members']} {calc_growth(final_metrics['wg3_members'], midterm_metrics['wg3_members'])}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Conferences</span>
                <span class="metric-value">{final_metrics['conferences']} {calc_growth(final_metrics['conferences'], midterm_metrics['conferences'])}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">Website</span>
                <span class="metric-value" style="font-size: 0.8rem;">fintech-ai-finance.com<span class="changed-badge">CHANGED</span></span>
            </div>
        </div>
    </div>'''

    # Summary growth stats
    total_wg_midterm = midterm_metrics['wg1_members'] + midterm_metrics['wg2_members'] + midterm_metrics['wg3_members']
    total_wg_final = final_metrics['wg1_members'] + final_metrics['wg2_members'] + final_metrics['wg3_members']

    growth_summary = f'''
    <div class="card">
        <h3>Growth Summary</h3>
        <div class="stats-grid">
            <div class="stat-box" style="background: linear-gradient(135deg, var(--cost-green) 0%, #5a8a00 100%);">
                <div class="value">+{final_metrics['researchers'] - midterm_metrics['researchers']}</div>
                <div class="label">New Researchers</div>
            </div>
            <div class="stat-box" style="background: linear-gradient(135deg, var(--cost-green) 0%, #5a8a00 100%);">
                <div class="value">+{final_metrics['countries'] - midterm_metrics['countries']}</div>
                <div class="label">New Countries</div>
            </div>
            <div class="stat-box" style="background: linear-gradient(135deg, var(--cost-green) 0%, #5a8a00 100%);">
                <div class="value">+{total_wg_final - total_wg_midterm}</div>
                <div class="label">WG Growth</div>
            </div>
            <div class="stat-box" style="background: linear-gradient(135deg, var(--cost-teal) 0%, #008090 100%);">
                <div class="value">{round((final_metrics['researchers']/midterm_metrics['researchers']-1)*100)}%</div>
                <div class="label">Network Growth</div>
            </div>
        </div>
    </div>'''

    # Objectives comparison (side by side for first few)
    obj_comparison = '''
    <h3>Objectives Progress Comparison</h3>
    <div class="card">
        <p style="margin-bottom: 1rem; color: var(--gray);">All 16 MoU objectives achieved 76-100% in both reports. Key objectives comparison:</p>
        <table class="deliverable-table">
            <thead>
                <tr>
                    <th>Objective</th>
                    <th>Mid-Term</th>
                    <th>Final</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>'''

    for i in range(min(8, len(midterm_objectives), len(final_objectives))):
        mid_obj = midterm_objectives[i] if i < len(midterm_objectives) else {'level': 'N/A', 'description': 'N/A'}
        fin_obj = final_objectives[i] if i < len(final_objectives) else {'level': 'N/A', 'description': 'N/A'}

        desc = fin_obj.get('description', mid_obj.get('description', 'Objective'))[:80] + '...'

        obj_comparison += f'''
                <tr>
                    <td>Obj {i+1}: {desc}</td>
                    <td>{mid_obj.get('level', 'N/A')}</td>
                    <td>{fin_obj.get('level', 'N/A')}</td>
                    <td><span class="status-badge status-delivered">Maintained</span></td>
                </tr>'''

    obj_comparison += '''
            </tbody>
        </table>
    </div>'''

    # Sections comparison
    sections_comparison = '''
    <h3>Document Sections Comparison</h3>
    <div class="comparison-grid">
        <div class="comparison-column column-midterm">
            <div class="column-header">
                <h4>Mid-Term Report Sections</h4>
            </div>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">1. Leadership Positions</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">2. Working Groups</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">3. Participants</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">4. Summary</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">5. MoU Objectives (16)</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">6. Deliverables</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">7. Additional Outputs</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">8. Co-authored Publications</li>
                <li style="padding: 0.5rem 0;">9. Future Plans (GP3/GP4)</li>
            </ul>
        </div>

        <div class="comparison-column column-final">
            <div class="column-header">
                <h4>Final Report Sections</h4>
            </div>
            <ul style="list-style: none; padding: 0;">
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">1. Leadership Positions</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">2. Working Groups</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">3. Participants</li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">4. Summary <span class="changed-badge">UPDATED</span></li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">5. MoU Objectives (16) <span class="changed-badge">FINALIZED</span></li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">6. Deliverables <span class="changed-badge">ALL DELIVERED</span></li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">7. Additional Outputs <span class="new-badge">EXPANDED</span></li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">8. Co-authored Publications <span class="new-badge">100+</span></li>
                <li style="padding: 0.5rem 0;">9. Impacts <span class="new-badge">NEW</span></li>
            </ul>
        </div>
    </div>'''

    content = f'''
    <nav>
        <div class="nav-content">
            <a href="index.html" class="logo">COST <span>CA19130</span></a>
            <div class="nav-links">
                <a href="index.html">Home</a>
                <a href="midterm-action-chair-report.html">Mid-Term</a>
                <a href="final-action-chair-report.html">Final Report</a>
                <a href="leadership.html">Leadership</a>
            </div>
        </div>
    </nav>

    <header class="hero">
        <h1>Mid-Term vs Final Report Comparison</h1>
        <p>Action Chair Reports: Progress Over Time</p>
        <p style="opacity: 0.8; margin-top: 0.5rem;">Comparing 24-month and 48-month achievements</p>
    </header>

    <div class="breadcrumb">
        <a href="index.html">Home</a> / <a href="midterm-report.html">Reports</a> / <span>Comparison</span>
    </div>

    <section>
        <h2>Key Metrics Comparison</h2>
        {metrics_comparison}
    </section>

    <section>
        {growth_summary}
    </section>

    <section>
        <h2>Objectives & Content</h2>
        {obj_comparison}
        {sections_comparison}
    </section>

    <section>
        <h2>Key Changes Highlighted</h2>
        <div class="card">
            <h4>Website Change</h4>
            <p>The Action website changed from <code>fin-ai.eu</code> to <code>fintech-ai-finance.com</code> during the Action period.</p>
        </div>
        <div class="card">
            <h4>Network Growth</h4>
            <p>The network grew from <strong>{midterm_metrics['researchers']} to {final_metrics['researchers']} researchers</strong> (+{final_metrics['researchers'] - midterm_metrics['researchers']}),
            representing a <strong>{round((final_metrics['researchers']/midterm_metrics['researchers']-1)*100)}% increase</strong> in network size.</p>
        </div>
        <div class="card">
            <h4>Geographic Expansion</h4>
            <p>The Action expanded from <strong>{midterm_metrics['countries']} to {final_metrics['countries']} countries</strong> (+{final_metrics['countries'] - midterm_metrics['countries']} new countries joined).</p>
        </div>
        <div class="card">
            <h4>Deliverables Completion</h4>
            <p>All planned deliverables were marked as <strong>Delivered</strong> in the Final Report, demonstrating full achievement of Action goals.</p>
        </div>
    </section>

    <footer>
        <p>COST Action CA19130 - Fintech and Artificial Intelligence in Finance</p>
        <div>
            <a href="midterm-action-chair-report.html">Mid-Term Report</a>
            <a href="final-action-chair-report.html">Final Report</a>
            <a href="index.html">Home</a>
        </div>
        <p style="margin-top: 1rem; opacity: 0.7; font-size: 0.85rem;">Comparison Page | Generated: {datetime.now().strftime('%Y-%m-%d')}</p>
    </footer>'''

    template = get_html_template()
    return template.format(title='Mid-Term vs Final Comparison', content=content)


def main():
    """Main function to generate HTML pages."""
    print("=" * 60)
    print("COST Action Chair Report HTML Generator")
    print("=" * 60)

    # Check files exist
    if not FINAL_TXT.exists():
        print(f"ERROR: Final report not found: {FINAL_TXT}")
        return
    if not MIDTERM_TXT.exists():
        print(f"ERROR: Mid-term report not found: {MIDTERM_TXT}")
        return

    print(f"Reading Final Report: {FINAL_TXT.name}")
    final_text = read_file(FINAL_TXT)
    print(f"  -> {len(final_text):,} characters")

    print(f"Reading Mid-Term Report: {MIDTERM_TXT.name}")
    midterm_text = read_file(MIDTERM_TXT)
    print(f"  -> {len(midterm_text):,} characters")

    # Extract data
    print("\nExtracting metrics from Final Report...")
    final_metrics = extract_key_metrics(final_text, is_final=True)
    print(f"  Researchers: {final_metrics['researchers']}")
    print(f"  Countries: {final_metrics['countries']}")
    print(f"  WG Members: {final_metrics['wg1_members']} + {final_metrics['wg2_members']} + {final_metrics['wg3_members']}")

    print("\nExtracting metrics from Mid-Term Report...")
    midterm_metrics = extract_key_metrics(midterm_text, is_final=False)
    print(f"  Researchers: {midterm_metrics['researchers']}")
    print(f"  Countries: {midterm_metrics['countries']}")
    print(f"  WG Members: {midterm_metrics['wg1_members']} + {midterm_metrics['wg2_members']} + {midterm_metrics['wg3_members']}")

    print("\nExtracting objectives...")
    final_objectives = extract_objectives(final_text)
    midterm_objectives = extract_objectives(midterm_text)
    print(f"  Final: {len(final_objectives)} objectives")
    print(f"  Mid-Term: {len(midterm_objectives)} objectives")

    print("\nExtracting deliverables...")
    final_deliverables = extract_deliverables(final_text)
    print(f"  Final: {len(final_deliverables)} deliverables")

    print("\nExtracting countries...")
    countries = extract_countries_list(final_text)
    print(f"  Found: {len(countries)} countries")

    # Generate HTML files
    print("\n" + "=" * 60)
    print("Generating HTML files...")

    # Generate Final Report HTML
    print(f"\nGenerating: {OUTPUT_FINAL.name}")
    final_html = generate_final_report_html(final_text, final_metrics, final_objectives, final_deliverables, countries)
    OUTPUT_FINAL.write_text(final_html, encoding='utf-8')
    print(f"  -> {len(final_html):,} characters written")

    # Generate Comparison HTML
    print(f"\nGenerating: {OUTPUT_COMPARISON.name}")
    comparison_html = generate_comparison_html(midterm_metrics, final_metrics, midterm_objectives, final_objectives)
    OUTPUT_COMPARISON.write_text(comparison_html, encoding='utf-8')
    print(f"  -> {len(comparison_html):,} characters written")

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print(f"Generated files:")
    print(f"  1. {OUTPUT_FINAL}")
    print(f"  2. {OUTPUT_COMPARISON}")
    print("=" * 60)


if __name__ == "__main__":
    main()
