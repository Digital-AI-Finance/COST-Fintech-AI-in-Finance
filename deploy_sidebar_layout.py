"""
COST CA19130 Sidebar Layout Deployment Script (v2)
Non-destructive deployment that adds sidebar layout via CSS injection
Created: 2026-01-04
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# CSS that overrides existing styles and adds sidebar layout
SIDEBAR_CSS = '''
    <!-- SIDEBAR LAYOUT STYLES -->
    <style id="sidebar-layout-css">
        /* Hide old navigation */
        body > nav:not(.sl-topbar-tabs), .mega-nav, .mega-mobile-menu, .nav-content { display: none !important; }

        /* Override old nav styles that affect all nav elements */
        nav.sl-topbar-tabs {
            background: transparent !important;
            padding: 0 !important;
            position: static !important;
            width: auto !important;
            box-shadow: none !important;
        }

        /* Sidebar Layout Variables */
        :root {
            --sl-topbar-height: 36px;
            --sl-sidebar-width: 160px;
        }

        /* Push all body content to make room for sidebar */
        body {
            padding-top: var(--sl-topbar-height) !important;
            padding-left: var(--sl-sidebar-width) !important;
        }

        /* Top Bar */
        .sl-topbar {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            height: var(--sl-topbar-height) !important;
            background: linear-gradient(135deg, #5B2D8A 0%, #2B5F9E 100%) !important;
            z-index: 10001 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            padding: 0 0.75rem !important;
            box-shadow: 0 1px 6px rgba(0,0,0,0.12) !important;
            font-family: 'Inter', -apple-system, sans-serif !important;
        }

        .sl-topbar-logo {
            display: flex !important;
            align-items: center !important;
            text-decoration: none !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 0.85rem !important;
        }
        .sl-topbar-logo .action-id { color: #E87722 !important; margin-left: 0.2rem !important; }
        .sl-topbar-logo .badge {
            font-size: 0.5rem !important;
            background: rgba(255,255,255,0.2) !important;
            padding: 0.1rem 0.35rem !important;
            border-radius: 2px !important;
            margin-left: 0.5rem !important;
        }

        .sl-topbar-tabs {
            display: flex !important;
            align-items: center !important;
            height: 100% !important;
        }

        .sl-topbar-tab {
            background: transparent !important;
            border: none !important;
            cursor: pointer !important;
            height: 100% !important;
            padding: 0 0.6rem !important;
            color: rgba(255,255,255,0.8) !important;
            font-family: inherit !important;
            font-size: 0.65rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            border-bottom: 2px solid transparent !important;
            transition: all 0.15s !important;
        }
        .sl-topbar-tab:hover { background: rgba(255,255,255,0.1) !important; color: white !important; }
        .sl-topbar-tab.active { color: white !important; background: rgba(255,255,255,0.12) !important; border-bottom-color: #E87722 !important; }

        .sl-hamburger {
            display: none !important;
            background: none !important;
            border: none !important;
            color: white !important;
            cursor: pointer !important;
            padding: 0.35rem !important;
            flex-direction: column !important;
            gap: 3px !important;
        }
        .sl-hamburger span { display: block; width: 18px; height: 2px; background: white; border-radius: 1px; }

        /* Sidebar */
        .sl-sidebar {
            position: fixed !important;
            top: var(--sl-topbar-height) !important;
            left: 0 !important;
            width: var(--sl-sidebar-width) !important;
            height: calc(100vh - var(--sl-topbar-height)) !important;
            background: #0f172a !important;
            z-index: 10000 !important;
            overflow-y: auto !important;
            font-family: 'Inter', -apple-system, sans-serif !important;
        }
        .sl-sidebar::-webkit-scrollbar { width: 6px; }
        .sl-sidebar::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

        .sl-sidebar-home {
            display: block !important;
            padding: 0.4rem 0.6rem !important;
            color: white !important;
            text-decoration: none !important;
            font-weight: 600 !important;
            font-size: 0.7rem !important;
            border-bottom: 1px solid #1e293b !important;
        }
        .sl-sidebar-home:hover { background: #1e293b !important; }
        .sl-sidebar-home.current { background: linear-gradient(90deg, #5B2D8A, transparent) !important; border-left: 2px solid #E87722 !important; }

        .sl-section { border-bottom: 1px solid #1e293b !important; }
        .sl-section-header {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            padding: 0.4rem 0.6rem !important;
            color: #94a3b8 !important;
            font-size: 0.65rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            cursor: pointer !important;
        }
        .sl-section-header:hover { background: #1e293b !important; color: white !important; }
        .sl-section.active .sl-section-header { color: #E87722 !important; background: #1e293b !important; }
        .sl-section-header .toggle { font-size: 0.5rem; transition: transform 0.2s; }
        .sl-section.active .sl-section-header .toggle { transform: rotate(180deg); }

        .sl-links { display: none !important; padding: 0 0 0.25rem 0 !important; }
        .sl-section.active .sl-links { display: block !important; }
        .sl-links a {
            display: block !important;
            padding: 0.2rem 0.5rem 0.2rem 0.8rem !important;
            color: #64748b !important;
            text-decoration: none !important;
            font-size: 0.7rem !important;
            border-left: 2px solid transparent !important;
        }
        .sl-links a:hover { color: white !important; background: rgba(255,255,255,0.05) !important; }
        .sl-links a.current { color: #E87722 !important; border-left-color: #E87722 !important; background: rgba(232,119,34,0.1) !important; }

        .sl-overlay {
            display: none !important;
            position: fixed !important;
            top: var(--sl-topbar-height) !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            background: rgba(0,0,0,0.5) !important;
            z-index: 9999 !important;
        }
        .sl-overlay.active { display: block !important; }

        /* Hero section fix */
        .hero { padding-top: 1.5rem !important; margin-top: 0 !important; }

        /* Mobile */
        @media (max-width: 900px) {
            body { padding-left: 0 !important; }
            .sl-topbar-tabs { display: none !important; }
            .sl-hamburger { display: flex !important; }
            .sl-sidebar { transform: translateX(-100%); transition: transform 0.3s; }
            .sl-sidebar.open { transform: translateX(0); }
        }
    </style>
'''

def get_topbar_html(prefix=""):
    return f'''
    <!-- SIDEBAR LAYOUT TOPBAR -->
    <header class="sl-topbar">
        <a href="{prefix}index.html" class="sl-topbar-logo">
            COST <span class="action-id">CA19130</span>
            <span class="badge">2020-2024</span>
        </a>
        <nav class="sl-topbar-tabs">
            <button class="sl-topbar-tab" data-category="home">HOME</button>
            <button class="sl-topbar-tab" data-category="impact">IMPACT</button>
            <button class="sl-topbar-tab" data-category="network">NETWORK</button>
            <button class="sl-topbar-tab" data-category="research">RESEARCH</button>
            <button class="sl-topbar-tab" data-category="activities">ACTIVITIES</button>
            <button class="sl-topbar-tab" data-category="archive">ARCHIVE</button>
        </nav>
        <button class="sl-hamburger" onclick="slToggleSidebar()">
            <span></span><span></span><span></span>
        </button>
    </header>
    <div class="sl-overlay" onclick="slToggleSidebar()"></div>
'''

def get_sidebar_html(prefix=""):
    return f'''
    <!-- SIDEBAR LAYOUT SIDEBAR -->
    <aside class="sl-sidebar">
        <a href="{prefix}index.html" class="sl-sidebar-home" data-category="home">HOME</a>
        <div class="sl-section" data-category="impact">
            <div class="sl-section-header" onclick="slToggleSection(this)">IMPACT <span class="toggle">&#9660;</span></div>
            <div class="sl-links">
                <a href="{prefix}final-achievements.html">Final Achievements</a>
                <a href="{prefix}final-report.html">Objectives Met (16/16)</a>
                <a href="{prefix}work-budget-plans/deliverables.html">Deliverables (15/15)</a>
                <a href="{prefix}final-impacts.html">Scientific Impact</a>
                <a href="{prefix}final-publications.html">Legacy & Continuation</a>
            </div>
        </div>
        <div class="sl-section" data-category="network">
            <div class="sl-section-header" onclick="slToggleSection(this)">NETWORK <span class="toggle">&#9660;</span></div>
            <div class="sl-links">
                <a href="{prefix}members.html">All Members (426)</a>
                <a href="{prefix}leadership.html">Leadership Team</a>
                <a href="{prefix}mc-members.html">Management Committee</a>
                <a href="{prefix}wg-members.html">Working Groups</a>
                <a href="{prefix}country-contributions.html">Countries (48)</a>
            </div>
        </div>
        <div class="sl-section" data-category="research">
            <div class="sl-section-header" onclick="slToggleSection(this)">RESEARCH <span class="toggle">&#9660;</span></div>
            <div class="sl-links">
                <a href="{prefix}publications.html">Publications</a>
                <a href="{prefix}preprints.html">Preprints</a>
                <a href="{prefix}datasets.html">Datasets</a>
                <a href="{prefix}other-outputs.html">Other Outputs</a>
            </div>
        </div>
        <div class="sl-section" data-category="activities">
            <div class="sl-section-header" onclick="slToggleSection(this)">ACTIVITIES <span class="toggle">&#9660;</span></div>
            <div class="sl-links">
                <a href="{prefix}financial-reports/meetings.html">All Meetings</a>
                <a href="{prefix}financial-reports/stsm.html">STSMs</a>
                <a href="{prefix}financial-reports/training-schools.html">Training Schools</a>
            </div>
        </div>
        <div class="sl-section" data-category="archive">
            <div class="sl-section-header" onclick="slToggleSection(this)">ARCHIVE <span class="toggle">&#9660;</span></div>
            <div class="sl-links">
                <a href="{prefix}final-action-chair-report-full.html">Final Report</a>
                <a href="{prefix}midterm-action-chair-report-full.html">Mid-Term Report</a>
                <a href="{prefix}financial-reports/overview.html">Financial Overview</a>
            </div>
        </div>
    </aside>
'''

SIDEBAR_JS = '''
    <!-- SIDEBAR LAYOUT JS -->
    <script>
    (function() {
        document.addEventListener('DOMContentLoaded', function() {
            slDetectPage();
            slInitTabs();
        });

        window.slToggleSidebar = function() {
            var sb = document.querySelector('.sl-sidebar');
            var ov = document.querySelector('.sl-overlay');
            if (sb) sb.classList.toggle('open');
            if (ov) ov.classList.toggle('active');
        };

        window.slToggleSection = function(header) {
            var section = header.parentElement;
            var wasActive = section.classList.contains('active');
            document.querySelectorAll('.sl-section').forEach(function(s) { s.classList.remove('active'); });
            if (!wasActive) {
                section.classList.add('active');
                slSetActiveTab(section.dataset.category);
            }
        };

        function slDetectPage() {
            var page = location.pathname.split('/').pop() || 'index.html';
            var map = {
                'index.html': 'home',
                'final-achievements.html': 'impact', 'final-report.html': 'impact', 'final-impacts.html': 'impact',
                'members.html': 'network', 'leadership.html': 'network', 'mc-members.html': 'network', 'wg-members.html': 'network',
                'publications.html': 'research', 'preprints.html': 'research', 'datasets.html': 'research',
                'progress-reports.html': 'activities'
            };
            var cat = map[page] || 'home';
            if (location.pathname.includes('financial-reports/')) cat = 'archive';
            if (location.pathname.includes('work-budget-plans/')) cat = 'archive';
            slSetActiveTab(cat);
            var sec = document.querySelector('.sl-section[data-category="' + cat + '"]');
            if (sec) sec.classList.add('active');
            document.querySelectorAll('.sl-links a').forEach(function(a) {
                if (a.href && a.href.endsWith(page)) a.classList.add('current');
            });
            if (cat === 'home') {
                var home = document.querySelector('.sl-sidebar-home');
                if (home) home.classList.add('current');
            }
        }

        function slSetActiveTab(cat) {
            document.querySelectorAll('.sl-topbar-tab').forEach(function(t) {
                t.classList.toggle('active', t.dataset.category === cat);
            });
        }

        function slInitTabs() {
            document.querySelectorAll('.sl-topbar-tab').forEach(function(tab) {
                tab.addEventListener('click', function() {
                    var cat = this.dataset.category;
                    slSetActiveTab(cat);
                    document.querySelectorAll('.sl-section').forEach(function(s) { s.classList.remove('active'); });
                    var sec = document.querySelector('.sl-section[data-category="' + cat + '"]');
                    if (sec) sec.classList.add('active');
                    if (window.innerWidth <= 900) slToggleSidebar();
                });
            });
        }
    })();
    </script>
'''

def get_prefix(file_path):
    rel = file_path.relative_to(BASE_DIR)
    depth = len(rel.parts) - 1
    return "../" * depth if depth > 0 else ""

def update_file(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        if 'sidebar-layout-css' in content:
            return False  # Already has sidebar layout

        prefix = get_prefix(file_path)

        # Add CSS before </head>
        content = content.replace('</head>', f'{SIDEBAR_CSS}</head>')

        # Add topbar and sidebar after <body...>
        body_match = re.search(r'<body[^>]*>', content)
        if body_match:
            insert_pos = body_match.end()
            html = get_topbar_html(prefix) + get_sidebar_html(prefix)
            content = content[:insert_pos] + html + content[insert_pos:]

        # Add JS before </body>
        content = content.replace('</body>', f'{SIDEBAR_JS}</body>')

        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error: {file_path}: {e}")
        return False

def main():
    files = list(BASE_DIR.glob('*.html')) + list((BASE_DIR / 'financial-reports').glob('*.html')) + list((BASE_DIR / 'work-budget-plans').glob('*.html'))
    files = [f for f in files if f.name != 'test-sidebar-layout.html']

    print(f"Deploying sidebar layout to {len(files)} files...")
    print("-" * 50)

    count = 0
    for f in sorted(files):
        if update_file(f):
            count += 1
            print(f"[OK] {f.relative_to(BASE_DIR)}")
        else:
            print(f"[--] {f.relative_to(BASE_DIR)}")

    print("-" * 50)
    print(f"Done: {count}/{len(files)} updated")

if __name__ == '__main__':
    main()
