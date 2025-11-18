from . import TopLevelNode
from .code import CodeBlock
from .paragraph import Paragraph
from .list import BulletList, OrderedList


class Quote(TopLevelNode):

    def __init__(self, *args: Paragraph | BulletList | OrderedList | CodeBlock):
        super().__init__()
        self._payload = {
            "type": "blockquote"
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
