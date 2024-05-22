from typing import Literal

from fastapi import APIRouter

from pydantic import BaseModel

from config import config
from common import common, log_endpoint_call

class FAQLikeRequest(BaseModel):
    text: str
    limit: int

    lang: Literal["en", "pl"] = "en"

class FAQLikeResult(BaseModel):
    faq_ids: list[str]

router = APIRouter()

@router.post("/faq_like")
async def faq_like(
    request: FAQLikeRequest
) -> FAQLikeResult:
    vector_store = common.faq_vector_store[request.lang]

    result = vector_store.similarity_search(
        query=request.text,
        k=request.limit,
        score_threshold=config.api.faq_like.score_threshold
    )

    result = FAQLikeResult(
        faq_ids=[
            x.metadata["_id"]
            for x in result
        ]
    )

    log_endpoint_call("faq_like", request, result)

    return result
