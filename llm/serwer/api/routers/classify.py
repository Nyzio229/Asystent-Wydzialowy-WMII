import re

import json

import logging

from pathlib import Path

from typing import Iterable, Literal, Optional, Type, TypeVar

from fuzzywuzzy import process

from fastapi import APIRouter

from pydantic import BaseModel, Field

from llama_cpp import LogitsProcessorList

from lmformatenforcer import CharacterLevelParser, JsonSchemaParser
from lmformatenforcer.integrations.llamacpp import (
    build_llamacpp_logits_processor,
    build_token_enforcer_tokenizer_data
)

from common import (
    common,
    chat_with_default_system_message,
    log_endpoint_call,
    Message
)

class ClassificationRequest(BaseModel):
    text: str

_NAVIGATION_DESCRIPTION_WHEN_SPECIFIED = (
    "When specified, it is assumed to be a place on a university campus. "
    "It can be a coded room name (the code is: a letter followed by a few digits); "
    "it doesn't have to be a valid name of an existing room/place."
)

def _get_navigation_point_description(preposition: str, point: str) -> str:
    return (
        f"{point.capitalize()} point for navigation. "
        "The navigation query may be incomplete, so "
        f"leave this field blank if the {point.lower()} point for navigation "
        "isn't explicitly specified within the query. "
        f"{_NAVIGATION_DESCRIPTION_WHEN_SPECIFIED} "
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

class Place(BaseModel):
    pl: str
    en: list[str]

class SynonymsContainer(BaseModel):
    synonyms: list[str]

    def extend_sentence(self, sentence: str) -> list[str]:
        extended: list[str] = []

        sentence_len = len(sentence)

        for i, synonym in enumerate(self.synonyms):
            try:
                idx = sentence.index(synonym)
            except ValueError:
                continue

            n_chars = len(synonym)

            next_char_idx = idx+n_chars

            if next_char_idx < sentence_len and sentence[next_char_idx] != " ":
                continue

            synonyms = self.synonyms[:i] + self.synonyms[i+1:]

            for new_part in synonyms:
                new_sentence = sentence[:idx] + new_part + sentence[next_char_idx:]
                extended.append(new_sentence)

        return extended

_places: list[Place] = []
_synonyms: list[SynonymsContainer] = []

_PLACES_DIR_PATH = Path("places")

def _format_place_name(place: str) -> str:
    place = place.lower()

    place = re.sub(r"[^a-z\d ]", "", place)

    words = place.split()

    filtered_words: list[str] = []

    for word in words:
        if word not in {"the", "on", "in", "of", "into"}:
            filtered_words.append(word)

    place = " ".join(filtered_words)

    def _replace_many(texts: Iterable[str], new: str) -> None:
        nonlocal place

        for text in texts:
            place = place.replace(text, new)

    def _set_floor_notation(
        floor: int,
        as_str: str,
        short: str
    ) -> None:
        def _floor_with_prefix(prefix: str) -> str:
            return f"{prefix} floor"

        texts = (f"{floor}.", str(floor), as_str, f"{floor}{short}")
        texts = map(_floor_with_prefix, texts)

        _replace_many(texts, f'{"i" * floor} floor')

    _set_floor_notation(1, "first", "st")
    _set_floor_notation(2, "second", "nd")

    def _remove_space_after_lowercase_letter(text: str):
        def _replace(match: re.Match[str]):
            return match.group(1) + match.group(2)

        cleaned_text = re.sub(r"([a-z]) (\d+)", _replace, text)
        return cleaned_text

    place = _remove_space_after_lowercase_letter(place)

    place = place.strip()

    return place

def _get_synonyms() -> list[SynonymsContainer]:
    global _synonyms

    if not _synonyms:
        synonyms_path = _PLACES_DIR_PATH / "synonyms.json"
        with open(synonyms_path, encoding="utf8") as file:
            synonyms_list = json.load(file)

        for synonyms in synonyms_list:
            synonyms = list(map(_format_place_name, synonyms))

            _synonyms.append(SynonymsContainer(
                synonyms=synonyms
            ))

    return _synonyms

def _get_places() -> list[Place]:
    global _places

    if not _places:
        def _read_simple_places(file_name: str) -> list[Place]:
            places: list[Place] = []

            simple_places_path = _PLACES_DIR_PATH / file_name
            with open(simple_places_path, encoding="utf8") as file:
                simple_places = file.readlines()
                simple_places = list(map(_format_place_name, simple_places))

                for place in simple_places:
                    places.append(Place(
                        pl=place,
                        en=[
                            place
                        ] + [
                            f"{prefix} {place}"
                            for prefix in ["room", "lab", "classroom", "class"]
                        ] + [
                            f"{place} {suffix}"
                            for suffix in ["class"]
                        ]
                    ))

            return places

        def _read_complex_places(file_name: str) -> list[Place]:
            places: list[Place] = []

            complex_places_path = _PLACES_DIR_PATH / file_name
            with open(complex_places_path, encoding="utf8") as file:
                complex_places = json.load(file)

                for place in complex_places:
                    en = place["en"]

                    if isinstance(en, str):
                        en = [en]

                    en = list(map(_format_place_name, en))

                    places.append(Place(
                        pl=place["pl"],
                        en=en
                    ))

            return places

        def _extend_places(places: list[Place]) -> None:
            synonyms = _get_synonyms()

            for place in places:
                en = place.en

                for synonym in synonyms:
                    extended: list[str] = []

                    for sentence in en:
                        extended += synonym.extend_sentence(sentence)

                    en += extended

        simple_places = _read_simple_places("simple_places.txt")
        complex_places = _read_complex_places("complex_places.json")

        places = simple_places + complex_places
        _extend_places(places)

        _places = places

    return _places

class ClassificationIfNavigation(BaseModel):
    is_navigation: bool = Field(
        description=(
            "Whether the user's query is a navigation query. "
            "A navigation query is a question which asks "
            "how to get from/to a certain place/location within a university campus. "
            "It can also be phrased in various ways, like asking for directions. "
            "The source/destination of navigation can be a coded room name (such as A5); "
            "it doesn't have to be a valid name of an existing room/place. "
            "A navigation query may consist of multiple sentences/questions.\n"
            "It's also possible that the user provides additional, irrelevant information or context;"
            "in such case, consider his query as a navigation query if ANY of his questions/sentences "
            "regard in some way: navigating/wanting to get somewhere/looking for directions/"
            "asking how the user the can get somewhere/reaching a certain place or location/"
            "asking if there's a way to get somewhere/where a place/room is located/"
            "asking to tell the user how to get somewhere/"
            "asking if it's possible to get to a place.\n"
            "In short, a navigation query is most of the times a text "
            "that contains any mention of a location/place."
        )
    )

class CategoryNavigationMetadata(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None

class CategoryNavigationRephraseQuery(BaseModel):
    rephrased_query: str = Field(
        description=(
            "The rephrased navigation query. "
            "It must be in the form of: "
            "'How to get from <source> to <destination>?'. "
            "If a piece of information (starting or destination point)"
            "is missing then it should be marked with: <unknown>. " +
            _NAVIGATION_DESCRIPTION_WHEN_SPECIFIED
        )
    )

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

        kwargs = common.llm_inference_params.model_dump()
        kwargs.update(
            max_tokens=100,
            temperature=0
        )

        output = common.llm(
            prompt,
            logits_processor=logits_processors,
            **kwargs
        )

        response = output["choices"][0]["text"]

        logger.debug("[Classify]")
        logger.debug(" * prompt: %s", prompt)
        logger.debug(" * response: %s", response)

        return response

    def _invoke_llm_for_task_2(
        query: str,
        task: str,
        suffix: Optional[str] = None
    ) -> str:
        if suffix:
            suffix = f"\n\n{suffix}"

        prompt = (
            f"{task}\n\n"
            "Here is the user's query:\n"
            f"'{query}'"
            f"{suffix if suffix else ''}"
        )

        llm_inference_params = common.llm_inference_params.model_copy(
            update=dict(
                temperature=0
            )
        )

        prompt_message = Message(
            role="user",
            content=prompt
        )

        response = chat_with_default_system_message(
            common.llm,
            [prompt_message],
            llm_inference_params
        )

        response = response.lower()

        logger.debug("[Classify]")
        logger.debug(" * prompt: %s", prompt)
        logger.debug(" * response: %s", response)

        return response

    T = TypeVar("T", bound=BaseModel)

    def _invoke_llm_for_task(
        query: str,
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
            f"'{query}'"
        )

        prompt = _get_prompt(prompt)
        response = _infer_with_character_level_parser(prompt, JsonSchemaParser(response_schema))
        result = response_type.model_validate(json.loads(response))

        return result

    request_text = request.text

    """
    result_if_navigation = _invoke_llm_for_task(
        request_text,
        "categorize",
        ClassificationIfNavigation
    )

    label = "navigation" if result_if_navigation.is_navigation else "chat"
    """

    is_navigation = _invoke_llm_for_task_2(
        request_text,
        "Please decide whether the user's query (given at the end) is a navigation query. "
        "A navigation query is a question which asks "
        "how to get from/to a certain place/location within a university campus. "
        "It can also be phrased in various ways, like asking for directions. "
        "The source/destination of navigation can be a coded room name (such as A5); "
        "it doesn't have to be a valid name of an existing room/place. "
        "A navigation query may consist of multiple sentences/questions.\n"
        "It's also possible that the user provides additional, irrelevant information or context;"
        "in such case, consider his query as a navigation query if ANY of his questions/sentences "
        "regard in some way: navigating/wanting to get somewhere/looking for directions/"
        "asking how the user the can get somewhere/reaching a certain place or location/"
        "asking if there's a way to get somewhere/where a place/room is located/"
        "asking to tell the user how to get somewhere/"
        "asking if it's possible to get to a place.\n"
        "In short, a navigation query is most of the times a text "
        "that contains any mention of a location/place.\n",
        "If you think the query is a navigation query then answer with 'yes', otherwise with 'no'."
    ) == "yes"

    label = "navigation" if is_navigation else "chat"

    if label == "navigation":
        def _get_navigation_metadata(
            navigation_query: str
        ) -> Optional[dict[str, Optional[str]]]:
            doc = common.nlp(navigation_query)

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

            result_source = _invoke_llm_for_task(
                navigation_query,
                "extract information from",
                CategoryNavigationMetadataSource
            )

            source = result_source.source

            if (
                "from" not in adps_texts and source and
                _format_place_name(source) not in _format_place_name(navigation_query)
            ):
                source = None

                _log_no_preposition_in_query_skip_point_extraction(
                    "from", "source"
                )

            if "to" in adps_texts:
                result_destination = _invoke_llm_for_task(
                    navigation_query,
                    "extract information from",
                    CategoryNavigationMetadataDestination
                )

                destination = result_destination.destination
            else:
                destination = None

                _log_no_preposition_in_query_skip_point_extraction(
                    "to", "destination"
                )

            metadata_str = dict(
                source=source,
                destination=destination
            )

            metadata_places: dict[str, Optional[Place]] = {}

            places = _get_places()

            for key, value in metadata_str.items():
                if not value:
                    continue

                name = _format_place_name(value)

                if value != name:
                    logger.debug(
                        "metadata['%s']: formatting '%s' -> '%s'",
                        key, value, name
                    )

                exact_match: Optional[Place] = None
                matching_places: dict[str, Place] = {}

                for place in places:
                    for en_name in place.en:
                        if en_name == name:
                            exact_match = place

                            break

                        if en_name in name:
                            matching_places[en_name] = place
                    else:
                        continue

                    break

                if exact_match:
                    place = exact_match
                elif not matching_places:
                    place = None
                elif len(matching_places) == 1:
                    place = next(iter(matching_places.values()))
                else:
                    best_match_result: tuple[
                        tuple[str, Place],
                        int
                    ] = process.extractOne(
                        query=name,
                        choices=matching_places.items(),
                        processor=lambda pair: pair[0]
                    )

                    best_match = best_match_result[0]

                    place = best_match[1]

                    logger.debug(
                        "metadata['%s']: '%s' contains %d places: %s. Best match is: '%s' (because of '%s')",
                        key, name,
                        len(matching_places),
                        list(map(lambda place: place.pl, matching_places.values())),
                        place.pl,
                        best_match[0]
                    )

                if place:
                    logger.debug(
                        "metadata['%s']: found place '%s' for '%s'",
                        key, place.pl, name
                    )
                else:
                    logger.debug(
                        "metadata['%s']: no such place '%s'. Setting to None",
                        key, name
                    )

                metadata_places[key] = place

            has_points = any(place for place in metadata_places.values())

            if has_points:
                metadata = {
                    key: value.pl if value else None
                    for key, value in metadata_places.items()
                }
            else:
                metadata = None

                logger.debug(
                    "metadata: no valid places"
                )

            return metadata

        def _set_metadata(navigation_query: str):
            nonlocal metadata
            metadata = _get_navigation_metadata(navigation_query)
            
        def _check_metadata() -> bool:
            if metadata:
                return True

            nonlocal label
            label = "chat"

            return False

        _set_metadata(request_text)

        if _check_metadata() and len(set(metadata.values())) == 1:
            logger.debug(
                "metadata: both points are equal ('%s'). "
                "Attempting to rephrase the query and try again.",
                next(iter(metadata.values()))
            )

            result_rephrase = _invoke_llm_for_task(
                request_text,
                "rephrase",
                CategoryNavigationRephraseQuery
            )

            navigation_query = result_rephrase.rephrased_query

            _set_metadata(navigation_query)

            _check_metadata()
    else:
        metadata = None

    result = ClassificationResult(
        label=label,
        metadata=metadata
    )

    log_endpoint_call("classify", request, result)

    return result
