"""
Validate COST CA19130 authors - check publication relevance to Finance/AI scope.
Identifies members whose publications are NOT related to the COST Action scope.

Outputs:
- Console report with flagged authors
- data/author_validation_report.json (full details)
- data/excluded_non_finance_orcids.json (RED flag ORCIDs for auto-exclusion)
"""
import json
import sys
import io
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Keywords indicating finance/AI relevance (COST Action CA19130 scope)
FINANCE_KEYWORDS = [
    # Finance terms
    'finance', 'financial', 'fintech', 'banking', 'bank', 'investment',
    'stock', 'market', 'trading', 'portfolio', 'risk management', 'credit',
    'loan', 'cryptocurrency', 'bitcoin', 'blockchain', 'insurance', 'pension',
    'asset', 'pricing', 'econom', 'monetary', 'fiscal', 'interest rate',
    'hedge fund', 'derivatives', 'option pricing', 'futures', 'bond',
    'equity', 'forex', 'exchange rate', 'volatility', 'var ', 'value at risk',
    'garch', 'capital', 'wealth', 'investor', 'shareholder', 'dividend',
    'profit', 'revenue', 'accounting', 'audit', 'tax', 'budget', 'debt',
    'corporate governance', 'esg', 'sustainable finance', 'green bond',
    'crowdfunding', 'p2p lending', 'robo-advisor', 'regtech', 'insurtech',
    'payment', 'mobile banking', 'digital currency', 'central bank',
    'inflation', 'deflation', 'gdp', 'macroeconom', 'microeconom',

    # AI/ML terms relevant to finance
    'machine learning', 'artificial intelligence', 'neural network',
    'deep learning', 'forecasting', 'prediction', 'algorithmic',
    'quantitative', 'time series', 'sentiment analysis', 'nlp',
    'natural language', 'text mining', 'data mining', 'big data',
    'finbert', 'transformer', 'lstm', 'random forest', 'xgboost',
    'classification', 'regression', 'clustering', 'anomaly detection',
    'fraud detection', 'credit scoring', 'default prediction',

    # Statistics/Econometrics
    'econometric', 'panel data', 'causal', 'instrumental variable',
    'difference-in-difference', 'regression discontinuity', 'propensity',
    'heteroskedasticity', 'autocorrelation', 'cointegration', 'granger',
    'bayesian', 'monte carlo', 'bootstrap', 'simulation'
]

# Compile regex patterns for faster matching
KEYWORD_PATTERNS = [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                    for kw in FINANCE_KEYWORDS]


def is_finance_related(text: str) -> bool:
    """Check if text contains any finance/AI keywords."""
    if not text:
        return False
    text_lower = text.lower()
    for pattern in KEYWORD_PATTERNS:
        if pattern.search(text_lower):
            return True
    return False


