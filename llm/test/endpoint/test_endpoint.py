import abc

import json

import unittest

from pathlib import Path

from typing import Type, TypeVar, Optional

import requests

from pydantic import BaseModel

from baza_wiedzy.utils import get_cached_translation, translate

T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)

class TestEndpoint(unittest.TestCase):
    lang_from = "pl"
    lang_to = "en-US"

    _TEST_CASES_DIR = "test_cases"
    _SERVER_URL = "http://158.75.112.151:9123"

    def __init__(
        self,
        endpoint: str,
        test_case_type: Type[T],
        translated_test_case_type: Optional[Type[U]] = None,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self._api_url = f"{self._SERVER_URL}/{endpoint}"

        self._test_case_type = test_case_type
        self._translated_test_case_type = (
            translated_test_case_type or test_case_type
        )

        self._test_cases_dir = Path(self._TEST_CASES_DIR)

        self._test_cases = self._get_translated_test_cases()
        self._expected_responses = self._get_expected_responses()

        if not self._expected_responses:
            return

        n_test_cases = len(self._test_cases)
        n_expected_responses = len(self._expected_responses)

        assert n_test_cases == n_expected_responses, (
            "Expected each test case to have exactly one expected response; "
            f"got: {n_test_cases} vs {n_expected_responses}"
        )

    @abc.abstractmethod
    def _assert_api_response(
        self,
        response: dict[str],
        expected_response: Optional[dict[str]]
    ) -> None:
        pass

    @abc.abstractmethod
    def _translate_test_cases(
        self,
        test_cases: list[T]
    ) -> list[U]:
        pass

    @abc.abstractmethod
    def _get_expected_responses(self) -> Optional[list[dict[str]]]:
        pass

    @classmethod
    def _translate(cls, message: str) -> str:
        return translate(message, cls.lang_from, cls.lang_to)

    @classmethod
    def _translate_back(cls, message: str) -> str:
        return translate(message, cls.lang_to, cls.lang_from)

    def _get_translated_test_cases(self) -> list[U]:
        dir_path = self._test_cases_dir
        translated = get_cached_translation(
            pl_path=dir_path / "pl.json",
            cache_path=dir_path / "translated.json",
            translator=self._translate_test_cases,
            with_pl=False,
            model_type=self._test_case_type,
            translated_model_type=self._translated_test_case_type
        )

        return translated

    def _call_remote_endpoint(self, **kwargs) -> dict[str]:
        response = requests.post(
            self._api_url,
            json=kwargs,
            timeout=20
        )

        response = response.json()

        return response

    def _run_test_case(
        self,
        test_case: U,
        expected_response: Optional[dict[str]]
    ) -> None:
        attr_names = list(test_case.model_fields.keys())

        attrs = {
            name: getattr(test_case, name)
            for name in attr_names
        }

        def _log_field(name: str, field) -> None:
            if isinstance(field, dict):
                field = json.dumps(field, ensure_ascii=False, indent=3)

            print(">", f"{name}: {field}")

        _log_field("Endpoint params", attrs)

        response = self._call_remote_endpoint(**attrs)

        _log_field("Response", response)

        if not expected_response:
            return

        _log_field("Expecting", expected_response)

        self._assert_api_response(
            response,
            expected_response
        )

    def test_endpoint(self) -> None:
        def _print_boundary() -> None:
            print("-" * 50)

        test_cases = self._test_cases

        class_name = self.__class__.__name__

        expected_responses = self._expected_responses

        for i, test_case in enumerate(test_cases):
            _print_boundary()

            test_id = f"{i+1}/{len(test_cases)}"

            print(f"Test ('{class_name}') [{test_id}]\n")

            expected_response = expected_responses[i] if expected_responses else None

            with self.subTest(test_id):
                self._run_test_case(test_case, expected_response)

            _print_boundary()
