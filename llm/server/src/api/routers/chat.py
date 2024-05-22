from llama_cpp import Llama

from fastapi import APIRouter

from pydantic import BaseModel

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
    doc_sep = f"\n{'-'*15}\nInformation about the faculty:\n\n"

    system_message = (
        f"{get_extended_system_message()}\n\n"
        "Here is information fetched from the faculty's websites that contains "
        "reliable facts that may help you provide a better (and factually correct) "
        "answer (don't let the user know that this information is provided to you, "
        "but you can say that you do have access to data from some of faculty's websites) "
        "(if none of the information answers the question then just say that you don't "
        "know the answer):"
        f"{doc_sep}{{context}}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])


    messages = messages.copy()

    # insert a system message at the beginning
    # so that the history aware retriever reformulates the user's question
    # likely adding the faculty and university name (which should help
    # get a more accurate embedding)
    messages.insert(0, Message(
        role="system",
        content=(
            "Your name is MikoAI and you are an AI assistant for students at "
            "Nicolaus Copernicus University (UMK), "
            "faculty of Mathematics and Computer Science (WMiI) "
            "in Toruń, Poland."
        )
    ))

    def _invoke_llm(prompt: ChatPromptTemplate) -> str:
        # skip the newly added system message (that was
        # only used for user query reformulation purposes)
        # (it has index 1 because the original system message
        # is the first)
        prompt.messages.pop(1)

        response = langchain_chat_completion(
            llm, prompt, llm_inference_params
        )

        return response

    chat_chain = create_stuff_documents_chain(
        llm=_invoke_llm,
        prompt=prompt,
        document_separator=doc_sep
    )

    rag_chain = create_retrieval_chain(
        retriever=common.history_aware_retriever,
        combine_docs_chain=chat_chain
    )

    input_message = messages.pop()

    messages = [
        (message.role, message.content)
        for message in messages
    ]

    prompt_template_input = dict(
        input=input_message.content,
        chat_history=messages
    )

    response = rag_chain.invoke(prompt_template_input)
    response = response["answer"]

    return response

class ChatResult(BaseModel):
    text: str

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest
) -> ChatResult:
    chat_args = (
        common.llm,
        request.messages,
        request.llm_inference_params
    )

    if request.rag:
        response = _rag(*chat_args)
    else:
        response = chat_with_default_system_message(
            *chat_args, extend_system_message=True
        )

    response = response.strip()

    result = ChatResult(
        text=response
    )

    log_endpoint_call("chat", request, result)

    return result
