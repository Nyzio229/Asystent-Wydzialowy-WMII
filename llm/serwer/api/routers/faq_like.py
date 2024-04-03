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
    faq_like_config = config.api.faq_like

    query_embedding = common.embedder.embed_query(request.text)

    result = common.vector_store_client.search(
        collection_name=faq_like_config.collection_name,
        query_vector=query_embedding,
        limit=request.limit,
        score_threshold=faq_like_config.score_threshold
    )

    result = FAQLikeResult(faq_ids=[x.id for x in result])

    return result
