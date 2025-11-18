import re
from enum import Enum


class MarkMixin:

    def to_json(self):
        ...


class MarkEnum(MarkMixin, Enum):

    CODE = {"type": "code"}
    BOLD = {"type": "strong"}
    ITALIC = {"type": "em"}
    STRIKETHROUGH = {"type": "strike"}
    SUPERSCRIPT = {"type": "subsup", "attrs": {"type": "sup"}}
    SUBSCRIPT = {"type": "subsup", "attrs": {"type": "sub"}}
    UNDERLINE = {"type": "underline"}

    def to_json(self):
        return self.value


class Link(MarkMixin):

    def __init__(self, title: str, href: str):
        self._payload = {
            "type": "link",
            "attrs": {
                "href": href,
                "title": title
            }
        }

    def to_json(self):
        return self._payload


class Color(MarkMixin):

    def __init__(self, color_hex: str):
        match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color_hex)
        if not match:
            raise ValueError(f"{color_hex} is not a valid HEX Color Code")
        self._payload = {
            "type": "textColor",
            "attrs": {
                "color": color_hex
            }
        }

    def to_json(self):
        return self._payload
