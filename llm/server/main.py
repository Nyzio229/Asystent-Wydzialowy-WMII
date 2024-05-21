import sys
import logging

import uvicorn

from fastapi import FastAPI

from common import LOGGER, common

from command_line import parse_args

from api.routers import (
    chat,
    classify,
    faq,
    faq_like,
    upload_faq,
    upload_rag_docs
)

def create_app() -> FastAPI:
    app = FastAPI()

    routers = [
        chat.router,
        classify.router,
        faq.router,
        faq_like.router,
        upload_faq.router,
        upload_rag_docs.router
    ]

    for router in routers:
        app.include_router(router)

    return app

def setup_logger():
    LOGGER.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("logs.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(stdout_handler)

def main() -> None:
    setup_logger()

    args = parse_args()

    common.initialize_from_cmd_line_args(
        args
    )

    app = create_app()

    uvicorn.run(
        app,
        port=args.port,
        host=args.host
    )

if __name__ == "__main__":
    main()
