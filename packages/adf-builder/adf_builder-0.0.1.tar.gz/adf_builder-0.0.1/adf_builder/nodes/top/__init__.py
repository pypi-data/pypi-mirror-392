from adf_builder.nodes.base import ADFNode


class TopLevelNode(ADFNode):

    def __init__(self):
        self._content = []

    def to_json(self):
        ...


from .paragraph import Paragraph
from .code import CodeBlock
from .quote import Quote
from .list import BulletList, OrderedList, CodeBlockItem, TextItem
from .heading import Heading
