from . import TopLevelNode
from adf_builder.nodes.inline.text import Text


class CodeBlock(TopLevelNode):

    def __init__(self, code: str, language: str = "text"):
        super().__init__()
        self._payload = {
            "type": "codeBlock",
            "attrs": {
                "language": language
            }
        }
        if not isinstance(code, str):
            raise ValueError(f"Code blocks only accept unformatted strings")
        self._item = Text(code)

    def to_json(self):
        payload = self._payload.copy()
        payload["content"] = [self._item.to_json()]
        return payload
