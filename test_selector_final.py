import sys

sys.path.insert(0, "backend")

from app.rag.rag_service import retrieve_context
from app.rag.answer_service import select_relevant_chunks

questions = [
    "What are Verxeon pricing plans and service packages?",
    "What does Verxeon offer in Chatbots and Voice AI?",
    "What is Verxeons employee leave policy?"
]

for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    retrieved = retrieve_context(
        question,
        "verxeon",
        top_k=12
    )

    selected = select_relevant_chunks(
        question,
        retrieved
    )

    print("RETRIEVED:", len(retrieved))
    print("SELECTED:", len(selected))

    for index, chunk in enumerate(selected, 1):

        print(
            "\nSELECTED", index,
            "| SECTION:",
            chunk["metadata"].get("section"),
            "| DISTANCE:",
            round(chunk["distance"], 4)
        )

        print(chunk["text"][:350])
