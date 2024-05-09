import re

from fastapi import APIRouter

from pydantic import BaseModel

from llama_cpp import Llama

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common import (
    common,
    chat_with_default_system_message,
    get_extended_system_message,
    langchain_chat_completion,
    log_endpoint_call,
    LLMInferenceParams,
    Message
)

class ChatRequest(BaseModel):
    messages: list[Message]
    rag: bool = True
    llm_inference_params: LLMInferenceParams = common.llm_inference_params

def _rag(
    llm: Llama,
    messages: list[Message],
    llm_inference_params: LLMInferenceParams
) -> str:
    doc_sep = f"\n{'-'*15}\nAdditional information about the faculty:\n\n"

    system_message = (
        f"{get_extended_system_message()}\n\n"
        "Here is information fetched from the faculty websites that contains "
        "reliable facts that may help you provide a better (and factually correct) answer "
        "(if some information is missing then let the user know that you don't know the answer or "
        "don't have access to the specific data):"
        f"{doc_sep}{{context}}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])

    chat_chain = create_stuff_documents_chain(
        llm=lambda prompt: langchain_chat_completion(
            llm,
            prompt,
            llm_inference_params
        ),
        prompt=prompt,
        document_separator=doc_sep
    )

    rag_chain = create_retrieval_chain(
        retriever=common.history_aware_retriever,
        combine_docs_chain=chat_chain
    )

    messages = [
        (message.role, message.content)
        for message in messages
    ]

    prompt_template_input = dict(
        input=messages[-1][1],
        chat_history=messages[:-1]
    )

    response = rag_chain.invoke(prompt_template_input)
    response = response["answer"]

    return response

class ChatResponse(BaseModel):
    text: str

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest
) -> ChatResponse:
    args = (
        common.llm,
        request.messages,
        request.llm_inference_params
    )

    if request.rag:
        response = _rag(*args)
    else:
        response = chat_with_default_system_message(
            *args, extend_system_message=True
        )

    response = re.sub("\n+", "\n", response)
    response = response.strip()

    result = ChatResponse(
        text=response
    )

    log_endpoint_call("chat", request, result)

    return result
