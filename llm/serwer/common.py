from llama_cpp import Llama

from pydantic import BaseModel

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from langchain_text_splitters import CharacterTextSplitter

from langchain_core.prompt_values import ChatPromptValue
from langchain_core.retrievers import RetrieverOutputLike
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.vectorstores.qdrant import Qdrant
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.document import Document as LangchainDocument

from langchain.chains.history_aware_retriever import create_history_aware_retriever

from config import config

# @TODO: rename Common
class Common:
    llm: Llama
    embedder: HuggingFaceEmbeddings
    faq_vector_store: dict[str, VectorStore]
    rag_vector_store: VectorStore
    vector_store_client: QdrantClient
    rag_retriever: VectorStoreRetriever
    history_aware_retriever: RetrieverOutputLike

common: Common = Common()

# @TODO: change initialization? i czy `common` jest za każdym importowaniem innym czy tym samym obiektem?
def init_common(cmd_line_args):
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

    common.rag_retriever = common.rag_vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])

    def _invoke_model(prompt: ChatPromptValue) -> str:
        system_prompt = (
            "Given a chat history and the latest user question " +
            "which might reference context in the chat history, formulate a standalone question " +
            "which can be FULLY understood without the chat history. Do NOT answer the question, " +
            "just reformulate it if needed and otherwise return it as is (you act like the user asking the question):"
        )

        messages = _langchain_chat_prompt_to_llama_messages(prompt)
        messages = [f'{message["role"]}: {message["content"]}'
                    for message in messages]
        prompt = "\n".join(messages)

        prompt = f"{system_prompt}\n\n{prompt}\n\nReformulated question:"
        response = common.llm(prompt)
        response = response["choices"][0]["text"]

        print("[History aware retriever]")
        print(" * prompt:", prompt)
        print(" * response:", response)

        return response

    common.history_aware_retriever = create_history_aware_retriever(
        llm=_invoke_model,
        retriever=common.rag_retriever,
        prompt=prompt
    )

def chat_completion(
    llm: Llama,
    messages: list[dict[str, str]],
    **kwargs
) -> str:
    response = llm.create_chat_completion(messages, **kwargs)
    response = response["choices"][0]["message"]["content"]

    print("[Chat completion]")
    print(" * messages:", messages)
    print(" * response:", response)

    return response

def _langchain_chat_prompt_to_llama_messages(
    prompt: ChatPromptValue
) -> list[dict[str, str]]:
    # mapping from langchain to llama2 role (without it the LLM doesn't work properly)
    _message_role_mapping = dict(
        ai="assistant",
        human="user"
    )

    def _convert_message_role(role: str) -> str:
        return _message_role_mapping.get(role, role)

    messages = [
        dict(
            role=_convert_message_role(message.type),
            content=message.content
        )
        for message in prompt.messages
    ]

    return messages

def langchain_chat_completion(
    llm: Llama,
    prompt: ChatPromptValue,
    **kwargs
) -> str:
    messages = _langchain_chat_prompt_to_llama_messages(prompt)
    response = chat_completion(llm, messages, **kwargs)

    return response

class Document(BaseModel):
    text: str
    metadata: dict[str, int | str]

def upload_docs(
    vector_store: VectorStore,
    docs: list[Document]
) -> None:
    docs_upload_config = config.api.docs_upload
    text_splitter = CharacterTextSplitter(
        separator=docs_upload_config.separator,
        chunk_size=docs_upload_config.chunk_size
    )

    docs = [
        LangchainDocument(
            page_content=doc.text,
            metadata=doc.metadata
        )
        for doc in docs
    ]

    docs = text_splitter.split_documents(docs)
    vector_store.add_documents(docs)
