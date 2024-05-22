from typing import Literal

from fastapi import APIRouter

from pydantic import BaseModel

from config import config
from common import common, log_endpoint_call

class FAQRequest(BaseModel):
    faq_ids: list[str]
    lang: Literal["en", "pl"] = "pl"

class FAQEntry(BaseModel):
    answer: str
    question: str

class FAQResult(BaseModel):
    faq: list[FAQEntry]

router = APIRouter()

@router.post("/faq")
async def faq(
    request: FAQRequest
) -> FAQResult:
    collection_name = config.vector_store.faq_collection_for_lang[request.lang]

    faq_ids = request.faq_ids

    result = common.vector_store_client.retrieve(
        collection_name=collection_name,
        ids=faq_ids
    )

    docs: list[
        dict[str, str | dict[str, str]]
    ] = []

    for faq_id in faq_ids:
        try:
            doc = next(record.payload
                       for record in result
                       if record.id == faq_id)
        except StopIteration:
            continue

        docs.append(doc)

    result = FAQResult(
        faq=[
            FAQEntry(
                question=doc["page_content"],
                answer=doc["metadata"]["answer"]
            )
            for doc in docs
        ]
    )

    log_endpoint_call("faq", request, result)

    return result
