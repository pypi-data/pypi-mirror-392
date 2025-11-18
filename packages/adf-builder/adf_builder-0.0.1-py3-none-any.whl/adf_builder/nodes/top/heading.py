from . import TopLevelNode
from adf_builder.nodes.inline import InlineNode


class Heading(TopLevelNode):

    def __init__(self, *args: InlineNode, level: int):
        super().__init__()
        self._payload = {
            "type": "heading",
            "attrs": {
                "level": level
            }
        }
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
