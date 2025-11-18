from adf_builder.nodes.top import TopLevelNode


class ADFDocument:

    def __init__(self, *args: TopLevelNode):
        self._payload: dict = {
            "version": 1,
            "type": "doc",
        }
        self._content = []
        for provided_arg in args:
            self._content.append(
                provided_arg
            )

    def to_json(self):
        payload = self._payload.copy()
        json_content = []
        for node in self._content:
            json_content.append(
                node.to_json()
            )
        payload["content"] = json_content
        return payload
