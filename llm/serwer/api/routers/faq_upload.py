from typing import Literal

from fastapi import APIRouter

from pydantic import BaseModel

from api.routers.faq import FaqEntry

from common import common, Document, upload_docs

class FAQUploadRequest(BaseModel):
    faq: list[FaqEntry]
    lang: Literal["en", "pl"]

router = APIRouter()

@router.post("/faq_upload")
async def faq_upload(
    request: FAQUploadRequest
) -> None:
    docs = [
        Document(
            text=faq_entry.question,
            metadata=dict(
                answer=faq_entry.answer
            )
        )
        for faq_entry in request.faq
    ]

    upload_docs(
        common.faq_vector_store[request.lang],
        docs
    )
