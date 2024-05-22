from test_text_endpoint import TextTestCase

from test_endpoint_classify import TestEndpointClassify

class TestEndpointClassifyLabelChat(TestEndpointClassify):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            "chat", TextTestCase,
            *args, **kwargs
        )
