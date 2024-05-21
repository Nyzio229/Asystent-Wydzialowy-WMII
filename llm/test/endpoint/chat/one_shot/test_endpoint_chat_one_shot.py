from test_text_endpoint import TextTestCase, TestTextEndpoint

class TestEndpointChatOneShot(TestTextEndpoint):
    def __init__(
        self, *args, **kwargs
    ) -> None:
        super().__init__(
            "chat", TextTestCase,
            *args, **kwargs
        )

    def _assert_api_response(
        self,
        response: dict[str],
        expected_response: None
    ) -> None:
        pass

    def _get_endpoint_params(
        self,
        test_case: TextTestCase
    ) -> dict[
        str, list[dict[str, str]]
    ]:
        return dict(
            messages=[
                dict(
                    role="user",
                    content=test_case.text
                )
            ]
        )

    def _get_expected_responses(self) -> None:
        return None
