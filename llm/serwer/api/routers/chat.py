from typing import Optional

from fastapi import APIRouter

from pydantic import BaseModel

from llama_cpp import Llama

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common import common, chat_completion, langchain_chat_completion

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

def _get_llm_params_kwargs(request: ChatCompletionRequest) -> dict[str]:
    kwargs = dict(
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

    return kwargs

def _rag(
    llm: Llama,
    retriever: VectorStoreRetriever,
    request: ChatCompletionRequest
) -> str:
    system_message = (
        "You're a helpful assistant."
    )

    system_message += "\n\n{context}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder("chat_history_without_input"),
        ("human", "{input}")
    ])

    kwargs = _get_llm_params_kwargs(request)
    chain = create_stuff_documents_chain(
        llm=lambda prompt: langchain_chat_completion(llm, prompt, **kwargs),
        prompt=prompt
    )

    rag_chain = create_retrieval_chain(
        retriever=common.history_aware_retriever,
        combine_docs_chain=chain
    )

    messages = [(message.role, message.content)
                for message in request.messages]

    prompt_template_input = dict(
        input=messages[-1][1],
        chat_history=messages,
        chat_history_without_input=messages[:-1]
    )

    response = rag_chain.invoke(prompt_template_input)

    # @TODO: remove
    print(response)

    response = response["answer"]

    return response

class ChatCompletionResponse(BaseModel):
    text: str

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatCompletionRequest
) -> ChatCompletionResponse:
    if request.rag:
        response = _rag(
            llm=common.llm,
            retriever=common.rag_retriever,
            request=request
        )
    else:
        kwargs = _get_llm_params_kwargs(request)
        messages = list(map(dict, request.messages))
        response = chat_completion(common.llm, messages, **kwargs)

    result = ChatCompletionResponse(
        text=response
    )

    return result
