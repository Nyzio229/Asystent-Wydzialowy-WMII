from typing import Literal

from fastapi import APIRouter

from pydantic import BaseModel

from common import common
from config import config

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
    result = common.faq_vector_store[request.lang].similarity_search(
        query=request.text,
        k=request.limit,
        score_threshold=config.api.faq_like.score_threshold
    )

    faq_ids = [x.metadata["_id"] for x in result]
    result = FAQLikeResult(faq_ids=faq_ids)

    return result
