from fastapi import APIRouter

from pydantic import BaseModel

from embed import embed

from common import common

from config import config

class FAQLikeRequest(BaseModel):
    text: str
    limit: int

class FAQLikeResult(BaseModel):
    faq_ids: list[int]

router = APIRouter()

@router.post("/faq_like")
async def faq_like(
    request: FAQLikeRequest
) -> FAQLikeResult:
    score_threshold = config["api"]["faq_like"]["score_threshold"]

    query_embedding = embed(common.embedder, request.text)
    result = common.qdrant_client.search("asystent_FAQ", query_embedding, limit=request.limit)
    result = filter(lambda x: x.score > score_threshold, result)
    result = sorted(result, key=lambda x: x.score, reverse=True)
    result = FAQLikeResult(faq_ids=[x.id for x in result])

    return result
