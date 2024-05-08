from test_endpoint_classify import MinimalClassifyTestCase, TestEndpointClassify

class TestEndpointClassifyLabelChat(TestEndpointClassify):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            "chat", MinimalClassifyTestCase,
            *args, **kwargs
        )
