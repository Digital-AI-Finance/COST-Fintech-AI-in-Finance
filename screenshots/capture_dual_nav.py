"""Capture screenshots of dual-navigation layout"""
from playwright.sync_api import sync_playwright
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8002"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Desktop viewport
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    # Capture homepage with dual nav
    url = f"{BASE_URL}/test-sidebar-layout.html"
    print(f"Capturing dual-nav homepage: {url}")
    page.goto(url, wait_until='domcontentloaded')
    page.wait_for_timeout(2000)  # Wait for charts to render

    # Full page screenshot
    page.screenshot(path=str(OUTPUT_DIR / "dual_nav_homepage_full.png"), full_page=True)

    # Above-the-fold screenshot
    page.screenshot(path=str(OUTPUT_DIR / "dual_nav_homepage_viewport.png"))
    print("  Saved dual_nav_homepage screenshots")

    # Click on NETWORK tab to show tab interaction
    page.click('.topbar-tab[data-category="network"]')
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUTPUT_DIR / "dual_nav_network_tab.png"))
    print("  Saved network tab screenshot")

    # Click on IMPACT tab
    page.click('.topbar-tab[data-category="impact"]')
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUTPUT_DIR / "dual_nav_impact_tab.png"))
    print("  Saved impact tab screenshot")

    # Mobile view
    mobile_page = browser.new_page(viewport={"width": 390, "height": 844})
    mobile_page.goto(url, wait_until='domcontentloaded')
    mobile_page.wait_for_timeout(2000)
    mobile_page.screenshot(path=str(OUTPUT_DIR / "dual_nav_mobile.png"))
    print("  Saved mobile screenshot")

    # Mobile with sidebar open
    mobile_page.click('.sidebar-toggle')
    mobile_page.wait_for_timeout(500)
    mobile_page.screenshot(path=str(OUTPUT_DIR / "dual_nav_mobile_sidebar.png"))
    print("  Saved mobile sidebar screenshot")

    browser.close()
    print("\nDual-navigation screenshots captured!")
