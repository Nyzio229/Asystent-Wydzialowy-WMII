from typing import Type, TypeVar

from pydantic import BaseModel

from test_endpoint import TestEndpoint

from knowledge_base.src.utils import translate_pl_to_en

class TextTestCase(BaseModel):
    text: str

T = TypeVar("T", bound=TextTestCase)

class TestTextEndpoint(TestEndpoint):
    def __init__(
        self,
        endpoint: str,
        test_case_type: Type[T],
        *args, **kwargs
    ) -> None:
        super().__init__(
            endpoint, test_case_type,
            *args, **kwargs
        )

    def _translate_test_case(
        self,
        test_case: T
    ) -> T:
        translated = test_case.model_copy(
            update=dict(
                text=translate_pl_to_en(
                    test_case.text
                )
            )
        )

        return translated
