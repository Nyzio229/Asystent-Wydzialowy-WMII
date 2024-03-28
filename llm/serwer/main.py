import uvicorn

from fastapi import FastAPI

from rag.rag import rag

from command_line import parse_args

from common import common, init_common

from api.routers import chat, classify, faq_like, rag_docs_upload

def create_app() -> FastAPI:
    app = FastAPI()

    routers = [
        chat.router,
        classify.router,
        faq_like.router,
        rag_docs_upload.router
    ]

    for router in routers:
        app.include_router(router)

    return app

def main():
    args = parse_args()

    init_common(args)

    app = create_app()

    from pydantic import BaseModel
    class RagRequest(BaseModel):
        query: str
    class RagResult(BaseModel):
        response: str
    from llama_index.llms.llama_cpp import LlamaCPP
    @app.post("/rag")
    async def _rag(request: RagRequest):
        response = rag(
            llm=LlamaCPP(model_path="vicuna-hf_13b_v1.5/ggml_fp16.gguf"),
            embedder=common.embedder,
            query=request.query
        )

        result = RagResult(response=response)

        return result

    uvicorn.run(app, port=args.port, host=args.host)

if __name__ == "__main__":
    main()
