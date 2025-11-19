"""Integration tests for the markdown converter."""

import os

from martian import markdown_to_blocks, markdown_to_rich_text
from martian import notion
from martian.notion.common import LIMITS


def read_fixture(filename: str) -> str:
    """Read a test fixture file."""
    fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


class TestMarkdownToBlocks:
    """Tests for markdown_to_blocks function."""

    def test_convert_markdown_to_blocks(self):
        """Test converting markdown to blocks."""
        text = """
hello _world_ 
*** 
## heading2
* [x] todo
"""
        actual = markdown_to_blocks(text)

        expected = [
            notion.paragraph([
                notion.rich_text("hello "),
                notion.rich_text("world", {"annotations": {"italic": True}}),
            ]),
            notion.divider(),
            notion.heading_two([notion.rich_text("heading2")]),
            notion.to_do(True, [notion.rich_text("todo")]),
        ]

        assert actual == expected

    def test_deal_with_code_use_plain_text_by_default(self):
        """Test code blocks use plain text by default."""
        text = """
## Code
```
const hello = "hello";
```
"""
        actual = markdown_to_blocks(text)

        expected = [
            notion.heading_two([notion.rich_text("Code")]),
            notion.code([notion.rich_text('const hello = "hello";')], "plain text"),
        ]

        assert actual == expected

    def test_deal_with_code_handle_notion_highlight_keys(self):
        """Test code blocks handle Notion highlight keys."""
        text = """
## Code
``` webassembly
const hello = "hello";
```
"""
        actual = markdown_to_blocks(text)

        expected = [
            notion.heading_two([notion.rich_text("Code")]),
            notion.code([notion.rich_text('const hello = "hello";')], "webassembly"),
        ]

        assert actual == expected

    def test_deal_with_code_handle_linguist_highlight_keys(self):
        """Test code blocks handle Linguist highlight keys."""
        text = """
## Code
``` ts
const hello = "hello";
```
"""
        actual = markdown_to_blocks(text)

        expected = [
            notion.heading_two([notion.rich_text("Code")]),
            notion.code([notion.rich_text('const hello = "hello";')], "typescript"),
        ]

        assert actual == expected

    def test_deal_with_complex_items(self):
        """Test dealing with complex items."""
        text = read_fixture("complex-items.md")
        actual = markdown_to_blocks(text)

        expected = [
            notion.heading_one([notion.rich_text("Images")]),
            notion.paragraph([notion.rich_text("This is a paragraph!")]),
            notion.blockquote([], [notion.paragraph([notion.rich_text("Quote")])]),
            notion.paragraph([notion.rich_text("Paragraph")]),
            notion.image("https://url.com/image.jpg"),
            notion.table_of_contents(),
        ]

        assert actual == expected

    def test_deal_with_divider(self):
        """Test dealing with divider."""
        text = read_fixture("divider.md")
        actual = markdown_to_blocks(text)

        expected = [
            notion.paragraph([notion.rich_text("Thematic Break")]),
            notion.divider(),
            notion.paragraph([notion.rich_text("Divider")]),
            notion.divider(),
            notion.paragraph([notion.rich_text("END")]),
        ]

        assert actual == expected

    def test_break_up_large_elements(self):
        """Test breaking up large elements."""
        text = read_fixture("large-item.md")
        actual = markdown_to_blocks(text)

        # Check that the second block (paragraph) has multiple rich text items
        if actual[1]["type"] == "paragraph":
            text_array = actual[1]["paragraph"]["rich_text"]
            assert len(text_array) == 9

    def test_deal_with_lists(self):
        """Test dealing with lists."""
        text = read_fixture("list.md")
        actual = markdown_to_blocks(text)

        expected = [
            notion.heading_one([notion.rich_text("List")]),
            notion.bulleted_list_item(
                [notion.rich_text("Item 1")],
                [notion.bulleted_list_item([notion.rich_text("Sub Item 1")], [])],
            ),
            notion.bulleted_list_item([notion.rich_text("Item 2")]),
        ]

        assert actual == expected

    def test_deal_with_tables(self):
        """Test dealing with tables."""
        text = read_fixture("table.md")
        actual = markdown_to_blocks(text)

        expected = [
            notion.heading_one([notion.rich_text("Table")]),
            notion.table(
                [
                    notion.table_row([
                        [notion.rich_text("First Header")],
                        [notion.rich_text("Second Header")],
                    ]),
                    notion.table_row([
                        [notion.rich_text("Content Cell")],
                        [notion.rich_text("Content Cell")],
                    ]),
                    notion.table_row([
                        [notion.rich_text("Content Cell")],
                        [notion.rich_text("Content Cell")],
                    ]),
                ],
                2,
            ),
        ]

        assert actual == expected

    def test_convert_markdown_to_blocks_deal_with_images_strict_mode(self):
        """Test converting markdown to blocks - deal with images - strict mode."""
        text = read_fixture("images.md")
        actual = markdown_to_blocks(text, {"strictImageUrls": True})

        expected = [
            notion.heading_one([notion.rich_text("Images")]),
            notion.paragraph([
                notion.rich_text("This is an image in a paragraph "),
                notion.rich_text(", which isnt supported in Notion."),
            ]),
            notion.image("https://image.com/url.jpg"),
            notion.image("https://image.com/paragraph.jpg"),
            notion.paragraph([notion.rich_text("https://image.com/blah")]),
        ]

        assert actual == expected

    def test_convert_markdown_to_blocks_deal_with_images_not_strict_mode(self):
        """Test converting markdown to blocks - deal with images - not strict mode."""
        text = read_fixture("images.md")
        actual = markdown_to_blocks(text, {"strictImageUrls": False})

        expected = [
            notion.heading_one([notion.rich_text("Images")]),
            notion.paragraph([
                notion.rich_text("This is an image in a paragraph "),
                notion.rich_text(", which isnt supported in Notion."),
            ]),
            notion.image("https://image.com/url.jpg"),
            notion.image("https://image.com/paragraph.jpg"),
            notion.image("https://image.com/blah"),
        ]

        assert actual == expected

    def test_parse_math(self):
        """Test parsing math."""
        text = read_fixture("math.md")
        actual = markdown_to_blocks(text)

        expected = [
            notion.paragraph([
                notion.rich_text("Lift("),
                notion.rich_text("L", {"type": "equation"}),
                notion.rich_text(") can be determined by Lift Coefficient ("),
                notion.rich_text("C_L", {"type": "equation"}),
                notion.rich_text(") like the following\nequation."),
            ]),
            notion.equation("L = \\frac{1}{2} \\rho v^2 S C_L\\\\\ntest"),
        ]

        assert actual == expected

    def test_split_paragraphs_on_hard_line_breaks(self):
        """Test splitting paragraphs on hard line breaks."""
        text = "You can _italicize_ or **bold** text.  \nThis is the second line of text.\nAnd this is in the same line"

        actual = markdown_to_blocks(text)

        expected = [
            notion.paragraph([
                notion.rich_text("You can "),
                notion.rich_text("italicize", {"annotations": {"italic": True}}),
                notion.rich_text(" or "),
                notion.rich_text("bold", {"annotations": {"bold": True}}),
                notion.rich_text(" text."),
            ]),
            notion.paragraph([
                notion.rich_text("This is the second line of text.\nAnd this is in the same line"),
            ]),
        ]

        assert actual == expected


