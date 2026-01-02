"""
Remove publications and ORCIDs from terminated/non-approved COST members.

These 6 members had their membership terminated or never approved:
1. Llesh LLESHAJ (0000-0002-7871-9176) - TERMINATED
2. Ferlanda Luna (0000-0002-7094-0749) - TERMINATED
3. Sergio Barbosa (0000-0003-3862-6132) - TERMINATED
4. Fatma Ozge Ozkok (0000-0002-1421-4670) - TERMINATED
5. Gulsah KEKLIK (0000-0002-1775-2773) - SUBMITTED (not approved)
6. Blisard Zani (0000-0001-8774-267X) - TERMINATED

Their 55 publications should be removed from the COST Action publications page.
"""
import json
import sys
import io
from pathlib import Path
from datetime import datetime
from collections import Counter

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Terminated/non-approved members to remove
MEMBERS_TO_REMOVE = [
    {'orcid': '0000-0002-7871-9176', 'name': 'Llesh LLESHAJ'},
    {'orcid': '0000-0002-7094-0749', 'name': 'Ferlanda Luna'},
    {'orcid': '0000-0003-3862-6132', 'name': 'Sérgio Barbosa'},
    {'orcid': '0000-0002-1421-4670', 'name': 'Fatma Ozge Ozkok'},
    {'orcid': '0000-0002-1775-2773', 'name': 'Gülşah KEKLİK'},
    {'orcid': '0000-0001-8774-267X', 'name': 'Blisard Zani'},
]

