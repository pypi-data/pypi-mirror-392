from . import TopLevelNode
from .code import CodeBlock
from .paragraph import Paragraph


class BulletList(TopLevelNode):

    def __init__(self, *args: 'ListItem'):
        super().__init__()
        self._payload = {
            "type": "bulletList"
        }
        for provided_arg in args:
            if not isinstance(provided_arg, ListItem):
                raise ValueError(f"Items provided to the BulletList must be an instance of the ListItem class")
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


class OrderedList(TopLevelNode):

    def __init__(self, *args: 'ListItem', start_at=1):
        super().__init__()
        self._payload = {
            "type": "orderedList",
            "attrs": {
                "order": start_at
            },
        }
        for provided_arg in args:
            if not isinstance(provided_arg, ListItem):
                raise ValueError(f"Items provided to the OrderedList must be an instance of the ListItem class")
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



class ListItem:

    def __init__(self, *args: BulletList | OrderedList | CodeBlock | Paragraph):
        super().__init__()
        self._payload = {
            "type": "listItem"
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
