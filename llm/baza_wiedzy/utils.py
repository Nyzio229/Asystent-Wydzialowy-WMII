import os
import json

from pathlib import Path

from typing import Callable, Type, TypeVar

import requests

from pydantic import BaseModel

class Config(BaseModel):
    docs_upload_url: str
    translation_url: str

_config = Config(
    docs_upload_url="http://158.75.112.151:9123",
    translation_url="https://521c-188-146-254-163.ngrok-free.app/Translation"
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

def get_cached_translation(
    pl_path: Path,
    cache_path: Path,
    translator: Callable[[list[T]], list[T]],
    model_type: Type[T],
    with_pl: bool = False,
    deserialize_pl: bool = True,
    serialize: bool = False
) -> list[dict[str]] | list[T] | tuple[
    list[dict[str]], list[dict[str]]
] | tuple[
    list[T], list[T]
]:
    with open(pl_path, encoding="utf8") as file:
        pl_data = json.load(file)

    def _serialize(data: list[T]) -> list[dict[str]]:
        return list(map(lambda entry: entry.model_dump(), data))

    def _deserialize(serialized: list[dict[str]]) -> list[T]:
        return list(map(model_type.model_validate, serialized))

    if deserialize_pl:
        pl_data = _deserialize(pl_data)

    cache_exists = os.path.exists(cache_path)

    if cache_exists:
        print(f"   * Używanie tłumaczeń z cache'a: '{cache_path}'")

        with open(cache_path, encoding="utf8") as file:
            translated = json.load(file)

        translated = _deserialize(translated)
    else:
        translated = translator(pl_data)

        path = cache_path.parent
        path.mkdir(parents=True, exist_ok=True)

        serialized = _serialize(translated)

        with open(cache_path, "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=3)

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
