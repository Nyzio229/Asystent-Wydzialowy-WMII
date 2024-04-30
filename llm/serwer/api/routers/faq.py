from typing import Literal

from fastapi import APIRouter

from pydantic import BaseModel

from common import common
from config import config

class FAQRequest(BaseModel):
    faq_ids: list[str]
    lang: Literal["en", "pl"] = "pl"

class FaqEntry(BaseModel):
    answer: str
    question: str

class FAQResult(BaseModel):
    faq: list[FaqEntry]

router = APIRouter()

@router.post("/faq")
async def faq(
    request: FAQRequest
) -> FAQResult:
    collection_name = config.vector_store.faq_collection_name[request.lang]

    faq_ids = request.faq_ids

    result = common.vector_store_client.retrieve(
        collection_name=collection_name,
        ids=faq_ids
    )

    docs = [next(record.payload
                 for record in result if record.id == id)
            for id in faq_ids]

    result = FAQResult(faq=[FaqEntry(
        question=doc["page_content"],
        answer=doc["metadata"]["answer"]
    ) for doc in docs])

    return result
