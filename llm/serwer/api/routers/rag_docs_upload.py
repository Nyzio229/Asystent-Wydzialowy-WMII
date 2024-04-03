from fastapi import APIRouter

from pydantic import BaseModel

from langchain_text_splitters import CharacterTextSplitter

from common import common
from config import config

class Document(BaseModel):
    text: str
    metadata: dict[str, int | str]

class RAGDocsUploadRequest(BaseModel):
    docs: list[Document]

router = APIRouter()

@router.post("/rag_docs_upload")
async def rag_docs_upload(
    request: RAGDocsUploadRequest
) -> None:
    rag_docs_upload_config = config.api.rag_docs_upload
    text_splitter = CharacterTextSplitter(
        separator=rag_docs_upload_config.separator,
        chunk_size=rag_docs_upload_config.chunk_size
    )

    docs = text_splitter.split_documents(request.docs)
    common.rag_vector_store.add_documents(docs)
