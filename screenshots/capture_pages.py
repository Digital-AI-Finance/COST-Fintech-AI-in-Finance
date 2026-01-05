"""Capture screenshots of COST website pages for whitespace analysis"""
from playwright.sync_api import sync_playwright
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

PAGES = [
    ("index.html", "homepage"),
    ("members.html", "members"),
    ("publications.html", "publications"),
    ("final-achievements.html", "achievements"),
    ("financial-reports/overview.html", "financial-overview"),
]

BASE_URL = "https://digital-ai-finance.github.io/COST-Fintech-AI-in-Finance"

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

    # Mobile viewport screenshots
    page_mobile = browser.new_page(viewport={"width": 375, "height": 812})

    for path, name in PAGES[:3]:  # Just first 3 for mobile
        url = f"{BASE_URL}/{path}"
        print(f"Capturing mobile {name}: {url}")
        page_mobile.goto(url)
        page_mobile.wait_for_load_state('networkidle')
        page_mobile.screenshot(path=str(OUTPUT_DIR / f"{name}_mobile.png"), full_page=True)
        print(f"  Saved {name}_mobile.png")

    browser.close()
    print("\nAll screenshots captured!")
