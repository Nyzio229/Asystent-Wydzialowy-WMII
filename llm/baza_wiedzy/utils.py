import requests

from pydantic import BaseModel

class Config(BaseModel):
    docs_upload_url: str
    translation_url: str

_config = Config(
    docs_upload_url="http://158.75.112.151:9123",
    translation_url="https://13ad-188-146-252-197.ngrok-free.app/Translation"
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

def upload_docs(api_path: str, **kwargs) -> None:
    url = f"{_config.docs_upload_url}/{api_path}"

    def _maybe_serialize(
        entry: int | str | dict | BaseModel | list[BaseModel]
    ) -> int | str | dict | list:
        if isinstance(entry, (int, str)):
            return entry

        if isinstance(entry, BaseModel):
            return entry.model_dump()

        if isinstance(entry, list):
            serialized_list = []

            for value in entry:
                serialized = _maybe_serialize(value)
                serialized_list.append(serialized)

            return serialized_list

        assert isinstance(entry, dict)

        serialized_dict = {}

        for key, value in entry.items():
            serialized_dict[key] = _maybe_serialize(value)

        return serialized_dict

    response = requests.post(
        url,
        json=_maybe_serialize(kwargs),
        timeout=10
    )

    response.raise_for_status()