def get_matching_keywords(text: str) -> list:
    """Get list of finance keywords found in text."""
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for kw, pattern in zip(FINANCE_KEYWORDS, KEYWORD_PATTERNS):
        if pattern.search(text_lower):
            found.append(kw)
    return found


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'

    print("=" * 70)
    print("AUTHOR VALIDATION - COST Action CA19130")
    print("Checking publication relevance to Finance/AI scope")
    print("=" * 70)

    # Load publications
    pub_file = data_dir / 'publications.json'
    if not pub_file.exists():
        print("ERROR: publications.json not found. Run combine_publications.py first.")
        return

    with open(pub_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    publications = data.get('publications', [])
    print(f"\nLoaded {len(publications)} publications")

    # Group publications by author ORCID
    author_pubs = defaultdict(list)
    author_names = {}

    for pub in publications:
        orcid = pub.get('author_orcid', '')
        if not orcid:
            continue
        author_pubs[orcid].append(pub)
        if orcid not in author_names:
            author_names[orcid] = pub.get('author', 'Unknown')

    print(f"Found {len(author_pubs)} unique authors with ORCIDs")

    # Analyze each author
    results = []

    for orcid, pubs in author_pubs.items():
        name = author_names[orcid]
        total = len(pubs)

        # Check each publication
        finance_count = 0
        finance_titles = []
        non_finance_titles = []

        for pub in pubs:
            title = pub.get('title', '')
            venue = pub.get('venue', '')
            combined = f"{title} {venue}"

            if is_finance_related(combined):
                finance_count += 1
                if len(finance_titles) < 3:
                    keywords = get_matching_keywords(combined)
                    finance_titles.append({
                        'title': title[:100],
                        'keywords': keywords[:3]
                    })
            else:
                if len(non_finance_titles) < 5:
                    non_finance_titles.append(title[:100] if title else '(no title)')

        relevance_pct = (finance_count / total * 100) if total > 0 else 0

        # Determine flag
        if relevance_pct == 0:
            flag = 'RED'
        elif relevance_pct < 10:
            flag = 'YELLOW'
        elif relevance_pct < 50:
            flag = 'ORANGE'
        else:
            flag = 'GREEN'

        results.append({
            'orcid': orcid,
            'name': name,
            'total_publications': total,
            'finance_related': finance_count,
            'relevance_pct': round(relevance_pct, 1),
            'flag': flag,
            'sample_finance_titles': finance_titles,
            'sample_non_finance_titles': non_finance_titles
        })

    # Sort by relevance (lowest first to show problems)
    results.sort(key=lambda x: (x['relevance_pct'], -x['total_publications']))

    # Count by flag
    flag_counts = {'RED': 0, 'YELLOW': 0, 'ORANGE': 0, 'GREEN': 0}
    for r in results:
        flag_counts[r['flag']] += 1

    # Print report
    print("\n" + "=" * 70)
    print("RED FLAGS (0% relevance - likely wrong field)")
    print("=" * 70)

    red_flags = [r for r in results if r['flag'] == 'RED']
    excluded_orcids = []

    for i, r in enumerate(red_flags, 1):
        print(f"\n{i}. {r['name']} ({r['orcid']})")
        print(f"   Publications: {r['total_publications']}, Finance-related: {r['finance_related']} ({r['relevance_pct']}%)")
        print(f"   Sample non-finance titles:")
        for title in r['sample_non_finance_titles'][:3]:
            print(f"     - {title}")
        excluded_orcids.append({
            'orcid': r['orcid'],
            'name': r['name'],
            'reason': f"0% finance relevance ({r['total_publications']} non-finance publications)"
        })

    print("\n" + "=" * 70)
    print("YELLOW FLAGS (<10% relevance - may need review)")
    print("=" * 70)

    yellow_flags = [r for r in results if r['flag'] == 'YELLOW']
    for i, r in enumerate(yellow_flags, 1):
        print(f"\n{i}. {r['name']} ({r['orcid']})")
        print(f"   Publications: {r['total_publications']}, Finance-related: {r['finance_related']} ({r['relevance_pct']}%)")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total authors analyzed: {len(results)}")
    print(f"  GREEN (>50% relevance):    {flag_counts['GREEN']}")
    print(f"  ORANGE (10-50% relevance): {flag_counts['ORANGE']}")
    print(f"  YELLOW (<10% relevance):   {flag_counts['YELLOW']}")
    print(f"  RED (0% relevance):        {flag_counts['RED']}")
    print(f"\nAuthors to be AUTO-EXCLUDED: {len(excluded_orcids)}")

    # Save full report
    report = {
        'generated': datetime.now().isoformat(),
        'summary': {
            'total_authors': len(results),
            'green': flag_counts['GREEN'],
            'orange': flag_counts['ORANGE'],
            'yellow': flag_counts['YELLOW'],
            'red': flag_counts['RED'],
            'excluded_count': len(excluded_orcids)
        },
        'authors': results
    }

    report_file = data_dir / 'author_validation_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nSaved full report: {report_file}")

    # Save exclusion list
    exclusion_file = data_dir / 'excluded_non_finance_orcids.json'
    exclusion_data = {
        'generated': datetime.now().isoformat(),
        'reason': 'Authors with 0% finance/AI publication relevance',
        'count': len(excluded_orcids),
        'excluded': excluded_orcids
    }
    with open(exclusion_file, 'w', encoding='utf-8') as f:
        json.dump(exclusion_data, f, indent=2, ensure_ascii=False)
    print(f"Saved exclusion list: {exclusion_file}")

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Review the flagged authors above")
    print("2. Run combine_publications.py to apply exclusions")
    print("3. The excluded authors will be removed from publication counts")
    print("=" * 70)


if __name__ == '__main__':
    main()
