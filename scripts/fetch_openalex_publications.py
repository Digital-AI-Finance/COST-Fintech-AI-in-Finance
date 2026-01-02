"""
Fetch publications from OpenAlex for COST Action CA19130 members.
Uses ORCID identifiers to query OpenAlex API.

OpenAlex API: https://docs.openalex.org/
- No authentication required for polite use
- Rate limit: ~100,000 requests/day
- Add email to User-Agent for polite pool

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
import urllib.parse
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Configuration
USER_EMAIL = "research@digital-ai-finance.org"  # For polite pool
START_YEAR = 2020
END_YEAR = 2025
REQUEST_DELAY = 0.2  # seconds between requests


def format_apa_authors(authors: List[Dict]) -> str:
    """Format author list in APA style."""
    if not authors:
        return "Unknown Author"

    formatted = []
    for i, author in enumerate(authors[:20]):  # Limit to 20 authors
        author_obj = author.get('author', {}) or {}
        name = author_obj.get('display_name', '') or 'Unknown'
        if not name or name == 'Unknown':
            continue
        parts = name.split()
        if len(parts) >= 2:
            # Last, F. M. format
            last = parts[-1]
            initials = ' '.join(p[0] + '.' for p in parts[:-1])
            formatted.append(f"{last}, {initials}")
        else:
            formatted.append(name)

    if not formatted:
        return "Unknown Author"

    if len(authors) > 20 and len(formatted) > 1:
        # APA: list first 19, then ..., then last author
        return ', '.join(formatted[:19]) + ', ... ' + formatted[-1]
    elif len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return ' & '.join(formatted)
    else:
        return ', '.join(formatted[:-1]) + ', & ' + formatted[-1]


def format_apa_citation(work: Dict) -> str:
    """Format a single work in APA style."""
    # Authors
    authors = format_apa_authors(work.get('authorships', []))

    # Year
    year = work.get('publication_year', 'n.d.')

    # Title
    title = work.get('title', 'Untitled')
    if title:
        title = title.rstrip('.')

    # Source (journal, book, etc.)
    source = work.get('primary_location', {})
    source_info = source.get('source', {}) or {}
    venue = source_info.get('display_name', '')

    # Type-specific formatting
    work_type = work.get('type', 'article')

    if work_type == 'article':
        # Journal article: Author. (Year). Title. Journal, Volume(Issue), Pages. DOI
        volume = work.get('biblio', {}).get('volume', '')
        issue = work.get('biblio', {}).get('issue', '')
        first_page = work.get('biblio', {}).get('first_page', '')
        last_page = work.get('biblio', {}).get('last_page', '')

        citation = f"{authors} ({year}). {title}."
        if venue:
            citation += f" *{venue}*"
            if volume:
                citation += f", *{volume}*"
                if issue:
                    citation += f"({issue})"
            if first_page:
                if last_page and last_page != first_page:
                    citation += f", {first_page}-{last_page}"
                else:
                    citation += f", {first_page}"
        citation += "."

    elif work_type in ['book', 'book-chapter']:
        # Book: Author. (Year). *Title*. Publisher.
        publisher = source_info.get('host_organization_name', '')
        citation = f"{authors} ({year}). *{title}*."
        if publisher:
            citation += f" {publisher}."

    elif work_type == 'proceedings-article':
        # Conference: Author. (Year). Title. In *Proceedings of Conference* (pp. X-Y).
        citation = f"{authors} ({year}). {title}."
        if venue:
            citation += f" In *{venue}*."

    else:
        # Default format
        citation = f"{authors} ({year}). {title}."
        if venue:
            citation += f" *{venue}*."

    # Add DOI
    doi = work.get('doi', '')
    if doi:
        # Ensure DOI is a URL
        if not doi.startswith('http'):
            doi = f"https://doi.org/{doi.replace('https://doi.org/', '')}"
        citation += f" {doi}"

    return citation


def fetch_works_for_orcid(orcid: str, start_year: int, end_year: int) -> List[Dict]:
    """
    Fetch all works for an ORCID from OpenAlex.
    Returns list of work dictionaries.
    """
    works = []
    cursor = '*'
    page = 0

    while cursor:
        # Build URL with filters
        params = {
            'filter': f'author.orcid:{orcid},publication_year:{start_year}-{end_year}',
            'per-page': 100,
            'cursor': cursor,
            'mailto': USER_EMAIL
        }

        url = f"https://api.openalex.org/works?{urllib.parse.urlencode(params)}"

        try:
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': f'COST-CA19130-Publications/1.0 (mailto:{USER_EMAIL})',
                    'Accept': 'application/json'
                }
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode())
                results = data.get('results', [])
                works.extend(results)

                # Get next cursor
                meta = data.get('meta', {})
                cursor = meta.get('next_cursor')

                page += 1

                # Safety limit
                if page > 50:  # Max 5000 works per author
                    break

        except urllib.error.HTTPError as e:
            print(f"    HTTP Error {e.code} for {orcid}")
            break
        except Exception as e:
            print(f"    Error for {orcid}: {e}")
            break

        time.sleep(REQUEST_DELAY)

    return works


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
    print("OpenAlex Publication Fetcher - COST Action CA19130")
    print("=" * 70)
    print(f"ORCIDs to process: {len(orcid_list)}")
    print(f"Date range: {START_YEAR}-{END_YEAR}")
    print(f"API: OpenAlex (polite pool)")
    print()

    all_publications = []
    author_stats = {}

    for i, entry in enumerate(orcid_list):
        orcid = entry['orcid']
        name = entry['name']

        print(f"[{i+1}/{len(orcid_list)}] Fetching: {name} ({orcid})...", end=' ')

        works = fetch_works_for_orcid(orcid, START_YEAR, END_YEAR)

        print(f"{len(works)} works")

        author_stats[orcid] = {
            'name': name,
            'orcid': orcid,
            'work_count': len(works)
        }

        # Process each work
        for work in works:
            pub = {
                'openalex_id': work.get('id', ''),
                'doi': work.get('doi', ''),
                'title': work.get('title', ''),
                'year': work.get('publication_year'),
                'type': work.get('type', ''),
                'venue': (work.get('primary_location', {}).get('source', {}) or {}).get('display_name', ''),
                'is_open_access': work.get('open_access', {}).get('is_oa', False),
                'cited_by_count': work.get('cited_by_count', 0),
                'apa_citation': format_apa_citation(work),
                'cost_author': {
                    'orcid': orcid,
                    'name': name
                },
                'all_authors': [
                    {
                        'name': a.get('author', {}).get('display_name', ''),
                        'orcid': a.get('author', {}).get('orcid', '')
                    }
                    for a in work.get('authorships', [])
                ]
            }
            all_publications.append(pub)

        # Progress save every 50 authors
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(orcid_list)}, Total pubs: {len(all_publications)}")

    # Sort by year (descending), then by citations
    all_publications.sort(key=lambda x: (-x.get('year', 0), -x.get('cited_by_count', 0)))

    # Create output
    output = {
        'metadata': {
            'source': 'OpenAlex',
            'date_fetched': datetime.now().isoformat(),
            'date_range': f'{START_YEAR}-{END_YEAR}',
            'total_authors': len(orcid_list),
            'total_publications': len(all_publications),
            'authors_with_publications': sum(1 for s in author_stats.values() if s['work_count'] > 0)
        },
        'author_stats': list(author_stats.values()),
        'publications': all_publications
    }

    # Save full output
    output_file = data_dir / 'openalex_publications.json'
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

    apa_file = data_dir / 'openalex_publications_apa.json'
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
    for y in sorted(by_year.keys(), reverse=True):
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
