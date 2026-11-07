
from pathlib import Path
import pymupdf


def load_pdf(file_path):
    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Path is not a file: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("The provided file is not a PDF.")

    documents = []

    try:
        with pymupdf.open(pdf_path) as pdf:

            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                if text:
                    documents.append({
                        "text": text,
                        "source": pdf_path.name,
                        "page": page_number
                    })

    except Exception as error:
        raise RuntimeError(
            f"Could not read PDF {pdf_path.name}: {error}"
        ) from error

    if not documents:
        raise ValueError(
            "No readable text found in the PDF. "
            "It may be scanned and require OCR."
        )

    return documents
