import json

import logging

from typing import Optional

from datetime import datetime

import spacy

from pydantic import BaseModel

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from qdrant_client.http.exceptions import UnexpectedResponse

from llama_cpp import Llama, ChatCompletionRequestMessage

from langchain.storage import LocalFileStore

from langchain_core.vectorstores import VectorStore

from langchain.retrievers.multi_vector import MultiVectorRetriever

from langchain_core.retrievers import RetrieverOutputLike

from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.vectorstores.qdrant import Qdrant
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from langchain_core.retrievers import RetrieverOutputLike
from langchain.chains.history_aware_retriever import create_history_aware_retriever

from config import config

class LLMInferenceParams(BaseModel):
    temperature: float
    top_p: float
    top_k: int
    min_p: float
    typical_p: float
    presence_penalty: float
    frequency_penalty: float
    repeat_penalty: float
    tfs_z: float
    mirostat_mode: int
    mirostat_tau: float
    mirostat_eta: float
    max_tokens: Optional[int] = None

class Common:
    llm: Llama
    nlp: spacy.language.Language
    embedder: HuggingFaceEmbeddings
    faq_vector_store: dict[str, VectorStore]
    rag_vector_store: VectorStore
    vector_store_client: QdrantClient
    rag_retriever: MultiVectorRetriever
    history_aware_retriever: RetrieverOutputLike

    llm_inference_params = LLMInferenceParams(
        temperature=0.2,
        top_p=0.95,
        top_k=40,
        min_p=0.05,
        typical_p=1,
        presence_penalty=0,
        frequency_penalty=0,
        repeat_penalty=1.1,
        tfs_z=1,
        mirostat_mode=0,
        mirostat_tau=5,
        mirostat_eta=0.1,
        max_tokens=None
    )

    def invoke_llm(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        inference_params = self.llm_inference_params.model_dump()
        inference_params |= kwargs

        response = self.llm(
            prompt, **inference_params
        )

        response = response["choices"][0]["text"]

        return response

LOGGER_NAME = "mikoAI"
LOGGER = logging.getLogger(LOGGER_NAME)

common: Common = Common()

def init_common(cmd_line_args):
    common.nlp = spacy.load("en_core_web_md")

    common.llm = Llama(
        model_path=cmd_line_args.model,
        n_ctx=cmd_line_args.n_ctx,
        n_gpu_layers=cmd_line_args.n_gpu_layers,
        chat_format="chatml",
        verbose=False
    )

    common.embedder = HuggingFaceEmbeddings(
        model_name=config.embed.model,
        model_kwargs=dict(
            trust_remote_code=True
        )
    )

    vector_store_config = config.vector_store
    vector_store_client_config = vector_store_config.client
    vector_store_client = QdrantClient(
        url=vector_store_client_config.url,
        api_key=vector_store_client_config.api_key
    )

    def _create_langchain_vector_store(collection_name: str) -> VectorStore:
        try:
            vector_store_client.get_collection(collection_name)
        except UnexpectedResponse:
            vector_store_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=768,
                    distance=Distance.COSINE
                )
            )

        vector_store = Qdrant(
            client=vector_store_client,
            collection_name=collection_name,
            embeddings=common.embedder
        )

        return vector_store

    common.faq_vector_store = {}

    common.vector_store_client = vector_store_client

    for lang, collection_name in (
        vector_store_config.faq_collection_for_lang.items()
    ):
        common.faq_vector_store[lang] = _create_langchain_vector_store(
            collection_name
        )

    rag_collection_name = vector_store_config.rag_collection_name

    common.rag_vector_store = _create_langchain_vector_store(
        rag_collection_name
    )

    common.rag_retriever = MultiVectorRetriever(
        vectorstore=common.rag_vector_store,
        byte_store=LocalFileStore(
            f"{rag_collection_name}_parent_file_store"
        ),
        search_kwargs=dict(
            k=5
        )
    )

    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])

    def _summarize_chat_history(prompt: ChatPromptValue) -> str:
        system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be FULLY "
            "understood without the chat history. "
            "Do NOT answer the question, just reformulate it "
            "if needed and otherwise return it as is "
            "(you act like the user asking the question):"
        )

        messages = _langchain_chat_prompt_to_llama_messages(prompt)
        messages = [f'{message["role"]}: {message["content"]}'
                    for message in messages]

        prompt = "\n".join(messages)
        prompt = f"{system_prompt}\n\n{prompt}\n\nReformulated question:"

        summary = common.invoke_llm(prompt)

        LOGGER.setLevel(logging.DEBUG)

        LOGGER.debug("[History aware retriever]")
        LOGGER.debug(" * prompt: %s", prompt)
        LOGGER.debug(" * summary: %s", summary)

        return summary

    common.history_aware_retriever = create_history_aware_retriever(
        llm=_summarize_chat_history,
        retriever=common.rag_retriever,
        prompt=prompt
    )

