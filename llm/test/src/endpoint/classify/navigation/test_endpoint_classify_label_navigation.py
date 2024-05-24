from typing import Literal, Optional

from test_text_endpoint import TextTestCase

from test_endpoint_classify import TestEndpointClassify

class ClassifyTestCaseLabelNavigation(TextTestCase):
    metadata: dict[
        Literal["source", "destination"], Optional[str]
    ]

class TestEndpointClassifyLabelNavigation(TestEndpointClassify):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            "navigation", ClassifyTestCaseLabelNavigation,
            *args, **kwargs
        )
