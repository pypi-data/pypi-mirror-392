from . import TopLevelNode
from .code import CodeBlock
from .paragraph import Paragraph
from ..inline import Text


class BulletList(TopLevelNode):

    def __init__(self, *items: 'ListItem'):
        super().__init__()
        self._payload = {
            "type": "bulletList"
        }
        for provided_arg in items:
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

    def __init__(self, *items: 'ListItem', start_at=1):
        super().__init__()
        self._payload = {
            "type": "orderedList",
            "attrs": {
                "order": start_at
            },
        }
        for provided_arg in items:
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

    def __init__(self, item: CodeBlock | Text):
        super().__init__()
        self._payload = {
            "type": "listItem"
        }
        if isinstance(item, Text):
            item = Paragraph(item)
        self._content = [item]

    def to_json(self):
        payload = self._payload.copy()
        json_content = []
        for node in self._content:
            json_content.append(
                node.to_json()
            )
        payload["content"] = json_content
        return payload

    def add_nested(self, nested_list: OrderedList | BulletList):
        self._content.append(nested_list)
        return nested_list


class CodeBlockItem(ListItem):

    def __init__(self, code_block: CodeBlock):
        super().__init__(code_block)


class TextItem(ListItem):

    def __init__(self, text: Text):
        super().__init__(text)
