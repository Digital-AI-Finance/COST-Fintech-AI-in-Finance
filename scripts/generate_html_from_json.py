"""
Generate HTML from JSON - Add data-source attributes to numbers

This script updates HTML files to add data-source attributes to hardcoded numbers,
enabling verification and dynamic updates from JSON data.

Approach:
1. Load JSON data files
2. Build a mapping of values to their JSON paths
3. Find numbers in HTML and add data-source attributes
4. Write updated HTML files
"""

import json
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
HTML_DIRS = [
    BASE_DIR / "work-budget-plans",
    BASE_DIR / "financial-reports",
]

# JSON files to load and their path prefixes
JSON_FILES = {
    "budget_data": DATA_DIR / "budget_data.json",
    "summary_statistics": DATA_DIR / "summary_statistics.json",
    "ffr_data": DATA_DIR / "ffr_data.json",
    "meetings": DATA_DIR / "meetings.json",
    "stsm_detailed": DATA_DIR / "stsm_detailed.json",
    "members": DATA_DIR / "members.json",
    "mc_members": DATA_DIR / "mc_members.json",
    "deliverables": DATA_DIR / "deliverables.json",
    "country_statistics": DATA_DIR / "country_statistics.json",
}


def load_all_json() -> dict:
    """Load all JSON data files."""
    data = {}
    for name, path in JSON_FILES.items():
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data[name] = json.load(f)
    return data


def extract_numbers_with_paths(data: Any, prefix: str = "") -> dict:
    """Extract all numbers from JSON with their full paths."""
    numbers = {}

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            numbers.update(extract_numbers_with_paths(value, new_prefix))
    elif isinstance(data, list):
        # Store list length
        if len(data) > 0:
            numbers[f"{prefix}.length"] = len(data)
        for i, item in enumerate(data):
            new_prefix = f"{prefix}[{i}]"
            numbers.update(extract_numbers_with_paths(item, new_prefix))
    elif isinstance(data, (int, float)):
        numbers[prefix] = data

    return numbers


def build_value_index(all_data: dict) -> dict:
    """Build an index of values to their JSON paths."""
    index = {}  # value -> [(file, path), ...]

    for file_name, data in all_data.items():
        paths = extract_numbers_with_paths(data)
        for path, value in paths.items():
            # Normalize value for matching
            if isinstance(value, float):
                key = round(value, 2)
            else:
                key = value

            if key not in index:
                index[key] = []
            index[key].append((file_name, path))

    return index


def format_number(num: float) -> str:
    """Format number for display."""
    if num == int(num):
        return f"{int(num):,}"
    return f"{num:,.2f}"


def find_best_source(value: float, value_index: dict, page_context: str) -> str | None:
    """Find the best JSON source for a value based on page context."""
    key = round(value, 2) if isinstance(value, float) else value

    if key not in value_index:
        return None

    sources = value_index[key]
    if len(sources) == 1:
        file_name, path = sources[0]
        return f"{file_name}.{path}"

    # Prioritize based on page context
    page_lower = page_context.lower()

    # GP pages prefer budget_data
    if 'gp' in page_lower:
        for file_name, path in sources:
            if file_name == 'budget_data':
                return f"{file_name}.{path}"

    # FFR pages prefer ffr_data
    if 'ffr' in page_lower:
        for file_name, path in sources:
            if file_name == 'ffr_data':
                return f"{file_name}.{path}"

    # Default to first source
    file_name, path = sources[0]
    return f"{file_name}.{path}"


def add_data_source_to_stat_boxes(html: str, value_index: dict, page_name: str) -> str:
    """Add data-source attributes to stat-box numbers."""
    # Pattern for stat boxes: <div class="num">62,986</div>
    pattern = r'(<div class="num">)([\d,]+(?:\.\d+)?)(</div>)'

    def replace_stat_box(match):
        prefix, num_str, suffix = match.groups()
        try:
            value = float(num_str.replace(',', ''))
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'{prefix[:-1]} data-source="{source}" data-format="currency">{num_str}{suffix}'
        except ValueError:
            pass
        return match.group(0)

    return re.sub(pattern, replace_stat_box, html)


def add_data_source_to_amounts(html: str, value_index: dict, page_name: str) -> str:
    """Add data-source attributes to amount cells."""
    # Pattern for amounts: <td class="amount">10,300</td>
    pattern = r'(<td class="amount">)([\d,]+(?:\.\d+)?)(</td>)'

    def replace_amount(match):
        prefix, num_str, suffix = match.groups()
        try:
            value = float(num_str.replace(',', ''))
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'<td class="amount" data-source="{source}" data-format="currency">{num_str}{suffix}'
        except ValueError:
            pass
        return match.group(0)

    return re.sub(pattern, replace_amount, html)


