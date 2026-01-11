"""
Verify HTML Numbers - Find every number in HTML pages and verify against JSON sources.

Approach:
1. Page-Specific Rules: Map HTML pages to their source JSON files
2. Data Attribute Audit: Check for data-* attributes with source annotations

Scope: All numbers (dates, counts, percentages, currency amounts)
Output: JSON report with verification status
"""

import json
import re
from pathlib import Path
from typing import Any
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
WBP_DIR = DATA_DIR / "wbp"
HTML_DIRS = [
    BASE_DIR / "work-budget-plans",
    BASE_DIR / "financial-reports",
]

# Page-to-JSON mappings
PAGE_JSON_MAPPINGS = {
    # Work & Budget Plans
    "work-budget-plans/gp1.html": ["data/wbp/wbp_gp1.json", "data/grant_period_goals.json", "data/budget_data.json", "data/summary_statistics.json"],
    "work-budget-plans/gp2.html": ["data/wbp/wbp_gp2.json", "data/grant_period_goals.json", "data/budget_data.json", "data/summary_statistics.json"],
    "work-budget-plans/gp3.html": ["data/wbp/wbp_gp3.json", "data/grant_period_goals.json", "data/budget_data.json", "data/summary_statistics.json"],
    "work-budget-plans/gp4.html": ["data/wbp/wbp_gp4.json", "data/grant_period_goals.json", "data/budget_data.json", "data/summary_statistics.json"],
    "work-budget-plans/gp5.html": ["data/wbp/wbp_gp5.json", "data/grant_period_goals.json", "data/budget_data.json", "data/summary_statistics.json"],
    "work-budget-plans/objectives.html": ["data/mou_objectives.json", "data/summary_statistics.json"],
    "work-budget-plans/gapg.html": ["data/grant_period_goals.json", "data/summary_statistics.json"],
    "work-budget-plans/overview.html": ["data/wbp/wbp_summary.json", "data/summary_statistics.json", "data/budget_data.json"],
    "work-budget-plans/index.html": ["data/wbp/wbp_summary.json", "data/summary_statistics.json"],
    "work-budget-plans/deliverables.html": ["data/deliverables.json", "data/summary_statistics.json"],
    "work-budget-plans/working-groups.html": ["data/working_groups.json", "data/summary_statistics.json"],
    # Financial Reports
    "financial-reports/ffr1.html": ["data/ffr_data.json", "data/budget_data.json", "data/summary_statistics.json", "data/meetings.json", "data/members.json", "data/mc_members.json", "data/deliverables.json"],
    "financial-reports/ffr2.html": ["data/ffr_data.json", "data/budget_data.json", "data/summary_statistics.json", "data/meetings.json", "data/members.json", "data/mc_members.json", "data/deliverables.json"],
    "financial-reports/ffr3.html": ["data/ffr_data.json", "data/budget_data.json", "data/summary_statistics.json", "data/meetings.json", "data/members.json", "data/mc_members.json", "data/deliverables.json"],
    "financial-reports/ffr4.html": ["data/ffr_data.json", "data/budget_data.json", "data/summary_statistics.json", "data/meetings.json", "data/members.json", "data/mc_members.json", "data/deliverables.json"],
    "financial-reports/ffr5.html": ["data/ffr_data.json", "data/budget_data.json", "data/summary_statistics.json", "data/meetings.json", "data/members.json", "data/mc_members.json", "data/deliverables.json"],
    "financial-reports/overview.html": ["data/summary_statistics.json", "data/budget_data.json", "data/ffr_data.json", "data/members.json", "data/mc_members.json"],
    "financial-reports/stsm.html": ["data/stsm_detailed.json", "data/summary_statistics.json"],
    "financial-reports/meetings.html": ["data/meetings.json", "data/meetings_participants.json", "data/summary_statistics.json"],
    "financial-reports/training-schools.html": ["data/training_school_attendees.json", "data/summary_statistics.json"],
    "financial-reports/index.html": ["data/summary_statistics.json", "data/budget_data.json", "data/members.json", "data/mc_members.json", "data/deliverables.json"],
    "financial-reports/participants.html": ["data/participant_master.json", "data/summary_statistics.json", "data/members.json"],
    "financial-reports/countries.html": ["data/summary_statistics.json", "data/country_statistics.json", "data/members.json", "data/mc_members.json", "data/deliverables.json"],
    "financial-reports/virtual-mobility.html": ["data/virtual_mobility_full.json", "data/summary_statistics.json"],
}

