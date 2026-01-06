"""
Fix broken links in documents.html by mapping filenames to their actual paths in Action Chair directory.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
ACTION_CHAIR_DIR = BASE_DIR / "Action Chair"
DOCUMENTS_HTML = BASE_DIR / "documents.html"

def find_all_html_files():
    """Find all HTML files in Action Chair and create filename -> path mapping."""
    file_map = {}

    for root, dirs, files in os.walk(ACTION_CHAIR_DIR):
        for file in files:
            if file.endswith('.html'):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(BASE_DIR)
                # Convert to URL-safe path with forward slashes
                url_path = str(rel_path).replace('\\', '/')

                # Store by filename (may have duplicates, keep first found)
                if file not in file_map:
                    file_map[file] = url_path
                else:
                    # If duplicate, prefer shorter path
                    if len(url_path) < len(file_map[file]):
                        file_map[file] = url_path

    return file_map

def fix_documents_html(file_map):
    """Fix the href attributes in documents.html."""

    with open(DOCUMENTS_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes_made = []

    # Find all href="filename.html" patterns that might be broken
    # Only match filenames that are in our file_map (Action Chair files)
    for filename, correct_path in file_map.items():
        # Pattern to match href="filename" (without path)
        # Be careful not to match files that already have correct paths
        pattern = rf'href="({re.escape(filename)})"'

        # Check if this exact pattern exists (filename without path)
        if re.search(pattern, content):
            # URL encode spaces in path
            encoded_path = correct_path.replace(' ', '%20')
            replacement = f'href="{encoded_path}"'

            # Count occurrences before replacement
            count = len(re.findall(pattern, content))

            content = re.sub(pattern, replacement, content)
            fixes_made.append((filename, encoded_path, count))

    if content != original_content:
        with open(DOCUMENTS_HTML, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed {len(fixes_made)} unique files in documents.html:")
        for filename, path, count in fixes_made:
            print(f"  {filename} -> {path} ({count} occurrences)")
    else:
        print("No changes needed in documents.html")

    return fixes_made

def main():
    print("Scanning Action Chair directory for HTML files...")
    file_map = find_all_html_files()
    print(f"Found {len(file_map)} unique HTML files\n")

    # Show some examples
    print("Sample mappings:")
    for i, (filename, path) in enumerate(list(file_map.items())[:10]):
        print(f"  {filename}")
        print(f"    -> {path}")
    print(f"  ... and {len(file_map) - 10} more\n")

    print("Fixing documents.html...")
    fixes = fix_documents_html(file_map)

    print(f"\nTotal fixes: {sum(count for _, _, count in fixes)} href attributes updated")

if __name__ == "__main__":
    main()
