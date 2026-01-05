"""Verify sidebar layout deployment across multiple pages"""
from playwright.sync_api import sync_playwright
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8002"

PAGES = [
    ("index.html", "deployed_homepage"),
    ("members.html", "deployed_members"),
    ("publications.html", "deployed_publications"),
    ("financial-reports/overview.html", "deployed_financial"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    for path, name in PAGES:
        url = f"{BASE_URL}/{path}"
        print(f"Capturing {name}: {url}")
        page.goto(url, wait_until='domcontentloaded')
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUTPUT_DIR / f"{name}.png"))
        print(f"  Saved {name}.png")

    browser.close()
    print("\nDeployment verification screenshots captured!")
