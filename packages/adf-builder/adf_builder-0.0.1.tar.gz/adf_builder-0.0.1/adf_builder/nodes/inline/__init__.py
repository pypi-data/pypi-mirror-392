from adf_builder.nodes.base import ADFNode


class InlineNode(ADFNode):

    def __init__(self):
        self._content = []

    def to_json(self):
        pass


from .text import Text
