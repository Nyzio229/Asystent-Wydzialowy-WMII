from fastapi import APIRouter

from pydantic import BaseModel

from llama_index.core.schema import TextNode

from llama_index.core.node_parser import SentenceSplitter

from embed import embed

from common import common

from config import config

from vector_store import get_vector_store

class Document(BaseModel):
    text: str
    metadata: dict[str, int | str]

def create_text_nodes(
    docs: list[Document],
    doc_idxs: list[int],
    text_chunks: list[str]
) -> list[TextNode]:
    def _create_text_node(idx: int, text_chunk: str) -> TextNode:
        node = TextNode(text=text_chunk)
        src_doc = docs[doc_idxs[idx]]

        node.metadata = src_doc.metadata
        text = node.get_content(metadata_mode="all")
        node.embedding = embed(common.embedder, text)

        return node

    nodes = list(map(lambda args: _create_text_node(*args), enumerate(text_chunks)))

    return nodes

def create_text_chunks(
    text_parser: SentenceSplitter,
    docs: list[Document]
) -> tuple[list[int], list[str]]:
    doc_idxs: list[int] = []
    text_chunks: list[str] = []

    for idx, doc in enumerate(docs):
        text_chunks = text_parser.split_text(doc.text)
        text_chunks.extend(text_chunks)
        doc_idxs.extend([idx] * len(text_chunks))

    return doc_idxs, text_chunks

class RAGDocsUploadRequest(BaseModel):
    docs: list[Document]

router = APIRouter()

@router.post("/rag_docs_upload")
async def rag_docs_upload(
    request: RAGDocsUploadRequest
) -> None:
    rag_docs_upload_config = config["api"]["rag_docs_upload"]
    text_parser = SentenceSplitter(
        chunk_size=rag_docs_upload_config["chunk_size"],
        separator=rag_docs_upload_config["separator"]
    )

    docs = request.docs
    doc_idxs, text_chunks = create_text_chunks(text_parser, docs)
    nodes = create_text_nodes(docs, doc_idxs, text_chunks)

    collection_name = config["vector_store"]["collection_name"]
    vector_store = get_vector_store(common.qdrant_client, collection_name)
    vector_store.add(nodes)
