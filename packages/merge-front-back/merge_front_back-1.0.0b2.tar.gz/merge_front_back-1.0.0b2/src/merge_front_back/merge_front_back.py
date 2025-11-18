
#!/usr/bin/env python3
"""
merge_front_back.py

Merge two single-sided scanned PDFs into one duplex document.
- `front.pdf` contains odd pages in forward order.
- `back.pdf` contains even pages in reverse order (scanned from the back).
Options:
--verbose : Print page source and index during merge.
--dry-run : Simulate merge without writing output.
"""

import argparse
import sys
from pypdf import PdfReader, PdfWriter
from os import path

def merge_pdfs(front_path, back_path, output_path, overwrite = False):
    front_pdf = PdfReader(front_path)
    back_pdf = PdfReader(back_path)

    if len(front_pdf.pages) != len(back_pdf.pages):
        print(f"Error: Page count mismatch � front has {len(front_pdf.pages)}, back has {len(back_pdf.pages)}.")
        print("Both PDFs must have the same number of pages for proper duplex merging.")
        sys.exit(1)

    back_pages = list(reversed(back_pdf.pages))
    front_pages = front_pdf.pages
    total_pages = len(front_pages)
    front_back = [(front_pages, "front"), (back_pages, "back")]
    writer = PdfWriter()
    for i in range(total_pages):
        for source, label in front_back:
            writer.add_page(source[i])
    if not overwrite and path.exists(output_path):
        print(f"Error: Output file {output_path} already exists. Use --overwrite to replace it.")
        sys.exit(1)
    with open(output_path, "wb") as f:
        writer.write(f)
    print(f"Merged PDF saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Merge odd and reversed even pages into a duplex-scanned PDF."
    )
    parser.add_argument("-f", "--front", required=True, help="Path to front (odd pages) PDF")
    parser.add_argument("-b", "--back", required=True, help="Path to back (even pages, reversed) PDF")
    parser.add_argument("-m", "--merged", required=True, help="Path to output merged PDF")
    parser.add_argument("-o", "--overwrite", required=False, help="Force overwrite of the file specified by --merged", action="store_true")

    args = parser.parse_args()
    merge_pdfs(args.front, args.back, args.merged,args.overwrite)

if __name__ == "__main__":
    main()
