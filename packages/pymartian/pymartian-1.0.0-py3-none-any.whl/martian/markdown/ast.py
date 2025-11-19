"""Markdown AST builder utilities."""

from typing import List, Literal, Optional

from .types import (
    Blockquote,
    Code,
    Delete,
    Emphasis,
    FlowContent,
    Heading,
    Image,
    InlineCode,
    InlineMath,
    Link,
    List as ListNode,
    ListItem,
    Math,
    Paragraph,
    PhrasingContent,
    Root,
    RowContent,
    StaticPhrasingContent,
    Strong,
    Table,
    TableCell,
    TableContent,
    TableRow,
    Text,
    ThematicBreak,
)


def text(value: str) -> Text:
    """Create a text node."""
    return {"type": "text", "value": value}


def image(url: str, alt: str = "", title: str = "") -> Image:
    """Create an image node."""
    return {"type": "image", "url": url, "title": title}


def emphasis(*children: PhrasingContent) -> Emphasis:
    """Create an emphasis node (italic)."""
    return {"type": "emphasis", "children": list(children)}


def strong(*children: PhrasingContent) -> Strong:
    """Create a strong node (bold)."""
    return {"type": "strong", "children": list(children)}


def inline_code(value: str) -> InlineCode:
    """Create an inline code node."""
    return {"type": "inlineCode", "value": value}


def inline_math(value: str) -> InlineMath:
    """Create an inline math node."""
    return {"type": "inlineMath", "value": value}


def paragraph(*children: PhrasingContent) -> Paragraph:
    """Create a paragraph node."""
    return {"type": "paragraph", "children": list(children)}


def root(*children: FlowContent) -> Root:
    """Create a root node."""
    return {"type": "root", "children": list(children)}


def link(url: str, *children: StaticPhrasingContent) -> Link:
    """Create a link node."""
    return {"type": "link", "url": url, "children": list(children)}


def thematic_break() -> ThematicBreak:
    """Create a thematic break node."""
    return {"type": "thematicBreak"}


def heading(
    depth: Literal[1, 2, 3, 4, 5, 6], *children: PhrasingContent
) -> Heading:
    """Create a heading node."""
    return {"type": "heading", "depth": depth, "children": list(children)}


def code(value: str, lang: Optional[str] = None) -> Code:
    """Create a code block node."""
    result: Code = {"type": "code", "value": value}
    if lang is not None:
        result["lang"] = lang
    return result


def math(value: str) -> Math:
    """Create a math block node."""
    return {"type": "math", "value": value}


def blockquote(*children: FlowContent) -> Blockquote:
    """Create a blockquote node."""
    return {"type": "blockquote", "children": list(children)}


def list_item(*children: FlowContent) -> ListItem:
    """Create a list item node."""
    return {"type": "listitem", "children": list(children)}


def checked_list_item(checked: bool, *children: FlowContent) -> ListItem:
    """Create a checked list item node."""
    return {"type": "listitem", "checked": checked, "children": list(children)}


def unordered_list(*children: ListItem) -> ListNode:
    """Create an unordered list node."""
    return {"type": "list", "ordered": False, "children": list(children)}


def ordered_list(*children: ListItem) -> ListNode:
    """Create an ordered list node."""
    return {"type": "list", "ordered": True, "start": 0, "children": list(children)}


def strikethrough(*children: PhrasingContent) -> Delete:
    """Create a strikethrough node."""
    return {"type": "delete", "children": list(children)}


def table(*children: TableRow) -> Table:
    """Create a table node."""
    return {"type": "table", "children": list(children)}


def table_row(*children: TableCell) -> TableRow:
    """Create a table row node."""
    return {"type": "tableRow", "children": list(children)}


def table_cell(*children: PhrasingContent) -> TableCell:
    """Create a table cell node."""
    return {"type": "tableCell", "children": list(children)}

