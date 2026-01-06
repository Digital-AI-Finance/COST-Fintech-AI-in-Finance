"""
Generate sitemap.json by scanning the actual site structure.
"""

import os
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

# Define category mappings
CATEGORY_MAP = {
    # IMPACT
    'impact.html': 'IMPACT',
    'final-achievements.html': 'IMPACT',
    'final-report.html': 'IMPACT',
    'final-impacts.html': 'IMPACT',
    'final-publications.html': 'IMPACT',
    'comparison-enhanced.html': 'IMPACT',

    # NETWORK
    'network.html': 'NETWORK',
    'members.html': 'NETWORK',
    'leadership.html': 'NETWORK',
    'mc-members.html': 'NETWORK',
    'wg-members.html': 'NETWORK',
    'country-contributions.html': 'NETWORK',
    'author-stats.html': 'NETWORK',

    # RESEARCH
    'research.html': 'RESEARCH',
    'publications.html': 'RESEARCH',
    'preprints.html': 'RESEARCH',
    'datasets.html': 'RESEARCH',
    'other-outputs.html': 'RESEARCH',
    'documents.html': 'RESEARCH',

    # ACTIVITIES
    'activities.html': 'ACTIVITIES',
    'progress-reports.html': 'ACTIVITIES',
    'progress-gp1.html': 'ACTIVITIES',
    'progress-gp2.html': 'ACTIVITIES',
    'progress-gp3.html': 'ACTIVITIES',
    'progress-gp4.html': 'ACTIVITIES',
    'progress-gp5.html': 'ACTIVITIES',

    # ARCHIVE
    'archive.html': 'ARCHIVE',
    'final-action-chair-report.html': 'ARCHIVE',
    'final-action-chair-report-full.html': 'ARCHIVE',
    'midterm-report.html': 'ARCHIVE',
    'midterm-action-chair-report.html': 'ARCHIVE',
    'midterm-action-chair-report-full.html': 'ARCHIVE',
    'midterm-public-report.html': 'ARCHIVE',
    'midterm-rapporteur-review.html': 'ARCHIVE',
    'comparison-action-chair-full.html': 'ARCHIVE',
    'report-editor.html': 'ARCHIVE',
}

# Page titles/descriptions
PAGE_TITLES = {
    'index.html': 'Homepage',
    'impact.html': 'Impact Overview',
    'network.html': 'Network Overview',
    'research.html': 'Research Overview',
    'activities.html': 'Activities Overview',
    'archive.html': 'Archive Overview',
    'final-achievements.html': 'Final Achievements',
    'final-report.html': 'Objectives Met (16/16)',
    'final-impacts.html': 'Scientific Impact',
    'final-publications.html': 'Legacy & Continuation',
    'final-action-chair-report.html': 'Final Action Chair Report',
    'final-action-chair-report-full.html': 'Final Report (Full)',
    'members.html': 'All Members (426)',
    'leadership.html': 'Leadership Team',
    'mc-members.html': 'Management Committee (70)',
    'wg-members.html': 'Working Groups',
    'country-contributions.html': 'Countries (48)',
    'author-stats.html': 'Author Statistics',
    'publications.html': 'Publications',
    'preprints.html': 'Preprints',
    'datasets.html': 'Datasets',
    'other-outputs.html': 'Other Outputs',
    'documents.html': 'Documents Archive',
    'progress-reports.html': 'Progress Reports',
    'progress-gp1.html': 'Grant Period 1',
    'progress-gp2.html': 'Grant Period 2',
    'progress-gp3.html': 'Grant Period 3',
    'progress-gp4.html': 'Grant Period 4',
    'progress-gp5.html': 'Grant Period 5',
    'midterm-report.html': 'Mid-Term Report',
    'midterm-action-chair-report.html': 'Mid-Term Action Chair Report',
    'midterm-action-chair-report-full.html': 'Mid-Term Report (Full)',
    'midterm-public-report.html': 'Public Mid-Term Report',
    'midterm-rapporteur-review.html': 'Rapporteur Review',
    'comparison-enhanced.html': 'Report Comparison',
    'comparison-action-chair-full.html': 'Full Comparison',
    'report-editor.html': 'Report Editor',
    'sitemap.html': 'Site Map',
}

def get_root_pages():
    """Get all root-level HTML pages."""
    pages = []
    for f in sorted(BASE_DIR.glob('*.html')):
        if f.name.startswith('test-'):
            continue
        pages.append({
            'name': f.name,
            'title': PAGE_TITLES.get(f.name, f.name.replace('.html', '').replace('-', ' ').title()),
            'category': CATEGORY_MAP.get(f.name, 'HOME' if f.name == 'index.html' else 'OTHER'),
            'path': f.name,
            'type': 'page'
        })
    return pages

