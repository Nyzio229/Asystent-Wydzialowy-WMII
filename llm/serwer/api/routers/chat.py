from fastapi import APIRouter

from pydantic import BaseModel

from llama_cpp import Llama

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from common import (
    common,
    chat_with_default_system_message,
    langchain_chat_completion,
    log_endpoint_call,
    LLMInferenceParams,
    Message,
    SYSTEM_MESSAGE
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
    system_message = f"{SYSTEM_MESSAGE}\n\n{{context}}"

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
        prompt=prompt
    )

    rag_chain = create_retrieval_chain(
        retriever=common.history_aware_retriever,
        combine_docs_chain=chat_chain
    )

    messages = [(message.role, message.content)
                for message in messages]

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
    if request.rag:
        response = _rag(
            common.llm,
            request.messages,
            request.llm_inference_params
        )
    else:
        response = chat_with_default_system_message(
            common.llm,
            request.messages,
            request.llm_inference_params
        )

    result = ChatResponse(
        text=response
    )

    log_endpoint_call("chat", request, result)

    return result
