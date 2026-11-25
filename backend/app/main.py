import re
import time
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.openapi.utils import get_openapi

from app.core.config import UPLOAD_DIR
from app.rag.rag_service import ingest_pdf


app = FastAPI(title="AURA API")

DOC_TYPE_ALIASES = {
    "faq": "faq",
    "faqs": "faq",
    "product": "product",
    "products": "product",
    "pricing": "pricing",
    "policy": "policy",
    "policies": "policy",
    "sales": "sales",
}


@app.get("/")
def home():
    return {"message": "AURA API is running"}


@app.post("/companies/{company_id}/documents")
async def upload_documents(
    company_id: str,
    doc_type: Annotated[str, Form()],
    files: Annotated[list[UploadFile], File()],
):
    company_id = company_id.strip()
    category = DOC_TYPE_ALIASES.get(doc_type.strip().lower())

    if not company_id:
        raise HTTPException(
            status_code=400,
            detail="company_id is required",
        )

    if category is None:
        raise HTTPException(
            status_code=400,
            detail="doc_type must be faq, product, pricing, policy, or sales",
        )

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Select at least one PDF",
        )

    safe_company_id = re.sub(r"[^a-zA-Z0-9_-]", "_", company_id)
    company_dir = Path(UPLOAD_DIR) / safe_company_id
    company_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for uploaded_file in files:
        original_filename = uploaded_file.filename or "upload.pdf"

        if Path(original_filename).suffix.lower() != ".pdf":
            results.append({
                "filename": original_filename,
                "status": "failed",
                "error": "Only PDF files are supported",
            })
            await uploaded_file.close()
            continue

        document_id = uuid4().hex
        saved_path = company_dir / f"{document_id}.pdf"
        started = time.perf_counter()

        print(
            f"[UPLOAD] {original_filename}: processing started",
            flush=True,
        )

        try:
            with saved_path.open("wb") as destination:
                while content := await uploaded_file.read(1024 * 1024):
                    destination.write(content)

            if saved_path.stat().st_size == 0:
                raise ValueError("Uploaded PDF is empty")

            ingest_result = ingest_pdf(
                pdf_path=saved_path,
                company_id=company_id,
                document_id=document_id,
                doc_type=category,
            )

            elapsed = time.perf_counter() - started
            print(
                f"[UPLOAD] {original_filename}: complete in {elapsed:.1f}s",
                flush=True,
            )

            results.append({
                **ingest_result,
                "filename": original_filename,
                "doc_type": category,
                "status": "ready",
            })

        except Exception as exc:
            elapsed = time.perf_counter() - started
            print(
                f"[UPLOAD] {original_filename}: failed after "
                f"{elapsed:.1f}s: {exc}",
                flush=True,
            )

            results.append({
                "document_id": document_id,
                "filename": original_filename,
                "doc_type": category,
                "status": "failed",
                "error": str(exc),
            })

        finally:
            await uploaded_file.close()

    return {
        "company_id": company_id,
        "documents": results,
    }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version="1.0.0",
        routes=app.routes,
        openapi_version="3.0.3",
    )

    operation = schema["paths"][
        "/companies/{company_id}/documents"
    ]["post"]

    request_schema = operation["requestBody"]["content"][
        "multipart/form-data"
    ]["schema"]

    schema_name = request_schema["$ref"].split("/")[-1]
    body_schema = schema["components"]["schemas"][schema_name]

    body_schema["properties"]["files"] = {
        "type": "array",
        "items": {
            "type": "string",
            "format": "binary",
        },
    }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi