"""
Add Verification Overlay to All HTML Pages

Injects CSS and JS links for the verification overlay system into all
HTML files in work-budget-plans/ and financial-reports/ directories.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
HTML_DIRS = [
    BASE_DIR / "work-budget-plans",
    BASE_DIR / "financial-reports",
]

# HTML to inject (relative paths from subdirectories)
CSS_LINK = '<link rel="stylesheet" href="../css/verification-overlay.css">'
JS_SCRIPT = '<script src="../js/verification-overlay.js"></script>'

# Marker to detect if already injected
MARKER = '<!-- verification-overlay -->'


def get_relative_path(html_file: Path) -> str:
    """Calculate relative path prefix based on file location."""
    # Both directories are at same level, so ../css/ and ../js/ work
    return ".."


def inject_overlay(filepath: Path) -> bool:
    """Inject overlay CSS and JS into an HTML file."""
    content = filepath.read_text(encoding='utf-8')

    # Check if already injected
    if MARKER in content:
        print(f"  [SKIP] {filepath.name} - already has overlay")
        return False

    # Calculate relative path
    rel_prefix = get_relative_path(filepath)

    css_link = f'<link rel="stylesheet" href="{rel_prefix}/css/verification-overlay.css">'
    js_script = f'<script src="{rel_prefix}/js/verification-overlay.js"></script>'

    # Build injection block
    injection = f"""
    {MARKER}
    {css_link}
    {js_script}
"""

    # Find </body> tag and inject before it
    if '</body>' in content:
        new_content = content.replace('</body>', f'{injection}</body>')
        filepath.write_text(new_content, encoding='utf-8')
        print(f"  [OK] {filepath.name} - overlay added")
        return True
    else:
        print(f"  [WARN] {filepath.name} - no </body> tag found")
        return False


def remove_overlay(filepath: Path) -> bool:
    """Remove overlay injection from an HTML file."""
    content = filepath.read_text(encoding='utf-8')

    if MARKER not in content:
        return False

    # Remove the injection block (marker + CSS + JS)
    # Pattern matches the marker and following lines until </body>
    pattern = r'\s*<!-- verification-overlay -->\s*<link[^>]+verification-overlay\.css[^>]*>\s*<script[^>]+verification-overlay\.js[^>]*></script>\s*'
    new_content = re.sub(pattern, '\n    ', content)

    filepath.write_text(new_content, encoding='utf-8')
    print(f"  [REMOVED] {filepath.name}")
    return True


def main(remove: bool = False):
    """Main function to process all HTML files."""
    action = "Removing" if remove else "Adding"
    print("=" * 60)
    print(f"{action} Verification Overlay")
    print("=" * 60)

    total_files = 0
    modified_files = 0

    for html_dir in HTML_DIRS:
        if not html_dir.exists():
            print(f"Directory not found: {html_dir}")
            continue

        print(f"\nProcessing: {html_dir.name}/")

        for html_file in sorted(html_dir.glob("*.html")):
            total_files += 1
            if remove:
                if remove_overlay(html_file):
                    modified_files += 1
            else:
                if inject_overlay(html_file):
                    modified_files += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total HTML files: {total_files}")
    print(f"Files modified: {modified_files}")

    if not remove:
        print("\nOverlay files:")
        print(f"  CSS: css/verification-overlay.css")
        print(f"  JS:  js/verification-overlay.js")
        print(f"\nTo remove overlay, run: python {Path(__file__).name} --remove")


if __name__ == "__main__":
    import sys
    remove_mode = "--remove" in sys.argv or "-r" in sys.argv
    main(remove=remove_mode)