def get_subdirectory_pages(subdir):
    """Get all HTML pages in a subdirectory."""
    subdir_path = BASE_DIR / subdir
    if not subdir_path.exists():
        return []

    pages = []
    for f in sorted(subdir_path.glob('*.html')):
        pages.append({
            'name': f.name,
            'title': f.name.replace('.html', '').replace('-', ' ').replace('_', ' ').title(),
            'path': f'{subdir}/{f.name}',
            'type': 'page'
        })
    return pages

def get_action_chair_structure():
    """Get the Action Chair archive structure."""
    action_chair = BASE_DIR / 'Action Chair'
    if not action_chair.exists():
        return []

    structure = []

    # Get immediate subdirectories
    for subdir in sorted(action_chair.iterdir()):
        if subdir.is_dir():
            html_files = list(subdir.rglob('*.html'))
            if html_files:
                folder = {
                    'name': subdir.name,
                    'type': 'folder',
                    'count': len(html_files),
                    'children': []
                }

                # Get direct HTML files
                for f in sorted(subdir.glob('*.html')):
                    rel_path = f.relative_to(BASE_DIR)
                    folder['children'].append({
                        'name': f.name,
                        'title': f.name.replace('.html', ''),
                        'path': str(rel_path).replace('\\', '/'),
                        'type': 'page'
                    })

                # Get nested subdirectories
                for nested in sorted(subdir.iterdir()):
                    if nested.is_dir():
                        nested_files = list(nested.glob('*.html'))
                        if nested_files:
                            nested_folder = {
                                'name': nested.name,
                                'type': 'folder',
                                'count': len(nested_files),
                                'children': []
                            }
                            for f in sorted(nested_files):
                                rel_path = f.relative_to(BASE_DIR)
                                nested_folder['children'].append({
                                    'name': f.name,
                                    'title': f.name.replace('.html', ''),
                                    'path': str(rel_path).replace('\\', '/'),
                                    'type': 'page'
                                })
                            folder['children'].append(nested_folder)

                structure.append(folder)

    return structure

def get_json_files():
    """Get all JSON data files."""
    data_dir = BASE_DIR / 'data'
    if not data_dir.exists():
        return []

    files = []
    for f in sorted(data_dir.glob('*.json')):
        if f.name == 'sitemap.json':
            continue
        files.append({
            'name': f.name,
            'path': f'data/{f.name}',
            'type': 'data'
        })
    return files

def generate_sitemap():
    """Generate the complete sitemap structure."""

    root_pages = get_root_pages()
    financial_reports = get_subdirectory_pages('financial-reports')
    work_budget_plans = get_subdirectory_pages('work-budget-plans')
    action_chair = get_action_chair_structure()
    json_files = get_json_files()

    # Count totals
    action_chair_count = sum(
        folder.get('count', 0) + sum(
            child.get('count', 0) if child.get('type') == 'folder' else 1
            for child in folder.get('children', [])
        )
        for folder in action_chair
    )

    sitemap = {
        'generated': datetime.now().isoformat(),
        'statistics': {
            'total_pages': len(root_pages) + len(financial_reports) + len(work_budget_plans) + action_chair_count,
            'root_pages': len(root_pages),
            'financial_reports': len(financial_reports),
            'work_budget_plans': len(work_budget_plans),
            'action_chair_documents': action_chair_count,
            'json_data_files': len(json_files)
        },
        'categories': {
            'HOME': [p for p in root_pages if p['category'] == 'HOME'],
            'IMPACT': [p for p in root_pages if p['category'] == 'IMPACT'],
            'NETWORK': [p for p in root_pages if p['category'] == 'NETWORK'],
            'RESEARCH': [p for p in root_pages if p['category'] == 'RESEARCH'],
            'ACTIVITIES': [p for p in root_pages if p['category'] == 'ACTIVITIES'],
            'ARCHIVE': [p for p in root_pages if p['category'] == 'ARCHIVE'],
            'OTHER': [p for p in root_pages if p['category'] == 'OTHER']
        },
        'subdirectories': {
            'financial-reports': {
                'title': 'Financial Reports',
                'count': len(financial_reports),
                'pages': financial_reports
            },
            'work-budget-plans': {
                'title': 'Work & Budget Plans',
                'count': len(work_budget_plans),
                'pages': work_budget_plans
            },
            'action-chair': {
                'title': 'Action Chair Archive',
                'count': action_chair_count,
                'folders': action_chair
            }
        },
        'data_files': json_files
    }

    return sitemap

def main():
    print("Generating sitemap.json...")
    sitemap = generate_sitemap()

    output_path = BASE_DIR / 'data' / 'sitemap.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sitemap, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {output_path}")
    print(f"\nStatistics:")
    for key, value in sitemap['statistics'].items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