# Number patterns to extract
NUMBER_PATTERNS = [
    # Currency amounts (62,985.50 or 62985.50 or 62,985)
    (r'\b(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\b', 'currency'),
    # Percentages (75% or 75.5%)
    (r'\b(\d+(?:\.\d+)?)\s*%', 'percentage'),
    # Dates (2021-03-18 or 18/03/2021 or March 2021)
    (r'\b(\d{4}-\d{2}-\d{2})\b', 'date_iso'),
    (r'\b(\d{1,2}/\d{1,2}/\d{4})\b', 'date_slash'),
    # Year only
    (r'\b(20[12]\d)\b', 'year'),
    # Plain integers
    (r'\b(\d+)\b', 'integer'),
]

# Common numbers to ignore (CSS, IDs, etc.)
IGNORE_PATTERNS = [
    r'rgba?\([^)]+\)',  # CSS rgba
    r'#[0-9a-fA-F]{3,8}',  # CSS hex colors
    r'z-index:\s*\d+',  # z-index
    r'font-size:\s*[\d.]+',  # font sizes
    r'font-weight:\s*\d+',  # font weights
    r'line-height:\s*[\d.]+',  # line heights
    r'padding[^:]*:\s*[\d.]+',  # padding
    r'margin[^:]*:\s*[\d.]+',  # margins
    r'width:\s*[\d.]+',  # widths
    r'height:\s*[\d.]+',  # heights
    r'opacity:\s*[\d.]+',  # opacity
    r'border-radius:\s*[\d.]+',  # border radius
    r'flex:\s*[\d.]+',  # flex values
    r'gap:\s*[\d.]+',  # gap values
    r'top:\s*[\d.]+',  # positioning
    r'left:\s*[\d.]+',  # positioning
    r'right:\s*[\d.]+',  # positioning
    r'bottom:\s*[\d.]+',  # positioning
    r'translateX?Y?\([^)]+\)',  # CSS transforms
    r'rotate\([^)]+\)',  # CSS rotate
    r'scale\([^)]+\)',  # CSS scale
    r'@media[^{]+',  # media queries
    r'max-width:\s*[\d.]+',  # max widths
    r'min-width:\s*[\d.]+',  # min widths
]


def extract_all_json_numbers(json_data: Any, path: str = "") -> dict:
    """Recursively extract all numbers from JSON with their paths."""
    numbers = {}

    if isinstance(json_data, dict):
        for key, value in json_data.items():
            new_path = f"{path}.{key}" if path else key
            numbers.update(extract_all_json_numbers(value, new_path))
    elif isinstance(json_data, list):
        # Also record list length as a computed number
        list_len = len(json_data)
        if list_len > 0:
            len_path = f"{path}.length" if path else "length"
            numbers[len_path] = {
                'raw': list_len,
                'formatted': str(list_len),
                'int': list_len,
            }
        for i, item in enumerate(json_data):
            new_path = f"{path}[{i}]"
            numbers.update(extract_all_json_numbers(item, new_path))
    elif isinstance(json_data, (int, float)):
        # Store number and its formatted variants
        num = json_data
        numbers[path] = {
            'raw': num,
            'formatted': format_number(num),
            'int': int(num) if isinstance(num, float) and num == int(num) else None,
        }
    elif isinstance(json_data, str):
        # Check if string contains a number
        if re.match(r'^[\d,.\-]+$', json_data):
            try:
                num = float(json_data.replace(',', ''))
                numbers[path] = {
                    'raw': num,
                    'formatted': json_data,
                    'int': int(num) if num == int(num) else None,
                }
            except ValueError:
                pass

    return numbers


def format_number(num: float) -> str:
    """Format number with commas."""
    if num == int(num):
        return f"{int(num):,}"
    return f"{num:,.2f}"


def extract_html_numbers(html_content: str, filepath: Path) -> list:
    """Extract all numbers from HTML content with context."""
    numbers = []
    lines = html_content.split('\n')

    # First, remove content that should be ignored (CSS, scripts)
    cleaned_content = html_content

    # Remove style blocks
    cleaned_content = re.sub(r'<style[^>]*>.*?</style>', '', cleaned_content, flags=re.DOTALL)

    # Remove script blocks
    cleaned_content = re.sub(r'<script[^>]*>.*?</script>', '', cleaned_content, flags=re.DOTALL)

    # Remove CSS properties
    for pattern in IGNORE_PATTERNS:
        cleaned_content = re.sub(pattern, '', cleaned_content)

    # Find all numbers with their line numbers
    for line_num, line in enumerate(lines, 1):
        # Skip style and script lines
        if '<style' in line.lower() or '</style>' in line.lower():
            continue
        if '<script' in line.lower() or '</script>' in line.lower():
            continue
        if line.strip().startswith('/*') or line.strip().startswith('*'):
            continue

        # Skip CSS-heavy lines
        skip_line = False
        for pattern in IGNORE_PATTERNS:
            if re.search(pattern, line):
                skip_line = True
                break
        if skip_line:
            continue

        # Extract numbers from this line
        for pattern, num_type in NUMBER_PATTERNS:
            for match in re.finditer(pattern, line):
                num_str = match.group(1)

                # Skip very small numbers that are likely CSS
                try:
                    num_val = float(num_str.replace(',', ''))
                    if num_val < 1 and num_type not in ['percentage', 'date_iso']:
                        continue
                except ValueError:
                    continue

                # Get context (surrounding text)
                context = get_context(line, match.start(), match.end())

                # Check for data attributes
                data_source = extract_data_source(line)

                numbers.append({
                    'value': num_str,
                    'normalized': normalize_number(num_str),
                    'type': num_type,
                    'line': line_num,
                    'context': context,
                    'data_source': data_source,
                })

    return numbers


