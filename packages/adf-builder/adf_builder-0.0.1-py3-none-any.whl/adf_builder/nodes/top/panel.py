from . import TopLevelNode
from .list import BulletList, OrderedList
from .paragraph import Paragraph
from .heading import Heading
from enum import Enum


class PanelType(Enum):

    INFO = "info"
    NOTE = "note"
    WARNING = "warning"
    SUCCESS = "success"
    ERROR = "error"


class Panel(TopLevelNode):

    def __init__(self, *args: Heading | BulletList | OrderedList | Paragraph, panel_type: PanelType):
        super().__init__()
        self._payload = {
            "type": "panel",
            "attrs": {
                "panelType": panel_type.value
            }
        }

    def to_json(self):
        payload = self._payload.copy()
        json_content = []
        for node in self._content:
            json_content.append(
                node.to_json()
            )
        payload["content"] = json_content
        return payload
