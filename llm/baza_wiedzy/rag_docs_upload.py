import os
import glob

from pathlib import Path

from typing import Optional

from pydantic import BaseModel

from faq_upload import fetch_faq

from utils import get_cached_translation, upload_docs, translate

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

def fetch_translated_rag_docs() -> list[dict[str, str]]:
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
            serialize=True
        )

        translated_docs += translated

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
