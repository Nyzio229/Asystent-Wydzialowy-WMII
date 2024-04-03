from fastapi import APIRouter

from pydantic import BaseModel

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
    result = common.rag_vector_store.search(
        query=request.text,
        search_type="similarity",
        score_threshold=config.api.faq_like.score_threshold,
        k=request.limit
    )

    # @TODO: get documents id
    print(result)

    result = FAQLikeResult(faq_ids=[1])

    return result
