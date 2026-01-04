"""
Update full report files that don't have standard nav/footer
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

FULL_REPORTS = [
    'comparison-action-chair-full.html',
    'comparison-enhanced.html',
    'final-action-chair-report-full.html',
    'midterm-action-chair-report-full.html',
    'report-editor.html'
]

NAV_HTML = '''    <!-- COST CA19130 Legacy Archive - Mega Menu Navigation -->
    <nav class="mega-nav">
        <div class="mega-nav-content">
            <a href="index.html" class="mega-nav-logo">
                COST <span>CA19130</span>
                <span class="completed-badge">2020-2024</span>
            </a>
            <ul class="mega-nav-menu">
                <li><a href="index.html" data-category="home">HOME</a></li>
                <li>
                    <a href="#" data-category="impact">IMPACT <span class="arrow">&#9660;</span></a>
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
                    <a href="#" data-category="network">NETWORK <span class="arrow">&#9660;</span></a>
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
                    <a href="#" data-category="research">RESEARCH <span class="arrow">&#9660;</span></a>
                    <div class="mega-dropdown mega-dropdown-single">
                        <a href="publications.html">Publications</a>
                        <a href="preprints.html">Preprints</a>
                        <a href="datasets.html">Datasets</a>
                        <a href="other-outputs.html">Other Outputs</a>
                        <a href="documents.html">Documents</a>
                    </div>
                </li>
                <li>
                    <a href="#" data-category="activities">ACTIVITIES <span class="arrow">&#9660;</span></a>
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
                    <a href="#" data-category="archive">ARCHIVE <span class="arrow">&#9660;</span></a>
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
                </div>
            </li>
            <li>
                <button>NETWORK <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="members.html">All Members (426)</a>
                    <a href="leadership.html">Leadership Team</a>
                    <a href="mc-members.html">Management Committee</a>
                    <a href="wg-members.html">Working Groups</a>
                </div>
            </li>
            <li>
                <button>RESEARCH <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="publications.html">Publications</a>
                    <a href="preprints.html">Preprints</a>
                    <a href="datasets.html">Datasets</a>
                </div>
            </li>
            <li>
                <button>ACTIVITIES <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="financial-reports/meetings.html">All Meetings</a>
                    <a href="financial-reports/stsm.html">STSMs</a>
                    <a href="financial-reports/training-schools.html">Training Schools</a>
                </div>
            </li>
            <li>
                <button>ARCHIVE <span class="toggle-icon">+</span></button>
                <div class="mega-mobile-submenu">
                    <a href="final-action-chair-report-full.html">Final Report</a>
                    <a href="midterm-action-chair-report-full.html">Mid-Term Report</a>
                    <a href="progress-reports.html">Progress Reports</a>
                    <a href="report-editor.html">Report Editor</a>
                </div>
            </li>
        </ul>
    </div>
'''

def update_full_report(file_path):
    """Add navigation to full report files"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if nav already exists
    if 'mega-nav' in content:
        print(f"[--] {file_path.name} - Already has mega-nav")
        return False

    # Insert nav after <body>
    if '<body>' in content:
        content = content.replace('<body>', '<body>\n' + NAV_HTML)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] {file_path.name} - Added navigation")
        return True
    else:
        print(f"[!!] {file_path.name} - No <body> tag found")
        return False

def main():
    for filename in FULL_REPORTS:
        file_path = BASE_DIR / filename
        if file_path.exists():
            update_full_report(file_path)
        else:
            print(f"[??] {filename} - File not found")

if __name__ == '__main__':
    main()
