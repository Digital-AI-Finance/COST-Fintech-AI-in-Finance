"""
Sync JSON Data to HTML Files.

This script reads the budget_data.json and updates the hardcoded values
in HTML files to match the JSON data.

Usage:
    python scripts/sync_json_to_html.py

Source: data/budget_data.json
Output: financial-reports/ffr[1-5].html, work-budget-plans/gp[1-5].html
"""

import sys
import re
import json
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / 'data'
FINANCIAL_REPORTS_DIR = REPO_ROOT / 'financial-reports'
WORK_BUDGET_DIR = REPO_ROOT / 'work-budget-plans'


def format_amount(value, decimals=0):
    """Format amount for HTML display."""
    if decimals == 0:
        return f"{int(round(value)):,}"
    return f"{value:,.{decimals}f}"


def update_stat_box_value(html_content, label_pattern, new_value):
    """
    Update a stat-box value in HTML content.

    Looks for pattern: <div class="num">OLD_VALUE</div><div class="label">LABEL</div>
    """
    # Pattern to find stat-box with specific label
    pattern = rf'(<div class="num">)([\d,\.]+)(</div>\s*<div class="label">[^<]*{label_pattern}[^<]*</div>)'

    def replacer(match):
        return f'{match.group(1)}{new_value}{match.group(3)}'

    return re.sub(pattern, replacer, html_content, flags=re.IGNORECASE)


def update_table_row_amount(html_content, row_label, column_index, new_value):
    """
    Update an amount in a table row.

    Args:
        html_content: HTML string
        row_label: Text in first <td> to identify the row
        column_index: Which amount column to update (1=Budget, 2=Actual)
        new_value: New formatted value
    """
    # More flexible pattern for table rows
    # Looks for: <tr>...<td>LABEL</td>...<td class="amount">VALUE</td>...
    lines = html_content.split('\n')
    updated_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line contains the row label
        if f'<td>{row_label}</td>' in line or f'<td>{row_label} </td>' in line:
            # Found the row, now find and update the right amount column
            amount_count = 0
            j = i

            # Look at following lines for amount cells
            while j < len(lines) and '</tr>' not in lines[j]:
                if 'class="amount"' in lines[j]:
                    amount_count += 1
                    if amount_count == column_index:
                        # Update this amount
                        lines[j] = re.sub(
                            r'(<td class="amount">)([\d,\.]+)(</td>)',
                            rf'\g<1>{new_value}\g<3>',
                            lines[j]
                        )
                j += 1

            # If amounts are on same line as label
            if 'class="amount"' in line:
                # Pattern for row with amounts on same line
                amounts = list(re.finditer(r'<td class="amount">([\d,\.]+)</td>', line))
                if len(amounts) >= column_index:
                    target = amounts[column_index - 1]
                    line = line[:target.start(1)] + new_value + line[target.end(1):]

        updated_lines.append(line)
        i += 1

    return '\n'.join(updated_lines)


def update_ffr_html(gp_num, gp_data):
    """
    Update an FFR HTML file with values from JSON data.

    Args:
        gp_num: Grant period number (1-5)
        gp_data: Dictionary with budget, actual, breakdown
    """
    ffr_path = FINANCIAL_REPORTS_DIR / f'ffr{gp_num}.html'
    if not ffr_path.exists():
        print(f"  SKIP: {ffr_path.name} not found")
        return False

    html_content = ffr_path.read_text(encoding='utf-8')
    original_content = html_content

    budget = gp_data['budget']
    actual = gp_data['actual']
    breakdown = gp_data['breakdown']

    # Update stat boxes (Budget EUR, Actual EUR)
    html_content = update_stat_box_value(html_content, 'Budget', format_amount(budget))
    html_content = update_stat_box_value(html_content, 'Actual', format_amount(actual))

    # Calculate utilization percentage
    utilization = (actual / budget * 100) if budget > 0 else 0
    html_content = update_stat_box_value(html_content, 'Utilization', f"{utilization:.1f}%")

    # Update table rows for each category
    category_mappings = {
        'meetings': 'Meetings',
        'training_schools': 'Training Schools',
        'stsm': 'STSMs',
        'virtual_mobility': 'Virtual Mobility',
        'virtual_networking': 'Virtual Networking',
        'itc_grants': 'ITC Conference',
        'dissemination': 'Dissemination',
        'oersa': 'OERSA',
        'fsac': 'FSAC',
    }

    for json_key, html_label in category_mappings.items():
        if json_key in breakdown:
            value = breakdown[json_key]
            # Update actual column (column 2)
            html_content = update_table_row_amount(
                html_content,
                html_label,
                2,  # Actual column
                format_amount(value)
            )

    # Check if anything changed
    if html_content != original_content:
        ffr_path.write_text(html_content, encoding='utf-8')
        print(f"  UPDATED: {ffr_path.name}")
        return True
    else:
        print(f"  NO CHANGE: {ffr_path.name}")
        return False


