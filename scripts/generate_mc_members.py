"""
Generate MC (Management Committee) members JSON from COST Action CA19130 data.
Extracts MC members from the WG members Excel file.
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


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent

    # Input file
    wg_file = project_dir / 'working_groups_members' / 'CA19130-WG-members.xlsx'

    # Output files
    output_dir = project_dir / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)
    mc_output = output_dir / 'mc_members.json'

    print(f"Reading: {wg_file}")
    df = pd.read_excel(wg_file)

    # Filter MC members
    mc_df = df[df['MC Membership Status'] == 'Member'].copy()
    print(f"Found {len(mc_df)} MC members")

    # Process MC members
    mc_members = []
    for _, row in mc_df.iterrows():
        first_name = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ''
        last_name = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name')) else ''

        if not first_name and not last_name:
            continue

        country_full = row.get('Country', '')

        member = {
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
            'wg1': str(row.get('WG1. Transparency in FinTech', '')).lower() == 'y',
            'wg2': str(row.get('WG2. Transparent versus Black Box Decision-Support Models in the Financial Industry', '')).lower() == 'y',
            'wg3': str(row.get('WG3. Transparency into Investment Product Performance for Clients', '')).lower() == 'y',
        }
        mc_members.append(member)

    # Sort by country then name
    mc_members.sort(key=lambda x: (x['country'].lower(), x['lastName'].lower(), x['firstName'].lower()))

    # Create output with metadata
    output_data = {
        'metadata': {
            'title': 'Management Committee Members',
            'description': 'COST Action CA19130 Management Committee',
            'totalMembers': len(mc_members),
            'countries': len(set(m['country'] for m in mc_members)),
            'generated': pd.Timestamp.now().isoformat()
        },
        'members': mc_members
    }

    # Save JSON
    with open(mc_output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Saved: {mc_output}")

    # Statistics
    print("\n=== MC Members Statistics ===")
    print(f"Total MC members: {len(mc_members)}")
    print(f"Countries: {len(set(m['country'] for m in mc_members))}")
    print(f"ITC members: {sum(1 for m in mc_members if m['itc'])}")
    print(f"Male: {sum(1 for m in mc_members if m.get('gender') == 'Male')}")
    print(f"Female: {sum(1 for m in mc_members if m.get('gender') == 'Female')}")

    # Country breakdown
    print("\n=== Members by Country ===")
    countries = {}
    for m in mc_members:
        c = m['country']
        countries[c] = countries.get(c, 0) + 1
    for c in sorted(countries.keys()):
        print(f"  {c}: {countries[c]}")


if __name__ == '__main__':
    main()
