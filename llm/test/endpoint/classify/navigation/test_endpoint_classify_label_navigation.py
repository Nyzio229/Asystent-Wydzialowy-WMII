from typing import Literal, Optional

from test_endpoint_classify import MinimalClassifyTestCase, TestEndpointClassify

class ClassifyTestCaseLabelNavigation(MinimalClassifyTestCase):
    metadata: dict[
        Literal["source", "destination"], Optional[str]
    ]

class TestEndpointClassifyLabelNavigation(TestEndpointClassify):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            "navigation", ClassifyTestCaseLabelNavigation,
            *args, **kwargs
        )
