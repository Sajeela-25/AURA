import sys

sys.path.insert(0, "backend")

from app.rag.answer_service import answer_question


questions = [
    "What are Verxeon pricing plans and service packages?",
    "What does Verxeon offer in Chatbots and Voice AI?",
    "What is Verxeons employee leave policy?"
]


for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:", question)

    try:

        result = answer_question(
            question=question,
            company_id="verxeon"
        )

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")

        for source in result.get("sources", []):

            print(
                "Reference:", source.get("reference"),
                "| Section:", source.get("section"),
                "| Pages:",
                source.get("page_start"),
                "-",
                source.get("page_end")
            )

    except Exception as error:

        print("\nERROR:", type(error).__name__, str(error))


print("\n" + "=" * 80)
print("PIPELINE TEST COMPLETED")