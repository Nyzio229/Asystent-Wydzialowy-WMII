from llama_cpp import Llama

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from transformers import pipeline, Pipeline

from langchain_core.prompt_values import ChatPromptValue
from langchain_core.retrievers import RetrieverOutputLike
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.vectorstores.qdrant import Qdrant
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from langchain.chains.history_aware_retriever import create_history_aware_retriever

from config import config

# @TODO: rename Common
class Common:
    llm: Llama
    classifier: Pipeline
    embedder: HuggingFaceEmbeddings
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

    common.classifier = pipeline(
        "zero-shot-classification",
        model=config.api.classify.model
    )

    vector_store_config = config.vector_store
    vector_store_client_config = vector_store_config.client
    vector_store_client = QdrantClient(
        url=vector_store_client_config.url,
        api_key=vector_store_client_config.api_key
    )

    rag_collection_name = vector_store_config.rag_collection_name

    try:
        vector_store_client.get_collection(rag_collection_name)
    except Exception:
        vector_store_client.create_collection(
            collection_name=rag_collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

    common.vector_store_client = vector_store_client

    common.rag_vector_store = Qdrant(
        client=vector_store_client,
        collection_name=rag_collection_name,
        embeddings=common.embedder
    )

    common.rag_retriever = common.rag_vector_store.as_retriever()

    system_prompt = (
        "Given a chat history and the latest user question " +
        "which might reference context in the chat history, formulate a standalone question " +
        "which can be understood without the chat history. Do NOT answer the question, " +
        "just reformulate it if needed and otherwise return it as is."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    common.history_aware_retriever = create_history_aware_retriever(
        llm=lambda prompt: langchain_chat_completion(common.llm, prompt),
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

    return response

def langchain_chat_completion(
    llm: Llama,
    prompt: ChatPromptValue,
    **kwargs
) -> str:
    messages = [
        dict(
            role=message.type,
            content=message.content
        )
        for message in prompt.messages
    ]

    response = chat_completion(llm, messages, **kwargs)

    print(response)

    return response
