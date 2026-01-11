"""
Update Member Statistics in summary_statistics.json

Extracts member counts from Excel source files and updates JSON.
"""

import json
import pandas as pd
from pathlib import Path


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'

    # Source files
    wg_excel = project_dir / 'working_groups_members' / 'CA19130-WG-members.xlsx'
    mc_json = data_dir / 'mc_members.json'
    summary_json = data_dir / 'summary_statistics.json'

    print("=" * 60)
    print("UPDATING MEMBER STATISTICS")
    print("=" * 60)

    # Read WG members Excel
    print(f"\nReading: {wg_excel}")
    df = pd.read_excel(wg_excel)
    print(f"  Total records: {len(df)}")

    # Get total members (excluding empty rows)
    valid_members = df[df['First Name'].notna() & (df['First Name'] != '')]
    total_members = len(valid_members)
    print(f"  Valid members: {total_members}")

    # Get unique countries
    countries = set()
    for country in valid_members['Country'].dropna():
        # Extract country name from "Country Name (XX)" format
        if '(' in str(country):
            country_name = str(country).split('(')[0].strip()
        else:
            country_name = str(country).strip()
        if country_name:
            countries.add(country_name)
    total_countries = len(countries)
    print(f"  Unique countries: {total_countries}")

    # WG column names
    wg1_col = 'WG1. Transparency in FinTech'
    wg2_col = 'WG2. Transparent versus Black Box Decision-Support Models in the Financial Industry'
    wg3_col = 'WG3. Transparency into Investment Product Performance for Clients'

    # Count WG members
    wg1_count = len(df[df[wg1_col] == 'y'])
    wg2_count = len(df[df[wg2_col] == 'y'])
    wg3_count = len(df[df[wg3_col] == 'y'])

    print(f"\n  WG1 members: {wg1_count}")
    print(f"  WG2 members: {wg2_count}")
    print(f"  WG3 members: {wg3_count}")

    # Count ITC members
    itc_count = len(df[df['ITC'].str.lower() == 'y']) if 'ITC' in df.columns else 0
    print(f"  ITC members: {itc_count}")

    # Count Young Researchers
    yr_count = len(df[df['Young Researcher'].str.lower() == 'y']) if 'Young Researcher' in df.columns else 0
    print(f"  Young Researchers: {yr_count}")

    # Read MC members JSON for MC stats
    print(f"\nReading: {mc_json}")
    with open(mc_json, 'r', encoding='utf-8') as f:
        mc_data = json.load(f)

    mc_total = mc_data['metadata']['totalMembers']
    mc_countries = mc_data['metadata']['countries']
    print(f"  MC members: {mc_total}")
    print(f"  MC countries: {mc_countries}")

    # Read existing summary_statistics.json
    print(f"\nReading: {summary_json}")
    with open(summary_json, 'r', encoding='utf-8') as f:
        summary = json.load(f)

    # Add members section
    summary['members'] = {
        'total': total_members,
        'countries': total_countries,
        'itc': itc_count,
        'young_researchers': yr_count,
        'by_working_group': {
            'WG1': wg1_count,
            'WG2': wg2_count,
            'WG3': wg3_count
        },
        'mc': {
            'total': mc_total,
            'countries': mc_countries
        }
    }

    # Write updated JSON
    print(f"\nWriting: {summary_json}")
    with open(summary_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Members: {total_members}")
    print(f"Countries: {total_countries}")
    print(f"WG1: {wg1_count}, WG2: {wg2_count}, WG3: {wg3_count}")
    print(f"MC Members: {mc_total} from {mc_countries} countries")
    print(f"ITC Members: {itc_count}")
    print(f"Young Researchers: {yr_count}")
    print(f"\nsummary_statistics.json updated successfully!")


if __name__ == '__main__':
    main()
