"""Capture screenshots of compact COST website pages"""
from playwright.sync_api import sync_playwright
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

PAGES = [
    ("index.html", "homepage_compact"),
    ("members.html", "members_compact"),
    ("publications.html", "publications_compact"),
]

BASE_URL = "http://localhost:8001"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Desktop viewport
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    for path, name in PAGES:
        url = f"{BASE_URL}/{path}"
        print(f"Capturing {name}: {url}")
        page.goto(url)
        page.wait_for_load_state('networkidle')

        # Full page screenshot
        page.screenshot(path=str(OUTPUT_DIR / f"{name}_full.png"), full_page=True)

        # Above-the-fold screenshot
        page.screenshot(path=str(OUTPUT_DIR / f"{name}_viewport.png"))

        print(f"  Saved {name}_full.png and {name}_viewport.png")

    browser.close()
    print("\nCompact screenshots captured!")
