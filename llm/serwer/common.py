from llama_cpp import Llama

from qdrant_client import QdrantClient

from transformers import pipeline, Pipeline

from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from config import config

# @TODO: rename Common
class Common:
    llm: Llama
    classifier: Pipeline
    embedder: HuggingFaceEmbeddings
    rag_vector_store: VectorStore
    vector_store_client: QdrantClient
    rag_retriever: VectorStoreRetriever

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
    common.vector_store_client = QdrantClient(
        url=vector_store_client_config.url,
        api_key=vector_store_client_config.api_key
    )

    common.rag_vector_store = Qdrant(
        client=common.vector_store_client,
        collection_name=vector_store_config.rag_collection_name,
        embeddings=common.embedder
    )

    common.rag_retriever = common.rag_vector_store.as_retriever()

    common.classifier = pipeline(
        "zero-shot-classification",
        model=config.api.classify.model
    )
