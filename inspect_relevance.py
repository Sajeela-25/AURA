import sys

sys.path.insert(0, "backend")

from app.rag.rag_service import retrieve_context

questions = [
    "What does Verxeon offer in Chatbots and Voice AI?",
    "What is Verxeons employee leave policy?"
]

for question in questions:

    print("\n" + "=" * 75)
    print("QUESTION:", question)

    chunks = retrieve_context(question, "verxeon", top_k=4)

    for index, chunk in enumerate(chunks):

        print("\nRANK:", index + 1)
        print("SECTION:", chunk["metadata"].get("section"))
        print("DISTANCE:", round(chunk["distance"], 4))
        print("TEXT:")
        print(chunk["text"][:1200])
