import sys
import re

sys.path.insert(0, "backend")

from app.rag.answer_service import answer_question

questions = [
    "Who is the CEO of Verxeon?",
    "What are Verxeons services?",
    "What are Verxeons pricing plans?"
]

for question in questions:
    result = answer_question(question, "verxeon")

    cited = {
        "Source " + number
        for number in re.findall(
            r"\[Source\s+(\d+)",
            result["answer"]
        )
    }

    available = {
        source["reference"]
        for source in result["sources"]
    }

    print("\nQUESTION:", question)
    print("CITED SOURCES:", cited)
    print("AVAILABLE SOURCES:", available)
    print("CITATIONS VALID:", cited.issubset(available))
