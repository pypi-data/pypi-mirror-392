from . import TopLevelNode


class Divider(TopLevelNode):

    def to_json(self):
        return {
            "type": "rule"
        }
