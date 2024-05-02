import os
import json

from pathlib import Path

from typing import Callable, TypeVar

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

T = TypeVar("T")

def get_cached_translation(
    cache_path: Path,
    translator: Callable[[], T],
    serializer: Callable[[T], dict[str] | list],
    deserializer: Callable[[dict[str] | list], T]
) -> T:
    if os.path.exists(cache_path):
        print(f"      * Używanie tłumaczeń z cache'a: '{cache_path}'")

        with open(cache_path, encoding="utf8") as file:
            translated = json.load(file)

        translated = deserializer(translated)
    else:
        translated = translator()

        path = cache_path.parent
        path.mkdir(parents=True, exist_ok=True)

        with open(cache_path, "w", encoding="utf8") as file:
            serialized = serializer(translated)
            json.dump(serialized, file, ensure_ascii=False, indent=3)

    return translated

def upload_docs(api_path: str, **kwargs) -> None:
    url = f"{_config.docs_upload_url}/{api_path}"

    response = requests.post(
        url,
        json=kwargs,
        timeout=10
    )

    response.raise_for_status()
