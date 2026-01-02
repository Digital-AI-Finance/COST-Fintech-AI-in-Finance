"""
TXT to HTML Converter for GitHub Pages
Converts extracted .txt files to styled HTML pages
"""

import sys
import re
import html
from pathlib import Path
from datetime import datetime


# HTML template for document pages
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - COST Action CA19130</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Code+Pro:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --cost-purple: #5B2D8A;
            --cost-blue: #2B5F9E;
            --cost-teal: #00A0B0;
            --cost-orange: #E87722;
            --dark: #1a1a2e;
            --light: #f8f9fa;
            --gray: #6c757d;
            --border: #dee2e6;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; line-height: 1.6; color: var(--dark); background: var(--light); }}
        nav {{ background: linear-gradient(135deg, var(--cost-purple), var(--cost-blue)); padding: 1rem 2rem; position: fixed; width: 100%; top: 0; z-index: 1000; }}
        nav .nav-content {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
        nav .logo {{ color: white; font-weight: 700; font-size: 1.2rem; }}
        nav .logo span {{ color: var(--cost-orange); }}
        nav ul {{ display: flex; list-style: none; gap: 2rem; }}
        nav a {{ color: rgba(255,255,255,0.9); text-decoration: none; font-size: 0.9rem; font-weight: 500; }}
        nav a:hover {{ color: white; }}
        .header {{ background: linear-gradient(135deg, var(--cost-purple), var(--cost-blue)); color: white; padding: 6rem 2rem 2rem; }}
        .header h1 {{ font-size: 1.8rem; max-width: 1200px; margin: 0 auto 0.5rem; }}
        .header .meta {{ font-size: 0.9rem; opacity: 0.8; max-width: 1200px; margin: 0 auto; }}
        .breadcrumb {{ background: white; padding: 1rem 2rem; border-bottom: 1px solid var(--border); }}
        .breadcrumb-content {{ max-width: 1200px; margin: 0 auto; font-size: 0.85rem; }}
        .breadcrumb a {{ color: var(--cost-purple); text-decoration: none; }}
        .breadcrumb span {{ color: var(--gray); }}
        .content {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .document {{ background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }}
        .doc-header {{ background: linear-gradient(135deg, rgba(91,45,138,0.05), rgba(43,95,158,0.05)); padding: 1.5rem 2rem; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }}
        .doc-header h2 {{ color: var(--cost-purple); font-size: 1.1rem; }}
        .doc-stats {{ display: flex; gap: 1.5rem; font-size: 0.85rem; color: var(--gray); }}
        .doc-stats span {{ display: flex; align-items: center; gap: 0.3rem; }}
        .doc-body {{ padding: 2rem; }}
        .page-break {{ border-top: 2px dashed var(--border); margin: 2rem 0; padding-top: 1rem; }}
        .page-break::before {{ content: attr(data-page); display: inline-block; background: var(--cost-purple); color: white; padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }}
        .text-content {{ font-family: 'Source Code Pro', monospace; font-size: 0.85rem; line-height: 1.8; white-space: pre-wrap; word-wrap: break-word; color: #333; }}
        .text-content .highlight {{ background: rgba(232,119,34,0.15); padding: 0.1rem 0.3rem; border-radius: 3px; }}
        .toc {{ background: white; border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .toc h3 {{ color: var(--cost-purple); margin-bottom: 1rem; font-size: 1rem; }}
        .toc ul {{ list-style: none; }}
        .toc li {{ margin-bottom: 0.5rem; }}
        .toc a {{ color: var(--cost-blue); text-decoration: none; font-size: 0.9rem; }}
        .toc a:hover {{ text-decoration: underline; }}
        .download-btn {{ display: inline-flex; align-items: center; gap: 0.5rem; background: var(--cost-purple); color: white; padding: 0.6rem 1.2rem; border-radius: 8px; text-decoration: none; font-size: 0.85rem; font-weight: 500; }}
        .download-btn:hover {{ background: #4a2470; }}
        .search-box {{ margin-bottom: 1.5rem; }}
        .search-box input {{ width: 100%; padding: 0.8rem 1rem; border: 2px solid var(--border); border-radius: 8px; font-size: 0.9rem; }}
        .search-box input:focus {{ outline: none; border-color: var(--cost-purple); }}
        footer {{ background: var(--dark); color: white; padding: 2rem; text-align: center; margin-top: 3rem; }}
        footer a {{ color: var(--cost-orange); text-decoration: none; }}
        @media (max-width: 768px) {{ nav ul {{ display: none; }} .header h1 {{ font-size: 1.4rem; }} .doc-body {{ padding: 1rem; }} }}
    </style>
</head>
<body>
    <nav>
        <div class="nav-content">
            <div class="logo">COST <span>CA19130</span></div>
            <ul>
                <li><a href="index.html">Home</a></li>
                <li><a href="documents.html">Documents</a></li>
                <li><a href="midterm-report.html">Mid-Term Report</a></li>
            </ul>
        </div>
    </nav>

    <header class="header">
        <h1>{title}</h1>
        <div class="meta">Source: {source_file} | Generated: {generated_date}</div>
    </header>

    <div class="breadcrumb">
        <div class="breadcrumb-content">
            <a href="index.html">Home</a> <span>/</span>
            <a href="documents.html">Documents</a> <span>/</span>
            <span>{title}</span>
        </div>
    </div>

    <main class="content">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search in document..." onkeyup="searchDocument()">
        </div>

        <div class="document">
            <div class="doc-header">
                <h2>Document Content</h2>
                <div class="doc-stats">
                    <span>{pages} pages</span>
                    <span>{chars:,} characters</span>
                    <span>{words:,} words</span>
                </div>
            </div>
            <div class="doc-body" id="documentBody">
{content}
            </div>
        </div>
    </main>

    <footer>
        <p>COST Action CA19130 - Fintech and AI in Finance</p>
        <p><a href="https://fin-ai.eu" target="_blank">fin-ai.eu</a> | <a href="https://www.cost.eu/actions/CA19130/" target="_blank">COST Website</a></p>
    </footer>

    <script>
        function searchDocument() {{
            const input = document.getElementById('searchInput').value.toLowerCase();
            const content = document.getElementById('documentBody');

            // Remove existing highlights
            content.innerHTML = content.innerHTML.replace(/<mark class="highlight">([^<]+)<\\/mark>/gi, '$1');

            if (input.length < 2) return;

            // Add new highlights
            const regex = new RegExp('(' + input.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&') + ')', 'gi');
            content.innerHTML = content.innerHTML.replace(regex, '<mark class="highlight">$1</mark>');
        }}
    </script>
</body>
</html>'''


# Index page template
INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documents - COST Action CA19130</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --cost-purple: #5B2D8A;
            --cost-blue: #2B5F9E;
            --cost-teal: #00A0B0;
            --cost-orange: #E87722;
            --dark: #1a1a2e;
            --light: #f8f9fa;
            --gray: #6c757d;
            --border: #dee2e6;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; line-height: 1.6; color: var(--dark); background: var(--light); }}
        nav {{ background: linear-gradient(135deg, var(--cost-purple), var(--cost-blue)); padding: 1rem 2rem; position: fixed; width: 100%; top: 0; z-index: 1000; }}
        nav .nav-content {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
        nav .logo {{ color: white; font-weight: 700; font-size: 1.2rem; }}
        nav .logo span {{ color: var(--cost-orange); }}
        nav ul {{ display: flex; list-style: none; gap: 2rem; }}
        nav a {{ color: rgba(255,255,255,0.9); text-decoration: none; font-size: 0.9rem; font-weight: 500; }}
        .hero {{ background: linear-gradient(135deg, var(--cost-purple), var(--cost-blue)); color: white; padding: 7rem 2rem 3rem; text-align: center; }}
        .hero h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .hero p {{ opacity: 0.9; }}
        .content {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .stats {{ display: flex; justify-content: center; gap: 3rem; background: white; padding: 1.5rem; border-radius: 12px; margin: -2rem auto 2rem; max-width: 600px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); position: relative; z-index: 10; }}
        .stat {{ text-align: center; }}
        .stat .num {{ font-size: 2rem; font-weight: 700; color: var(--cost-purple); }}
        .stat .label {{ font-size: 0.8rem; color: var(--gray); }}
        .search {{ margin-bottom: 2rem; }}
        .search input {{ width: 100%; padding: 1rem; border: 2px solid var(--border); border-radius: 8px; font-size: 1rem; }}
        .search input:focus {{ outline: none; border-color: var(--cost-purple); }}
        .folders {{ margin-bottom: 2rem; }}
        .folder {{ background: white; border-radius: 12px; margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.08); overflow: hidden; }}
        .folder-header {{ background: linear-gradient(135deg, rgba(91,45,138,0.08), rgba(43,95,158,0.08)); padding: 1rem 1.5rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }}
        .folder-header:hover {{ background: linear-gradient(135deg, rgba(91,45,138,0.12), rgba(43,95,158,0.12)); }}
        .folder-header h3 {{ color: var(--cost-purple); font-size: 1rem; }}
        .folder-header .count {{ background: var(--cost-purple); color: white; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; }}
        .folder-content {{ padding: 0 1.5rem; max-height: 0; overflow: hidden; transition: max-height 0.3s, padding 0.3s; }}
        .folder-content.open {{ max-height: 2000px; padding: 1rem 1.5rem; }}
        .doc-item {{ display: flex; justify-content: space-between; align-items: center; padding: 0.8rem 0; border-bottom: 1px solid var(--border); }}
        .doc-item:last-child {{ border-bottom: none; }}
        .doc-item a {{ color: var(--cost-blue); text-decoration: none; font-size: 0.9rem; }}
        .doc-item a:hover {{ text-decoration: underline; }}
        .doc-item .meta {{ font-size: 0.8rem; color: var(--gray); }}
        footer {{ background: var(--dark); color: white; padding: 2rem; text-align: center; margin-top: 3rem; }}
        footer a {{ color: var(--cost-orange); text-decoration: none; }}
        @media (max-width: 768px) {{ nav ul {{ display: none; }} .stats {{ flex-direction: column; gap: 1rem; }} }}
    </style>
</head>
<body>
    <nav>
        <div class="nav-content">
            <div class="logo">COST <span>CA19130</span></div>
            <ul>
                <li><a href="index.html">Home</a></li>
                <li><a href="documents.html">Documents</a></li>
                <li><a href="midterm-report.html">Mid-Term Report</a></li>
            </ul>
        </div>
    </nav>

    <header class="hero">
        <h1>Document Library</h1>
        <p>All extracted PDF documents converted to searchable HTML</p>
    </header>

    <div class="stats">
        <div class="stat"><div class="num">{total_docs}</div><div class="label">Documents</div></div>
        <div class="stat"><div class="num">{total_pages}</div><div class="label">Pages</div></div>
        <div class="stat"><div class="num">{total_folders}</div><div class="label">Folders</div></div>
    </div>

    <main class="content">
        <div class="search">
            <input type="text" id="searchInput" placeholder="Search documents..." onkeyup="filterDocs()">
        </div>

        <div class="folders" id="folderList">
{folders_html}
        </div>
    </main>

    <footer>
        <p>COST Action CA19130 - Fintech and AI in Finance</p>
        <p>Generated: {generated_date}</p>
    </footer>

    <script>
        function toggleFolder(id) {{
            const content = document.getElementById(id);
            content.classList.toggle('open');
        }}

        function filterDocs() {{
            const input = document.getElementById('searchInput').value.toLowerCase();
            const items = document.querySelectorAll('.doc-item');
            items.forEach(item => {{
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(input) ? '' : 'none';
            }});
        }}

        // Open first folder by default
        document.querySelector('.folder-content')?.classList.add('open');
    </script>
</body>
</html>'''


def clean_title(filename: str) -> str:
    """Convert filename to readable title."""
    # Remove extension and clean up
    title = Path(filename).stem
    # Replace underscores and hyphens with spaces
    title = re.sub(r'[_-]+', ' ', title)
    # Remove dates like (1), (2), etc.
    title = re.sub(r'\s*\(\d+\)\s*$', '', title)
    # Clean up extra spaces
    title = ' '.join(title.split())
    return title


def format_text_content(text: str) -> str:
    """Format text content for HTML display with page breaks."""
    # Escape HTML
    text = html.escape(text)

    # Convert page markers to styled dividers
    def replace_page(match):
        page_num = match.group(1)
        return f'</pre><div class="page-break" data-page="Page {page_num}"></div><pre class="text-content">'

    text = re.sub(r'--- Page (\d+) ---', replace_page, text)

    # Wrap in pre tag
    text = f'<pre class="text-content">{text}</pre>'

    # Remove the leading </pre> from first page break replacement
    text = text.replace('<pre class="text-content"></pre><div', '<div', 1)

    return text


def convert_txt_to_html(txt_path: Path, output_path: Path = None) -> dict:
    """
    Convert a TXT file to styled HTML.

    Args:
        txt_path: Path to TXT file
        output_path: Path for output HTML (default: same name with .html)

    Returns:
        dict with conversion results
    """
    if output_path is None:
        output_path = txt_path.with_suffix('.html')

    result = {
        'txt': str(txt_path),
        'html': str(output_path),
        'title': clean_title(txt_path.name),
        'pages': 0,
        'chars': 0,
        'words': 0,
        'success': False,
        'error': None
    }

    try:
        # Read text content
        text = txt_path.read_text(encoding='utf-8')
        result['chars'] = len(text)
        result['words'] = len(text.split())

        # Count pages
        result['pages'] = len(re.findall(r'--- Page \d+ ---', text))

        # Format content
        formatted_content = format_text_content(text)

        # Generate HTML
        html_content = HTML_TEMPLATE.format(
            title=result['title'],
            source_file=txt_path.name,
            generated_date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            pages=result['pages'],
            chars=result['chars'],
            words=result['words'],
            content=formatted_content
        )

        # Write HTML file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')

        result['success'] = True

    except Exception as e:
        result['error'] = str(e)

    return result


def generate_index_page(results: list, output_dir: Path) -> None:
    """Generate the documents index page."""
    # Group by folder
    folders = {}
    for r in results:
        if not r['success']:
            continue
        txt_path = Path(r['txt'])
        folder = txt_path.parent.name
        if folder == output_dir.name:
            folder = "Root"
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(r)

    # Generate folder HTML
    folders_html = []
    folder_id = 0
    for folder_name, docs in sorted(folders.items()):
        folder_id += 1
        docs_html = []
        for doc in sorted(docs, key=lambda x: x['title']):
            html_file = Path(doc['html']).name
            docs_html.append(f'''            <div class="doc-item">
                <a href="{html_file}">{doc['title']}</a>
                <span class="meta">{doc['pages']} pages</span>
            </div>''')

        folders_html.append(f'''        <div class="folder">
            <div class="folder-header" onclick="toggleFolder('folder{folder_id}')">
                <h3>{folder_name}</h3>
                <span class="count">{len(docs)} docs</span>
            </div>
            <div class="folder-content" id="folder{folder_id}">
{chr(10).join(docs_html)}
            </div>
        </div>''')

    # Calculate totals
    successful = [r for r in results if r['success']]
    total_pages = sum(r['pages'] for r in successful)

    # Generate index HTML
    index_html = INDEX_TEMPLATE.format(
        total_docs=len(successful),
        total_pages=total_pages,
        total_folders=len(folders),
        folders_html='\n'.join(folders_html),
        generated_date=datetime.now().strftime('%Y-%m-%d %H:%M')
    )

    # Write index file
    index_path = output_dir / 'documents.html'
    index_path.write_text(index_html, encoding='utf-8')
    print(f"\nGenerated index: {index_path}")


def process_directory(root_dir: Path) -> list:
    """
    Process all TXT files in directory tree.

    Args:
        root_dir: Root directory to search

    Returns:
        List of conversion results
    """
    results = []

    # Find all .txt files that have corresponding .pdf (extracted texts)
    txt_files = []
    for txt_path in root_dir.rglob("*.txt"):
        # Check if there's a corresponding PDF (means it was extracted)
        pdf_path = txt_path.with_suffix('.pdf')
        if pdf_path.exists():
            txt_files.append(txt_path)

    print(f"Found {len(txt_files)} TXT files (with PDF sources)")
    print("-" * 60)

    for i, txt_path in enumerate(txt_files, 1):
        print(f"[{i}/{len(txt_files)}] Converting: {txt_path.name}")

        result = convert_txt_to_html(txt_path)
        results.append(result)

        if result['success']:
            print(f"           -> {result['pages']} pages, {result['words']:,} words")
        else:
            print(f"           -> ERROR: {result['error']}")

    return results


def main():
    """Main entry point."""
    # Configure stdout for unicode
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    # Get directory
    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
    else:
        root_dir = Path(__file__).parent

    if not root_dir.exists():
        print(f"ERROR: Directory not found: {root_dir}")
        sys.exit(1)

    print("=" * 60)
    print("TXT to HTML Converter for GitHub Pages")
    print("=" * 60)
    print(f"Directory: {root_dir}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Process all TXT files
    results = process_directory(root_dir)

    # Generate index page
    if results:
        generate_index_page(results, root_dir)

    # Summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    total_pages = sum(r['pages'] for r in successful)
    total_words = sum(r['words'] for r in successful)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Converted: {len(results)} files")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total pages: {total_pages:,}")
    print(f"Total words: {total_words:,}")

    if failed:
        print("\nFailed files:")
        for r in failed:
            print(f"  - {r['txt']}: {r['error']}")

    print("=" * 60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
