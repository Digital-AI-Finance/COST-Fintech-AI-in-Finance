"""
COST CA19130 Navigation Update Script
Updates all HTML files with new Legacy Archive mega-menu navigation
Created: 2026-01-03
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Navigation HTML for root-level pages
ROOT_NAV_HTML = '''    <!-- COST CA19130 Legacy Archive - Mega Menu Navigation -->
    <nav class="mega-nav">
        <div class="mega-nav-content">
            <a href="index.html" class="mega-nav-logo">
                COST <span>CA19130</span>
                <span class="completed-badge">2020-2024</span>
            </a>
            <ul class="mega-nav-menu">
                <li><a href="index.html" data-category="home">HOME</a></li>
                <li>
                    <a href="impact.html" data-category="impact">IMPACT <span class="arrow">&#9660;</span></a>
                    <div class="mega-dropdown mega-dropdown-single">
                        <a href="final-achievements.html">Final Achievements</a>
                        <a href="final-report.html">Objectives Met (16/16)</a>
                        <a href="work-budget-plans/deliverables.html">Deliverables Completed (15/15)</a>
                        <a href="final-impacts.html">Scientific Impact</a>
                        <a href="final-publications.html">Legacy & Continuation</a>
                        <a href="comparison-enhanced.html">Report Comparison</a>
                    </div>
                </li>
                <li>
                    <a href="network.html" data-category="network">NETWORK <span class="arrow">&#9660;</span></a>
                    <div class="mega-dropdown mega-dropdown-single">
                        <a href="members.html">All Members (426)</a>
                        <a href="leadership.html">Leadership Team</a>
                        <a href="mc-members.html">Management Committee (70)</a>
                        <a href="wg-members.html">Working Groups</a>
                        <a href="country-contributions.html">Countries (48)</a>
                        <a href="author-stats.html">Author Statistics</a>
                    </div>
                </li>
                <li>
                    <a href="research.html" data-category="research">RESEARCH <span class="arrow">&#9660;</span></a>
                    <div class="mega-dropdown mega-dropdown-single">
                        <a href="publications.html">Publications</a>
                        <a href="preprints.html">Preprints</a>
                        <a href="datasets.html">Datasets</a>
                        <a href="other-outputs.html">Other Outputs</a>
                        <a href="documents.html">Documents</a>
                    </div>
                </li>
                <li>
                    <a href="activities.html" data-category="activities">ACTIVITIES <span class="arrow">&#9660;</span></a>
                    <div class="mega-dropdown mega-dropdown-multi">
                        <div class="mega-dropdown-column">
                            <h4>Meetings</h4>
                            <a href="financial-reports/meetings.html">All Meetings</a>
                            <a href="progress-reports.html">By Grant Period</a>
                            <a href="financial-reports/participants.html">Participants</a>
                        </div>
                        <div class="mega-dropdown-column">
                            <h4>Mobility</h4>
                            <a href="financial-reports/stsm.html">STSMs</a>
                            <a href="financial-reports/virtual-mobility.html">Virtual Mobility</a>
                            <a href="financial-reports/countries.html">ITC Grants</a>
                        </div>
                        <div class="mega-dropdown-column">
                            <h4>Training</h4>
                            <a href="financial-reports/training-schools.html">Training Schools</a>
                        </div>
                    </div>
                </li>
                <li>
                    <a href="archive.html" data-category="archive">ARCHIVE <span class="arrow">&#9660;</span></a>
                    <div class="mega-dropdown mega-dropdown-multi wide">
                        <div class="mega-dropdown-column">
                            <h4>Reports</h4>
                            <a href="final-action-chair-report-full.html">Final Report (Full)</a>
                            <a href="midterm-action-chair-report-full.html">Mid-Term Report (Full)</a>
                            <a href="progress-reports.html">Progress Reports</a>
                            <a href="midterm-rapporteur-review.html">Rapporteur Review</a>
                        </div>
                        <div class="mega-dropdown-column">
                            <h4>Finances</h4>
                            <a href="financial-reports/overview.html">Financial Overview</a>
                            <a href="work-budget-plans/index.html">Budget Plans</a>
                            <a href="financial-reports/ffr1.html">FFR 1-5</a>
                        </div>
                        <div class="mega-dropdown-column">
                            <h4>Tools</h4>
                            <a href="report-editor.html">Report Editor</a>
                            <a href="comparison-enhanced.html">Report Comparison</a>
                        </div>
                    </div>
                </li>
            </ul>
            <button class="mega-nav-hamburger" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </nav>

    <!-- Mobile Menu -->
    <div class="mega-mobile-menu">
        <ul>
            <li><a href="index.html">HOME</a></li>
            <li>
                <button>IMPACT <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="final-achievements.html">Final Achievements</a>
                    <a href="final-report.html">Objectives Met (16/16)</a>
                    <a href="work-budget-plans/deliverables.html">Deliverables Completed</a>
                    <a href="final-impacts.html">Scientific Impact</a>
                    <a href="final-publications.html">Legacy & Continuation</a>
                    <a href="comparison-enhanced.html">Report Comparison</a>
                </div>
            </li>
            <li>
                <button>NETWORK <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="members.html">All Members (426)</a>
                    <a href="leadership.html">Leadership Team</a>
                    <a href="mc-members.html">Management Committee</a>
                    <a href="wg-members.html">Working Groups</a>
                    <a href="country-contributions.html">Countries (48)</a>
                    <a href="author-stats.html">Author Statistics</a>
                </div>
            </li>
            <li>
                <button>RESEARCH <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="publications.html">Publications</a>
                    <a href="preprints.html">Preprints</a>
                    <a href="datasets.html">Datasets</a>
                    <a href="other-outputs.html">Other Outputs</a>
                    <a href="documents.html">Documents</a>
                </div>
            </li>
            <li>
                <button>ACTIVITIES <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="financial-reports/meetings.html">All Meetings</a>
                    <a href="financial-reports/stsm.html">STSMs</a>
                    <a href="financial-reports/virtual-mobility.html">Virtual Mobility</a>
                    <a href="financial-reports/training-schools.html">Training Schools</a>
                </div>
            </li>
            <li>
                <button>ARCHIVE <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="final-action-chair-report-full.html">Final Report</a>
                    <a href="midterm-action-chair-report-full.html">Mid-Term Report</a>
                    <a href="progress-reports.html">Progress Reports</a>
                    <a href="financial-reports/overview.html">Financial Overview</a>
                    <a href="report-editor.html">Report Editor</a>
                </div>
            </li>
        </ul>
    </div>'''

ROOT_FOOTER_HTML = '''    <!-- Legacy Footer -->
    <footer class="legacy-footer">
        <div class="legacy-footer-content">
            <div class="legacy-footer-title">
                <h3>COST Action CA19130 - Fintech and Artificial Intelligence in Finance</h3>
                <p class="completed">October 2020 - October 2024 (Completed)</p>
            </div>
            <div class="legacy-footer-grid">
                <div class="legacy-footer-col">
                    <h4>Impact</h4>
                    <a href="final-achievements.html">Achievements</a>
                    <a href="final-report.html">16/16 Objectives</a>
                    <a href="work-budget-plans/deliverables.html">15/15 Deliverables</a>
                </div>
                <div class="legacy-footer-col">
                    <h4>Network</h4>
                    <a href="members.html">426 Members</a>
                    <a href="country-contributions.html">48 Countries</a>
                    <a href="leadership.html">Leadership</a>
                </div>
                <div class="legacy-footer-col">
                    <h4>Archive</h4>
                    <a href="final-action-chair-report-full.html">Final Report</a>
                    <a href="midterm-action-chair-report-full.html">Mid-Term Report</a>
                    <a href="financial-reports/overview.html">Financial Reports</a>
                </div>
            </div>
            <div class="legacy-footer-grid" style="margin-bottom: 0;">
                <div class="legacy-footer-col">
                    <h4>Connect</h4>
                    <a href="https://www.cost.eu/actions/CA19130/" target="_blank" rel="noopener">COST Official Page</a>
                    <a href="https://fin-ai.eu" target="_blank" rel="noopener">fin-ai.eu</a>
                    <a href="https://github.com/Digital-AI-Finance" target="_blank" rel="noopener">GitHub</a>
                </div>
            </div>
            <div class="legacy-footer-bottom">
                <p>Data sourced from <a href="https://openalex.org" target="_blank" rel="noopener">OpenAlex</a> and <a href="https://orcid.org" target="_blank" rel="noopener">ORCID</a> | Archive maintained since 2024</p>
            </div>
        </div>
    </footer>'''


def get_relative_path_prefix(file_path):
    """Get the relative path prefix for CSS/JS links based on file location"""
    rel_path = file_path.relative_to(BASE_DIR)
    depth = len(rel_path.parts) - 1
    if depth == 0:
        return ""
    return "../" * depth


def adjust_hrefs(html, prefix):
    """Adjust href paths for subdirectory files"""
    if not prefix:
        return html

    # Adjust relative hrefs (not absolute URLs or anchors)
    def replace_href(match):
        href = match.group(1)
        if href.startswith(('http', '#', 'mailto:', 'tel:')):
            return match.group(0)
        return f'href="{prefix}{href}"'

    html = re.sub(r'href="([^"]+)"', replace_href, html)
    return html


def update_html_file(file_path):
    """Update a single HTML file with new navigation"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        prefix = get_relative_path_prefix(file_path)

        # Adjust navigation and footer for subdirectories
        nav_html = adjust_hrefs(ROOT_NAV_HTML, prefix)
        footer_html = adjust_hrefs(ROOT_FOOTER_HTML, prefix)

        # Add CSS link if not present
        if 'mega-menu.css' not in content:
            css_link = f'    <link rel="stylesheet" href="{prefix}css/mega-menu.css">\n'
            # Insert before </head> or after last link/script in head
            if '</head>' in content:
                content = content.replace('</head>', f'{css_link}</head>')

        # Replace existing nav with new nav
        # Pattern to match various nav structures
        nav_patterns = [
            r'<nav[^>]*>[\s\S]*?</nav>',
            r'<nav\s*>[\s\S]*?</nav>',
        ]

        nav_replaced = False
        for pattern in nav_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, nav_html, content, count=1, flags=re.IGNORECASE)
                nav_replaced = True
                break

        # Replace existing footer with new footer
        footer_patterns = [
            r'<footer[^>]*>[\s\S]*?</footer>',
            r'<footer\s*>[\s\S]*?</footer>',
        ]

        footer_replaced = False
        for pattern in footer_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, footer_html, content, count=1, flags=re.IGNORECASE)
                footer_replaced = True
                break

        # Add JS script if not present
        if 'mobile-menu.js' not in content:
            js_script = f'    <script src="{prefix}js/mobile-menu.js"></script>\n'
            # Insert before </body>
            if '</body>' in content:
                content = content.replace('</body>', f'{js_script}</body>')

        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, nav_replaced, footer_replaced

        return False, nav_replaced, footer_replaced

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, False, False


