"""Compare original vs sidebar layout screenshots"""
from playwright.sync_api import sync_playwright
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

PAGES = [
    ("index.html", "original_homepage"),
    ("test-sidebar-layout.html", "sidebar_homepage"),
]

BASE_URL = "http://localhost:8002"

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

    # Also capture mobile view of sidebar layout
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(f"{BASE_URL}/test-sidebar-layout.html")
    page.wait_for_load_state('networkidle')
    page.screenshot(path=str(OUTPUT_DIR / "sidebar_mobile.png"))
    print("  Saved sidebar_mobile.png")

    # Capture sidebar open on mobile
    page.click('.sidebar-toggle')
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUTPUT_DIR / "sidebar_mobile_open.png"))
    print("  Saved sidebar_mobile_open.png")

    browser.close()
    print("\nLayout comparison screenshots captured!")
