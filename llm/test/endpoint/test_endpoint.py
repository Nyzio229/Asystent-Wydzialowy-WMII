import abc

import json

import unittest

from pathlib import Path

from typing import Any, Type, TypeVar, Optional

import requests

from pydantic import BaseModel

from knowledge_base.utils import (
    get_cached_translation,
    save_json
)

T = TypeVar("T", bound=BaseModel)

class TestCaseResult(BaseModel):
    passed: bool
    response: dict[str, Any]
    expected_response: Optional[dict[str, Any]]

class TestEndpoint(unittest.TestCase):
    __TEST_CASES_DIR = "test_cases"
    __SERVER_URL = "http://158.75.112.151:9123"

    def __init__(
        self,
        endpoint: str,
        test_case_type: Type[T],
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self._api_url = f"{self.__SERVER_URL}/{endpoint}"

        self._test_case_type = test_case_type

        self._test_cases_dir = Path(
            self.__TEST_CASES_DIR
        )

        self._test_cases = self._get_translated_test_cases()
        self._expected_responses = self._get_expected_responses()

        self._last_response: dict[str] = {}

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

    def _get_endpoint_params(
        self,
        test_case: T
    ) -> dict[str]:
        return test_case.model_dump()

    @abc.abstractmethod
    def _translate_test_case(
        self,
        test_case: T
    ) -> T:
        pass

    @abc.abstractmethod
    def _get_expected_responses(self) -> Optional[list[dict[str]]]:
        pass

    def _get_translated_test_cases(self) -> list[T]:
        def _translate_test_cases(
            test_cases: list[T]
        ) -> list[T]:
            print("   * Tłumaczenie (pl -> en)...")

            translated = list(map(
                self._translate_test_case, test_cases
            ))

            return translated

        dir_path = self._test_cases_dir
        translated = get_cached_translation(
            pl_path=dir_path / "pl.json",
            cache_path=dir_path / "translated.json",
            translator=_translate_test_cases,
            with_pl=False,
            model_type=self._test_case_type
        )

        return translated

    def _call_remote_endpoint(self, **kwargs) -> dict[str]:
        response = requests.post(
            self._api_url,
            json=kwargs,
            timeout=20
        )

        response.raise_for_status()

        response = response.json()

        return response

    def _run_test_case(
        self,
        test_case: T,
        expected_response: Optional[dict[str]]
    ) -> None:
        def _log_field(name: str, field) -> None:
            if isinstance(field, dict):
                field = json.dumps(
                    field,
                    ensure_ascii=False,
                    indent=3
                )

            print(">", f"{name}: {field}")

        endpoint_params = self._get_endpoint_params(test_case)

        _log_field("Endpoint params", endpoint_params)

        response = self._call_remote_endpoint(**endpoint_params)

        _log_field("Response", response)

        self._last_response = response

        if not expected_response:
            return

        _log_field("Expecting", expected_response)

        self._assert_api_response(
            response, expected_response
        )

    def _get_test_case_result(
        self,
        test_case: T,
        expected_response: Optional[dict[str]],
        test_id: str
    ) -> TestCaseResult:
        failed = True

        with self.subTest(test_id):
            self._run_test_case(
                test_case, expected_response
            )

            failed = False

        test_case_result = TestCaseResult(
            passed=not failed,
            response=self._last_response,
            expected_response=expected_response
        )

        return test_case_result

    def test_endpoint(self) -> None:
        def _print_boundary() -> None:
            print("-" * 50)

        test_cases = self._test_cases

        n_test_cases = len(test_cases)

        class_name = self.__class__.__name__

        expected_responses = self._expected_responses

        test_case_results: list[TestCaseResult] = []

        for i, (test_case, expected_response) in enumerate(
            zip(
                test_cases,
                expected_responses
                if expected_responses
                else [None] * n_test_cases
            )
        ):
            _print_boundary()

            test_id = f"{i+1}/{n_test_cases}"

            print(f"Test ('{class_name}') [{test_id}]\n")

            test_case_result = self._get_test_case_result(
                test_case, expected_response, test_id
            )

            test_case_results.append(test_case_result)

            _print_boundary()

        serialized_test_case_results: list[
            dict[str]
        ] = list(map(
            lambda test_case_result: test_case_result.model_dump(
                exclude_none=True
            ),
            test_case_results
        ))

        test_result_file_path = Path(
            "test_result.json"
        )

        save_json(
            test_result_file_path,
            serialized_test_case_results
        )
