import json

import logging

from typing import Optional

from datetime import datetime

import spacy

from pydantic import BaseModel

from llama_cpp import Llama, LlamaGrammar

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.prompt_values import ChatPromptValue
from langchain_core.retrievers import RetrieverOutputLike
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.docstore.document import Document
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

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
    rag_retriever: VectorStoreRetriever
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

common: Common = Common()

def init_common(cmd_line_args):
    common.nlp = spacy.load("en_core_web_md")

    common.llm = Llama(
        model_path=cmd_line_args.model,
        chat_format=cmd_line_args.chat_format,
        n_ctx=cmd_line_args.n_ctx,
        n_gpu_layers=cmd_line_args.n_gpu_layers,
        verbose=False
    )

    common.embedder = HuggingFaceEmbeddings(
        model_name=config.embed.model
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
        except Exception:
            vector_store_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )

        vector_store = Qdrant(
            client=vector_store_client,
            collection_name=collection_name,
            embeddings=common.embedder
        )

        return vector_store

    common.vector_store_client = vector_store_client

    common.faq_vector_store = {}

    for lang, collection_name in vector_store_config.faq_collection_name.items():
        common.faq_vector_store[lang] = _create_langchain_vector_store(
            collection_name
        )

    common.rag_vector_store = _create_langchain_vector_store(
        vector_store_config.rag_collection_name
    )

    common.rag_retriever = common.rag_vector_store.as_retriever(
        search_kwargs=dict(
            k=10
        )
    )

    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])

    def _invoke_model(prompt: ChatPromptValue) -> str:
        system_prompt = (
            "Given a chat history and the latest user question " +
            "which might reference context in the chat history, formulate a standalone question " +
            "which can be FULLY understood without the chat history. Do NOT answer the question, " +
            "just reformulate it if needed and otherwise return it as is "
            "(you act like the user asking the question):"
        )

        messages = _langchain_chat_prompt_to_llama_messages(prompt)
        messages = [f'{message["role"]}: {message["content"]}'
                    for message in messages]

        prompt = "\n".join(messages)
        prompt = f"{system_prompt}\n\n{prompt}\n\nReformulated question:"

        response = common.llm(
            prompt,
            **common.llm_inference_params.model_dump()
        )

        response = response["choices"][0]["text"]

        logger = logging.getLogger("mikolAI")
        logger.setLevel(logging.DEBUG)
        logger.debug("[History aware retriever]")
        logger.debug(" * prompt: %s", prompt)
        logger.debug(" * response: %s", response)

        return response

    common.history_aware_retriever = create_history_aware_retriever(
        llm=_invoke_model,
        retriever=common.rag_retriever,
        prompt=prompt
    )

def chat_completion(
    llm: Llama,
    messages: list[dict[str, str]],
    llm_inference_params: LLMInferenceParams,
    grammar: Optional[LlamaGrammar] = None
) -> str:
    response = llm.create_chat_completion(
        messages,
        grammar=grammar,
        **llm_inference_params.model_dump()
    )

    response = response["choices"][0]["message"]["content"]

    logger = logging.getLogger("mikolAI")
    logger.setLevel(logging.DEBUG)
    logger.debug("[Chat completion]")
    logger.debug(
        " * messages: %s",
        json.dumps([
            message.copy() | dict(
                content=list(filter(
                    lambda x: x,
                    message["content"].splitlines()
                ))
            )
            for message in messages
        ], ensure_ascii=False, indent=3)
    )
    logger.debug(" * response: %s", response)

    return response

def _convert_langchain_message_role_to_llama(role: str) -> str:
    # mapping from langchain to llama2 role (without it the LLM doesn't work properly)
    _message_role_mapping = dict(
        ai="assistant",
        human="user"
    )

    return _message_role_mapping.get(role, role)

def _langchain_chat_prompt_to_llama_messages(
    prompt: ChatPromptValue
) -> list[dict[str, str]]:
    # mapping from langchain to llama2 role (without it the LLM doesn't work properly)
    messages = [
        dict(
            role=_convert_langchain_message_role_to_llama(message.type),
            content=message.content
        )
        for message in prompt.messages
    ]

    return messages

class Message(BaseModel):
    role: str
    content: str

_SYSTEM_MESSAGE = (
    "Your name is MikołAI and you are a helpful, respectful, friendly and honest personal for students "
    "at Nicolaus Copernicus University (faculty of Mathematics and Computer Science) in Toruń, Poland. "
    "Your main task is responding to students' questions regarding their studies, but you can also engage "
    "in a friendly informal chat. Always answer as helpfully as possible, while being safe. "
    "Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, "
    "or illegal content. If a question does not make any sense, or is not factually coherent, "
    "explain why instead of answering something not correct. "
    "Please ensure that your responses are socially unbiased and positive in nature. "
    "If you don't know the answer to a question, please don't share false information.\n"
    "Please try to keep your answers as concise and short as possible, unless you are "
    "specifically asked for a detailed answer."
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
    extend_system_message: bool = False,
    grammar: Optional[LlamaGrammar] = None
) -> str:
    def _message_mapping(message: Message) -> dict[str, str]:
        role = _convert_langchain_message_role_to_llama(message.role)

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
        llm_inference_params,
        grammar
    )

    return response

def langchain_chat_completion(
    llm: Llama,
    prompt: ChatPromptValue,
    llm_inference_params: LLMInferenceParams
) -> str:
    messages = _langchain_chat_prompt_to_llama_messages(prompt)
    response = chat_completion(llm, messages, llm_inference_params)

    return response

def upload_docs(
    vector_store: VectorStore,
    docs: list[Document],
    ids: Optional[list[str]] = None
) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=100
    )

    docs = text_splitter.split_documents(docs)
    ids = vector_store.add_documents(docs, ids=ids)

    return ids

def log_endpoint_call(
    endpoint: str,
    request: BaseModel,
    result: BaseModel
) -> None:
    logger = logging.getLogger("mikolAI")
    logger.setLevel(logging.DEBUG)

    logger.debug("[endpoint '/%s']", endpoint)

    def _log_model(name: str, model: BaseModel) -> str:
        logger.debug(
            "-> %s:\n%s",
            name,
            model.model_dump_json(indent=3)
        )

    _log_model("request", request)
    _log_model("result", result)
