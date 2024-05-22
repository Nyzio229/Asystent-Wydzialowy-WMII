import os
import json

from pathlib import Path

from typing import Callable, Type, TypeVar, Optional

import requests

from pydantic import BaseModel

class Config(BaseModel):
    docs_upload_host: str
    translation_host: str

_config = Config(
    docs_upload_host="http://158.75.112.151:9123",
    translation_host="https://ec1e-188-146-248-103.ngrok-free.app"
)

class Document(BaseModel):
    page_content: str
    metadata: dict[
        str, str | int | list[str]
    ] = {}

def make_dir(path: Path) -> None:
    path.mkdir(
        parents=True, exist_ok=True
    )

def translate(
    message: str,
    lang_from: str,
    lang_to: str
) -> str:
    response = requests.post(
        f"{_config.translation_host}/Translation",
        json=dict(
            message=message,
            translateFrom=lang_from,
            translateTo=lang_to
        ),
        timeout=10
    )

    response.raise_for_status()

    translated = response.text

    return translated

_LANG_PL = "pl"
_LANG_EN = "en-US"

def translate_pl_to_en(
    message: str
) -> str:
    return translate(
        message, _LANG_PL, _LANG_EN
    )

def translate_en_to_pl(
    message: str
) -> str:
    return translate(
        message, _LANG_EN, _LANG_PL
    )

T = TypeVar("T", bound=BaseModel)

def read_json(
    file_path: Path
) -> dict | list:
    with open(file_path, encoding="utf8") as file:
        data = json.load(file)

    return data

def save_json(
    file_path: Path,
    data: dict | list
) -> None:
    make_dir(
        file_path.parent
    )

    with open(file_path, "w", encoding="utf8") as file:
        json.dump(
            data, file, ensure_ascii=False, indent=3
        )

def get_cached_translation(
    pl_path: Path,
    cache_path: Path,
    translator: Callable[
        [list[T]], list[T]
    ],
    model_type: Type[T],
    as_list: bool = True,
    with_pl: bool = False,
    serialize: bool = False,
    overwrite_existing: bool = False,
    create_pl_data: Optional[Callable[[], T]] = None
):
    if not create_pl_data:
        assert not overwrite_existing, (
            "'overwrite_existing' cannot be `True` if "
            "'create_pl_data' is unspecified"
        )

    def _serialize(
        data: T | list[T]
    ) -> dict[str] | list[dict[str]]:
        if not as_list:
            data = [data]

        serialized = list(map(
            lambda entry: entry.model_dump(),
            data
        ))

        if not as_list:
            serialized = serialized[0]

        return serialized

    will_create_pl_data = overwrite_existing or not pl_path.exists()

    if will_create_pl_data:
        assert create_pl_data, (
            "'create_pl_data' cannot be `None` if Polish data is to be created. "
            "Perhaps the data was assumed to have been created in another way, "
            "but the file got deleted?"
        )

        pl_data = _serialize(
            create_pl_data()
        )

        save_json(pl_path, pl_data)
    else:
        pl_data = read_json(pl_path)

    def _deserialize(
        serialized: dict[str] | list[dict[str]],
        output_model_type: Type[T]
    ) -> T | list[T]:
        if not as_list:
            serialized = [serialized]

        deserialized = list(map(
            output_model_type.model_validate,
            serialized
        ))

        if not as_list:
            deserialized = deserialized[0]

        return deserialized

    pl_data = _deserialize(
        pl_data, model_type
    )

    cache_exists = (
        not will_create_pl_data and
        os.path.exists(cache_path)
    )

    if cache_exists:
        print(
            f"   * Używanie tłumaczeń z cache'a: '{cache_path}'"
        )

        translated = read_json(cache_path)

        translated = _deserialize(
            translated, model_type
        )
    else:
        translated = translator(pl_data)

        serialized = _serialize(translated)

        save_json(cache_path, serialized)

    if as_list:
        n_pl = len(pl_data)
        n_tr = len(translated)

        assert n_pl == n_tr, (
            f"[PL data ({n_pl})] <-> [translated data ({n_tr})] size mismatch."
        )

    if serialize:
        if with_pl:
            pl_data = _serialize(pl_data)

        translated = (
            _serialize(translated)
            if cache_exists
            else serialized
        )

    if with_pl:
        return pl_data, translated

    return translated

def upload_docs(api_path: str, **kwargs) -> None:
    url = f"{_config.docs_upload_host}/{api_path}"

    response = requests.post(
        url,
        json=kwargs,
        timeout=10
    )

    response.raise_for_status()

def get_docs_root_dir_path() -> Path:
    return Path("docs")

def get_misc_docs_file_path(
    relative_file_path: str
) -> Path:
    return get_docs_root_dir_path() / "misc" / relative_file_path
