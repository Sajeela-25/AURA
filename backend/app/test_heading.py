
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.chunker import is_heading


test_lines = [
    "1. Company Information",
    "2. Services",
    "3. Service Packages",
    "2. Verxeon acknowledges the request, normally within 24 hours.",
    "4. The client confirms the fix and the request is closed.",
    "3. Inquiry. The client contacts Verxeon.",
    "COMPANY INFORMATION",
    "Section: General"
]

print("\n========== HEADING DETECTION TEST ==========\n")

for line in test_lines:
    result = is_heading(line)

    print(f"{line}")
    print(f"Is heading: {result}")
    print("-" * 60)
