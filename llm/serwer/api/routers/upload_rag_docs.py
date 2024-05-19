import re

import uuid

import logging

from typing import Optional

from fastapi import APIRouter

from pydantic import BaseModel

from langchain_community.docstore.document import Document as LangchainDocument
from langchain_text_splitters import TextSplitter, RecursiveCharacterTextSplitter

from common import common, LOGGER

class Document(BaseModel):
    page_content: str
    metadata: Optional[
        dict[str, str | int]
    ] = {}

class UploadRAGDocsRequest(BaseModel):
    docs: list[Document]

router = APIRouter()

def _invoke_llm(prompt: str) -> str:
    kwargs = common.llm_inference_params.model_dump()
    response = common.llm(prompt, **kwargs)
    response = response["choices"][0]["text"]

    return response

def _get_docs_summaries(docs: list[str]) -> list[str]:
    def _get_doc_summary(doc: str) -> str:
        LOGGER.debug("Generating a summary...")

        prompt = f"Summarize the following document:\n{doc}\n\nThe summary:\n\n"

        summary = _invoke_llm(prompt)

        LOGGER.debug("Summary: %s", summary)

        return summary

    LOGGER.setLevel(logging.DEBUG)

    summaries = list(map(
        _get_doc_summary, docs
    ))

    return summaries

def _get_docs_questions(docs: list[str]) -> list[list[str]]:
    def _get_doc_questions(doc: str) -> list[str]:
        LOGGER.debug("Generating hypothetical questions...")

        prompt = (
            "Generate hypothetical questions that the below document could be used to answer. "
            "Provide these hypothetical questions separated by newlines.\n"
            f"The document:\n{doc}\n\nHypothetical questions:\n\n"""
        )

        questions = _invoke_llm(prompt)

        questions = questions.split("\n")

        questions = list(map(
            # if line starts with: "<number>. " or "* ", then remove the prefix
            lambda x: re.sub(r"^([0-9]+\.|\*) ", "", x),
            filter(lambda x: x, questions)
        ))

        LOGGER.debug("Hypothetical questions: %s", questions)

        return questions

    LOGGER.setLevel(logging.DEBUG)

    questions = list(map(
        _get_doc_questions, docs
    ))

    return questions

def _get_doc_chunks(
    docs: list[str],
    doc_id_key: str,
    doc_ids: list[str],
    text_splitter: TextSplitter,
) -> list[LangchainDocument]:
    chunked_docs: list[LangchainDocument] = []

    for doc_id, doc in zip(doc_ids, docs):
        sub_docs = text_splitter.split_documents([doc])

        for sub_doc in sub_docs:
            sub_doc.metadata[doc_id_key] = doc_id

        chunked_docs += sub_docs

    return chunked_docs

def _make_langchain_doc(
    page_content: str,
    doc_id_key: str,
    doc_id: str
) -> LangchainDocument:
    return LangchainDocument(
        page_content=page_content,
        metadata={
            doc_id_key: doc_id
        }
    )

def _get_langchain_doc_summaries(
    docs: list[str],
    doc_id_key: str,
    doc_ids: list[str]
) -> list[LangchainDocument]:
    summaries = _get_docs_summaries(docs)

    summary_docs = [
        _make_langchain_doc(summary, doc_id_key, doc_id)
        for doc_id, summary in zip(doc_ids, summaries)
    ]

    return summary_docs

def _get_langchain_doc_questions(
    docs: list[str],
    doc_id_key: str,
    doc_ids: list[str]
) -> list[LangchainDocument]:
    questions = _get_docs_questions(docs)

    questions = [
        _make_langchain_doc(question, doc_id_key, doc_id)
        for doc_id, questions in zip(doc_ids, questions)
        for question in questions
    ]

    return questions

def _get_langchain_doc_chunks_with_splitter(
    docs: list[str],
    doc_id_key: str,
    doc_ids: list[str]
) -> list[LangchainDocument]:
    return _get_doc_chunks(
        docs, doc_id_key, doc_ids,
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=20
        )
    )

def _get_vector_store_docs(
    docs: list[str],
    doc_id_key: str,
    doc_ids: list[str]
) -> list[LangchainDocument]:
    doc_getters = (
        _get_langchain_doc_summaries,
        _get_langchain_doc_questions,
        _get_langchain_doc_chunks_with_splitter
    )

    args = docs, doc_id_key, doc_ids

    vector_store_docs: list[LangchainDocument] = []

    for doc_getter in doc_getters:
        vector_store_docs += doc_getter(*args)

    return vector_store_docs

@router.post("/upload_rag_docs")
async def upload_rag_docs(
    request: UploadRAGDocsRequest
) -> None:
    docs = [
        LangchainDocument(
            page_content=doc.page_content,
            metadata=doc.metadata
        )
        for doc in request.docs
    ]

    doc_ids = list(map(
        lambda _: str(uuid.uuid4()), docs
    ))

    retriever = common.rag_retriever

    vector_store_docs = _get_vector_store_docs(
        docs, retriever.id_key, doc_ids
    )

    retriever.vectorstore.add_documents(vector_store_docs)

    retriever.docstore.mset(list(zip(
        doc_ids, docs
    )))
