"""Unit tests for the parser module."""

from martian import markdown as md
from martian import notion
from martian.parser.internal import parse_blocks, parse_rich_text


def test_parse_paragraph_with_nested_annotations():
    """Test parsing paragraph with nested annotations."""
    ast = md.root(
        md.paragraph(
            md.text("Hello "),
            md.emphasis(md.text("world "), md.strong(md.text("foo"))),
            md.text("! "),
            md.inline_code("code"),
        )
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.paragraph([
            notion.rich_text("Hello "),
            notion.rich_text("world ", {"annotations": {"italic": True}}),
            notion.rich_text("foo", {"annotations": {"italic": True, "bold": True}}),
            notion.rich_text("! "),
            notion.rich_text("code", {"annotations": {"code": True}}),
        ])
    ]

    assert actual == expected


def test_parse_text_with_hrefs_and_annotations():
    """Test parsing text with links and annotations."""
    ast = md.root(
        md.paragraph(
            md.text("hello world "),
            md.link(
                "https://example.com",
                md.text("this is a "),
                md.emphasis(md.text("url")),
            ),
            md.text(" end"),
        )
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.paragraph([
            notion.rich_text("hello world "),
            notion.rich_text("this is a ", {"url": "https://example.com"}),
            notion.rich_text("url", {
                "annotations": {"italic": True},
                "url": "https://example.com",
            }),
            notion.rich_text(" end"),
        ])
    ]

    assert actual == expected


def test_parse_thematic_breaks():
    """Test parsing thematic breaks (horizontal rules)."""
    ast = md.root(
        md.paragraph(md.text("hello")),
        md.thematic_break(),
        md.paragraph(md.text("world")),
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.paragraph([notion.rich_text("hello")]),
        notion.divider(),
        notion.paragraph([notion.rich_text("world")]),
    ]

    assert actual == expected


def test_parse_headings():
    """Test parsing headings."""
    ast = md.root(
        md.heading(1, md.text("heading1")),
        md.heading(2, md.text("heading2")),
        md.heading(3, md.text("heading3")),
        md.heading(4, md.text("heading4")),
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.heading_one([notion.rich_text("heading1")]),
        notion.heading_two([notion.rich_text("heading2")]),
        notion.heading_three([notion.rich_text("heading3")]),
        notion.heading_three([notion.rich_text("heading4")]),
    ]

    assert actual == expected


def test_parse_code_block_with_no_language():
    """Test parsing code block without language."""
    ast = md.root(
        md.paragraph(md.text("hello")),
        md.code("const foo = () => {}", None),
    )

    actual = parse_blocks(ast)

    expected = [
        notion.paragraph([notion.rich_text("hello")]),
        notion.code([notion.rich_text("const foo = () => {}")], "plain text"),
    ]

    assert actual == expected


def test_parse_code_block_with_language():
    """Test parsing code block with language."""
    ast = md.root(
        md.paragraph(md.text("hello")),
        md.code("public class Foo {}", "java"),
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.paragraph([notion.rich_text("hello")]),
        notion.code([notion.rich_text("public class Foo {}")], "java/c/c++/c#"),
    ]

    assert actual == expected


def test_parse_code_block_with_unsupported_language():
    """Test parsing code block with unsupported language."""
    ast = md.root(
        md.paragraph(md.text("hello")),
        md.code("const foo = () => {}", "not-supported"),
    )

    actual = parse_blocks(ast)

    expected = [
        notion.paragraph([notion.rich_text("hello")]),
        notion.code([notion.rich_text("const foo = () => {}")], "plain text"),
    ]

    assert actual == expected


def test_parse_blockquote():
    """Test parsing blockquote."""
    ast = md.root(
        md.blockquote(
            md.heading(1, md.text("hello"), md.emphasis(md.text("world"))),
        )
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.blockquote(
            [],
            [
                notion.heading_one([
                    notion.rich_text("hello"),
                    notion.rich_text("world", {"annotations": {"italic": True}}),
                ]),
            ],
        )
    ]

    assert actual == expected


def test_parse_callout_with_emoji_and_formatting():
    """Test parsing callout with emoji and formatting."""
    ast = md.root(
        md.blockquote(
            md.paragraph(
                md.text("📘 "),
                md.strong(md.text("Note:")),
                md.text(" Important "),
                md.emphasis(md.text("information")),
            )
        )
    )

    actual = parse_blocks(ast, {
        "allowUnsupportedObjectType": False,
        "strictImageUrls": True,
        "enableEmojiCallouts": True,
    })

    expected = [
        notion.callout(
            [
                notion.rich_text("Note:", {"annotations": {"bold": True}}),
                notion.rich_text(" Important "),
                notion.rich_text("information", {"annotations": {"italic": True}}),
            ],
            "📘",
            "blue_background",
            [],
        )
    ]

    assert actual == expected


def test_parse_callout_with_children_blocks():
    """Test parsing callout with child blocks."""
    ast = md.root(
        md.blockquote(
            md.paragraph(md.text("🚧 Under Construction")),
            md.paragraph(md.text("More details:")),
            md.unordered_list(
                md.list_item(md.paragraph(md.text("Work in progress"))),
            ),
        )
    )

    actual = parse_blocks(ast, {
        "allowUnsupportedObjectType": False,
        "strictImageUrls": True,
        "enableEmojiCallouts": True,
    })

    expected = [
        notion.callout(
            [notion.rich_text("Under Construction")],
            "🚧",
            "yellow_background",
            [
                notion.paragraph([notion.rich_text("More details:")]),
                notion.bulleted_list_item([notion.rich_text("Work in progress")], []),
            ],
        )
    ]

    assert actual == expected


