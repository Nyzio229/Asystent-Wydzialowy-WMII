from typing import Literal

from fastapi import APIRouter

from pydantic import BaseModel

from common import common

from api.routers.faq import FAQEntry

from langchain_community.docstore.document import Document

class LangFAQ(BaseModel):
    faq: list[FAQEntry]
    lang: Literal["en", "pl"]

class UploadFAQRequest(BaseModel):
    lang_faqs: list[LangFAQ]

router = APIRouter()

@router.post("/upload_faq")
async def upload_faq(
    request: UploadFAQRequest
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

        vector_store = common.faq_vector_store[lang_faq.lang]

        ids = vector_store.add_documents(
            docs,
            ids=faq_entry_ids
        )

        if i == 0:
            faq_entry_ids = ids
