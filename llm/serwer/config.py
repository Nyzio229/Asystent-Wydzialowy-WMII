from pydantic import BaseModel

class Config(BaseModel):
    class CommandLine(BaseModel):
        host: str
        port: int
        chat_format: str
        n_ctx: int
        n_gpu_layers: int

    class RagVectorStore(BaseModel):
        class Client(BaseModel):
            url: str
            api_key: str

        client: Client
        collection_name: str

    class Embed(BaseModel):
        model: str

    class Api(BaseModel):
        class FaqLike(BaseModel):
            collection_name: str
            score_threshold: float

        class Classify(BaseModel):
            model: str

        class RagDocsUpload(BaseModel):
            separator: str
            chunk_size: int

        faq_like: FaqLike
        classify: Classify
        rag_docs_upload: RagDocsUpload

    command_line: CommandLine
    rag_vector_store: RagVectorStore
    embed: Embed
    api: Api

config = Config(
    command_line=Config.CommandLine(
        host="0.0.0.0",
        port=9123,
        chat_format="chatml",
        n_ctx=2048,
        n_gpu_layers=-1
    ),
    rag_vector_store=Config.RagVectorStore(
        client=Config.RagVectorStore.Client(
            url="http://158.75.112.151:6333",
            api_key="MikoAI"
        ),
        collection_name="rag_docs"
    ),
    embed=Config.Embed(
        model="sentence-transformers/all-MiniLM-L6-v2"
    ),
    api=Config.Api(
        faq_like=Config.Api.FaqLike(
            collection_name="asystent_FAQ",
            score_threshold=0.75
        ),
        classify=Config.Api.Classify(
            model="facebook/bart-large-mnli"
        ),
        rag_docs_upload=Config.Api.RagDocsUpload(
            chunk_size=1024,
            separator="\n"
        )
    )
)
