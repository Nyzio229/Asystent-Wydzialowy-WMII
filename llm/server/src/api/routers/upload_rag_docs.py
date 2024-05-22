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
    metadata: dict[
        str, str | int | list[str]
    ] = {}

class UploadRAGDocsRequest(BaseModel):
    docs: list[Document]

router = APIRouter()

def _get_docs_summaries(docs: list[str]) -> list[str]:
    n_docs = len(docs)

    def _get_doc_summary(doc_idx, doc: str) -> str:
        LOGGER.debug(
            "[%d/%d] Generating a summary...",
            doc_idx+1, n_docs
        )

        prompt = (
            f"Summarize the following document:\n{doc}\n\nThe summary:\n\n"
        )

        summary = common.invoke_llm(prompt)

        LOGGER.debug("Summary: %s", summary)

        return summary

    LOGGER.setLevel(logging.DEBUG)

    summaries = list(map(
        lambda pair: _get_doc_summary(*pair),
        enumerate(docs)
    ))

    return summaries

def _get_docs_questions(docs: list[str]) -> list[list[str]]:
    n_docs = len(docs)

    def _get_doc_questions(idx: int, doc: str) -> list[str]:
        LOGGER.debug(
            "[%d/%d] Generating hypothetical questions...",
            idx+1, n_docs
        )

        prompt = (
            "Generate as many hypothetical questions as possible that "
            "the below document could be used to answer. The questions "
            "should cover as many main and important pieces of information "
            "found in the document as possible. Provide these hypothetical "
            "questions separated by newlines.\n"
            f"The document:\n{doc}\n\nHypothetical questions:\n\n"
        )

        questions = common.invoke_llm(prompt)

        questions = questions.split("\n")

        questions = list(map(
            # if line starts with: "<number>. ", "* " or "Q: ", then remove the prefix
            lambda x: re.sub(r"^([0-9]+\.|\*|Q\:) ", "", x),
            filter(
                lambda x: x,
                questions
            )
        ))

        questions = list(set(
            questions
        ))

        LOGGER.debug("Questions: %s", questions)

        return questions

    LOGGER.setLevel(logging.DEBUG)

    questions = list(map(
        lambda pair: _get_doc_questions(*pair),
        enumerate(docs)
    ))

    return questions

def _split_docs(
    docs: list[str],
    text_splitter: TextSplitter,
    doc_id_key: str,
    doc_ids: Optional[list[str]] = None
) -> list[LangchainDocument]:
    chunked_docs: list[LangchainDocument] = []

    LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug(
        "Splitting documents (n_docs=%d)...",
        len(docs)
    )

    for i, doc in enumerate(docs):
        sub_docs = text_splitter.split_documents([doc])

        if doc_ids:
            doc_id = doc_ids[i]

            for sub_doc in sub_docs:
                sub_doc.metadata[doc_id_key] = doc_id

        chunked_docs += sub_docs

    LOGGER.debug(
        "Finished splitting (n_docs=%d).",
        len(chunked_docs)
    )

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

_UMK_ABBREVIATION_HEADER = (
    "(UMK stands for Nicolaus Copernicus University in Toruń)"
)

def _insert_umk_abbreviation_header(content: str) -> str:
    return (
        f"{_UMK_ABBREVIATION_HEADER}\n\n{content}"
    )

def _insert_header(header: str, content: str) -> str:
    return f"{header}\n\n{content}"

def _insert_tags_header(
    doc: str,
    metadata: dict[
        str, str | int | list[str]
    ]
) -> str:
    tags: Optional[
        list[str]
    ] = metadata.get("tags", None)

    if not tags:
        return doc

    def _insert_markdown_header(
        header: str,
        content: str
    ) -> str:
        if "\n" not in header:
            header = f"*{header}*"

        return _insert_header(header, content)

    section_title = metadata.get("section_title", None)

    if section_title:
        doc = _insert_markdown_header(section_title, doc)

    news_date = metadata.get("news_date", None)

    if news_date:
        doc = _insert_header(
            f"(publication date: {news_date})", doc
        )

    title = metadata.get("title", None)

    news_title = metadata.get("news_title", None)

    title_header = title or news_title

    if title_header:
        doc = _insert_markdown_header(title_header, doc)

    tags = ", ".join(tags)

    doc = _insert_header(
        f"(Tags: {tags})", doc
    )

    return doc

