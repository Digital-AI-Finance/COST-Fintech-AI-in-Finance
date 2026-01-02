"""
Fetch publications from ORCID API for COST Action CA19130 members.
Uses ORCID public API v3.0.

ORCID API: https://info.orcid.org/documentation/api-tutorials/
- Public API: No authentication required
- Rate limit: 24 requests per second (public)

Date range: 2020-2025 (COST Action period)
"""
import json
import time
import sys
import io
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.error
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Configuration
START_YEAR = 2020
END_YEAR = 2025
REQUEST_DELAY = 0.1  # seconds between requests


def format_apa_authors_from_contributors(contributors: List[Dict]) -> str:
    """Format author list in APA style from ORCID contributors."""
    if not contributors:
        return "Unknown Author"

    formatted = []
    for contrib in contributors[:20]:
        name = contrib.get('credit-name', {}).get('value', '')
        if not name:
            # Try to construct from given/family names
            given = contrib.get('contributor-attributes', {}).get('contributor-sequence', '')
            name = contrib.get('credit-name', {}).get('value', 'Unknown')

        if name and name != 'Unknown':
            parts = name.split()
            if len(parts) >= 2:
                last = parts[-1]
                initials = ' '.join(p[0] + '.' for p in parts[:-1])
                formatted.append(f"{last}, {initials}")
            else:
                formatted.append(name)

    if not formatted:
        return "Unknown Author"

    if len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return ' & '.join(formatted)
    else:
        return ', '.join(formatted[:-1]) + ', & ' + formatted[-1]


def get_publication_year(work: Dict) -> Optional[int]:
    """Extract publication year from ORCID work."""
    pub_date = work.get('publication-date', {})
    if pub_date:
        year = pub_date.get('year', {})
        if year and year.get('value'):
            try:
                return int(year.get('value'))
            except:
                pass
    return None


def get_doi(work: Dict) -> Optional[str]:
    """Extract DOI from ORCID work external identifiers."""
    ext_ids = work.get('external-ids', {}).get('external-id', [])
    for ext_id in ext_ids:
        if ext_id.get('external-id-type', '').lower() == 'doi':
            doi_value = ext_id.get('external-id-value', '')
            if doi_value:
                if not doi_value.startswith('http'):
                    return f"https://doi.org/{doi_value}"
                return doi_value
    return None


def format_apa_from_orcid_work(work: Dict, author_name: str) -> str:
    """Format ORCID work in APA style."""
    # Title
    title_obj = work.get('title', {})
    title = title_obj.get('title', {}).get('value', 'Untitled') if title_obj else 'Untitled'

    # Year
    year = get_publication_year(work) or 'n.d.'

    # Journal/Venue
    journal = work.get('journal-title', {})
    venue = journal.get('value', '') if journal else ''

    # Type
    work_type = work.get('type', 'OTHER')

    # For ORCID, we often don't have full author list, so use the COST author
    # In a real scenario, we'd need to fetch the full work details
    authors = author_name
    if ',' not in authors:
        # Convert "First Last" to "Last, F."
        parts = authors.split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = ' '.join(p[0] + '.' for p in parts[:-1])
            authors = f"{last}, {initials}"

    # Build citation
    if work_type == 'JOURNAL_ARTICLE':
        citation = f"{authors} ({year}). {title}."
        if venue:
            citation += f" *{venue}*."
    elif work_type in ['BOOK', 'BOOK_CHAPTER']:
        citation = f"{authors} ({year}). *{title}*."
    elif work_type == 'CONFERENCE_PAPER':
        citation = f"{authors} ({year}). {title}."
        if venue:
            citation += f" In *{venue}*."
    else:
        citation = f"{authors} ({year}). {title}."
        if venue:
            citation += f" *{venue}*."

    # Add DOI
    doi = get_doi(work)
    if doi:
        citation += f" {doi}"

    return citation


