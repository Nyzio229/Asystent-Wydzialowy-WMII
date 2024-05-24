from pydantic import BaseModel

class Config(BaseModel):
    class CommandLine(BaseModel):
        host: str
        port: int
        n_ctx: int
        n_gpu_layers: int

    class VectorStore(BaseModel):
        class Client(BaseModel):
            url: str
            api_key: str

        client: Client

        rag_collection_name: str
        faq_collection_for_lang: dict[str, str]

    class Embed(BaseModel):
        model: str

    class Api(BaseModel):
        class FaqLike(BaseModel):
            score_threshold: float

        faq_like: FaqLike

    command_line: CommandLine
    vector_store: VectorStore
    embed: Embed
    api: Api

config = Config(
    command_line=Config.CommandLine(
        host="0.0.0.0",
        port=9123,
        n_ctx=0,
        n_gpu_layers=-1
    ),
    vector_store=Config.VectorStore(
        client=Config.VectorStore.Client(
            url="http://158.75.112.151:6333",
            api_key="BsAH4N7HZ4sZ353ImgG1P0ZomqMxq5h4"
        ),
        faq_collection_for_lang=dict(
            en="faq_en",
            pl="faq_pl"
        ),
        rag_collection_name="rag_docs"
    ),
    embed=Config.Embed(
        model="Alibaba-NLP/gte-base-en-v1.5"
    ),
    api=Config.Api(
        faq_like=Config.Api.FaqLike(
            score_threshold=0.75
        )
    )
)
