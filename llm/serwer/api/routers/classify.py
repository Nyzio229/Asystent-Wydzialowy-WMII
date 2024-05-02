import json

import logging

from typing import Literal, Optional, Type, TypeVar

from fastapi import APIRouter

from pydantic import BaseModel, Field

from llama_cpp import LogitsProcessorList

from lmformatenforcer import CharacterLevelParser, JsonSchemaParser
from lmformatenforcer.integrations.llamacpp import (
    build_llamacpp_logits_processor,
    build_token_enforcer_tokenizer_data
)

from common import common, log_endpoint_call

class ClassificationRequest(BaseModel):
    text: str

def _get_navigation_point_description(preposition: str, point: str) -> str:
    return (
        f"{point.capitalize()} point for navigation. "
        "The navigation query may be incomplete, so "
        f"leave this field blank if the {point.lower()} point for navigation "
        "isn't explicitly specified within the query. "
        "When specified, it is assumed to be a place on a university campus. "
        "It can be a coded room name (such as A5); "
        "it doesn't have to be a valid name of an existing room/place. "
        f"It's IMPORTANT that the {point.lower()} point must come right after "
        f"the following preposition: '{preposition.lower()}'"
    )

class CategoryNavigationMetadataSource(BaseModel):
    source: Optional[str] = Field(
        description=_get_navigation_point_description("from", "starting")
    )

class CategoryNavigationMetadataDestination(BaseModel):
    destination: Optional[str] = Field(
        description=_get_navigation_point_description("to", "destination")
    )

_rooms: list[str] = []

def _format_room(room: str) -> str:
    room = room.lower()

    room = room.replace("classroom", "")
    room = room.replace("room", "")
    room = room.strip()

    return room

def _read_rooms() -> list[str]:
    global _rooms

    if not _rooms:
        with open("rooms.txt", encoding="utf8") as file:
            _rooms = file.readlines()
            _rooms = list(map(_format_room, _rooms))

    return _rooms

class ClassificationIfNavigation(BaseModel):
    is_navigation: bool = Field(
        description=("Whether the user's query is a navigation query. "
                     "A navigation query is a question which asks "
                     "how to get from/to a certain place within a university campus. "
                     "The source/destination of navigation can be a coded room name (such as A5); "
                     "it doesn't have to be a valid name of an existing room/place.")
    )

class CategoryNavigationMetadata(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None

class ClassificationResult(BaseModel):
    label: Literal["navigation", "chat"]

    metadata: Optional[CategoryNavigationMetadata] = None

router = APIRouter()

@router.post("/classify")
async def classify(
    request: ClassificationRequest
) -> ClassificationResult:
    # https://github.com/noamgat/lm-format-enforcer/blob/main/samples/colab_llamacpppython_integration.ipynb
    _DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful, respectful and honest assistant. "
        "Always answer as helpfully as possible, while being safe. "
        "Your answers should not include any harmful, unethical, racist, "
        "sexist, toxic, dangerous, or illegal content. "
        "Please ensure that your responses are socially unbiased and positive in nature. "
        "If a question does not make any sense, or is not factually coherent, explain why "
        "instead of answering something not correct. "
        "If you don't know the answer to a question, please don't share false information."
    )

    def _get_prompt(
        message: str,
        system_prompt: Optional[str] = _DEFAULT_SYSTEM_PROMPT
    ) -> str:
        return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{message} [/INST]"

    tokenizer_data = build_token_enforcer_tokenizer_data(common.llm)

    logger = logging.getLogger("mikolAI")
    logger.setLevel(logging.DEBUG)

    def _infer_with_character_level_parser(
        prompt: str,
        character_level_parser: Optional[CharacterLevelParser] = None
    ) -> str:
        logits_processors: Optional[LogitsProcessorList] = None

        if character_level_parser:
            logits_processor = build_llamacpp_logits_processor(
                tokenizer_data,
                character_level_parser
            )

            logits_processors = LogitsProcessorList([logits_processor])

        output = common.llm(
            prompt,
            logits_processor=logits_processors,
            max_tokens=100,
            temperature=0.2
        )

        response = output["choices"][0]["text"]

        logger.debug("[Classify]")
        logger.debug(" * prompt: %s", prompt)
        logger.debug(" * response: %s", response)

        return response

    T = TypeVar("T", bound=BaseModel)

    request_text = request.text

    def _invoke_llm_for_task(
        task: str,
        response_type: Type[T]
    ) -> T:
        response_schema = response_type.model_json_schema()
        response_schema_str = json.dumps(response_schema)

        prompt = (
            f"Please {task} the user's query (given at the end). " +
            "You MUST answer using the following json schema:"
            f"{response_schema_str}\n\n" +
            "Here is the user's query:\n" +
            request_text
        )

        prompt = _get_prompt(prompt)
        response = _infer_with_character_level_parser(prompt, JsonSchemaParser(response_schema))
        result = response_type.model_validate(json.loads(response))

        return result

    result_if_navigation = _invoke_llm_for_task(
        "categorize",
        ClassificationIfNavigation
    )

    label = "navigation" if result_if_navigation.is_navigation else "chat"

    if label == "navigation":
        doc = common.nlp(request_text)

        adps_texts = []

        for token in doc:
            if token.pos_ == "ADP":
                adps_texts.append(token.text.lower())

        def _log_no_preposition_in_query_skip_point_extraction(
            preposition: str,
            point: str
        ) -> None:
            logger.debug(
                "Navigation query doesn't contain the '%s' word (POS: preposition/ADP), "
                "so skipping '%s' point extraction.",
                preposition,
                point
            )

        if "from" in adps_texts:
            result_source = _invoke_llm_for_task(
                "extract information from",
                CategoryNavigationMetadataSource
            )

            source = result_source.source
        else:
            source = None

            _log_no_preposition_in_query_skip_point_extraction("from", "source")

        if "to" in adps_texts:
            result_destination = _invoke_llm_for_task(
                "extract information from",
                CategoryNavigationMetadataDestination
            )

            destination = result_destination.destination
        else:
            destination = None

            _log_no_preposition_in_query_skip_point_extraction("to", "destination")

        metadata = dict(
            source=source,
            destination=destination
        )

        rooms = _read_rooms()

        def _check_metadata_navigation_point(key: str) -> bool:
            room = metadata.get(key, None)

            if room is None:
                return False

            formatted_room = _format_room(room)

            if formatted_room not in rooms:
                formatted_room = None

            if room != formatted_room:
                logger.debug("Invalid navigation place name -> updating metadata['%s']: '%s' -> '%s'",
                             key, room, formatted_room)

                metadata[key] = formatted_room

            return formatted_room is not None

        has_source = _check_metadata_navigation_point("source")
        has_destination = _check_metadata_navigation_point("destination")

        if not has_source and not has_destination:
            label = "chat"
            metadata = None

            logger.debug(
                "Navigation metadata: no 'source' and 'destination' fields -> setting label to '%s'",
                label
            )
    else:
        metadata = None

    result = ClassificationResult(
        label=label,
        metadata=metadata
    )

    log_endpoint_call("classify", request, result)

    return result