def update_overview_html(budget_data):
    """Update the overview.html with totals."""
    overview_path = FINANCIAL_REPORTS_DIR / 'overview.html'
    if not overview_path.exists():
        print(f"  SKIP: overview.html not found")
        return False

    html_content = overview_path.read_text(encoding='utf-8')
    original_content = html_content

    totals = budget_data['totals']

    # Update stat boxes
    html_content = update_stat_box_value(
        html_content, 'Budget', format_amount(totals['total_budget'])
    )
    html_content = update_stat_box_value(
        html_content, 'Actual', format_amount(totals['total_actual'])
    )

    utilization = (totals['total_actual'] / totals['total_budget'] * 100)
    html_content = update_stat_box_value(html_content, 'Utilization', f"{utilization:.1f}%")

    if html_content != original_content:
        overview_path.write_text(html_content, encoding='utf-8')
        print(f"  UPDATED: overview.html")
        return True
    else:
        print(f"  NO CHANGE: overview.html")
        return False


def update_wbp_html(gp_num, gp_data):
    """
    Update a Work-Budget-Plan HTML file with values from JSON data.

    Args:
        gp_num: Grant period number (1-5)
        gp_data: Dictionary with budget, actual, breakdown
    """
    wbp_path = WORK_BUDGET_DIR / f'gp{gp_num}.html'
    if not wbp_path.exists():
        print(f"  SKIP: {wbp_path.name} not found")
        return False

    html_content = wbp_path.read_text(encoding='utf-8')
    original_content = html_content

    budget = gp_data['budget']
    actual = gp_data['actual']

    # Update stat boxes (Budget EUR, Actual EUR)
    html_content = update_stat_box_value(html_content, 'Budget', format_amount(budget))
    html_content = update_stat_box_value(html_content, 'Actual', format_amount(actual))

    # Calculate utilization percentage
    utilization = (actual / budget * 100) if budget > 0 else 0
    html_content = update_stat_box_value(html_content, 'Utilization', f"{utilization:.0f}%")

    # Check if anything changed
    if html_content != original_content:
        wbp_path.write_text(html_content, encoding='utf-8')
        print(f"  UPDATED: {wbp_path.name}")
        return True
    else:
        print(f"  NO CHANGE: {wbp_path.name}")
        return False


def update_wbp_overview_html(budget_data):
    """Update the work-budget-plans/overview.html with totals."""
    overview_path = WORK_BUDGET_DIR / 'overview.html'
    if not overview_path.exists():
        print(f"  SKIP: work-budget-plans/overview.html not found")
        return False

    html_content = overview_path.read_text(encoding='utf-8')
    original_content = html_content

    totals = budget_data['totals']

    # Update stat boxes
    html_content = update_stat_box_value(
        html_content, 'Budget', format_amount(totals['total_budget'])
    )
    html_content = update_stat_box_value(
        html_content, 'Actual', format_amount(totals['total_actual'])
    )

    utilization = (totals['total_actual'] / totals['total_budget'] * 100)
    html_content = update_stat_box_value(html_content, 'Utilization', f"{utilization:.1f}%")

    if html_content != original_content:
        overview_path.write_text(html_content, encoding='utf-8')
        print(f"  UPDATED: work-budget-plans/overview.html")
        return True
    else:
        print(f"  NO CHANGE: work-budget-plans/overview.html")
        return False


def update_stsm_html():
    """
    Update the financial-reports/stsm.html with STSM statistics.

    Syncs stat-boxes from summary_statistics.json:
    - Total STSMs (count)
    - Total EUR Funded
    - Average EUR/STSM
    """
    stsm_path = FINANCIAL_REPORTS_DIR / 'stsm.html'
    if not stsm_path.exists():
        print(f"  SKIP: stsm.html not found")
        return False

    # Load summary statistics
    summary_stats_path = DATA_DIR / 'summary_statistics.json'
    if not summary_stats_path.exists():
        print(f"  SKIP: summary_statistics.json not found")
        return False

    with open(summary_stats_path, encoding='utf-8') as f:
        summary_stats = json.load(f)

    html_content = stsm_path.read_text(encoding='utf-8')
    original_content = html_content

    stsm_data = summary_stats['by_category']['stsm']
    stsm_count = stsm_data['count']
    stsm_total = stsm_data['total']
    stsm_average = stsm_total / stsm_count if stsm_count > 0 else 0

    # Update stat boxes (using same pattern as other files)
    html_content = update_stat_box_value(html_content, 'Total STSMs', str(stsm_count))
    html_content = update_stat_box_value(html_content, 'Total EUR Funded', format_amount(stsm_total))
    html_content = update_stat_box_value(html_content, 'Average EUR/STSM', format_amount(stsm_average))

    if html_content != original_content:
        stsm_path.write_text(html_content, encoding='utf-8')
        print(f"  UPDATED: stsm.html")
        return True
    else:
        print(f"  NO CHANGE: stsm.html")
        return False


