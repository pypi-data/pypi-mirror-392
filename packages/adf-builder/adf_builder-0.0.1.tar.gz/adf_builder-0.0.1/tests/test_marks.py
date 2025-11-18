from adf_builder.nodes.marks import MarkEnum, Link, Color


class TestMarks:


    def test_to_json(self):
        assert MarkEnum.CODE.to_json() == {"type": "code"}
        assert MarkEnum.BOLD.to_json() == {"type": "strong"}
        assert MarkEnum.ITALIC.to_json() == {"type": "em"}
        assert MarkEnum.STRIKETHROUGH.to_json() == {"type": "strike"}
        assert MarkEnum.SUPERSCRIPT.to_json() == {"type": "subsup", "attrs": {"type": "sup"}}
        assert MarkEnum.SUBSCRIPT.to_json() == {"type": "subsup", "attrs": {"type": "sub"}}
        assert MarkEnum.UNDERLINE.to_json() == {"type": "underline"}
        assert Link(title="Test", href="example.com").to_json() == {
            "type": "link",
            "attrs": {
                "href": "example.com",
                "title": "Test"
            }
        }
        assert Color("#FFFFFF").to_json() == {
            "type": "textColor",
            "attrs": {
                "color": "#FFFFFF"
            }
        }