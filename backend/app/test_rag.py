import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))

from app.rag.pdf_loader import load_pdf
from app.rag.cleaner import clean_documents
from app.rag.chunker import chunk_documents

from app.rag.rag_service import (
    ingest_pdf,
    retrieve_context
)


PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "test_company"
    / "aura_generic_rag_test_company.pdf"
)


def main():

    company_id = "northstar_learning_labs"
    document_id = "northstar_profile_v1"

    print("\n========== AURA RAG TEST ==========\n")

    # STEP 1: Extract PDF
    print("STEP 1: Extracting PDF...")

    documents = load_pdf(PDF_PATH)

    print("Pages extracted:", len(documents))

    # STEP 2: Clean documents
    print("\nSTEP 2: Cleaning documents...")

    cleaned_documents = clean_documents(documents)

    print("Pages after cleaning:", len(cleaned_documents))

    # STEP 3: Create chunks
    print("\nSTEP 3: Creating section-aware chunks...")

    chunks = chunk_documents(
        cleaned_documents,
        chunk_size=1200,
        overlap=150
    )

    print("Chunks created:", len(chunks))
    print("\n========== CONTEXTUALIZED EMBEDDING PREVIEW ==========\n")

    for chunk in chunks:

        if chunk["section"] == "2. Services":

            print("CHUNK:", chunk["chunk_index"])

            print("\nORIGINAL TEXT:")
            print(chunk["text"])

            print("\nEMBEDDING TEXT:")
            print(chunk["embedding_text"])

            print("\n" + "=" * 60)

    # STEP 4: Inspect all chunks
    print("\n========== ALL CREATED CHUNKS ==========\n")

    for chunk in chunks:

        print(f"\nCHUNK: {chunk['chunk_index']}")
        print("SECTION:", chunk["section"])

        print(
            f"PAGES: {chunk['page_start']}"
            f"-{chunk['page_end']}"
        )

        print("-" * 60)
        print(chunk["text"])
        print("-" * 60)

    # STEP 5: Ingest into ChromaDB
    print("\nSTEP 5: Generating embeddings and storing vectors...\n")

    result = ingest_pdf(
        pdf_path=PDF_PATH,
        company_id=company_id,
        document_id=document_id
    )

    print("INGESTION RESULT:")
    print(result)

    # STEP 6: Test semantic retrieval
    print("\nSTEP 6: Testing semantic retrieval...\n")

    question = input("Enter your question: ")

    results = retrieve_context(
        question=question,
        company_id=company_id,
        top_k=12
    )

    print("\n========== RETRIEVED RESULTS ==========\n")

    for index, result in enumerate(results, start=1):

        metadata = result["metadata"]

        print(f"\nRESULT {index}")

        print("SECTION:", metadata["section"])
        print("SOURCE:", metadata["source"])

        print(
            "PAGES:",
            metadata["page_start"],
            "-",
            metadata["page_end"]
        )

        print("DISTANCE:", result["distance"])

        print("\nCONTENT:")
        print(result["text"])

        print("\n" + "=" * 60)

    print("\n========== TEST COMPLETED ==========\n")


if __name__ == "__main__":
    main()