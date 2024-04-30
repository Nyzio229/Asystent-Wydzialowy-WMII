import os
import glob
import json

from pathlib import Path

from typing import Optional

from langchain_community.docstore.document import Document

from faq_upload import fetch_faq

from utils import get_cached_translation, upload_docs, translate

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

def fetch_translated_rag_docs() -> list[dict[str, str]]:
    dump_dir_path = os.path.join(
        "scrapowane_strony_wydzialowe",
        "dump"
    )

    glob_path = os.path.join(dump_dir_path, "*.json")

    file_paths = glob.glob(glob_path)

    if not file_paths:
        raise ValueError(f"No dump files at '{glob_path}'. Run 'scrap.py' first")

    def _serialize_docs(
        docs: list[Document]
    ) -> list[dict[str, str]]:
        return [
            dict(
                page_content=doc.page_content,
                metadata=doc.metadata
            )
            for doc in docs
        ]

    translated_docs: list[Document] = []

    for i, file_path in enumerate(file_paths):
        print(">", f"[{i+1}/{len(file_paths)}]", file_path)

        with open(file_path, encoding="utf8") as file:
            data = json.load(file)

        lang_from = "pl"
        lang_to = "en-US"

        print(f"   * Tłumaczenie ({lang_from} -> {lang_to})...")

        file_path = Path(file_path)
        cache_path = file_path.parent.parent / "translated" / file_path.name
        translated = get_cached_translation(
            cache_path=cache_path,
            translator=lambda: doc_translate(data, lang_from, lang_to),
            serializer=_serialize_docs,
            deserializer=lambda serialized: [
                Document(
                    page_content=doc["page_content"],
                    metadata=doc["metadata"]
                )
                for doc in serialized
            ]
        )

        translated_docs += translated

    translated_docs = list(map(_serialize_docs, translated_docs))

    return translated_docs

def fetch_translated_faq() -> list[dict[str, str]]:
    _, translated_faq = fetch_faq()

    n_faq_entries = len(translated_faq)

    def _faq_entry_mapper(idx: int, faq_entry: dict[str, str]) -> dict[str, str]:
        question = faq_entry["question"]
        answer = faq_entry["answer"]

        page_content = f"Q: {question}\nA: {answer}"

        mapped_faq_entry = dict(
            page_content=page_content,
            metadata=dict(
                origin=f"FAQ ({idx+1}/{n_faq_entries})"
            )
        )

        return mapped_faq_entry

    translated_faq = list(map(lambda pair: _faq_entry_mapper(*pair), enumerate(translated_faq)))

    return translated_faq

def main() -> None:
    print("Pobieranie zescrapowanych danych ze stron wydziałowych...")

    translated_rag_docs = fetch_translated_rag_docs()

    print("\nPobieranie FAQ...")

    translated_faq = fetch_translated_faq()

    docs = translated_rag_docs + translated_faq

    print("\nPrzesyłanie do bazy wektorowej...")

    upload_docs(
        "rag_docs_upload",
        docs=docs
    )

if __name__ == "__main__":
    main()
