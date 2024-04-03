from fastapi import FastAPI

from llama_cpp import Llama

from qdrant_client import QdrantClient

from transformers import pipeline, Pipeline

from sentence_transformers import SentenceTransformer

from config import config

# @TODO: rename Common
class Common:
    llm: Llama
    qdrant_client: QdrantClient
    classifier: Pipeline
    embedder: SentenceTransformer

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

    client_config = config["vector_store"]["client"]
    common.qdrant_client = QdrantClient(
        url=client_config["url"],
        api_key=client_config["api_key"]
    )

    common.classifier = pipeline(
        "zero-shot-classification",
        model=config["api"]["classify"]["model"]
    )

    common.embedder = SentenceTransformer(config["embed"]["model"])
