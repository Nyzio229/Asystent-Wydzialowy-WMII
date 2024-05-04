# for importing from `baza_wiedzy`
import sys
sys.path.append("..")

import unittest

from pathlib import Path

from typing import Literal, Optional

import requests

from pydantic import BaseModel

from baza_wiedzy.utils import get_cached_translation, translate

class NavigationTestCase(BaseModel):
    text: str
    metadata: dict[
        Literal["source", "destination"], Optional[str]
    ]

class TestEndpointClassify(unittest.TestCase):
    def setUp(self):
        self._api_url = "http://158.75.112.151:9123/classify"

        self._test_cases_dir = Path("endpoint_classify_test_cases")

        self._load_navigation_test_cases()

    @staticmethod
    def _translate(message: str) -> str:
        return translate(message, "pl", "en-US")

    def _load_navigation_test_cases(self) -> None:
        def _translate_navigation_test_cases(
            test_cases: list[NavigationTestCase]
        ) -> list[NavigationTestCase]:
            return [
                NavigationTestCase(
                    text=self._translate(test_case.text),
                    metadata=test_case.metadata
                )
                for test_case in test_cases
            ]

        root_dir = self._test_cases_dir / "navigation"
        translated: list[NavigationTestCase] = get_cached_translation(
            pl_path=root_dir / "pl.json",
            cache_path=root_dir / "translated.json",
            translator=_translate_navigation_test_cases,
            with_pl=False,
            model_type=NavigationTestCase
        )

        self._navigation_test_cases = translated

    def _classify(
        self,
        text: str
    ) -> dict[
        str, str | dict[str, Optional[str]]
    ]:
        response = requests.post(
            self._api_url,
            json=dict(
                text=text
            ),
            timeout=10
        )

        response = response.json()

        return response

    def _assert_api_response(
        self,
        query: str,
        expected_label: str,
        expected_metadata: Optional[
            dict[str, Optional[str]]
        ] = None
    ) -> None:
        response = self._classify(query)

        def _log_field(name: str, field) -> None:
            print(">", f"{name}: {field}")

        _log_field("Query", f"'{query}'")
        _log_field("Expected label", expected_label)
        _log_field("Expected metadata", expected_metadata)

        print()

        self.assertEqual(response["label"], expected_label)

        def _make_metadata_lower_case(
            metadata: dict[
                str, Optional[str]
            ]
        ) -> None:
            for key, value in metadata.items():
                if value:
                    metadata[key] = value.lower()

        response_metadata = response["metadata"]

        if expected_metadata:
            _make_metadata_lower_case(expected_metadata)
            _make_metadata_lower_case(response_metadata)

        self.assertEqual(response_metadata, expected_metadata)

    def test_loaded_navigation_test_cases(self):
        test_cases = self._navigation_test_cases
        for i, test_case in enumerate(test_cases):
            with self.subTest(msg=f"'{test_case.text}'"):
                self._assert_api_response(
                    test_case.text,
                    "navigation",
                    test_case.metadata
                )

    def test_chat_query(self):
        self._assert_api_response(
            "Can you tell me about the weather?",
            "chat",
            None
        )

if __name__ == "__main__":
    unittest.main()
