from typing import Optional

from fastapi import APIRouter

from pydantic import BaseModel

from common import common

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: list[Message]
    temperature: float = 0.2
    top_p: float = 0.95
    top_k: int = 40
    min_p: float = 0.05
    typical_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    repeat_penalty: float = 1.1
    tfs_z: float = 1.0
    mirostat_mode: int = 0
    mirostat_tau: float = 5.0
    mirostat_eta: float = 0.1
    max_tokens: Optional[int] = None

router = APIRouter()

# @TODO: lepiej opisać wynik
@router.post("/chat")
async def chat(
    request: ChatCompletionRequest
) -> dict:
    messages = list(map(dict, request.messages))

    result = common.llm.create_chat_completion(
        messages=messages,
        temperature=request.temperature,
        top_p=request.top_p,
        top_k=request.top_k,
        min_p=request.min_p,
        typical_p=request.typical_p,
        presence_penalty=request.presence_penalty,
        frequency_penalty=request.frequency_penalty,
        repeat_penalty=request.repeat_penalty,
        tfs_z=request.tfs_z,
        mirostat_mode=request.mirostat_mode,
        mirostat_tau=request.mirostat_tau,
        mirostat_eta=request.mirostat_eta,
        max_tokens=request.max_tokens
    )

    return result
