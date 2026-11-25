import sys
from uuid import uuid4

sys.path.insert(0, "backend")

from app.rag.vector_store import store_chunks, search_chunks, delete_document

company_a = "isolation_test_A_" + uuid4().hex
company_b = "isolation_test_B_" + uuid4().hex

document_a = "test_document_A"
document_b = "test_document_B"

embedding = [1.0] + [0.0] * 383

chunk_a = [{
    "chunk_index": 0,
    "text": "Company A secret code is ALPHA-741.",
    "page_start": 1,
    "page_end": 1,
    "section": "Testing"
}]

chunk_b = [{
    "chunk_index": 0,
    "text": "Company B secret code is BRAVO-852.",
    "page_start": 1,
    "page_end": 1,
    "section": "Testing"
}]

try:
    store_chunks(
        chunk_a, [embedding], company_a, document_a, "test_A.pdf"
    )

    store_chunks(
        chunk_b, [embedding], company_b, document_b, "test_B.pdf"
    )

    results_a = search_chunks(embedding, company_a, top_k=5)
    results_b = search_chunks(embedding, company_b, top_k=5)

    text_a = " ".join(item["text"] for item in results_a)
    text_b = " ".join(item["text"] for item in results_b)

    print("COMPANY A RESULTS:", text_a)
    print("COMPANY B RESULTS:", text_b)

    assert "ALPHA-741" in text_a
    assert "BRAVO-852" not in text_a

    assert "BRAVO-852" in text_b
    assert "ALPHA-741" not in text_b

    print("\nPASS: Company data isolation is working.")

finally:
    delete_document(company_a, document_a)
    delete_document(company_b, document_b)
