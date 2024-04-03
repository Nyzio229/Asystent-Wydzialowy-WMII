from fastapi import APIRouter

from pydantic import BaseModel

from langchain_text_splitters import CharacterTextSplitter
from langchain_community.docstore.document import Document as LangchainDocument

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

    docs = [
        LangchainDocument(
            page_content=doc.text,
            **doc.metadata
        )
        for doc in request.docs
    ]

    docs = text_splitter.split_documents(docs)
    common.rag_vector_store.add_documents(docs)
