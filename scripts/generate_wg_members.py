"""
Generate Working Group members JSON from COST Action CA19130 data.
Creates separate lists for WG1, WG2, WG3 and a combined view.
"""
import pandas as pd
import json
from pathlib import Path


def extract_country_name(country_str):
    """Extract country name from format 'Country Name (XX)'"""
    if pd.isna(country_str):
        return 'Unknown'
    if '(' in str(country_str):
        return str(country_str).split('(')[0].strip()
    return str(country_str).strip()


def extract_country_code(country_str):
    """Extract country code from format 'Country Name (XX)'"""
    if pd.isna(country_str):
        return 'XX'
    if '(' in str(country_str) and ')' in str(country_str):
        code = str(country_str).split('(')[1].split(')')[0]
        return code.strip()
    return 'XX'


def process_member(row):
    """Process a single member row into a dictionary."""
    first_name = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ''
    last_name = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name')) else ''

    if not first_name and not last_name:
        return None

    country_full = row.get('Country', '')

    return {
        'firstName': first_name,
        'lastName': last_name,
        'name': f"{first_name} {last_name}".strip(),
        'affiliation': str(row.get('Affiliation', '')).strip() if pd.notna(row.get('Affiliation')) else None,
        'country': extract_country_name(country_full),
        'countryCode': extract_country_code(country_full),
        'email': str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else None,
        'orcid': str(row.get('Orcid', '')).strip() if pd.notna(row.get('Orcid')) else None,
        'homepage': str(row.get('Homepages', '')).strip() if pd.notna(row.get('Homepages')) else None,
        'gender': str(row.get('Gender', '')).strip() if pd.notna(row.get('Gender')) else None,
        'itc': str(row.get('ITC', '')).lower() == 'y',
        'mc': str(row.get('MC Membership Status', '')).lower() == 'member',
        'youngResearcher': str(row.get('Young Researcher', '')).lower() == 'y',
        'scientificExpertise': str(row.get('Scientific Expertise', '')).strip() if pd.notna(row.get('Scientific Expertise')) else None,
    }


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent

    # Input file
    wg_file = project_dir / 'working_groups_members' / 'CA19130-WG-members.xlsx'

    # Output directory
    output_dir = project_dir / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading: {wg_file}")
    df = pd.read_excel(wg_file)
    print(f"Total records: {len(df)}")

    # WG column names
    wg1_col = 'WG1. Transparency in FinTech'
    wg2_col = 'WG2. Transparent versus Black Box Decision-Support Models in the Financial Industry'
    wg3_col = 'WG3. Transparency into Investment Product Performance for Clients'

    # Filter by WG
    wg1_df = df[df[wg1_col] == 'y']
    wg2_df = df[df[wg2_col] == 'y']
    wg3_df = df[df[wg3_col] == 'y']

    print(f"WG1 members: {len(wg1_df)}")
    print(f"WG2 members: {len(wg2_df)}")
    print(f"WG3 members: {len(wg3_df)}")

    # Process each WG
    def process_wg(wg_df, wg_name, wg_title):
        members = []
        for _, row in wg_df.iterrows():
            member = process_member(row)
            if member:
                members.append(member)

        # Sort by country then name
        members.sort(key=lambda x: (x['country'].lower(), x['lastName'].lower(), x['firstName'].lower()))

        return {
            'metadata': {
                'workingGroup': wg_name,
                'title': wg_title,
                'totalMembers': len(members),
                'countries': len(set(m['country'] for m in members)),
                'itcMembers': sum(1 for m in members if m['itc']),
                'mcMembers': sum(1 for m in members if m['mc']),
                'generated': pd.Timestamp.now().isoformat()
            },
            'members': members
        }

    wg1_data = process_wg(wg1_df, 'WG1', 'Transparency in FinTech')
    wg2_data = process_wg(wg2_df, 'WG2', 'Transparent versus Black Box Decision-Support Models in the Financial Industry')
    wg3_data = process_wg(wg3_df, 'WG3', 'Transparency into Investment Product Performance for Clients')

    # Save individual WG files
    for wg_data, filename in [(wg1_data, 'wg1_members.json'),
                               (wg2_data, 'wg2_members.json'),
                               (wg3_data, 'wg3_members.json')]:
        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(wg_data, f, indent=2, ensure_ascii=False)
        print(f"Saved: {output_file}")

    # Create combined WG file
    combined_data = {
        'metadata': {
            'title': 'Working Group Members',
            'description': 'COST Action CA19130 Working Groups',
            'generated': pd.Timestamp.now().isoformat()
        },
        'workingGroups': {
            'WG1': wg1_data,
            'WG2': wg2_data,
            'WG3': wg3_data
        }
    }

    combined_output = output_dir / 'wg_members.json'
    with open(combined_output, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {combined_output}")

    # Print statistics
    print("\n=== Working Group Statistics ===")
    for wg_name, wg_data in [('WG1', wg1_data), ('WG2', wg2_data), ('WG3', wg3_data)]:
        meta = wg_data['metadata']
        print(f"\n{wg_name}: {meta['title'][:50]}...")
        print(f"  Members: {meta['totalMembers']}")
        print(f"  Countries: {meta['countries']}")
        print(f"  ITC members: {meta['itcMembers']}")
        print(f"  MC members: {meta['mcMembers']}")


if __name__ == '__main__':
    main()
