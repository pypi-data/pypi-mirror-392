from . import TopLevelNode
from adf_builder.nodes.inline import InlineNode


class Paragraph(TopLevelNode):

    def __init__(self, *args: InlineNode):
        super().__init__()
        self._payload = {
            "type": "paragraph"
        }
        for inline_node in args:
            self._content.append(
                inline_node
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