# Create sets for fast lookup
ORCIDS_TO_REMOVE = {m['orcid'] for m in MEMBERS_TO_REMOVE}
NAMES_TO_REMOVE = {m['name'] for m in MEMBERS_TO_REMOVE}


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'

    print("=" * 70)
    print("Removing Terminated/Non-Approved COST Members")
    print("=" * 70)
    print(f"\nMembers to remove: {len(MEMBERS_TO_REMOVE)}")
    for m in MEMBERS_TO_REMOVE:
        print(f"  - {m['name']} ({m['orcid']})")
    print()

    # 1. Clean orcid_list.json
    print("Step 1: Cleaning orcid_list.json...")
    orcid_file = data_dir / 'orcid_list.json'
    with open(orcid_file, 'r', encoding='utf-8') as f:
        orcid_list = json.load(f)

    original_count = len(orcid_list)
    orcid_list = [entry for entry in orcid_list if entry['orcid'] not in ORCIDS_TO_REMOVE]
    removed_orcids = original_count - len(orcid_list)

    with open(orcid_file, 'w', encoding='utf-8') as f:
        json.dump(orcid_list, f, indent=2, ensure_ascii=False)

    print(f"  Original: {original_count}, After: {len(orcid_list)}, Removed: {removed_orcids}")

    # 2. Clean validated_orcids.json if exists
    validated_file = data_dir / 'validated_orcids.json'
    if validated_file.exists():
        print("\nStep 2: Cleaning validated_orcids.json...")
        with open(validated_file, 'r', encoding='utf-8') as f:
            validated_data = json.load(f)

        if 'validated_orcids' in validated_data:
            orig = len(validated_data['validated_orcids'])
            validated_data['validated_orcids'] = [
                entry for entry in validated_data['validated_orcids']
                if entry.get('orcid') not in ORCIDS_TO_REMOVE
            ]
            removed_validated = orig - len(validated_data['validated_orcids'])

            # Update metadata
            if 'metadata' in validated_data:
                validated_data['metadata']['members_with_orcid'] = len(validated_data['validated_orcids'])
                validated_data['metadata']['valid_format'] = len(validated_data['validated_orcids'])

            with open(validated_file, 'w', encoding='utf-8') as f:
                json.dump(validated_data, f, indent=2, ensure_ascii=False)

            print(f"  Removed {removed_validated} entries")
    else:
        print("\nStep 2: validated_orcids.json not found, skipping")

    # 3. Clean publications.json (full version)
    print("\nStep 3: Cleaning publications.json...")
    full_pub_file = data_dir / 'publications.json'
    if full_pub_file.exists():
        with open(full_pub_file, 'r', encoding='utf-8') as f:
            full_pub_data = json.load(f)

        full_pubs = full_pub_data['publications']
        orig_full = len(full_pubs)

        # Filter using ORCID for more accurate matching
        full_filtered = [p for p in full_pubs if p.get('author_orcid', '') not in ORCIDS_TO_REMOVE]

        full_pub_data['publications'] = full_filtered
        full_pub_data['metadata']['total_publications'] = len(full_filtered)
        full_pub_data['metadata']['total_authors'] = len(orcid_list)

        # Recalculate statistics for full version
        by_year_full = Counter()
        by_type_full = Counter()
        by_author_full = Counter()

        for pub in full_filtered:
            year = pub.get('year')
            if year:
                by_year_full[year] = by_year_full.get(year, 0) + 1
            by_type_full[pub.get('type', 'unknown')] += 1
            by_author_full[pub.get('author', '')] += 1

        full_pub_data['statistics']['by_year'] = dict(sorted(by_year_full.items(), key=lambda x: -x[0] if isinstance(x[0], int) else 0))
        full_pub_data['statistics']['by_type'] = dict(sorted(by_type_full.items(), key=lambda x: -x[1]))
        full_pub_data['statistics']['top_authors'] = dict(sorted(by_author_full.items(), key=lambda x: -x[1])[:50])

        with open(full_pub_file, 'w', encoding='utf-8') as f:
            json.dump(full_pub_data, f, indent=2, ensure_ascii=False)

        print(f"  Original: {orig_full}, After: {len(full_filtered)}, Removed: {orig_full - len(full_filtered)}")

    # 4. Clean publications_apa.json
    print("\nStep 4: Cleaning publications_apa.json...")
    pub_file = data_dir / 'publications_apa.json'
    with open(pub_file, 'r', encoding='utf-8') as f:
        pub_data = json.load(f)

    pubs = pub_data['publications']
    original_pubs = len(pubs)

    # Remove publications from terminated members (using ORCID for accuracy)
    removed_pubs_details = []
    filtered_pubs = []
    for pub in pubs:
        author = pub.get('author', '')
        author_orcid = pub.get('author_orcid', '')
        # Check both ORCID and name for matching
        if author_orcid in ORCIDS_TO_REMOVE or author in NAMES_TO_REMOVE:
            removed_pubs_details.append({'author': author, 'doi': pub.get('doi', 'N/A')})
        else:
            filtered_pubs.append(pub)

    removed_pubs = original_pubs - len(filtered_pubs)

    # Update publications list
    pub_data['publications'] = filtered_pubs

    # Update metadata
    pub_data['metadata']['total_publications'] = len(filtered_pubs)
    pub_data['metadata']['total_authors'] = len(orcid_list)  # Updated count

    # Recalculate statistics
    by_year = Counter()
    by_type = Counter()
    by_author = Counter()

    for pub in filtered_pubs:
        year = pub.get('year')
        if year:
            by_year[str(year)] += 1

        pub_type = pub.get('type', 'unknown')
        by_type[pub_type] += 1

        author = pub.get('author', '')
        if author:
            by_author[author] += 1

    pub_data['statistics']['by_year'] = dict(sorted(by_year.items(), reverse=True))
    pub_data['statistics']['by_type'] = dict(sorted(by_type.items(), key=lambda x: -x[1]))
    pub_data['statistics']['top_authors'] = dict(sorted(by_author.items(), key=lambda x: -x[1])[:50])

    with open(pub_file, 'w', encoding='utf-8') as f:
        json.dump(pub_data, f, indent=2, ensure_ascii=False)

    print(f"  Original: {original_pubs}, After: {len(filtered_pubs)}, Removed: {removed_pubs}")

    # Show removed publications by author
    print("\n  Removed publications by author:")
    author_counts = Counter(p['author'] for p in removed_pubs_details)
    for author, count in sorted(author_counts.items(), key=lambda x: -x[1]):
        print(f"    - {author}: {count} publications")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"ORCIDs removed:       {removed_orcids}")
    print(f"Publications removed: {removed_pubs}")
    print(f"\nFinal counts:")
    print(f"  orcid_list.json:        {len(orcid_list)} members")
    print(f"  publications_apa.json:  {len(filtered_pubs)} publications")
    print("=" * 70)

    return removed_pubs == 55 and removed_orcids == 6


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
