import os
import json

from pathlib import Path

from typing import Callable, Type, TypeVar, Optional

import requests

from pydantic import BaseModel

class Config(BaseModel):
    docs_upload_url: str
    translation_url: str

_config = Config(
    docs_upload_url="http://158.75.112.151:9123",
    translation_url="https://5d83-188-146-254-12.ngrok-free.app/Translation"
)

def translate(message: str, lang_from: str, lang_to: str) -> str:
    response = requests.post(
        _config.translation_url,
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

T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)

def get_cached_translation(
    pl_path: Path,
    cache_path: Path,
    translator: Callable[[list[T]], list[U]],
    model_type: Type[T],
    as_list: bool = True,
    with_pl: bool = False,
    deserialize_pl: bool = True,
    serialize: bool = False,
    verify_translated_data_size: bool = True,
    translated_model_type: Optional[Type[U]] = None,
    overwrite_existing: bool = False,
    create_pl_data: Optional[Callable[[], T]] = None
):
    def _serialize(
        data: T | U | list[T] | list[U]
    ) -> dict[str] | list[dict[str]]:
        if not as_list:
            data = [data]

        serialized = list(map(
            lambda entry: entry.model_dump(), data
        ))

        if not as_list:
            serialized = serialized[0]

        return serialized

    will_create_pl_data = overwrite_existing or not pl_path.exists()

    if will_create_pl_data:
        pl_data = _serialize(create_pl_data())

        with open(pl_path, "w", encoding="utf8") as file:
            json.dump(pl_data, file, ensure_ascii=False, indent=3)
    else:
        with open(pl_path, encoding="utf8") as file:
            pl_data = json.load(file)

    def _deserialize(
        serialized: dict[str] | list[dict[str]],
        output_model_type: Type[T] | Type[U]
    ) -> T | U | list[T] | list[U]:
        if not as_list:
            serialized = [serialized]

        deserialized = list(map(output_model_type.model_validate, serialized))

        if not as_list:
            deserialized = deserialized[0]

        return deserialized

    if deserialize_pl:
        pl_data = _deserialize(pl_data, model_type)

    cache_exists = not will_create_pl_data and os.path.exists(cache_path)

    if cache_exists:
        print(f"   * Używanie tłumaczeń z cache'a: '{cache_path}'")

        with open(cache_path, encoding="utf8") as file:
            translated = json.load(file)

        translated = _deserialize(
            translated, translated_model_type or model_type
        )
    else:
        translated = translator(pl_data)

        path = cache_path.parent
        path.mkdir(parents=True, exist_ok=True)

        serialized = _serialize(translated)

        with open(cache_path, "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=3)

    if as_list and verify_translated_data_size:
        assert len(pl_data) == len(translated), (
            "[PL data] <-> [translated data] size mismatch."
        )

    if serialize:
        if with_pl and deserialize_pl:
            pl_data = _serialize(pl_data)

        translated = _serialize(translated) if cache_exists else serialized

    if with_pl:
        return pl_data, translated

    return translated

def upload_docs(api_path: str, **kwargs) -> None:
    url = f"{_config.docs_upload_url}/{api_path}"

    response = requests.post(
        url,
        json=kwargs,
        timeout=10
    )

    response.raise_for_status()

def get_misc_docs_file_path(
    relative_file_path: str,
    is_dir: bool = False
) -> Path:
    file_path = Path("misc_docs") / relative_file_path

    dir_path = file_path if is_dir else file_path.parent
    dir_path.mkdir(parents=True, exist_ok=True)

    return file_path
