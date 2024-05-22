import re

import json

import logging

from pathlib import Path

from typing import Iterable, Literal, Optional, Type, TypeVar

from fastapi import APIRouter

from fuzzywuzzy import process

from pydantic import BaseModel, Field

from llama_cpp import LogitsProcessorList

from lmformatenforcer import CharacterLevelParser, JsonSchemaParser
from lmformatenforcer.integrations.llamacpp import (
    build_llamacpp_logits_processor,
    build_token_enforcer_tokenizer_data
)

from common import (
    common,
    LOGGER,
    chat_with_default_system_message,
    log_endpoint_call,
    Message
)

_NAVIGATION_DESCRIPTION_WHEN_SPECIFIED = (
    "When specified, it is assumed to be a place on "
    "a university campus. If it is a letter followed by "
    "a few digits (example: B202) then consider it "
    "a correctly coded room name; it doesn't have to be "
    "a valid name of an existing room/place. The location "
    "may also consist of a few words, for example: "
    "'toilet near <a room>' or 'stairs next to <a room>'."
)

def _get_navigation_point_description(
    description: str,
    preposition: str,
    point: str
) -> str:
    return (
        f"{point.capitalize()} point for navigation. "
        f"{description}\nThe navigation query may be "
        f"incomplete (that is, the {point} point might "
        "not be specified at all). In such case, answer "
        f"with '<unknown>' if the {point} point for navigation "
        "isn't explicitly specified within the query. "
        f"{_NAVIGATION_DESCRIPTION_WHEN_SPECIFIED} "
        f"The {point} point usually comes right after "
        f"the following preposition: '{preposition}'"
    )

class CategoryNavigationMetadataSource(BaseModel):
    source: Optional[str] = Field(
        description=_get_navigation_point_description(
            (
                "The starting point is the location that "
                "the user wants to go from, where he is "
                "currently located or where he is starting from."
            ),
            "from", "starting"
        )
    )

