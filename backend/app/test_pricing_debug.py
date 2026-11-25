
import sys

sys.path.insert(0, "backend")

from app.rag.rag_service import retrieve_context
from app.rag.answer_service import (
    select_relevant_chunks,
    build_context
)

question = "What are Verxeon pricing plans and service packages?"

retrieved = retrieve_context(
    question,
    "verxeon",
    top_k=12
)

selected = select_relevant_chunks(
    question,
    retrieved
)

print("\nRETRIEVED CHUNKS:", len(retrieved))
print("SELECTED CHUNKS:", len(selected))

for i, chunk in enumerate(selected, start=1):

    metadata = chunk.get("metadata", {})

    print("\n" + "=" * 70)
    print("SELECTED CHUNK:", i)
    print("SECTION:", metadata.get("section"))
    print("PAGE:", metadata.get("page_start"), "-", metadata.get("page_end"))
    print("\nTEXT:\n")
    print(chunk.get("text", ""))

context, sources = build_context(selected)

print("\n" + "=" * 70)
print("COMPLETE CONTEXT SENT TO EVIDENCE CHECKER:")
print(context)
