import os
import glob
import json

from utils import translate, upload_docs

def doc_translate(
    doc: dict[str, str | list],
    lang_from: str,
    lang_to: str
) -> list[dict[str, str | dict[str]]]:
    def _translate(message: str) -> str:
        return translate(message, lang_from, lang_to)

    translated: list[dict[str, str | dict[str]]] = []

    def _append_translated_doc(
        text: str,
        doc_metadata: dict[str],
        metadata: dict[str] = None
    ) -> None:
        if metadata:
            metadata = metadata | doc_metadata
        else:
            metadata = doc_metadata

        text = _translate(text)

        for key, value in metadata.items():
            if isinstance(value, str):
                metadata[key] = _translate(value)

        translated.append(dict(
            text=text,
            metadata=metadata
        ))

    metadata = dict(
        origin=doc["origin"]
    )

    page_content: list[dict[str, str | dict | list]] = doc["page_content"]

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

            doc_metadata = doc_metadata | metadata

            _append_translated_doc(
                text=entry["body"],
                doc_metadata=doc_metadata
            )
        elif keys == {"section_title", "news", "articles", "stray_text"}:
            doc_metadata = dict(
                section_title=entry["section_title"]
            ) | metadata

            for news in entry["news"]:
                assert news.keys() == {"title", "date", "abstract"}

                _append_translated_doc(
                    text=news["abstract"],
                    doc_metadata=doc_metadata,
                    metadata=dict(
                        news_title=news["title"],
                        news_date=news["date"]
                    )
                )

            for i, article in enumerate(entry["articles"]):
                _append_translated_doc(
                    text=article,
                    doc_metadata=doc_metadata,
                    metadata=dict(
                        article_id=i
                    )
                )

            if entry["stray_text"]:
                _append_translated_doc(
                    text=entry["stray_text"],
                    doc_metadata=doc_metadata
                )
        else:
            assert ValueError(f"Invalid 'page_content' keys: {keys}")

    return translated

def main() -> None:
    dump_dir_path = "dump"

    glob_path = os.path.join(dump_dir_path, "*.json")

    file_paths = glob.glob(glob_path)

    if not file_paths:
        raise ValueError(f"No dump files at '{glob_path}'. Run 'scrap.py' first")

    file_paths = sorted(file_paths)

    translated_docs: list[dict[str, str | list]] = []

    for i, file_path in enumerate(file_paths):
        print(">", f"[{i+1}/{len(file_paths)}]", file_path)

        with open(file_path, encoding="utf8") as file:
            data = json.load(file)

        translated = doc_translate(data, lang_from="pl", lang_to="en-US")
        translated_docs += translated

    upload_docs(
        "rag_docs_upload",
        docs=translated_docs
    )

if __name__ == "__main__":
    main()
