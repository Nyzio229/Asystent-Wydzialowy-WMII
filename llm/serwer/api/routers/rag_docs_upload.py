from typing import Optional

from fastapi import APIRouter

from pydantic import BaseModel

from common import common, upload_docs

class Document(BaseModel):
    page_content: str
    metadata: Optional[dict[str, str | int]] = dict()

class RAGDocsUploadRequest(BaseModel):
    docs: list[Document]

router = APIRouter()

@router.post("/rag_docs_upload")
async def rag_docs_upload(
    request: RAGDocsUploadRequest
) -> None:
    docs = [
        Document(
            page_content=doc.page_content,
            metadata=doc.metadata
        )
        for doc in request.docs
    ]

    upload_docs(
        common.rag_vector_store,
        docs
    )
