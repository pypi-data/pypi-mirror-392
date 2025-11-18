from adf_builder.doc import ADFDocument
from adf_builder.nodes.inline import Text
from adf_builder.nodes.marks import MarkEnum
from adf_builder.nodes.top import Paragraph


class TestADFDocument:


    def test_creation(self):
        payload = ADFDocument().to_json()
        assert payload.get('version') == 1
        assert payload.get('type') == 'doc'
        assert payload.get('content') == []

    def test_simple_doc(self):
        doc = ADFDocument(
            Paragraph(
                Text(
                    "This is a test string!"
                )
            )
        )
        assert doc.to_json() == {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a test string!"
                        }
                    ]
                }
            ]
        }

    def test_formatted_doc(self):
        formatted_doc = ADFDocument(
            Paragraph(
                Text(
                    "A "
                ),
                Text("simple").mark(MarkEnum.BOLD),
                Text(
                    " text string!"
                )
            )
        )
        assert formatted_doc.to_json() == {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "A "
                        },
                        {
                            "type": "text",
                            "text": "simple",
                            "marks": [
                                {
                                    "type": "strong"
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": " text string!"
                        }
                    ]
                }
            ]
        }