class CategoryNavigationMetadataDestination(BaseModel):
    destination: Optional[str] = Field(
        description=_get_navigation_point_description(
            (
                "The destination point is the location that "
                "the user wants to go to."
            ),
            "to", "destination"
        )
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

            if (
                next_char_idx < sentence_len and
                sentence[next_char_idx] != " "
            ):
                continue

            synonyms = self.synonyms[:i] + self.synonyms[i+1:]

            for new_part in synonyms:
                new_sentence = (
                    sentence[:idx] +
                    new_part +
                    sentence[next_char_idx:]
                )

                extended.append(new_sentence)

        return extended

_places: list[Place] = []
_simple_places_names: list[str] = []

_synonyms: list[SynonymsContainer] = []

_PLACES_DIR_PATH = Path("places")

def _format_place_name(place: str) -> str:
    place = place.lower()

    place = re.sub(r"[^a-z\d ]", "", place)

    words = place.split()

    filtered_words: list[str] = []

    for word in words:
        if word not in {
            "the", "on", "in", "of", "into"
        }:
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

        texts = (
            f"{floor}.", str(floor), as_str, f"{floor}{short}"
        )

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

def _read_json(
    file_path: Path
) -> dict | list:
    with open(file_path, encoding="utf8") as file:
        data = json.load(file)

    return data

def _get_synonyms() -> list[SynonymsContainer]:
    global _synonyms

    if not _synonyms:
        synonyms_list = _read_json(
            _PLACES_DIR_PATH / "synonyms.json"
        )

        for synonyms in synonyms_list:
            synonyms = list(map(_format_place_name, synonyms))

            _synonyms.append(SynonymsContainer(
                synonyms=synonyms
            ))

    return _synonyms

def _get_places() -> tuple[
    list[str], list[Place]
]:
    global _places
    global _simple_places_names

    if not _places or not _simple_places_names:
        def _read_simple_places(
            file_name: str
        ) -> list[Place]:
            places: list[Place] = []

            simple_places_path = _PLACES_DIR_PATH / file_name
            with open(simple_places_path, encoding="utf8") as file:
                simple_places = file.readlines()

                simple_places = list(map(
                    _format_place_name, simple_places
                ))

                for place in simple_places:
                    places.append(Place(
                        pl=place,
                        en=[
                            place
                        ] + [
                            f"{prefix} {place}"
                            for prefix in [
                                "room", "lab", "classroom", "class"
                            ]
                        ] + [
                            f"{place} {suffix}"
                            for suffix in ["class"]
                        ]
                    ))

            return places

        def _read_complex_places(file_name: str) -> list[Place]:
            places: list[Place] = []

            complex_places = _read_json(
                _PLACES_DIR_PATH / file_name
            )

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
                        extended += synonym.extend_sentence(
                            sentence
                        )

                    en += extended

        simple_places = _read_simple_places(
            "simple_places.txt"
        )

        complex_places = _read_complex_places(
            "complex_places.json"
        )

        places = simple_places + complex_places

        _extend_places(places)

        _places = places
        _simple_places_names = list(map(
            lambda place: place.pl.lower(),
            simple_places
        ))

    return _simple_places_names, _places

class CategoryNavigationMetadata(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None

class ClassificationRequest(BaseModel):
    text: str

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
        "sexist, toxic, dangerous, or illegal content. Please ensure that "
        "your responses are socially unbiased and positive in nature. "
        "If a question does not make any sense, or is not factually coherent, "
        "explain why instead of answering something not correct. "
        "If you don't know the answer to a question, please don't share false information."
    )

    def _get_prompt(
        message: str,
        system_prompt: Optional[str] = _DEFAULT_SYSTEM_PROMPT
    ) -> str:
        return (
            f"<s>[INST] <<SYS>>\n{system_prompt}\n"
            f"<</SYS>>\n\n{message} [/INST]"
        )

    tokenizer_data = build_token_enforcer_tokenizer_data(common.llm)

    LOGGER.setLevel(logging.DEBUG)

    def _infer_with_character_level_parser(
        prompt: str,
        character_level_parser: Optional[
            CharacterLevelParser
        ] = None
    ) -> str:
        logits_processors: Optional[
            LogitsProcessorList
        ] = None

        if character_level_parser:
            logits_processor = build_llamacpp_logits_processor(
                tokenizer_data,
                character_level_parser
            )

            logits_processors = LogitsProcessorList(
                [logits_processor]
            )

        kwargs = dict(
            max_tokens=100,
            temperature=0,
            logits_processor=logits_processors
        )

        response = common.invoke_llm(
            prompt, **kwargs
        )

        LOGGER.debug("[Classify]")
        LOGGER.debug(" * prompt: %s", prompt)
        LOGGER.debug(" * response: %s", response)

        return response

    def _chat_with_llm_for_task(
        query: str,
        task: str,
        suffix: Optional[str] = None
    ) -> str:
        if suffix:
            suffix = f"\n\n{suffix}"

        prompt = (
            f"{task}\n\n"
            "Here is the user's query:\n"
            f'"{query}"'
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

        LOGGER.debug("[Classify]")
        LOGGER.debug(" * prompt: %s", prompt)
        LOGGER.debug(" * response: %s", response)

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
            f"Please {task} the user's query (given at the end). "
            "You MUST answer using the following json schema: "
            f"{response_schema_str}\n\n"
            "Here is the user's query:\n"
            f'"{query}"'
        )

        prompt = _get_prompt(prompt)

        response = _infer_with_character_level_parser(
            prompt, JsonSchemaParser(response_schema)
        )

        result = response_type.model_validate(
            json.loads(response)
        )

        return result

    def _get_next_nearest_substring(
        text: str | list[str],
        substrings: Iterable[str],
        start_idx: Optional[int] = None
    ) -> tuple[Optional[str], Optional[int]]:
        lowest_idx: Optional[int] = None
        next_substring: Optional[str] = None

        for substring in substrings:
            try:
                idx = text.index(substring, start_idx)
            except ValueError:
                continue

            if lowest_idx is None or idx < lowest_idx:
                lowest_idx = idx
                next_substring = substring

        return next_substring, lowest_idx

    def _split_preserve_punctuation(
        text: str,
        punctuation: Iterable[str]
    ) -> list[str]:
        split_words: list[str] = []

        words = text.split()

        for word in words:
            start_idx = 0

            while True:
                next_char, idx = _get_next_nearest_substring(
                    word, punctuation, start_idx
                )

                if idx is None:
                    break

                split_words += [word[start_idx:idx], next_char]

                start_idx = idx+1

            if start_idx < len(word):
                split_words.append(word[start_idx:])

        split_words = list(filter(
            lambda x: x,
            split_words
        ))

        return split_words

    def _find_best_matching_place(
        location: str,
        places: list[Place]
    ) -> Optional[Place]:
        exact_match: Optional[Place] = None
        matching_places: dict[str, Place] = {}

        for place in places:
            for en_name in place.en:
                if en_name == location:
                    exact_match = place

                    break

                if en_name in location:
                    matching_places[en_name] = place
            else:
                continue

            break

        if exact_match:
            place = exact_match
        elif not matching_places:
            place = None
        elif len(matching_places) == 1 or len(set(map(
            lambda place: place.pl, matching_places.values()
        ))) == 1:
            place = next(iter(matching_places.values()))
        else:
            best_match_result: tuple[
                tuple[str, Place], int
            ] = process.extractOne(
                query=location,
                choices=matching_places.items(),
                processor=lambda pair: pair[0]
            )

            best_match = best_match_result[0]

            place = best_match[1]

            LOGGER.debug(
                "'%s' contains %d places: %s. Best match is: '%s' (because of '%s')",
                location,
                len(matching_places),
                list(map(
                    lambda place: place.pl, matching_places.values()
                )),
                place.pl,
                best_match[0]
            )

        return place

    def _get_navigation_metadata_using_brute_force(
        query: str,
        places: list[Place]
    ) -> Optional[dict[str, Optional[Place]]]:
        punctuation = {
            ".", ",", "?", "!"
        }

        words = _split_preserve_punctuation(
            query.lower(), punctuation
        )

        source_words = {
            "from"
        }

        destination_words = {
            "to", "into", "where", "for"
        }

        stops = source_words | destination_words | punctuation

        metadata: dict[list[str], list[str]] = {
            key: []
            for key in [
                "source", "destination"
            ]
        }

        idx = 0

        n_words = len(words)

        while idx < n_words:
            word = words[idx]

            idx += 1

            if word in source_words:
                metadata_key = "source"
            elif word in destination_words:
                metadata_key = "destination"
            else:
                continue

            _, stop_idx = _get_next_nearest_substring(
                words, stops, idx
            )

            if not stop_idx:
                stop_idx = n_words

            location = " ".join(words[idx:stop_idx])
            location = _format_place_name(location)

            metadata[metadata_key].append(location)

            idx = stop_idx

        metadata_places: dict[str, Optional[Place]] = {}

        for key, value in metadata.items():
            for location in value:
                best_match = _find_best_matching_place(
                    location, places
                )

                if best_match:
                    break
            else:
                best_match = None

            metadata_places[key] = best_match

        if any(value for value in metadata_places.values()):
            return metadata_places

        return None

    def _extend_places_names(
        navigation_query: str,
        places_names: list[str],
        extension_word: str
    ) -> str:
        new_words: list[str] = []

        words = navigation_query.split()

        lower_words = list(map(
            str.lower, words
        ))

        n_words = len(words)

        for i, word in enumerate(words):
            def _has_neighbor_at(idx: int) -> bool:
                return lower_words[idx] == extension_word

            def _has_left_neighbor() -> bool:
                return _has_neighbor_at(i-1)

            def _has_right_neighbor() -> bool:
                return _has_neighbor_at(i+1)

            filtered_word = re.sub(r"[^a-z\d ]", "", lower_words[i])

            if filtered_word in places_names:
                if i == 0:
                    has_neighbor = _has_right_neighbor()
                elif i == n_words-1:
                    has_neighbor = _has_left_neighbor()
                else:
                    has_neighbor = _has_left_neighbor() or _has_right_neighbor()

                if not has_neighbor:
                    new_words.append(extension_word)

            new_words.append(word)

        extended_query = " ".join(new_words)

        return extended_query

    request_text = request.text

    simple_places_names, places = _get_places()

    metadata = _get_navigation_metadata_using_brute_force(
        request_text, places
    )

    is_metadata_complete = (
        metadata and all(value for value in metadata.values())
    )

    if metadata:
        LOGGER.debug(
            "Got navigation metadata using brute force:"
        )

        for key, value in metadata.items():
            if value:
                LOGGER.debug(
                    "metadata['%s'] = '%s'",
                    key, value.pl
                )

    extended_request_text = _extend_places_names(
        request_text, simple_places_names, "room"
    )

    if (
        not is_metadata_complete and
        extended_request_text != request_text
    ):
        LOGGER.debug(
            'Extended request text: "%s" -> "%s"',
            request_text, extended_request_text
        )

        request_text = extended_request_text

    if metadata:
        label = "navigation"
    else:
        is_navigation = _chat_with_llm_for_task(
            request_text,
            "Please decide whether the user's query (given at the end) is a spatial navigation query. "
            "A spatial navigation query is a question which asks "
            "how to get from/to a certain place/location within a university campus. "
            "It can also be phrased in various ways, like asking for directions. "
            "The source/destination of navigation can be a coded room name (such as A5); "
            "it doesn't have to be a valid name of an existing room/place. "
            "A spatial navigation query may consist of multiple sentences/questions.\n"
            "It's also possible that the user provides additional, irrelevant information or context;"
            "in such case, consider his query as a spatial navigation query if ANY of his questions/sentences "
            "regard in some way: navigating/wanting or needing to get to, in or into somewhere/looking for directions/"
            "asking how the user can get somewhere/reaching a certain place or location/"
            "asking if there's a way to get somewhere/where a place or room is located/"
            "asking to tell the user how to get somewhere/"
            "asking if it's possible to get to a place.\n"
            "Keep in mind that many room/place names are coded, like B302 or L5 (a letter and a few digits).\n"
            "If you think the query is a spatial navigation query then answer with 'true', otherwise with 'false'."
        ) == "true"

        label = "navigation" if is_navigation else "chat"

    if label == "navigation":
        def _set_missing_navigation_metadata_using_llm(
            navigation_query: str,
            metadata: dict[str, Optional[Place]]
        ) -> None:
            doc = common.nlp(navigation_query)

            adps_texts = []

            for token in doc:
                if token.pos_ == "ADP":
                    adps_texts.append(token.text.lower())

            def _log_no_preposition_in_query_skip_point_extraction(
                preposition: str | tuple[str, ...],
                point: str,
                additional_check: Optional[str] = None
            ) -> None:
                LOGGER.debug(
                    "Navigation query doesn't contain the '%s' word(s) (POS: preposition/ADP)%s, "
                    "so skipping '%s' point extraction.",
                    preposition,
                    f" (in addition: {additional_check})" if additional_check else "",
                    point
                )

            if metadata["source"]:
                source = None
            else:
                result_source = _invoke_llm_for_task(
                    navigation_query,
                    "extract information from",
                    CategoryNavigationMetadataSource
                )

                source = result_source.source

                if source and "from" in source:
                    source = source.replace("from", "")

                has_from_adp = "from" in adps_texts

                if (
                    not has_from_adp and source and
                    _format_place_name(source) not in _format_place_name(navigation_query)
                ):
                    if source:
                        additional_check = (
                            f"'source' value ('{_format_place_name(source)}') "
                            "wasn't found in the query"
                        )
                    else:
                        additional_check = "'source' value is `None`"

                    _log_no_preposition_in_query_skip_point_extraction(
                        "from", "source", additional_check
                    )

                    source = None

            if metadata["destination"]:
                destination = None
            else:
                words_to = ("where", "there")
                prepositions_to = ("to", "into")

                if (
                    any(
                        word in navigation_query.lower()
                        for word in words_to
                    )
                    or
                    any(
                        preposition in adps_texts
                        for preposition in prepositions_to
                    )
                ):
                    result_destination = _invoke_llm_for_task(
                        navigation_query,
                        "extract information from",
                        CategoryNavigationMetadataDestination
                    )

                    destination = result_destination.destination
                else:
                    destination = None

                    _log_no_preposition_in_query_skip_point_extraction(
                        prepositions_to, "destination", f"it doesn't contain any of the words: {words_to}"
                    )

            metadata_str = dict(
                source=source,
                destination=destination
            )

            if any(value for value in metadata.values()):
                missing_metadata_key = next(
                    (key for key, value in metadata.items() if not value),
                    None
                )
            else:
                missing_metadata_key = None

            for key, value in metadata_str.items():
                if not value:
                    continue

                name = _format_place_name(value)

                if value != name:
                    LOGGER.debug(
                        "metadata['%s']: formatting '%s' -> '%s'",
                        key, value, name
                    )

                place = _find_best_matching_place(
                    name, places
                )

                if place:
                    LOGGER.debug(
                        "metadata['%s']: found place '%s' for '%s'",
                        key, place.pl, name
                    )
                else:
                    LOGGER.debug(
                        "metadata['%s']: no such place '%s'. Setting to `None`",
                        key, name
                    )

                metadata[key] = place

            # check for llm hallucination of the missing place
            # (it usually assigns the same place as
            # both source and destination if one is missing)
            if (
                any(value for value in metadata.values()) and
                metadata["source"] == metadata["destination"]
            ):
                # we assume that it's more likely for the user not to specify
                # the source point (rather than the destination point)
                if not missing_metadata_key:
                    missing_metadata_key = "source"

                LOGGER.debug(
                    "Hallucination check: LLM most likely hallucinated "
                    "the '%s' metadata value ('%s'). "
                    "Therefore, setting it to `None`.",
                    missing_metadata_key, metadata[missing_metadata_key].pl
                )

                metadata[missing_metadata_key] = None

        if not metadata:
            metadata = dict(
                source=None,
                destination=None
            )

        if not is_metadata_complete:
            _set_missing_navigation_metadata_using_llm(
                request_text, metadata
            )

        has_points = any(place for place in metadata.values())

        if has_points:
            metadata = {
                key: value.pl if value else None
                for key, value in metadata.items()
            }
        else:
            label = "chat"
            metadata = None

            LOGGER.debug(
                "metadata: no valid places"
            )
    else:
        metadata = None

    result = ClassificationResult(
        label=label,
        metadata=metadata
    )

    log_endpoint_call("classify", request, result)

    return result
