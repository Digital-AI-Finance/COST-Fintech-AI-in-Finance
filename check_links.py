"""
Comprehensive Link Checker for COST-Fintech-AI-in-Finance Website
Deep crawls the entire site and checks all internal and external links.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import time
import concurrent.futures

BASE_URL = "https://digital-ai-finance.github.io/COST-Fintech-AI-in-Finance/"

# Track results
visited_pages = set()
checked_links = {}  # url -> status
broken_links = defaultdict(list)  # broken_url -> [pages_containing_it]
external_links = {}  # url -> status
all_pages_found = set()

def get_page_links(url):
    """Fetch a page and extract all links."""
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return None, [], response.status_code

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        # Get all href attributes
        for tag in soup.find_all(['a', 'link']):
            href = tag.get('href')
            if href:
                links.append(href)

        # Get all src attributes (images, scripts)
        for tag in soup.find_all(['img', 'script']):
            src = tag.get('src')
            if src:
                links.append(src)

        return soup, links, 200
    except requests.exceptions.Timeout:
        return None, [], 'TIMEOUT'
    except requests.exceptions.ConnectionError:
        return None, [], 'CONNECTION_ERROR'
    except Exception as e:
        return None, [], str(e)

def check_link(url, timeout=10):
    """Check if a link is accessible."""
    if url in checked_links:
        return checked_links[url]

    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        status = response.status_code
    except requests.exceptions.Timeout:
        status = 'TIMEOUT'
    except requests.exceptions.ConnectionError:
        status = 'CONNECTION_ERROR'
    except Exception as e:
        status = f'ERROR: {str(e)[:50]}'

    checked_links[url] = status
    return status

def normalize_url(base_url, href):
    """Normalize a URL relative to a base."""
    if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
        return None

    # Handle relative URLs
    full_url = urljoin(base_url, href)
    return full_url

def is_internal_link(url):
    """Check if URL is internal to the site."""
    return url.startswith(BASE_URL)

def crawl_site():
    """Crawl the entire site starting from the homepage."""
    pages_to_visit = [BASE_URL]

    print(f"Starting deep crawl of {BASE_URL}")
    print("=" * 70)

    while pages_to_visit:
        current_url = pages_to_visit.pop(0)

        if current_url in visited_pages:
            continue

        visited_pages.add(current_url)
        print(f"\n[Crawling] {current_url}")

        soup, links, status = get_page_links(current_url)

        if status != 200:
            print(f"  ERROR: Page returned {status}")
            broken_links[current_url].append(('SELF', status))
            continue

        print(f"  Found {len(links)} links")

        for href in links:
            full_url = normalize_url(current_url, href)
            if not full_url:
                continue

            if is_internal_link(full_url):
                # Internal link - add to crawl queue if HTML
                if full_url.endswith('.html') or full_url.endswith('/'):
                    if full_url not in visited_pages and full_url not in pages_to_visit:
                        pages_to_visit.append(full_url)
                        all_pages_found.add(full_url)

                # Check internal link
                if full_url not in checked_links:
                    link_status = check_link(full_url)
                    if link_status != 200:
                        broken_links[full_url].append((current_url, link_status))
                        print(f"  BROKEN: {href} -> {link_status}")
            else:
                # External link - just record it
                external_links[full_url] = None

    print("\n" + "=" * 70)
    print("Crawl complete. Checking external links...")
    print("=" * 70)

def check_external_links():
    """Check all external links found during crawl."""
    print(f"\nChecking {len(external_links)} external links...")

    for url in list(external_links.keys()):
        if url.startswith('data:'):  # Skip data URLs
            external_links[url] = 'DATA_URL'
            continue

        print(f"  Checking: {url[:60]}...")
        status = check_link(url, timeout=10)
        external_links[url] = status

        if status != 200:
            print(f"    -> {status}")

        time.sleep(0.3)  # Rate limiting

def print_report():
    """Print final report."""
    print("\n")
    print("=" * 70)
    print("LINK CHECK REPORT")
    print("=" * 70)

    print(f"\n## Summary")
    print(f"- Pages crawled: {len(visited_pages)}")
    print(f"- Total links checked: {len(checked_links)}")
    print(f"- External links found: {len(external_links)}")

    # Broken internal links
    internal_broken = {url: pages for url, pages in broken_links.items()
                       if is_internal_link(url)}

    print(f"\n## Broken Internal Links ({len(internal_broken)})")
    if internal_broken:
        for url, sources in sorted(internal_broken.items()):
            print(f"\n  BROKEN: {url}")
            for source, status in sources[:3]:  # Show first 3 sources
                print(f"    - Found on: {source} (status: {status})")
    else:
        print("  None found!")

    # Broken external links
    external_broken = {url: status for url, status in external_links.items()
                       if status not in [200, 'DATA_URL', None]}

    print(f"\n## External Link Issues ({len(external_broken)})")
    if external_broken:
        for url, status in sorted(external_broken.items()):
            print(f"  {status}: {url[:80]}")
    else:
        print("  None found!")

    # All pages found
    print(f"\n## All Internal Pages Found ({len(all_pages_found)})")
    for page in sorted(all_pages_found):
        status = checked_links.get(page, 'NOT_CHECKED')
        status_mark = "[OK]" if status == 200 else f"[{status}]"
        short_page = page.replace(BASE_URL, '')
        print(f"  {status_mark} {short_page}")

    # Working external links
    external_ok = [url for url, status in external_links.items() if status == 200]
    print(f"\n## Working External Links ({len(external_ok)})")
    for url in sorted(set(external_ok))[:20]:  # Show first 20
        print(f"  [OK] {url[:70]}")
    if len(external_ok) > 20:
        print(f"  ... and {len(external_ok) - 20} more")

if __name__ == "__main__":
    try:
        crawl_site()
        check_external_links()
        print_report()
    except KeyboardInterrupt:
        print("\n\nInterrupted! Partial report:")
        print_report()
