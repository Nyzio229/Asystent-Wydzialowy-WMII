import os
import glob

import urllib.parse

from pathlib import Path

from typing import Optional

import scrap

from utils import (
    Document,
    read_json,
    get_cached_translation,
    translate_pl_to_en
)

def _get_tags_from_url(url: str) -> list[str]:
    path = urllib.parse.urlparse(url.lower()).path

    path_parts = path[1:].split("/")[1:]

    path_parts.append("wmii")

    tags = list(set(map(
        lambda part: part.replace("-", " "),
        path_parts
    )))

    _TAGS_MAPPING = {
        "kni": "Koło naukowe informatyków (KNI)",
        "knm": "Koło naukowe matematyków (KNM)",
        "wmii": "Wydział Matematyki i Informatyki (WMiI)",
        "laboratorium eksploatacji systemu komputerowego": "Laboratorium eksploatacji systemu komputerowego (LESK)"
    }

    tags = list(map(
        lambda tag: (
            _TAGS_MAPPING[tag]
            if tag in _TAGS_MAPPING
            else tag.capitalize()
        ),
        tags
    ))

    tags.append(
        "Uniwersytet Mikołaja Kopernika w Toruniu (UMK)"
    )

    return tags

def _create_docs(
    scrapped_content: dict[str, str | dict | list]
) -> list[Document]:
    docs: list[Document] = []

    def _append_doc(
        page_content: str,
        doc_metadata: dict[
            str, str | int | list[str]
        ],
        metadata: Optional[dict[str]] = None
    ) -> None:
        if metadata:
            metadata |= doc_metadata
        else:
            metadata = doc_metadata

        doc = Document(
            page_content=page_content,
            metadata=metadata
        )

        docs.append(doc)

    origin = scrapped_content["origin"]

    metadata = dict(
        origin=origin,
        tags=_get_tags_from_url(origin)
    )

    page_content: list[
        dict[str, str | dict | list]
    ] = scrapped_content["page_content"]

    for entry in page_content:
        keys = entry.keys()

        if keys == {
            "title", "body"
        }:
            title = entry["title"]

            if title:
                doc_metadata = dict(
                    title=title
                )
            else:
                doc_metadata = {}

            doc_metadata |= metadata

            _append_doc(
                page_content=entry["body"],
                doc_metadata=doc_metadata
            )
        elif keys == {
            "section_title", "news", "articles", "stray_text"
        }:
            doc_metadata = dict(
                section_title=entry["section_title"]
            ) | metadata

            for news in entry["news"]:
                assert news.keys() == {
                    "title", "date", "abstract"
                }

                _append_doc(
                    page_content=news["abstract"],
                    doc_metadata=doc_metadata,
                    metadata=dict(
                        news_date=news["date"],
                        news_title=news["title"]
                    )
                )

            for i, article in enumerate(
                entry["articles"]
            ):
                _append_doc(
                    page_content=article,
                    doc_metadata=doc_metadata,
                    metadata=dict(
                        article_id=i
                    )
                )

            stray_text = entry["stray_text"]

            if stray_text:
                _append_doc(
                    page_content=stray_text,
                    doc_metadata=doc_metadata
                )
        else:
            raise ValueError(
                f"Unexpected combination of 'page_content' keys: {keys}"
            )

    return docs

def _translate_scrapped_doc(
    doc: Document
) -> Document:
    def _translate(message: str) -> str:
        translated = translate_pl_to_en(message)

        # sometimes DeepL translates university name incorrectly
        translated = translated.replace(
            "University of Krakow",
            "Nicolaus Copernicus University"
        )

        return translated

    metadata = doc.metadata

    page_content = _translate(doc.page_content)

    for key, value in metadata.items():
        if key == "origin":
            continue

        if isinstance(value, str):
            metadata[key] = _translate(value)
        elif isinstance(value, list):
            metadata[key] = list(map(
                _translate, value
            ))

    translated = Document(
        page_content=page_content,
        metadata=metadata
    )

    return translated

def _translate_scrapped_docs(
    docs: list[Document]
) -> list[Document]:
    print("   * Tłumaczenie (pl -> en)...")

    translated = list(map(
        _translate_scrapped_doc, docs
    ))

    return translated

def fetch_scrapped_faculty_webpages() -> list[Document]:
    glob_path = str(
        scrap.get_dump_dir_path() / "*.json"
    )

    file_paths = glob.glob(glob_path)

    if not file_paths:
        raise ValueError((
            f"No files at '{glob_path}'. "
            f"Run '{scrap.__name__}.py' first"
        ))

    translated_docs: list[Document] = []

    for i, file_path in enumerate(file_paths):
        print(">", f"[{i+1}/{len(file_paths)}]", file_path)

        file_path = Path(file_path)

        file_name = file_path.name

        parent_path = file_path.parent.parent

        translated = get_cached_translation(
            pl_path=parent_path / "pl" / file_name,
            cache_path=parent_path / "translated" / file_name,
            translator=_translate_scrapped_docs,
            model_type=Document,
            create_pl_data=lambda: _create_docs(
                read_json(file_path)
            )
        )

        translated_docs += translated

    return translated_docs
