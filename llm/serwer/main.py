import uvicorn

from fastapi import FastAPI

from command_line import parse_args

from common import common, init_common

from api.routers import (
    chat,
    classify,
    faq_like,
    rag_docs_upload
)

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

    uvicorn.run(app, port=args.port, host=args.host)

if __name__ == "__main__":
    main()
