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

    result = common.vector_store_client.retrieve(
        collection_name=collection_name,
        ids=request.faq_ids
    )

    result = FAQResult(faq=[FaqEntry(
        question=doc.text,
        answer=doc.metadata["answer"]
    ) for doc in result])

    return result