def get_context(line: str, start: int, end: int, context_chars: int = 50) -> str:
    """Extract context around a number in a line."""
    # Remove HTML tags for cleaner context
    clean_line = re.sub(r'<[^>]+>', ' ', line)
    clean_line = re.sub(r'\s+', ' ', clean_line).strip()

    # Find the number in cleaned line
    return clean_line[:100] if len(clean_line) > 100 else clean_line


def extract_data_source(line: str) -> str | None:
    """Extract data-source or similar attributes from line."""
    match = re.search(r'data-source="([^"]+)"', line)
    if match:
        return match.group(1)

    match = re.search(r'data-json="([^"]+)"', line)
    if match:
        return match.group(1)

    return None


def normalize_number(num_str: str) -> float | None:
    """Normalize a number string to a float."""
    try:
        # Remove commas and convert
        return float(num_str.replace(',', ''))
    except ValueError:
        return None


def load_json_sources(json_paths: list) -> dict:
    """Load all JSON files and extract their numbers."""
    all_numbers = {}

    for rel_path in json_paths:
        filepath = BASE_DIR / rel_path
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                numbers = extract_all_json_numbers(data)
                all_numbers[rel_path] = numbers
            except Exception as e:
                print(f"  Warning: Could not load {rel_path}: {e}")

    return all_numbers


def find_number_source(num_value: float, json_numbers: dict, tolerance: float = 0.01) -> list:
    """Find potential JSON sources for a number."""
    sources = []

    for json_file, numbers in json_numbers.items():
        for path, num_info in numbers.items():
            raw = num_info['raw']
            if raw is not None:
                # Check if numbers match within tolerance
                if abs(raw - num_value) <= tolerance:
                    sources.append({
                        'file': json_file,
                        'path': path,
                        'json_value': raw,
                    })
                # Also check integer version
                if num_info['int'] is not None and abs(num_info['int'] - num_value) <= tolerance:
                    if not any(s['path'] == path for s in sources):
                        sources.append({
                            'file': json_file,
                            'path': path,
                            'json_value': num_info['int'],
                        })

    return sources


def verify_html_page(html_path: Path) -> dict:
    """Verify all numbers in an HTML page."""
    rel_path = str(html_path.relative_to(BASE_DIR)).replace('\\', '/')

    print(f"\nVerifying: {rel_path}")

    # Get JSON sources for this page
    json_paths = PAGE_JSON_MAPPINGS.get(rel_path, [])
    if not json_paths:
        # Try to find a default mapping
        json_paths = ["data/summary_statistics.json"]

    # Load JSON numbers
    json_numbers = load_json_sources(json_paths)

    # Build flat number lookup
    all_json_values = set()
    for numbers in json_numbers.values():
        for num_info in numbers.values():
            if num_info['raw'] is not None:
                all_json_values.add(round(num_info['raw'], 2))
                if num_info['int'] is not None:
                    all_json_values.add(num_info['int'])

    # Extract HTML numbers
    html_content = html_path.read_text(encoding='utf-8')
    html_numbers = extract_html_numbers(html_content, html_path)

    # Deduplicate by value and line
    seen = set()
    unique_numbers = []
    for num in html_numbers:
        key = (num['value'], num['line'])
        if key not in seen:
            seen.add(key)
            unique_numbers.append(num)

    # Verify each number
    verified = []
    unverified = []

    for num in unique_numbers:
        norm_val = num['normalized']
        if norm_val is None:
            continue

        # Find sources
        sources = find_number_source(norm_val, json_numbers)

        if sources or num['data_source']:
            verified.append({
                'value': num['value'],
                'type': num['type'],
                'line': num['line'],
                'context': num['context'],
                'verified': True,
                'sources': sources if sources else [{'file': 'data-attribute', 'path': num['data_source']}],
            })
        else:
            # Check if it's a common ignorable number
            if is_ignorable_number(norm_val, num['type'], num['context']):
                continue

            unverified.append({
                'value': num['value'],
                'type': num['type'],
                'line': num['line'],
                'context': num['context'],
                'verified': False,
                'sources': [],
            })

    print(f"  Total numbers: {len(unique_numbers)}")
    print(f"  Verified: {len(verified)}")
    print(f"  Unverified: {len(unverified)}")

    return {
        'file': rel_path,
        'json_sources': json_paths,
        'total_numbers': len(unique_numbers),
        'verified_count': len(verified),
        'unverified_count': len(unverified),
        'verified': verified[:50],  # Limit for readability
        'unverified': unverified,
    }