def fetch_works_for_orcid(orcid: str) -> List[Dict]:
    """
    Fetch all works for an ORCID from ORCID API.
    Returns list of work dictionaries.
    """
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"

    try:
        request = urllib.request.Request(
            url,
            headers={
                'Accept': 'application/json',
                'User-Agent': 'COST-CA19130-Publications/1.0'
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode())

            works = []
            groups = data.get('group', [])

            for group in groups:
                # Each group may have multiple work summaries (from different sources)
                # Take the first one (usually the most complete)
                summaries = group.get('work-summary', [])
                if summaries:
                    works.append(summaries[0])

            return works

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        print(f"    HTTP Error {e.code}")
        return []
    except Exception as e:
        print(f"    Error: {e}")
        return []


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'

    # Load validated ORCIDs
    orcid_file = data_dir / 'orcid_list.json'
    if not orcid_file.exists():
        print("ERROR: Run extract_and_validate_orcids.py first")
        sys.exit(1)

    with open(orcid_file, 'r', encoding='utf-8') as f:
        orcid_list = json.load(f)

    print("=" * 70)
    print("ORCID Publication Fetcher - COST Action CA19130")
    print("=" * 70)
    print(f"ORCIDs to process: {len(orcid_list)}")
    print(f"Date range: {START_YEAR}-{END_YEAR}")
    print(f"API: ORCID Public API v3.0")
    print()

    all_publications = []
    author_stats = {}

    for i, entry in enumerate(orcid_list):
        orcid = entry['orcid']
        name = entry['name']

        print(f"[{i+1}/{len(orcid_list)}] Fetching: {name} ({orcid})...", end=' ')

        works = fetch_works_for_orcid(orcid)

        # Filter by year
        filtered_works = []
        for work in works:
            year = get_publication_year(work)
            if year and START_YEAR <= year <= END_YEAR:
                filtered_works.append(work)

        print(f"{len(filtered_works)} works (in range)")

        author_stats[orcid] = {
            'name': name,
            'orcid': orcid,
            'total_works': len(works),
            'works_in_range': len(filtered_works)
        }

        # Process each work
        for work in filtered_works:
            title_obj = work.get('title', {})
            title = title_obj.get('title', {}).get('value', '') if title_obj else ''

            pub = {
                'orcid_put_code': work.get('put-code'),
                'doi': get_doi(work),
                'title': title,
                'year': get_publication_year(work),
                'type': work.get('type', ''),
                'venue': work.get('journal-title', {}).get('value', '') if work.get('journal-title') else '',
                'apa_citation': format_apa_from_orcid_work(work, name),
                'cost_author': {
                    'orcid': orcid,
                    'name': name
                },
                'source': work.get('source', {}).get('source-name', {}).get('value', '')
            }
            all_publications.append(pub)

        time.sleep(REQUEST_DELAY)

        # Progress save every 50 authors
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(orcid_list)}, Total pubs: {len(all_publications)}")

    # Sort by year (descending)
    all_publications.sort(key=lambda x: -(x.get('year') or 0))

    # Create output
    output = {
        'metadata': {
            'source': 'ORCID',
            'date_fetched': datetime.now().isoformat(),
            'date_range': f'{START_YEAR}-{END_YEAR}',
            'total_authors': len(orcid_list),
            'total_publications': len(all_publications),
            'authors_with_publications': sum(1 for s in author_stats.values() if s['works_in_range'] > 0)
        },
        'author_stats': list(author_stats.values()),
        'publications': all_publications
    }

    # Save full output
    output_file = data_dir / 'orcid_publications.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {output_file}")

    # Save APA-only version (compact)
    apa_output = {
        'metadata': output['metadata'],
        'publications': [
            {
                'apa': p['apa_citation'],
                'doi': p['doi'],
                'year': p['year'],
                'cost_author': p['cost_author']['name'],
                'cost_author_orcid': p['cost_author']['orcid']
            }
            for p in all_publications
        ]
    }

    apa_file = data_dir / 'orcid_publications_apa.json'
    with open(apa_file, 'w', encoding='utf-8') as f:
        json.dump(apa_output, f, indent=2, ensure_ascii=False)
    print(f"Saved: {apa_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total authors processed:     {len(orcid_list)}")
    print(f"Authors with publications:   {output['metadata']['authors_with_publications']}")
    print(f"Total publications found:    {len(all_publications)}")

    # By year breakdown
    by_year = {}
    for p in all_publications:
        y = p.get('year', 'Unknown')
        by_year[y] = by_year.get(y, 0) + 1

    print("\nPublications by year:")
    for y in sorted([k for k in by_year.keys() if k], reverse=True):
        print(f"  {y}: {by_year[y]}")

    # By type breakdown
    by_type = {}
    for p in all_publications:
        t = p.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1

    print("\nPublications by type:")
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    print("=" * 70)


if __name__ == '__main__':
    main()