def update_stat_item_value(html_content, label_pattern, new_value):
    """
    Update a stat-item value in HTML content (for index.html style).

    Looks for pattern: <div class="stat-number">OLD_VALUE</div>...<div class="stat-label">LABEL</div>
    """
    # Pattern to find stat-item with specific label
    pattern = rf'(<div class="stat-number">)([^<]+)(</div>\s*<div class="stat-label">[^<]*{label_pattern}[^<]*</div>)'

    def replacer(match):
        return f'{match.group(1)}{new_value}{match.group(3)}'

    return re.sub(pattern, replacer, html_content, flags=re.IGNORECASE | re.DOTALL)


def update_fr_index_html():
    """
    Update the financial-reports/index.html with summary statistics.

    Syncs stat-items from summary_statistics.json and other JSON files:
    - Total Expenditure (EUR)
    - Meetings count
    - STSMs Funded count
    - VM Grants count
    - Training Schools count
    - Participants count
    """
    index_path = FINANCIAL_REPORTS_DIR / 'index.html'
    if not index_path.exists():
        print(f"  SKIP: financial-reports/index.html not found")
        return False

    # Load summary statistics
    summary_stats_path = DATA_DIR / 'summary_statistics.json'
    if not summary_stats_path.exists():
        print(f"  SKIP: summary_statistics.json not found")
        return False

    with open(summary_stats_path, encoding='utf-8') as f:
        summary_stats = json.load(f)

    html_content = index_path.read_text(encoding='utf-8')
    original_content = html_content

    # Get totals and category data
    total_actual = summary_stats['totals']['actual']
    meetings_count = summary_stats['by_category']['meetings']['count']
    stsm_count = summary_stats['by_category']['stsm']['count']
    training_schools_count = summary_stats['by_category']['training_schools']['count']

    # Get VM grants count from virtual_mobility_full.json
    vm_grants_count = 39  # Default from scan
    vm_path = DATA_DIR / 'virtual_mobility_full.json'
    if vm_path.exists():
        with open(vm_path, encoding='utf-8') as f:
            vm_data = json.load(f)
            vm_grants_count = len(vm_data)

    # Get participants count from participant_master.json
    participants_count = 182  # Default from scan
    participants_path = DATA_DIR / 'participant_master.json'
    if participants_path.exists():
        with open(participants_path, encoding='utf-8') as f:
            participants_data = json.load(f)
            participants_count = len(participants_data)

    # Format total as "775K" style
    total_k = f"{int(round(total_actual / 1000))}K"

    # Update stat-items (different CSS class than other pages)
    html_content = update_stat_item_value(html_content, 'Total Expenditure', total_k)
    html_content = update_stat_item_value(html_content, 'Meetings', str(meetings_count))
    html_content = update_stat_item_value(html_content, 'STSMs', str(stsm_count))
    html_content = update_stat_item_value(html_content, 'VM Grants', str(vm_grants_count))
    html_content = update_stat_item_value(html_content, 'Training Schools', str(training_schools_count))
    html_content = update_stat_item_value(html_content, 'Participants', str(participants_count))

    if html_content != original_content:
        index_path.write_text(html_content, encoding='utf-8')
        print(f"  UPDATED: financial-reports/index.html")
        return True
    else:
        print(f"  NO CHANGE: financial-reports/index.html")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("COST Action CA19130 - JSON to HTML Sync")
    print("=" * 60)

    # Load budget data
    budget_data_path = DATA_DIR / 'budget_data.json'
    if not budget_data_path.exists():
        print(f"ERROR: budget_data.json not found: {budget_data_path}")
        print("Run sync_ffr_to_json.py first!")
        sys.exit(1)

    with open(budget_data_path) as f:
        budget_data = json.load(f)

    # Update FFR HTML files
    print("\n[1/6] Updating FFR HTML files...")
    for gp_data in budget_data['grant_periods']:
        gp_num = int(gp_data['id'].replace('GP', ''))
        update_ffr_html(gp_num, gp_data)

    # Update FFR overview
    print("\n[2/6] Updating financial-reports/overview.html...")
    update_overview_html(budget_data)

    # Update Work-Budget-Plan HTML files
    print("\n[3/6] Updating Work-Budget-Plan HTML files...")
    for gp_data in budget_data['grant_periods']:
        gp_num = int(gp_data['id'].replace('GP', ''))
        update_wbp_html(gp_num, gp_data)

    # Update WBP overview
    print("\n[4/6] Updating work-budget-plans/overview.html...")
    update_wbp_overview_html(budget_data)

    # Update STSM page
    print("\n[5/6] Updating financial-reports/stsm.html...")
    update_stsm_html()

    # Update financial-reports index
    print("\n[6/6] Updating financial-reports/index.html...")
    update_fr_index_html()

    print("\n" + "=" * 60)
    print("HTML sync complete!")
    print("=" * 60)
    print("\nNote: Run 'pytest tests/ -v' to verify all values match.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
