"""Extract text from all PDFs in directory to searchable .txt files."""
import fitz  # PyMuPDF
from pathlib import Path
import sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def extract_pdf_text(pdf_path: Path) -> tuple[str, int]:
    """Extract text from PDF, return (text, page_count)."""
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    text_parts = []
    for page_num, page in enumerate(doc, 1):
        text = page.get_text()
        if text.strip():
            text_parts.append(f"--- Page {page_num} ---\n{text}")
    doc.close()
    return "\n\n".join(text_parts), page_count


def main():
    root_dir = Path(__file__).parent
    pdf_files = list(root_dir.rglob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF files")
    print("-" * 50)

    processed = 0
    skipped = 0
    errors = []
    total_pages = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        txt_path = pdf_path.with_suffix(".txt")

        # Skip if txt exists and is newer than pdf
        if txt_path.exists() and txt_path.stat().st_mtime > pdf_path.stat().st_mtime:
            print(f"[{i}/{len(pdf_files)}] SKIP (exists): {pdf_path.name}")
            skipped += 1
            continue

        try:
            print(f"[{i}/{len(pdf_files)}] Processing: {pdf_path.name}...", end=" ")
            text, pages = extract_pdf_text(pdf_path)
            total_pages += pages

            txt_path.write_text(text, encoding="utf-8")
            print(f"OK ({pages} pages)")
            processed += 1

        except Exception as e:
            print(f"ERROR: {e}")
            errors.append((pdf_path, str(e)))

    print("-" * 50)
    print(f"Processed: {processed}")
    print(f"Skipped:   {skipped}")
    print(f"Errors:    {len(errors)}")
    print(f"Total pages extracted: {total_pages}")

    if errors:
        print("\nErrors encountered:")
        for path, err in errors:
            print(f"  - {path.name}: {err}")


if __name__ == "__main__":
    main()
