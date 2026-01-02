"""
PDF to TXT Converter - Exact text extraction from PDFs
Extracts text from all PDFs in directory tree to .txt files
"""

import sys
from pathlib import Path
from datetime import datetime

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)


def extract_pdf_to_txt(pdf_path: Path, output_path: Path = None) -> dict:
    """
    Extract text from PDF and save to TXT file.

    Args:
        pdf_path: Path to PDF file
        output_path: Path for output TXT (default: same name as PDF with .txt)

    Returns:
        dict with extraction results
    """
    if output_path is None:
        output_path = pdf_path.with_suffix('.txt')

    result = {
        'pdf': str(pdf_path),
        'txt': str(output_path),
        'pages': 0,
        'chars': 0,
        'success': False,
        'error': None
    }

    try:
        doc = fitz.open(pdf_path)
        result['pages'] = len(doc)

        text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Extract text with layout preservation
            text = page.get_text("text")

            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")

        doc.close()

        # Combine all pages
        full_text = "\n\n".join(text_parts)
        result['chars'] = len(full_text)

        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(full_text, encoding='utf-8')

        result['success'] = True

    except Exception as e:
        result['error'] = str(e)

    return result


def process_directory(root_dir: Path, skip_existing: bool = False) -> list:
    """
    Process all PDFs in directory tree.

    Args:
        root_dir: Root directory to search
        skip_existing: Skip if .txt already exists and is newer

    Returns:
        List of extraction results
    """
    results = []
    pdf_files = list(root_dir.rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")
    print("-" * 60)

    for i, pdf_path in enumerate(pdf_files, 1):
        txt_path = pdf_path.with_suffix('.txt')

        # Skip if txt exists and is newer than pdf
        if skip_existing and txt_path.exists():
            if txt_path.stat().st_mtime > pdf_path.stat().st_mtime:
                print(f"[{i}/{len(pdf_files)}] SKIP: {pdf_path.name}")
                continue

        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")

        result = extract_pdf_to_txt(pdf_path, txt_path)
        results.append(result)

        if result['success']:
            print(f"           -> {result['pages']} pages, {result['chars']:,} chars")
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
    print("PDF to TXT Converter")
    print("=" * 60)
    print(f"Directory: {root_dir}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Process all PDFs
    results = process_directory(root_dir, skip_existing=True)

    # Summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    total_pages = sum(r['pages'] for r in successful)
    total_chars = sum(r['chars'] for r in successful)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Processed: {len(results)} PDFs")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total pages: {total_pages:,}")
    print(f"Total characters: {total_chars:,}")

    if failed:
        print("\nFailed files:")
        for r in failed:
            print(f"  - {r['pdf']}: {r['error']}")

    print("=" * 60)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
