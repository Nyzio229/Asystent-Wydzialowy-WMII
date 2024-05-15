import os

import re

from pathlib import Path

from typing import Optional

from urllib.parse import unquote

import pypdf

import requests

import wikipedia

from pydantic import BaseModel

from scrap import soup_for

from utils import get_cached_translation, get_misc_docs_file_path, translate

def _get_academic_year_organization_file_path() -> tuple[
    str, Path, bool
]:
    base_url = "https://www.umk.pl/uczelnia/dokumenty/rok_akademicki"

    soup = soup_for(base_url)

    latest_year: int = None
    latest_pdf_name: str = None

    for link in soup.find_all("a"):
        href: Optional[str] = link.get("href", None)

        if not href or not href.endswith(".pdf"):
            continue

        year = int(href[-8:-4])

        if not latest_pdf_name or year > latest_year:
            latest_year = year
            latest_pdf_name = href

    file_path = get_misc_docs_file_path(
        os.path.join(
            "organizacja_roku_akademickiego",
            f"{latest_year}.pdf"
        )
    )

    remote_file_path = f"{base_url}/{latest_pdf_name}"

    if file_path.exists():
        return remote_file_path, file_path, True

    with open(file_path, "wb") as file:
        response = requests.get(
            remote_file_path,
            timeout=10
        )

        response.raise_for_status()

        file.write(response.content)

    return remote_file_path, file_path, False

class AcademicYearOrganization(BaseModel):
    file_content: str
    remote_file_path: str

def _translate(message: str) -> str:
    return translate(message, "pl", "en-US")

def _fix_whitespaces(string: str) -> str:
    # zamień 2 lub więcej spacji na 1
    string = re.sub(" +", " ", string)
    # zamień spację + \n na \n
    string = re.sub(" \n", "\n", string)
    # zamień więcej niż 1 \n na \n
    string = re.sub("\n+", "\n", string)
    # zamień \n + spacja na \n
    string = re.sub("\n ", "\n", string)

    return string

def get_academic_year_organization() -> AcademicYearOrganization:
    remote_file_path, file_path, existed = _get_academic_year_organization_file_path()

    def _create_pl_data() -> AcademicYearOrganization:
        pdf_reader = pypdf.PdfReader(file_path)

        file_content = "\n".join(map(
            lambda page: page.extract_text(extraction_mode="layout"),
            pdf_reader.pages
        ))

        file_content = _fix_whitespaces(file_content)

        file_content = file_content.strip()

        ayo = AcademicYearOrganization(
            remote_file_path=remote_file_path,
            file_content=file_content
        )

        return ayo

    dir_path = file_path.parent

    def _translate_ayo(ayo: AcademicYearOrganization) -> AcademicYearOrganization:
        return ayo.model_copy(
            update=dict(
                file_content=_translate(ayo.file_content)
            )
        )

    translated = get_cached_translation(
        pl_path=dir_path / "pl.json",
        cache_path=dir_path / "translated.json",
        translator=_translate_ayo,
        model_type=AcademicYearOrganization,
        as_list=False,
        with_pl=False,
        overwrite_existing=not existed,
        create_pl_data=_create_pl_data
    )

    return translated

class WikipediaPage(BaseModel):
    url: str
    page_content: str

def get_umk_wiki_page() -> WikipediaPage:
    page_title = "Uniwersytet_Mikołaja_Kopernika_w_Toruniu"

    dir_path = get_misc_docs_file_path(
        os.path.join(
            "wikipedia",
            page_title
        ),
        is_dir=True
    )

    def _create_pl_data() -> WikipediaPage:
        wikipedia.set_lang("pl")

        page = wikipedia.page(page_title)
        page_content = _fix_whitespaces(page.content)

        wp = WikipediaPage(
            url=unquote(page.url),
            page_content=page_content
        )

        return wp

    def _translate_wp(wp: WikipediaPage) -> WikipediaPage:
        return wp.model_copy(
            update=dict(
                page_content=_translate(wp.page_content)
            )
        )

    translated = get_cached_translation(
        pl_path=dir_path / "pl.json",
        cache_path=dir_path / "translated.json",
        translator=_translate_wp,
        model_type=WikipediaPage,
        as_list=False,
        with_pl=False,
        create_pl_data=_create_pl_data
    )

    return translated