def test_parse_list():
    """Test parsing lists."""
    ast = md.root(
        md.paragraph(md.text("hello")),
        md.unordered_list(
            md.list_item(md.paragraph(md.text("a"))),
            md.list_item(md.paragraph(md.emphasis(md.text("b")))),
            md.list_item(md.paragraph(md.strong(md.text("c")))),
        ),
        md.ordered_list(md.list_item(md.paragraph(md.text("d")))),
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.paragraph([notion.rich_text("hello")]),
        notion.bulleted_list_item([notion.rich_text("a")]),
        notion.bulleted_list_item([
            notion.rich_text("b", {"annotations": {"italic": True}})
        ]),
        notion.bulleted_list_item([
            notion.rich_text("c", {"annotations": {"bold": True}})
        ]),
        notion.numbered_list_item([notion.rich_text("d")]),
    ]

    assert actual == expected


def test_split_paragraphs_on_hard_line_breaks():
    """Test splitting paragraphs on hard line breaks."""
    # Simulate a break node
    br = {"type": "break"}

    ast = md.root(
        md.paragraph(
            md.text("You can "),
            md.emphasis(md.text("italicize")),
            md.text(" or "),
            md.strong(md.text("bold")),
            md.text(" text."),
            br,  # type: ignore
            md.text("This is the second line of text"),
        )
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.paragraph([
            notion.rich_text("You can "),
            notion.rich_text("italicize", {"annotations": {"italic": True}}),
            notion.rich_text(" or "),
            notion.rich_text("bold", {"annotations": {"bold": True}}),
            notion.rich_text(" text."),
        ]),
        notion.paragraph([notion.rich_text("This is the second line of text")]),
    ]

    assert actual == expected


def test_parse_github_extensions():
    """Test parsing GitHub Flavored Markdown extensions."""
    ast = md.root(
        md.paragraph(
            md.link("https://example.com", md.text("https://example.com")),
        ),
        md.paragraph(md.strikethrough(md.text("strikethrough content"))),
        md.table(
            md.table_row(
                md.table_cell(md.text("a")),
                md.table_cell(md.text("b")),
                md.table_cell(md.text("c")),
                md.table_cell(md.text("d")),
            ),
        ),
        md.unordered_list(
            md.checked_list_item(False, md.paragraph(md.text("to do"))),
            md.checked_list_item(True, md.paragraph(md.text("done"))),
        ),
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.paragraph([
            notion.rich_text("https://example.com", {"url": "https://example.com"}),
        ]),
        notion.paragraph([
            notion.rich_text("strikethrough content", {
                "annotations": {"strikethrough": True}
            }),
        ]),
        notion.table(
            [
                notion.table_row([
                    [notion.rich_text("a")],
                    [notion.rich_text("b")],
                    [notion.rich_text("c")],
                    [notion.rich_text("d")],
                ]),
            ],
            4,
        ),
        notion.to_do(False, [notion.rich_text("to do")]),
        notion.to_do(True, [notion.rich_text("done")]),
    ]

    assert actual == expected


def test_parse_rich_text():
    """Test parsing rich text."""
    ast = md.root(
        md.paragraph(
            md.text("a"),
            md.strong(md.emphasis(md.text("b")), md.text("c")),
            md.link("https://example.com", md.text("d")),
        )
    )

    actual = parse_rich_text(ast)

    expected = [
        notion.rich_text("a"),
        notion.rich_text("b", {"annotations": {"italic": True, "bold": True}}),
        notion.rich_text("c", {"annotations": {"bold": True}}),
        notion.rich_text("d", {"url": "https://example.com"}),
    ]

    assert actual == expected


def test_parse_basic_gfm_alert():
    """Test parsing basic GFM alert."""
    ast = md.root(
        md.blockquote(
            md.paragraph(md.text("[!NOTE]")),
            md.paragraph(md.text("Important information")),
        )
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.callout(
            [notion.rich_text("Note")],
            "📘",
            "blue_background",
            [
                notion.paragraph([notion.rich_text("Important information")]),
            ],
        )
    ]

    assert actual == expected


def test_parse_gfm_alert_with_formatted_content():
    """Test parsing GFM alert with formatted content."""
    ast = md.root(
        md.blockquote(
            md.paragraph(md.text("[!TIP]")),
            md.paragraph(md.text("This is a tip with "), md.inline_code("code")),
        )
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.callout(
            [notion.rich_text("Tip")],
            "💡",
            "green_background",
            [
                notion.paragraph([
                    notion.rich_text("This is a tip with "),
                    notion.rich_text("code", {"annotations": {"code": True}}),
                ]),
            ],
        )
    ]

    assert actual == expected


def test_parse_gfm_alert_with_multiple_paragraphs_and_lists():
    """Test parsing GFM alert with multiple paragraphs and lists."""
    ast = md.root(
        md.blockquote(
            md.paragraph(md.text("[!IMPORTANT]")),
            md.paragraph(
                md.strong(md.text("Note:")),
                md.text(" Important "),
                md.emphasis(md.text("information")),
            ),
            md.paragraph(md.text("Additional details")),
            md.unordered_list(
                md.list_item(md.paragraph(md.text("Work in progress"))),
            ),
        )
    )

    actual = parse_blocks(ast, {"allowUnsupportedObjectType": False, "strictImageUrls": True})

    expected = [
        notion.callout(
            [notion.rich_text("Important")],
            "☝️",
            "purple_background",
            [
                notion.paragraph([
                    notion.rich_text("Note:", {"annotations": {"bold": True}}),
                    notion.rich_text(" Important "),
                    notion.rich_text("information", {"annotations": {"italic": True}}),
                ]),
                notion.paragraph([notion.rich_text("Additional details")]),
                notion.bulleted_list_item([notion.rich_text("Work in progress")], []),
            ],
        )
    ]

    assert actual == expected