class TestMarkdownToRichText:
    """Tests for markdown_to_rich_text function."""

    def test_convert_markdown_to_rich_text(self):
        """Test converting markdown to rich text."""
        text = "hello [_url_](https://example.com)"
        actual = markdown_to_rich_text(text)

        expected = [
            notion.rich_text("hello "),
            notion.rich_text("url", {
                "annotations": {"italic": True},
                "url": "https://example.com",
            }),
        ]

        assert actual == expected

    def test_convert_markdown_with_invalid_link_to_rich_text_without_link(self):
        """Test converting markdown with invalid link like "#title2" to rich text without link."""
        text = "hello [url](#head)"
        actual = markdown_to_rich_text(text)

        expected = [notion.rich_text("hello "), notion.rich_text("url")]
        assert actual == expected

    def test_convert_markdown_with_multiple_newlines_to_rich_text(self):
        """Test converting markdown with multiple newlines to rich text."""
        text = "hello\n\n[url](http://google.com)"
        actual = markdown_to_rich_text(text)

        expected = [
            notion.rich_text("hello"),
            notion.rich_text("url", {"url": "http://google.com"}),
        ]

        assert actual == expected

    def test_truncate_items_when_truncate_is_true(self):
        """Test truncating items when options.notionLimits.truncate = true."""
        text = "a *a* " * (LIMITS.RICH_TEXT_ARRAYS + 10)

        actual_default = markdown_to_rich_text(text)
        actual_explicit = markdown_to_rich_text(text, {"notionLimits": {"truncate": True}})

        assert len(actual_default) == LIMITS.RICH_TEXT_ARRAYS
        assert len(actual_explicit) == LIMITS.RICH_TEXT_ARRAYS

    def test_not_truncate_items_when_truncate_is_false(self):
        """Test not truncating items when options.notionLimits.truncate = false."""
        text = "a *a* " * (LIMITS.RICH_TEXT_ARRAYS + 10)

        actual = markdown_to_rich_text(text, {"notionLimits": {"truncate": False}})

        assert len(actual) > LIMITS.RICH_TEXT_ARRAYS

    def test_call_callback_when_onError_is_defined(self):
        """Test calling the callback when options.notionLimits.onError is defined."""
        text = "a *a* " * (LIMITS.RICH_TEXT_ARRAYS + 10)
        errors = []

        def on_error(err):
            errors.append(err)

        markdown_to_rich_text(text, {"notionLimits": {"onError": on_error}})

        assert len(errors) == 1
        assert isinstance(errors[0], Exception)

    def test_ignore_unsupported_elements_by_default(self):
        """Test ignoring unsupported elements by default."""
        text1 = "# Header first\nOther text"
        text2 = "Other text\n# Header second"

        actual1 = markdown_to_rich_text(text1)
        actual2 = markdown_to_rich_text(text2)

        expected = [notion.rich_text("Other text")]

        assert actual1 == expected
        assert actual2 == expected

    def test_ignore_unsupported_elements_when_nonInline_is_ignore(self):
        """Test ignoring unsupported elements when nonInline = 'ignore'."""
        text = "# Header first\nOther text"

        actual = markdown_to_rich_text(text, {"nonInline": "ignore"})

        expected = [notion.rich_text("Other text")]

        assert actual == expected

    def test_throw_when_unsupported_element_and_nonInline_is_throw(self):
        """Test throwing when there's an unsupported element and nonInline = 'throw'."""
        text = "# Header first\nOther text"

        try:
            markdown_to_rich_text(text, {"nonInline": "throw"})
            assert False, "Should have thrown"
        except Exception:
            pass

        # Should not throw with 'ignore'
        try:
            markdown_to_rich_text(text, {"nonInline": "ignore"})
        except Exception:
            assert False, "Should not have thrown"