def chat_completion(
    llm: Llama,
    messages: list[ChatCompletionRequestMessage],
    llm_inference_params: LLMInferenceParams
) -> str:
    response = llm.create_chat_completion(
        messages,
        **llm_inference_params.model_dump()
    )

    response = response["choices"][0]["message"]["content"]

    LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug("[Chat completion]")

    LOGGER.debug(
        " * messages: %s",
        json.dumps([
            message | dict(
                content=list(filter(
                    lambda x: x,
                    message["content"].splitlines()
                ))
            )
            for message in messages
        ], ensure_ascii=False, indent=3)
    )

    LOGGER.debug(" * response: %s", response)

    return response

def _convert_langchain_message_role_to_llama(role: str) -> str:
    # mapping from langchain to llama2 role
    # (without it the LLM doesn't work properly)
    _message_role_mapping = dict(
        ai="assistant",
        human="user"
    )

    return _message_role_mapping.get(role, role)

def _langchain_chat_prompt_to_llama_messages(
    prompt: ChatPromptValue
) -> list[dict[str, str]]:
    # mapping from langchain to llama2 role
    # (without it the LLM doesn't work properly)
    messages = [
        dict(
            role=_convert_langchain_message_role_to_llama(
                message.type
            ),
            content=message.content
        )
        for message in prompt.messages
    ]

    return messages

class Message(BaseModel):
    role: str
    content: str

_SYSTEM_MESSAGE = (
    "Your name is MikoAI and you are a helpful, respectful, "
    "friendly and honest personal assistant for students at "
    "Nicolaus Copernicus University (UMK), faculty of "
    "Mathematics and Computer Science (WMiI) in Toruń, Poland. "
    "Your main task is responding to students' questions regarding "
    "their studies, but you can also engage in a friendly informal chat. "
    "Always answer as helpfully as possible, while being safe. "
    "Your answers should not include any harmful, unethical, racist, "
    "sexist, toxic, dangerous, or illegal content. If a question "
    "does not make any sense, or is not factually coherent, "
    "explain why instead of answering something not correct. "
    "Please ensure that your responses are socially unbiased "
    "and positive in nature. If you don't know the answer "
    "to a question, please don't share false information. "
    "Please try to keep your answers as concise and short "
    "as possible, unless you are specifically asked for a detailed answer."
)

def get_extended_system_message() -> str:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%A, %d %B %Y")

    system_message = (
        f"{_SYSTEM_MESSAGE}\n\n"
        f"Today's date: {current_date}\n"
        f"Current time: {current_time}"
    )

    return system_message

def chat_with_default_system_message(
    llm: Llama,
    messages: list[Message],
    llm_inference_params: LLMInferenceParams,
    extend_system_message: bool = False
) -> str:
    def _message_mapping(message: Message) -> dict[str, str]:
        role = _convert_langchain_message_role_to_llama(
            message.role
        )

        return dict(
            role=role,
            content=message.content
        )

    system_message = (
        get_extended_system_message()
        if extend_system_message else _SYSTEM_MESSAGE
    )

    system_message = Message(
        role="system",
        content=system_message
    )

    messages = [system_message] + messages
    messages = list(map(_message_mapping, messages))

    response = chat_completion(
        llm,
        messages,
        llm_inference_params
    )

    return response

def langchain_chat_completion(
    llm: Llama,
    prompt: ChatPromptValue,
    llm_inference_params: LLMInferenceParams
) -> str:
    messages = _langchain_chat_prompt_to_llama_messages(
        prompt
    )

    response = chat_completion(
        llm, messages, llm_inference_params
    )

    return response

def log_endpoint_call(
    endpoint: str,
    request: BaseModel,
    result: BaseModel
) -> None:
    LOGGER.setLevel(logging.DEBUG)

    LOGGER.debug("[endpoint '/%s']", endpoint)

    def _log_model(name: str, model: BaseModel) -> str:
        LOGGER.debug(
            "-> %s:\n%s",
            name,
            model.model_dump_json(indent=3)
        )

    _log_model("request", request)
    _log_model("result", result)
