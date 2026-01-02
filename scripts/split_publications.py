"""
Split publications into separate categories for different pages.

Categories:
1. Traditional Publications - articles, books, chapters, conference papers
2. Preprints - not yet peer-reviewed
3. Datasets - data deposits and software
4. Other - paratext, peer-reviews, errata, etc.
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

# Type classifications
PUBLICATION_TYPES = [
    'article', 'journal-article', 'book', 'book-chapter', 'review',
    'conference-paper', 'report', 'editorial', 'working-paper',
    'edited-book', 'dissertation', 'dissertation-thesis', 'letter',
    'encyclopedia-entry', 'conference-proceedings', 'magazine-article',
    'online-resource', 'conference-output'
]

PREPRINT_TYPES = ['preprint']

DATASET_TYPES = ['dataset', 'data-set', 'software']

# Everything else goes to "other"


def create_output_file(pubs, output_path, category_name):
    """Create a JSON file for a category of publications."""
    # Calculate statistics
    by_year = Counter()
    by_type = Counter()
    by_author = Counter()
    unique_dois = set()

    for pub in pubs:
        year = pub.get('year')
        if year:
            by_year[str(year)] += 1

        pub_type = pub.get('type', 'unknown')
        by_type[pub_type] += 1

        author = pub.get('author', '')
        if author:
            by_author[author] += 1

        doi = pub.get('doi', '')
        if doi:
            unique_dois.add(doi.lower())

    output = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'category': category_name,
            'total_publications': len(pubs),
            'unique_dois': len(unique_dois),
            'total_authors': len(by_author)
        },
        'statistics': {
            'by_year': dict(sorted(by_year.items(), reverse=True)),
            'by_type': dict(sorted(by_type.items(), key=lambda x: -x[1])),
            'top_authors': dict(sorted(by_author.items(), key=lambda x: -x[1])[:50])
        },
        'publications': pubs
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return len(pubs)


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'

    print("=" * 70)
    print("Publication Splitter - COST Action CA19130")
    print("=" * 70)

    # Load source data
    source_file = data_dir / 'publications_apa.json'
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_pubs = data['publications']
    print(f"\nSource: {len(all_pubs)} total items")

    # Split into categories
    publications = []
    preprints = []
    datasets = []
    other = []

    for pub in all_pubs:
        pub_type = pub.get('type', 'unknown')

        if pub_type in PUBLICATION_TYPES:
            publications.append(pub)
        elif pub_type in PREPRINT_TYPES:
            preprints.append(pub)
        elif pub_type in DATASET_TYPES:
            datasets.append(pub)
        else:
            other.append(pub)

    # Verify no publications lost
    total_split = len(publications) + len(preprints) + len(datasets) + len(other)
    if total_split != len(all_pubs):
        print(f"ERROR: Split total ({total_split}) != source total ({len(all_pubs)})")
        return False

    print(f"\nSplit results:")
    print(f"  Publications: {len(publications)}")
    print(f"  Preprints:    {len(preprints)}")
    print(f"  Datasets:     {len(datasets)}")
    print(f"  Other:        {len(other)}")
    print(f"  TOTAL:        {total_split}")

    # Re-number IDs within each category
    for i, pub in enumerate(publications, 1):
        pub['id'] = i
    for i, pub in enumerate(preprints, 1):
        pub['id'] = i
    for i, pub in enumerate(datasets, 1):
        pub['id'] = i
    for i, pub in enumerate(other, 1):
        pub['id'] = i

    # Create output files
    print("\nGenerating output files...")

    count_pubs = create_output_file(
        publications,
        data_dir / 'publications_main.json',
        'Traditional Publications'
    )
    print(f"  publications_main.json: {count_pubs} items")

    count_preprints = create_output_file(
        preprints,
        data_dir / 'preprints.json',
        'Preprints'
    )
    print(f"  preprints.json: {count_preprints} items")

    count_datasets = create_output_file(
        datasets,
        data_dir / 'datasets.json',
        'Datasets'
    )
    print(f"  datasets.json: {count_datasets} items")

    count_other = create_output_file(
        other,
        data_dir / 'other_outputs.json',
        'Other Outputs'
    )
    print(f"  other_outputs.json: {count_other} items")

    # Show type breakdown for "other"
    print("\n'Other' category breakdown:")
    other_types = Counter(p.get('type', 'unknown') for p in other)
    for t, c in sorted(other_types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Publications (articles, books, etc.): {count_pubs}")
    print(f"Preprints:                            {count_preprints}")
    print(f"Datasets:                             {count_datasets}")
    print(f"Other:                                {count_other}")
    print(f"TOTAL:                                {count_pubs + count_preprints + count_datasets + count_other}")
    print("=" * 70)

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
