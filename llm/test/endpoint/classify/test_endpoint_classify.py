from typing import Literal, Type, TypeVar, Optional

from pydantic import BaseModel

from test_endpoint import TestEndpoint

class MinimalClassifyTestCase(BaseModel):
    text: str

T = TypeVar("T", bound=MinimalClassifyTestCase)

class TestEndpointClassify(TestEndpoint):
    def __init__(
        self,
        label: Literal["chat", "navigation"],
        test_case_type: Type[T],
        *args, **kwargs
    ) -> None:
        self._label = label

        super().__init__(
            "classify", test_case_type, None,
            *args, **kwargs
        )

    def _assert_api_response(
        self,
        response: dict[str],
        expected_response: dict[str]
    ) -> None:
        self.assertEqual(
            response["label"],
            expected_response["label"]
        )

        def _make_metadata_lower_case(
            metadata: dict[
                str, Optional[str]
            ]
        ) -> None:
            for key, value in metadata.items():
                if value:
                    metadata[key] = value.lower()

        response_metadata = response["metadata"]
        expected_metadata = expected_response["metadata"]

        if expected_metadata:
            _make_metadata_lower_case(expected_metadata)
            _make_metadata_lower_case(response_metadata)

        self.assertEqual(response_metadata, expected_metadata)

    def _translate_test_cases(
        self,
        test_cases: list[T]
    ) -> list[T]:
        translated = list(map(
            lambda test_case: test_case.model_copy(
                update=dict(
                    text=self._translate(test_case.text)
                )
            ),
            test_cases
        ))

        return translated

    def _get_expected_responses(self) -> list[dict[str]]:
        return list(map(
            lambda test_case: dict(
                label=self._label,
                metadata=getattr(test_case, "metadata", None)
            ),
            self._test_cases
        ))