def add_data_source_to_percentages(html: str, value_index: dict, page_name: str) -> str:
    """Add data-source attributes to percentage values."""
    # Pattern for percentages in stat boxes
    pattern = r'(<div class="num">)(\d+(?:\.\d+)?)(%)([^<]*</div>)'

    def replace_percent(match):
        prefix, num_str, percent, suffix = match.groups()
        try:
            value = float(num_str)
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'{prefix[:-1]} data-source="{source}" data-format="percent">{num_str}{percent}{suffix}'
        except ValueError:
            pass
        return match.group(0)

    return re.sub(pattern, replace_percent, html)


def add_data_source_to_member_links(html: str, value_index: dict, page_name: str) -> str:
    """Add data-source attributes to member count links in navigation."""
    # Pattern for "All Members (426)" style links (handles relative paths like ../members.html)
    pattern1 = r'(<a[^>]*href="[^"]*members\.html"[^>]*>)All Members \((\d+)\)(</a>)'

    def replace_member_link(match):
        prefix, num_str, suffix = match.groups()
        try:
            value = int(num_str)
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'{prefix[:-1]} data-source="{source}">All Members ({num_str}){suffix}'
        except ValueError:
            pass
        return match.group(0)

    html = re.sub(pattern1, replace_member_link, html)

    # Pattern for "426 Members" style footer links
    pattern2 = r'(<a[^>]*href="[^"]*members\.html"[^>]*>)(\d+) Members(</a>)'

    def replace_member_count(match):
        prefix, num_str, suffix = match.groups()
        try:
            value = int(num_str)
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'{prefix[:-1]} data-source="{source}">{num_str} Members{suffix}'
        except ValueError:
            pass
        return match.group(0)

    html = re.sub(pattern2, replace_member_count, html)

    # Pattern for "Countries (48)" style links
    pattern3 = r'(<a[^>]*href="[^"]*country-contributions\.html"[^>]*>)Countries \((\d+)\)(</a>)'

    def replace_country_count(match):
        prefix, num_str, suffix = match.groups()
        try:
            value = int(num_str)
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'{prefix[:-1]} data-source="{source}">Countries ({num_str}){suffix}'
        except ValueError:
            pass
        return match.group(0)

    html = re.sub(pattern3, replace_country_count, html)

    # Pattern for "48 Countries" style footer links
    pattern4 = r'(<a[^>]*href="[^"]*country-contributions\.html"[^>]*>)(\d+) Countries(</a>)'

    def replace_country_count2(match):
        prefix, num_str, suffix = match.groups()
        try:
            value = int(num_str)
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'{prefix[:-1]} data-source="{source}">{num_str} Countries{suffix}'
        except ValueError:
            pass
        return match.group(0)

    html = re.sub(pattern4, replace_country_count2, html)

    # Pattern for "Management Committee (70)" style links
    pattern5 = r'(<a[^>]*href="[^"]*mc-members\.html"[^>]*>)Management Committee \((\d+)\)(</a>)'

    def replace_mc_link(match):
        prefix, num_str, suffix = match.groups()
        try:
            value = int(num_str)
            source = find_best_source(value, value_index, page_name)
            if source:
                return f'{prefix[:-1]} data-source="{source}">Management Committee ({num_str}){suffix}'
        except ValueError:
            pass
        return match.group(0)

    html = re.sub(pattern5, replace_mc_link, html)

    return html


def add_cost_data_script(html: str) -> str:
    """Add cost-data.js script if not already present."""
    if 'cost-data.js' in html:
        return html

    # Add before </body>
    script_tag = '    <script src="../js/cost-data.js"></script>\n'
    return html.replace('</body>', f'{script_tag}</body>')


def process_html_file(filepath: Path, value_index: dict) -> bool:
    """Process a single HTML file."""
    page_name = filepath.stem

    content = filepath.read_text(encoding='utf-8')
    original = content

    # Add data-source attributes
    content = add_data_source_to_stat_boxes(content, value_index, page_name)
    content = add_data_source_to_amounts(content, value_index, page_name)
    content = add_data_source_to_percentages(content, value_index, page_name)
    content = add_data_source_to_member_links(content, value_index, page_name)

    # Add cost-data.js
    content = add_cost_data_script(content)

    if content != original:
        filepath.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    print("=" * 60)
    print("GENERATING HTML FROM JSON")
    print("=" * 60)

    # Load JSON data
    print("\nLoading JSON data...")
    all_data = load_all_json()
    print(f"  Loaded {len(all_data)} data files")

    # Build value index
    print("\nBuilding value index...")
    value_index = build_value_index(all_data)
    print(f"  Indexed {len(value_index)} unique values")

    # Process HTML files
    print("\nProcessing HTML files...")
    modified = 0
    total = 0

    for html_dir in HTML_DIRS:
        if not html_dir.exists():
            continue

        for html_file in sorted(html_dir.glob("*.html")):
            total += 1
            rel_path = html_file.relative_to(BASE_DIR)

            if process_html_file(html_file, value_index):
                print(f"  [UPDATED] {rel_path}")
                modified += 1
            else:
                print(f"  [UNCHANGED] {rel_path}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files: {total}")
    print(f"Modified: {modified}")
    print(f"\nRun verify_html_numbers.py to check verification rate improvement")


if __name__ == "__main__":
    main()