def _insert_doc_headers(doc: LangchainDocument) -> None:
    metadata = doc.metadata

    markdown_header: Optional[str] = metadata.get(
        "markdown_header", None
    )

    if markdown_header:
        doc.page_content = _insert_header(
            markdown_header, doc.page_content
        )

    abbreviations: list[str] = metadata.get(
        "abbreviations", []
    )

    if "umk" in abbreviations:
        doc.page_content = _insert_umk_abbreviation_header(
            doc.page_content
        )

    doc.page_content = _insert_tags_header(
        doc.page_content, metadata
    )

    origin = metadata.get("origin", None)

    if origin:
        doc.page_content = _insert_header(
            f"(Source: {origin})", doc.page_content
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
        _make_langchain_doc(
            question, doc_id_key, doc_id
        )
        for doc_id, questions in zip(doc_ids, questions)
        for question in questions
    ]

    return questions

def _get_llm_generated_vector_store_docs(
    docs: list[str],
    doc_id_key: str,
    doc_ids: list[str]
) -> list[LangchainDocument]:
    docs_getters = (
        _get_langchain_doc_summaries,
        _get_langchain_doc_questions,
    )

    vector_store_docs = [
        doc
        for docs_getter in docs_getters
        for doc in docs_getter(
            docs, doc_id_key, doc_ids
        )
    ]

    return vector_store_docs

def _generate_doc_ids(n_ids: int) -> list[str]:
    doc_ids = list(map(
        lambda _: str(uuid.uuid4()),
        range(n_ids)
    ))

    return doc_ids

def _move_markdown_header_to_metadata(
    doc: LangchainDocument
) -> None:
    # A group of consisting of two asterisks (markdown bold text);
    # each group must consist of at least 2 characters
    # (not at least one because strings like "* * * TEXT * * *"
    # get matched then).
    # A newline characters breaks the group.
    pattern = r"(\*[^\*\n]{2,}\*)"

    markdown_header: Optional[str] = None

    def _on_match(match: re.Match) -> str:
        nonlocal markdown_header

        markdown_header = match.group(0)

        return ""

    # Replace at least two such asterisk groups with an empty text
    # (the groups must be separated by at least one space)
    page_content = re.sub(
        fr"^{pattern}(?: +{pattern})+",
        _on_match, doc.page_content
    )

    if not markdown_header:
        return

    doc.page_content = page_content.lstrip()

    doc.metadata["markdown_header"] = markdown_header

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

    for doc in docs:
        _move_markdown_header_to_metadata(doc)

    retriever = common.rag_retriever

    doc_id_key = retriever.id_key

    def _chunk_docs(
        chunk_size: int,
        doc_ids: Optional[list[int]] = None
    ) -> list[LangchainDocument]:
        chunked_docs = _split_docs(
            docs,
            RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=0
            ),
            doc_id_key,
            doc_ids
        )

        return chunked_docs

    docs = _chunk_docs(
        chunk_size=1024
    )

    doc_ids = _generate_doc_ids(len(docs))

    # split docs before adding headers to the original docs
    # so that the headers don't get split as/into chunks
    # (but add headers before adding summaries/questions
    # so that the hedears are seen by the LLM during generation)
    vector_store_docs = _chunk_docs(
        chunk_size=200,
        doc_ids=doc_ids
    )

    for doc in docs:
        _insert_doc_headers(doc)

    retriever.docstore.mset(list(zip(
        doc_ids, docs
    )))

    vector_store_docs += _get_llm_generated_vector_store_docs(
        docs, doc_id_key, doc_ids
    )

    retriever.vectorstore.add_documents(vector_store_docs)