def main():
    """Main function to update all HTML files"""
    # Get all HTML files
    html_files = []

    # Root level files (exclude index.html as it's already done)
    for f in BASE_DIR.glob('*.html'):
        if f.name != 'index.html':
            html_files.append(f)

    # Subdirectory files
    for subdir in ['financial-reports', 'work-budget-plans']:
        subdir_path = BASE_DIR / subdir
        if subdir_path.exists():
            for f in subdir_path.glob('*.html'):
                html_files.append(f)

    print(f"Found {len(html_files)} HTML files to update (excluding index.html)")
    print("-" * 50)

    updated_count = 0
    nav_count = 0
    footer_count = 0

    for file_path in sorted(html_files):
        rel_path = file_path.relative_to(BASE_DIR)
        updated, nav_ok, footer_ok = update_html_file(file_path)

        status = []
        if updated:
            updated_count += 1
            if nav_ok:
                nav_count += 1
                status.append("nav")
            if footer_ok:
                footer_count += 1
                status.append("footer")
            print(f"[OK] {rel_path} - Updated: {', '.join(status) if status else 'CSS/JS only'}")
        else:
            print(f"[--] {rel_path} - No changes needed")

    print("-" * 50)
    print(f"Summary:")
    print(f"  Files updated: {updated_count}/{len(html_files)}")
    print(f"  Navigation replaced: {nav_count}")
    print(f"  Footer replaced: {footer_count}")


if __name__ == '__main__':
    main()
