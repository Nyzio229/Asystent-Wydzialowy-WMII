import os
import glob

from pathlib import Path

from typing import Optional

from pydantic import BaseModel

from upload_faq import fetch_faq, FaqEntry

from utils import get_cached_translation, upload_docs, translate

from fetch_misc_docs import (
    get_academic_year_organization,
    get_umk_wiki_page
)

class Document(BaseModel):
    page_content: str
    metadata: Optional[dict[str, str | int]] = None

def doc_translate(
    doc: dict[str, str | list],
    lang_from: str,
    lang_to: str
) -> list[Document]:
    def _translate(message: str) -> str:
        return translate(message, lang_from, lang_to)

    translated: list[Document] = []

    def _append_translated_doc(
        page_content: str,
        doc_metadata: dict[str],
        metadata: Optional[dict[str]] = None
    ) -> None:
        if metadata:
            metadata |= doc_metadata
        else:
            metadata = doc_metadata

        page_content = _translate(page_content)

        for key, value in metadata.items():
            if isinstance(value, str):
                metadata[key] = _translate(value)

        doc = Document(
            page_content=page_content,
            metadata=metadata
        )

        translated.append(doc)

    metadata = dict(
        origin=doc["origin"]
    )

    page_content: list[
        dict[str, str | dict | list]
    ] = doc["page_content"]

    print(f"   * Tłumaczenie ('{lang_from}' -> '{lang_to}')...")

    for entry in page_content:
        keys = entry.keys()

        if keys == {"title", "body"}:
            title = entry["title"]

            if title:
                doc_metadata = dict(
                    title=title
                )
            else:
                doc_metadata = {}

            doc_metadata |= metadata

            _append_translated_doc(
                page_content=entry["body"],
                doc_metadata=doc_metadata
            )
        elif keys == {"section_title", "news", "articles", "stray_text"}:
            doc_metadata = dict(
                section_title=entry["section_title"]
            ) | metadata

            for news in entry["news"]:
                assert news.keys() == {"title", "date", "abstract"}

                _append_translated_doc(
                    page_content=news["abstract"],
                    doc_metadata=doc_metadata,
                    metadata=dict(
                        news_title=news["title"],
                        news_date=news["date"]
                    )
                )

            for i, article in enumerate(entry["articles"]):
                _append_translated_doc(
                    page_content=article,
                    doc_metadata=doc_metadata,
                    metadata=dict(
                        article_id=i
                    )
                )

            if entry["stray_text"]:
                _append_translated_doc(
                    page_content=entry["stray_text"],
                    doc_metadata=doc_metadata
                )
        else:
            assert ValueError(f"Invalid 'page_content' keys: {keys}")

    return translated

def get_scrapped_webpages_docs() -> list[Document]:
    dump_dir_path = os.path.join(
        "scrapowane_strony_wydzialowe",
        "dump"
    )

    glob_path = os.path.join(dump_dir_path, "*.json")

    file_paths = glob.glob(glob_path)

    if not file_paths:
        raise ValueError(f"No dump files at '{glob_path}'. Run 'scrap.py' first")

    lang_from = "pl"
    lang_to = "en-US"

    translated_docs: list[Document] = []

    for i, file_path in enumerate(file_paths):
        print(">", f"[{i+1}/{len(file_paths)}]", file_path)

        file_path = Path(file_path)
        translated = get_cached_translation(
            pl_path=file_path,
            cache_path=file_path.parent.parent / "translated" / file_path.name,
            translator=lambda doc: doc_translate(doc, lang_from, lang_to),
            model_type=Document,
            deserialize_pl=False,
            verify_translated_data_size=False
        )

        translated_docs += translated

    return translated_docs

def get_umk_wiki_page_doc() -> Document:
    wp = get_umk_wiki_page()

    doc = Document(
        metadata=dict(
            origin=wp.url
        ),
        page_content=wp.page_content
    )

    return doc

def get_academic_year_organization_doc() -> Document:
    ayo = get_academic_year_organization()

    doc = Document(
        metadata=dict(
            origin=ayo.remote_file_path
        ),
        page_content=ayo.file_content
    )

    return doc

def get_faq_docs() -> list[Document]:
    faq = fetch_faq(
        with_pl=False,
        serialize=False
    )

    n_faq_entries = len(faq)

    def _faq_entry_to_doc(idx: int, faq_entry: FaqEntry) -> Document:
        question = faq_entry.question
        answer = faq_entry.answer

        page_content = f"Q: {question}\nA: {answer}"

        doc = Document(
            page_content=page_content,
            metadata=dict(
                origin=f"FAQ ({idx+1}/{n_faq_entries})"
            )
        )

        return doc

    faq = list(map(
        lambda pair: _faq_entry_to_doc(*pair),
        enumerate(faq)
    ))

    return faq

def main() -> None:
    downloading_texts_with_getters = (
        ("zescrapowanych danych ze stron wydziałowych", get_scrapped_webpages_docs),
        ("FAQ", get_faq_docs),
        ("organizacji roku akademickiego", get_academic_year_organization_doc),
        ("strony UMK na wikipedii", get_umk_wiki_page_doc)
    )

    print("Pobieranie:")

    docs: list[Document] = []

    for i, (text, doc_getter) in enumerate(downloading_texts_with_getters):
        print(f"\n{i+1}. {text}...")

        doc = doc_getter()

        if isinstance(doc, Document):
            doc = [doc]

        docs += doc

    docs = list(map(
        lambda doc: doc.model_dump(),
        docs
    ))

    print("\nPrzesyłanie do bazy wektorowej...")

    upload_docs(
        "rag_docs_upload",
        docs=docs
    )

if __name__ == "__main__":
    main()
