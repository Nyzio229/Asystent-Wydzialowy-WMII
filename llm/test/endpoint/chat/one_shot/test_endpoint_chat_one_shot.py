from typing import Optional

from pydantic import BaseModel

from test_endpoint import TestEndpoint

class ChatOneShotTestCase(BaseModel):
    text: str

class ChatTestCase(BaseModel):
    messages: list[dict[str, str]]

class TestEndpointChatOneShot(TestEndpoint):
    def __init__(
        self, *args, **kwargs
    ) -> None:
        super().__init__(
            "chat", ChatOneShotTestCase, ChatTestCase,
            *args, **kwargs
        )

    def _assert_api_response(
        self,
        response: dict[str],
        expected_response: None
    ) -> None:
        pass

    def _translate_test_cases(
        self,
        test_cases: list[ChatOneShotTestCase]
    ) -> list[ChatTestCase]:
        translated = list(map(
            lambda test_case: ChatTestCase(
                messages=[
                    dict(
                        role="user",
                        content=self._translate(test_case.text)
                    )
                ]
            ),
            test_cases
        ))

        return translated

    def _get_expected_responses(self) -> None:
        return None
