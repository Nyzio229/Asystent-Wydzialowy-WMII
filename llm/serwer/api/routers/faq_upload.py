from typing import Literal

from fastapi import APIRouter

from pydantic import BaseModel

from api.routers.faq import FaqEntry

from common import common, upload_docs

from langchain_community.docstore.document import Document

class LangFAQ(BaseModel):
    faq: list[FaqEntry]
    lang: Literal["en", "pl"]

class FAQUploadRequest(BaseModel):
    lang_faqs: list[LangFAQ]

router = APIRouter()

@router.post("/faq_upload")
async def faq_upload(
    request: FAQUploadRequest
) -> None:
    faq_entry_ids: list[str] = []

    for i, lang_faq in enumerate(request.lang_faqs):
        docs = [
            Document(
                page_content=faq_entry.question,
                metadata=dict(
                    answer=faq_entry.answer
                )
            )
            for faq_entry in lang_faq.faq
        ]

        ids = upload_docs(
            common.faq_vector_store[lang_faq.lang],
            docs,
            faq_entry_ids
        )

        if i == 0:
            faq_entry_ids = ids
