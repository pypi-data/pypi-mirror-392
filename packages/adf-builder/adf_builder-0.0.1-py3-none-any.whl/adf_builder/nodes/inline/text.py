from adf_builder.nodes.inline import InlineNode
from adf_builder.nodes.marks import MarkMixin, MarkEnum, Link, Color


class Text(InlineNode):

    def __init__(self, text: str):
        super().__init__()
        if text is None:
            raise ValueError(F"Text cannot be empty")
        self._payload = {
            "type": "text",
            "text": text
        }
        self._marks: list[MarkMixin] = []

    def to_json(self):
        payload = self._payload.copy()
        if self._marks:
            _marks_payload = [mark.to_json() for mark in self._marks]
            payload["marks"] = _marks_payload
        return payload

    def mark(self, mark_type: MarkMixin):
        if mark_type == MarkEnum.CODE:
            for existing_mark in self._marks:
                if not isinstance(existing_mark, MarkEnum):
                    raise ValueError(f"Code blocks can only be combined with a link")
        if isinstance(mark_type, Color):
            for existing_mark in self._marks:
                if isinstance(existing_mark, Link) or existing_mark == MarkEnum.CODE:
                    raise ValueError(f"Color cannot be set for links or code blocks")
        self._marks.append(
            mark_type
        )
        return self

    def is_marked(self):
        return True if len(self._marks) > 0 else False
