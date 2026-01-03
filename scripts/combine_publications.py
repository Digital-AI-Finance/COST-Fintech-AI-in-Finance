"""
Combine publications from OpenAlex and ORCID sources.
Merges publications, keeping unique entries per author (as requested).
Generates final publications.json for GitHub Pages.

Features:
- Preprint deduplication: Removes preprints that match published articles
- Per-author type breakdown: Shows article/book-chapter/dataset counts
"""
import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
from collections import Counter

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Type groupings: map 33 publication types to 6 clean categories
TYPE_GROUPS = {
    'peer_reviewed': ['article', 'review', 'journal-article'],
    'books_chapters': ['book', 'book-chapter', 'edited-book'],
    'conference': ['conference-paper', 'conference-abstract', 'conference-poster',
                   'conference-presentation', 'conference-proceedings', 'conference-output'],
    'preprints': ['preprint', 'working-paper'],
    'datasets': ['dataset', 'data-set', 'software'],
    'other': ['editorial', 'report', 'paratext', 'letter', 'erratum',
              'peer-review', 'dissertation', 'dissertation-thesis',
              'encyclopedia-entry', 'dictionary-entry', 'online-resource',
              'magazine-article', 'book-review', 'license', 'journal-issue',
              'retraction', 'standards-and-policy', 'other']
}

def get_type_group(pub_type: str) -> str:
    """Map a publication type to its group."""
    pub_type = pub_type.lower() if pub_type else 'other'
    for group, types in TYPE_GROUPS.items():
        if pub_type in types:
            return group
    return 'other'


def normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    if not title:
        return ''
    # Lowercase, remove punctuation, normalize whitespace
    title = title.lower().strip()
    for char in '.,;:!?()[]{}"\'-':
        title = title.replace(char, ' ')
    return ' '.join(title.split())


def title_similarity(title1: str, title2: str) -> float:
    """Calculate similarity between two titles (0-1)."""
    t1 = normalize_title(title1)
    t2 = normalize_title(title2)
    if not t1 or not t2:
        return 0.0
    if t1 == t2:
        return 1.0
    # Check if one is substring of other (common for preprints)
    if t1 in t2 or t2 in t1:
        return 0.95
    # Word overlap ratio
    words1 = set(t1.split())
    words2 = set(t2.split())
    if not words1 or not words2:
        return 0.0
    overlap = len(words1 & words2)
    return overlap / max(len(words1), len(words2))


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


def deduplicate_preprints(publications: List[dict]) -> tuple:
    """
    Remove preprints that have matching published articles.
    Returns (deduplicated_list, count_removed).
    """
    # Build index of articles by normalized title
    articles = {}
    for p in publications:
        if p.get('type') == 'article':
            title = normalize_title(p.get('title', ''))
            if title:
                articles[title] = p

    # Check each preprint
    removed = 0
    deduplicated = []

    for p in publications:
        if p.get('type') == 'preprint':
            title = normalize_title(p.get('title', ''))

            # Check for exact title match
            if title in articles:
                removed += 1
                continue

            # Check for high similarity match
            is_duplicate = False
            for article_title in articles:
                if title_similarity(title, article_title) > 0.85:
                    removed += 1
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

        deduplicated.append(p)

    return deduplicated, removed


