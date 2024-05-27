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
    tags_metadata = [
        dict(
            name="classify",
            description=(
                "Kategoryzacja zapytania użytkownika (kategorie: 'chat', 'navigation')."
            )
        ),
        dict(
            name="faq_like",
            description=(
                "Zwraca identyfikatory pytań z bazy danych FAQ podobnych do zadanego."
            )
        ),
        dict(
            name="faq",
            description=(
                "Zwraca pytania z bazy danych FAQ i odpowiedź na nie dla danych identyfikatorów."
            )
        ),
        dict(
            name="chat",
            description=(
                "Czat z dużym modelem językowym."
            )
        ),
        dict(
            name="upload_faq",
            description=(
                "Przesyłanie pytań i odpowiedzi do bazy danych FAQ."
            )
        ),
        dict(
            name="upload_rag_docs",
            description=(
                "Przesyłanie dokumentów, z których duży model językowy "
                "korzysta realizując RAG, do wektorowej bazy danych."
            )
        )
    ]

    app = FastAPI(
        tags_metadata=tags_metadata
    )

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
