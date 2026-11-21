
from pathlib import Path
import fitz


def extract_page_tables(page):
    """Extract detected tables while preserving individual cell text."""

    tables = []

    detected_tables = page.find_tables()

    for table_index, table in enumerate(detected_tables.tables):

        rows = []

        for row in table.rows:
            cells = []

            for cell in row.cells:

                if cell is None:
                    cells.append("")
                    continue

                cell_rect = fitz.Rect(cell)

                cell_text = page.get_text(
                    "text",
                    clip=cell_rect
                ).strip()

                # Normalize spaces inside individual cells
                cell_text = " ".join(cell_text.split())

                cells.append(cell_text)

            if any(cells):
                rows.append(cells)

        if rows:
            tables.append({
                "table_index": table_index,
                "rows": rows
            })

    return tables


def extract_page_text(page, tables):
    """
    Extract ordinary page text while excluding detected table areas.
    This prevents table information from being indexed twice.
    """

    table_rectangles = [
        fitz.Rect(table.bbox)
        for table in page.find_tables().tables
    ]

    text_blocks = page.get_text(
        "blocks",
        sort=True
    )

    page_text = []

    for block in text_blocks:

        x0, y0, x1, y1, text = block[:5]

        # Ignore non-text blocks
        if len(block) > 6 and block[6] != 0:
            continue

        block_rect = fitz.Rect(x0, y0, x1, y1)

        # Exclude blocks whose center lies inside a detected table
        center = block_rect.tl + (block_rect.br - block_rect.tl) * 0.5

        inside_table = any(
            rectangle.contains(center)
            for rectangle in table_rectangles
        )

        if inside_table:
            continue

        if text.strip():
            page_text.append(text.strip())

    return "\n".join(page_text)


def load_pdf(pdf_path):

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    documents = []

    with fitz.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            # Detect and extract structured tables
            tables = extract_page_tables(page)

            # Extract ordinary text separately
            text = extract_page_text(page, tables)

            if text.strip() or tables:
                documents.append({
                    "text": text,
                    "tables": tables,
                    "source": pdf_path.name,
                    "page": page_number
                })

    if not documents:
        raise ValueError(
            "No readable text found in this PDF."
        )

    return documents
