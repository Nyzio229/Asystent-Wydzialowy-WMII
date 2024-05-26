import os
import sys
import glob

import types

import inspect

import unittest

import importlib.util

from pathlib import Path

from typing import Callable, Optional, Type

from pydantic import BaseModel

class TestModuleDescriptor(BaseModel):
    dir_path: Path
    module_name: str

    def get_module(self) -> types.ModuleType:
        module_name = self.module_name
        file_path = self.dir_path / f"{module_name}.py"

        spec = importlib.util.spec_from_file_location(
            module_name, file_path
        )

        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)

        return module

    @staticmethod
    def _to_camel_case(snake_case: str) -> str:
        return "".join(
            x.capitalize()
            for x in snake_case.lower().split("_")
        )

    def get_test_class(self) -> Type[unittest.TestCase]:
        module = self.get_module()

        module_name = self.module_name

        exported_classes_with_names = inspect.getmembers(
            module,
            lambda member: (
                inspect.isclass(member) and
                member.__module__ == module_name
            )
        )

        test_class_name = self._to_camel_case(module_name)

        exported_classes_with_names = filter(
            lambda pair: pair[0] == test_class_name,
            exported_classes_with_names
        )

        exported_classes = list(map(
            lambda pair: pair[1],
            exported_classes_with_names
        ))

        assert len(exported_classes) == 1, (
            f"Expected exactly one exported test class "
            f"named '{test_class_name}', got: {exported_classes}"
        )

        test_class = exported_classes[0]

        return test_class

def get_test_module_descriptors(
    dir_paths: list[Path]
) -> list[TestModuleDescriptor]:
    dir_paths = list(filter(
        lambda dir_path: not any(
            other
            for other in dir_paths
            if dir_path == other.parent
        ), dir_paths
    ))

    test_module_descriptors: list[TestModuleDescriptor] = []

    for dir_path in dir_paths:
        file_pattern = "test_*.py"
        glob_path = str(dir_path / file_pattern)
        paths = glob.glob(glob_path)

        assert len(paths) == 1, (
            f"Expected exactly one '{file_pattern}' "
            f"script at '{dir_path}', got: {paths}"
        )

        script_path = paths[0]
        module_name = Path(script_path).stem

        test_module_descriptors.append(TestModuleDescriptor(
            dir_path=dir_path,
            module_name=module_name
        ))

    return test_module_descriptors

def get_script_subdirs_paths() -> list[Path]:
    dir_paths = [
        Path(x[0])
        for x in os.walk(".")
        if x[0] != "."
    ]

    dirs_to_skip = {
        "test_cases", "__pycache__"
    }

    dir_paths = list(filter(
        lambda path: path.name not in dirs_to_skip,
        dir_paths
    ))

    return dir_paths

def extend_sys_path(dir_paths: list[Path]) -> None:
    dir_paths = list(map(str, dir_paths))

    # append `".."`` to be able to import from `knowledge_base``
    dir_paths.append("..")

    sys.path += dir_paths

def run_test(test_class: Type[unittest.TestCase]) -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        test_class
    )

    unittest.TextTestRunner().run(suite)

def run_tests(
    test_dir_filter: Optional[
        Callable[[Path], bool]
    ] = None
) -> None:
    dir_paths = get_script_subdirs_paths()

    extend_sys_path(dir_paths)

    test_module_descriptors = get_test_module_descriptors(
        dir_paths
    )

    if test_dir_filter:
        test_module_descriptors = list(filter(
            lambda descriptor: test_dir_filter(
                descriptor.dir_path
            ),
            test_module_descriptors
        ))

    n_tests = len(test_module_descriptors)

    print(
        f"Found {n_tests} test{'' if n_tests == 1 else 's'}:"
    )

    for descriptor in test_module_descriptors:
        print(
            f"   * {descriptor.module_name}.py ('{descriptor.dir_path}')"
        )

    print()

    base_cwd = os.getcwd()

    for i, descriptor in enumerate(
        test_module_descriptors
    ):
        test_class = descriptor.get_test_class()

        # change cwd in order to see the "test_cases" dir
        os.chdir(descriptor.dir_path)

        print(
            f"[{i+1}/{n_tests}] Running test ({descriptor.module_name})... "
        )

        run_test(test_class)

        os.chdir(base_cwd)

def main() -> None:
    run_tests()

if __name__ == "__main__":
    main()
