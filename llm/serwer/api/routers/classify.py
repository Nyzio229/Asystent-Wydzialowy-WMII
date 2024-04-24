from typing import Generic, Literal, Optional, Type, TypeVar

import json

from fastapi import APIRouter

from pydantic import BaseModel, Field

from llama_cpp import LogitsProcessorList

from lmformatenforcer import JsonSchemaParser
from lmformatenforcer import CharacterLevelParser
from lmformatenforcer.integrations.llamacpp import build_llamacpp_logits_processor, build_token_enforcer_tokenizer_data

from common import common

class ClassificationRequest(BaseModel):
    text: str

class CategoryNavigationMetadata(BaseModel):
    source: Optional[str] = Field(
        description=(
            "Starting point for navigation. " +
            "MUST be ONLY the name of the starting place and "
            "MUST be specified explicitly " +
            "(by saying e.g. " +
            "'How to get from <the source> to (...)?'" +
            ")."
        )
    )

    destination: str = Field(
        description=(
            "Destination point for navigation. " +
            "MUST be ONLY the name of the destination place. "
        )
    )

class ClassificationLabel(BaseModel):
    label: Literal["navigation", "chat"] = Field(
        description=("The category of the user's prompt: " +
                     "'navigation' for navigation queries (within the university campus) or " + 
                     "'chat' for general conversation or if you are unsure of the category.")
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
        "You are a helpful, respectful and honest assistant. " +
        "Always answer as helpfully as possible, while being safe. " +
        "Your answers should not include any harmful, unethical, racist, " +
        "sexist, toxic, dangerous, or illegal content. " +
        "Please ensure that your responses are socially unbiased and positive in nature. " +
        "If a question does not make any sense, or is not factually coherent, explain why " +
        "instead of answering something not correct. " +
        "If you don't know the answer to a question, please don't share false information."
    )

    def _get_prompt(
        message: str,
        system_prompt: str = _DEFAULT_SYSTEM_PROMPT
    ) -> str:
        return f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{message} [/INST]"

    tokenizer_data = build_token_enforcer_tokenizer_data(common.llm)

    def _infer_with_character_level_parser(
        prompt: str,
        character_level_parser: Optional[CharacterLevelParser]
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
            max_tokens=100
        )

        response = output["choices"][0]["text"]

        print("[Classify]")
        print(" * prompt:", prompt)
        print(" * response:", response)
        print("\n")

        return response

    T = TypeVar("T", bound=BaseModel)

    def _json_classify(
        task: str,
        response_type: Type[T],
    ) -> T:
        response_schema = response_type.model_json_schema()
        response_schema_str = json.dumps(response_schema)

        prompt = (
            f"Please {task} the user's query (given at the end). " +
            "You MUST answer using the following json schema:"
            f"{response_schema_str}\n\n" +
            "Here is the user's query:\n" +
            request.text
        )

        prompt = _get_prompt(prompt)
        response = _infer_with_character_level_parser(prompt, JsonSchemaParser(response_schema))
        result = response_type.model_validate(json.loads(response))

        return result

    result_label: ClassificationLabel = _json_classify(
        "categorize",
        ClassificationLabel
    )

    if result_label.label == "navigation":
        metadata: CategoryNavigationMetadata = _json_classify(
            "extract information from",
            CategoryNavigationMetadata
        )
    else:
        metadata = None

    result = ClassificationResult(
        label=result_label.label,
        metadata=metadata
    )

    return result
