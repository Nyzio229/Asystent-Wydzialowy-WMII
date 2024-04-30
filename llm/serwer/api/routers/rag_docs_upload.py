from fastapi import APIRouter

from pydantic import BaseModel

from common import common, Document, upload_docs

class RAGDocsUploadRequest(BaseModel):
    docs: list[Document]

router = APIRouter()

@router.post("/rag_docs_upload")
async def rag_docs_upload(
    request: RAGDocsUploadRequest
) -> None:
    upload_docs(
        common.rag_vector_store,
        request.docs
    )
