from test_endpoint_classify import MinimalClassifyTestCase, TestEndpointClassify

class TestEndpointClassifyLabelChat(TestEndpointClassify):
    def __init__(self, method_name: str) -> None:
        super().__init__(
            method_name, "chat", MinimalClassifyTestCase
        )
