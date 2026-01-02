"""
Combine publications from OpenAlex and ORCID sources.
Merges publications, keeping unique entries per author (as requested).
Generates final publications.json for GitHub Pages.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set


def normalize_doi(doi: str) -> str:
    """Normalize DOI for comparison."""
    if not doi:
        return ''
    doi = str(doi).lower().strip()
    # Remove URL prefix
    for prefix in ['https://doi.org/', 'http://doi.org/', 'doi.org/', 'doi:']:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'

    print("=" * 70)
    print("Publication Combiner - COST Action CA19130")
    print("=" * 70)

    # Load OpenAlex publications
    openalex_file = data_dir / 'openalex_publications.json'
    orcid_file = data_dir / 'orcid_publications.json'

    openalex_pubs = []
    orcid_pubs = []

    if openalex_file.exists():
        with open(openalex_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            openalex_pubs = data.get('publications', [])
        print(f"OpenAlex publications: {len(openalex_pubs)}")
    else:
        print("OpenAlex file not found - skipping")

    if orcid_file.exists():
        with open(orcid_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            orcid_pubs = data.get('publications', [])
        print(f"ORCID publications: {len(orcid_pubs)}")
    else:
        print("ORCID file not found - skipping")

    if not openalex_pubs and not orcid_pubs:
        print("ERROR: No publications to combine. Run fetcher scripts first.")
        return

    # Combine publications
    # Strategy: Show per author (as requested), but track duplicates for statistics
    # Use DOI as unique identifier where available

    combined = []
    seen_per_author = {}  # {author_orcid: set of DOIs}

    # Process OpenAlex first (generally better metadata)
    for pub in openalex_pubs:
        author_orcid = pub.get('cost_author', {}).get('orcid', '')
        doi = normalize_doi(pub.get('doi', ''))

        if author_orcid not in seen_per_author:
            seen_per_author[author_orcid] = set()

        # Skip if we've seen this DOI for this author
        if doi and doi in seen_per_author[author_orcid]:
            continue

        if doi:
            seen_per_author[author_orcid].add(doi)

        combined.append({
            'id': len(combined) + 1,
            'source': 'OpenAlex',
            'doi': pub.get('doi', ''),
            'title': pub.get('title', ''),
            'year': pub.get('year'),
            'type': pub.get('type', ''),
            'venue': pub.get('venue', ''),
            'apa': pub.get('apa_citation', ''),
            'author': pub.get('cost_author', {}).get('name', ''),
            'author_orcid': author_orcid,
            'cited_by': pub.get('cited_by_count', 0),
            'is_open_access': pub.get('is_open_access', False)
        })

    openalex_count = len(combined)

    # Process ORCID publications (add unique ones)
    orcid_added = 0
    for pub in orcid_pubs:
        author_orcid = pub.get('cost_author', {}).get('orcid', '')
        doi = normalize_doi(pub.get('doi', ''))

        if author_orcid not in seen_per_author:
            seen_per_author[author_orcid] = set()

        # Skip if we've seen this DOI for this author
        if doi and doi in seen_per_author[author_orcid]:
            continue

        if doi:
            seen_per_author[author_orcid].add(doi)

        combined.append({
            'id': len(combined) + 1,
            'source': 'ORCID',
            'doi': pub.get('doi', ''),
            'title': pub.get('title', ''),
            'year': pub.get('year'),
            'type': pub.get('type', ''),
            'venue': pub.get('venue', ''),
            'apa': pub.get('apa_citation', ''),
            'author': pub.get('cost_author', {}).get('name', ''),
            'author_orcid': author_orcid,
            'cited_by': 0,
            'is_open_access': False
        })
        orcid_added += 1

    print(f"\nCombined total: {len(combined)}")
    print(f"  From OpenAlex: {openalex_count}")
    print(f"  From ORCID (unique): {orcid_added}")

    # Sort by year (descending), then by citations
    combined.sort(key=lambda x: (-(x.get('year') or 0), -(x.get('cited_by') or 0)))

    # Generate statistics
    by_year = {}
    by_type = {}
    by_author = {}
    unique_dois = set()

    for pub in combined:
        y = pub.get('year', 'Unknown')
        by_year[y] = by_year.get(y, 0) + 1

        t = pub.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1

        a = pub.get('author', 'Unknown')
        by_author[a] = by_author.get(a, 0) + 1

        doi = normalize_doi(pub.get('doi', ''))
        if doi:
            unique_dois.add(doi)

    # Create output
    output = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'sources': ['OpenAlex', 'ORCID'],
            'date_range': '2020-2025',
            'total_publications': len(combined),
            'unique_dois': len(unique_dois),
            'total_authors': len(by_author),
            'from_openalex': openalex_count,
            'from_orcid_unique': orcid_added
        },
        'statistics': {
            'by_year': dict(sorted([(k, v) for k, v in by_year.items() if k], key=lambda x: -x[0] if isinstance(x[0], int) else 0)),
            'by_type': dict(sorted(by_type.items(), key=lambda x: -x[1])),
            'top_authors': dict(sorted(by_author.items(), key=lambda x: -x[1])[:50])
        },
        'publications': combined
    }

    # Save combined output
    output_file = data_dir / 'publications.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {output_file}")

    # Save compact APA-only version for web display
    apa_output = {
        'metadata': output['metadata'],
        'statistics': output['statistics'],
        'publications': [
            {
                'id': p['id'],
                'apa': p['apa'],
                'doi': p['doi'],
                'year': p['year'],
                'author': p['author'],
                'type': p['type']
            }
            for p in combined
        ]
    }

    apa_file = data_dir / 'publications_apa.json'
    with open(apa_file, 'w', encoding='utf-8') as f:
        json.dump(apa_output, f, indent=2, ensure_ascii=False)
    print(f"Saved: {apa_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("COMBINED PUBLICATIONS SUMMARY")
    print("=" * 70)
    print(f"Total publications:    {len(combined)}")
    print(f"Unique DOIs:          {len(unique_dois)}")
    print(f"Authors represented:   {len(by_author)}")

    print("\nBy year:")
    for y in sorted([k for k in by_year.keys() if isinstance(k, int)], reverse=True):
        print(f"  {y}: {by_year[y]}")

    print("\nBy type (top 10):")
    for t, c in list(sorted(by_type.items(), key=lambda x: -x[1]))[:10]:
        print(f"  {t}: {c}")

    print("\nTop 10 authors by publication count:")
    for a, c in list(sorted(by_author.items(), key=lambda x: -x[1]))[:10]:
        print(f"  {a}: {c}")

    print("=" * 70)


if __name__ == '__main__':
    main()