def compute_author_stats(publications: List[dict]) -> dict:
    """
    Compute per-author statistics with type breakdown, grouped categories,
    open access counts, and citation metrics.

    Returns dict: {orcid: {name, total, by_type, by_group, open_access, cited_works, total_citations}}
    """
    author_stats = {}

    for p in publications:
        orcid = p.get('author_orcid', '')
        if not orcid:
            continue

        if orcid not in author_stats:
            author_stats[orcid] = {
                'name': p.get('author', 'Unknown'),
                'total': 0,
                'by_type': Counter(),
                'by_group': Counter(),
                'open_access': 0,
                'cited_works': 0,
                'total_citations': 0
            }

        author_stats[orcid]['total'] += 1

        # Track by individual type
        pub_type = p.get('type', 'unknown')
        author_stats[orcid]['by_type'][pub_type] += 1

        # Track by grouped category
        group = get_type_group(pub_type)
        author_stats[orcid]['by_group'][group] += 1

        # Track open access
        if p.get('is_open_access', False):
            author_stats[orcid]['open_access'] += 1

        # Track citations
        cited_by = p.get('cited_by', 0) or 0
        if cited_by > 0:
            author_stats[orcid]['cited_works'] += 1
        author_stats[orcid]['total_citations'] += cited_by

    # Convert Counters to dicts and add traditional_pubs count
    for orcid, stats in author_stats.items():
        by_type = dict(stats['by_type'])
        stats['by_type'] = by_type

        by_group = dict(stats['by_group'])
        # Ensure all groups exist (even if 0)
        for group in TYPE_GROUPS.keys():
            if group not in by_group:
                by_group[group] = 0
        stats['by_group'] = by_group

        # Traditional publications = articles + book-chapters + books + reviews
        stats['traditional_pubs'] = sum(
            by_type.get(t, 0) for t in ['article', 'book-chapter', 'book', 'review']
        )

    return author_stats


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

    print(f"\nCombined total (before dedup): {len(combined)}")
    print(f"  From OpenAlex: {openalex_count}")
    print(f"  From ORCID (unique): {orcid_added}")

    # Deduplicate preprints that match published articles
    combined, preprints_removed = deduplicate_preprints(combined)
    print(f"\nPreprint deduplication:")
    print(f"  Duplicate preprints removed: {preprints_removed}")
    print(f"  Final count: {len(combined)}")

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

    # Compute per-author statistics with type breakdown
    author_stats = compute_author_stats(combined)

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
            'from_orcid_unique': orcid_added,
            'preprints_deduplicated': preprints_removed
        },
        'statistics': {
            'by_year': dict(sorted([(k, v) for k, v in by_year.items() if k], key=lambda x: -x[0] if isinstance(x[0], int) else 0)),
            'by_type': dict(sorted(by_type.items(), key=lambda x: -x[1])),
            'top_authors': dict(sorted(by_author.items(), key=lambda x: -x[1])[:50])
        },
        'author_stats': author_stats,
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
        'author_stats': output['author_stats'],
        'publications': [
            {
                'id': p['id'],
                'apa': p['apa'],
                'doi': p['doi'],
                'year': p['year'],
                'author': p['author'],
                'author_orcid': p['author_orcid'],  # Include ORCID for verification
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
    print("  {:<25} {:>6} {:>6} {:>5} {:>5} {:>5} {:>5} {:>5} {:>6}".format(
        "Author", "Total", "PeerRv", "Books", "Conf", "Pre", "Data", "OA", "Cited"))
    print("  " + "-" * 75)

    sorted_authors = sorted(author_stats.items(), key=lambda x: -x[1]['total'])[:10]
    for orcid, stats in sorted_authors:
        name = stats['name'][:25]
        bg = stats['by_group']
        print("  {:<25} {:>6} {:>6} {:>5} {:>5} {:>5} {:>5} {:>5} {:>6}".format(
            name, stats['total'],
            bg.get('peer_reviewed', 0), bg.get('books_chapters', 0),
            bg.get('conference', 0), bg.get('preprints', 0), bg.get('datasets', 0),
            stats['open_access'], stats['cited_works']))

    print("\n" + "-" * 70)
    print("Detailed type breakdown for top 3 authors:")
    for orcid, stats in sorted_authors[:3]:
        name = stats['name']
        by_type = stats['by_type']
        type_str = ", ".join(f"{t}: {c}" for t, c in sorted(by_type.items(), key=lambda x: -x[1]))
        print(f"  {name}:")
        print(f"    {type_str}")
        print(f"    Total citations: {stats['total_citations']}")

    print("=" * 70)


if __name__ == '__main__':
    main()