def is_ignorable_number(value: float, num_type: str, context: str) -> bool:
    """Check if a number should be ignored (CSS values, IDs, etc.)."""
    ctx_lower = context.lower()

    # Empty context lines (likely from HTML head/meta)
    if not context.strip():
        return True

    # Common CSS font-weight values
    if value in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
        if 'font' in ctx_lower or 'weight' in ctx_lower:
            return True

    # Common CSS/style values
    if value in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 24, 100]:
        if any(word in ctx_lower for word in ['px', 'rem', 'em', 'pt', 'width', 'height', 'size', 'padding', 'margin', 'border', 'radius']):
            return True

    # Very small decimals (likely CSS)
    if value < 1 and num_type != 'percentage':
        return True

    # Navigation numbers (GP1, GP2, FFR 1-5, etc.)
    if ('gp' in ctx_lower or 'ffr' in ctx_lower) and value <= 5:
        return True

    # Years in date ranges (2020-2024, 2019130)
    if num_type == 'year' and value in [2019, 2020, 2021, 2022, 2023, 2024, 2025]:
        if '-' in context or 'cost' in ctx_lower or 'ca' in ctx_lower:
            return True

    # COST Action ID (CA19130)
    if value == 19130 or value == 130:
        return True

    # CSS-related contexts
    css_keywords = ['color:', 'background:', 'transform:', 'transition:', 'animation:',
                    'flex:', 'grid:', 'display:', 'position:', 'z-index:', 'opacity:',
                    'translatex', 'translatey', 'rotate', 'scale', 'var(--',
                    '{', '}', 'style', 'class=']
    if any(kw in ctx_lower for kw in css_keywords):
        return True

    # JavaScript Math operations (likely calculations, not data)
    if 'math.' in ctx_lower or '* 100' in ctx_lower or '/ 100' in ctx_lower:
        return True

    # Footer/meta content
    if 'footer' in ctx_lower or 'copyright' in ctx_lower or 'license' in ctx_lower:
        return True

    return False


def main():
    print("=" * 60)
    print("HTML NUMBER VERIFICATION")
    print("=" * 60)
    print(f"Base directory: {BASE_DIR}")

    # Find all HTML files
    html_files = []
    for html_dir in HTML_DIRS:
        if html_dir.exists():
            html_files.extend(html_dir.glob("*.html"))

    print(f"\nFound {len(html_files)} HTML files to verify")

    # Verify each file
    results = []
    for html_path in sorted(html_files):
        result = verify_html_page(html_path)
        results.append(result)

    # Generate summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_numbers = sum(r['total_numbers'] for r in results)
    total_verified = sum(r['verified_count'] for r in results)
    total_unverified = sum(r['unverified_count'] for r in results)

    print(f"\nTotal numbers found: {total_numbers}")
    print(f"Verified: {total_verified} ({100*total_verified/total_numbers:.1f}%)" if total_numbers > 0 else "Verified: 0")
    print(f"Unverified: {total_unverified}")

    # Files with most unverified numbers
    print("\nFiles with unverified numbers:")
    for r in sorted(results, key=lambda x: x['unverified_count'], reverse=True)[:10]:
        if r['unverified_count'] > 0:
            print(f"  {r['file']}: {r['unverified_count']} unverified")

    # Save report
    report = {
        'generated': datetime.now().isoformat(),
        'summary': {
            'total_files': len(results),
            'total_numbers': total_numbers,
            'verified': total_verified,
            'unverified': total_unverified,
            'verification_rate': round(100 * total_verified / total_numbers, 2) if total_numbers > 0 else 0,
        },
        'files': results,
    }

    report_path = BASE_DIR / "reports" / "html_number_verification.json"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nReport saved to: {report_path}")

    return total_unverified == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
