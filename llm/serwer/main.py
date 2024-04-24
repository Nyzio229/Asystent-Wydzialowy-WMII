import uvicorn

from fastapi import FastAPI

from common import init_common
from command_line import parse_args

from api.routers import (
    chat,
    classify,
    faq,
    faq_like,
    faq_upload,
    rag_docs_upload
)

def create_app() -> FastAPI:
    app = FastAPI()

    routers = [
        chat.router,
        classify.router,
        faq.router,
        faq_like.router,
        faq_upload.router,
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
