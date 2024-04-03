from typing import Optional

from fastapi import APIRouter

from pydantic import BaseModel

from llama_cpp import Llama

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStoreRetriever

from common import common

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: list[Message]
    rag: bool = True
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

def rag(
    retriever: VectorStoreRetriever,
    llm: Llama,
    messages: list[Message]
) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [(message.role, message.content)
         for message in messages]
    )

    chain = create_stuff_documents_chain(llm, prompt)

    rag_chain = create_retrieval_chain(retriever, chain)

    response = rag_chain.invoke({})

    # @TODO: return only the answer
    print(response)

    return response

router = APIRouter()

# @TODO: lepiej opisać wynik
# @TODO: parametry llma będą podawane z linii poleceń? bo rag nie pozwala ich zmienić
@router.post("/chat")
async def chat(
    request: ChatCompletionRequest
) -> dict:
    if request.rag:
        result = rag(
            retriever=common.rag_retriever,
            llm=common.llm,
            messages=request.messages
        )

        return result

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
