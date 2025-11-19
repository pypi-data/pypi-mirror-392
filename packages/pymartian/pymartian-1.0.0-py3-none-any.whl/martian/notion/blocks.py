"""Notion block builder functions."""

from typing import Any, Dict, List, Literal, Optional

from .common import (
    ApiColor,
    EmojiRequest,
    RichText,
    SupportedCodeLang,
    TableRowBlock,
    rich_text,
)

# Type alias for Block
Block = Dict[str, Any]


def divider() -> Block:
    """Create a divider block."""
    return {"object": "block", "type": "divider", "divider": {}}


def paragraph(text: List[RichText]) -> Block:
    """Create a paragraph block."""
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": text}}


def code(text: List[RichText], lang: SupportedCodeLang = "plain text") -> Block:
    """Create a code block."""
    return {
        "object": "block",
        "type": "code",
        "code": {"rich_text": text, "language": lang},
    }


def blockquote(text: Optional[List[RichText]] = None, children: Optional[List[Block]] = None) -> Block:
    """Create a blockquote/quote block.
    
    Args:
        text: Rich text for the quote (empty list by default)
        children: Child blocks (empty list by default)
        
    Returns:
        A Notion quote block
    """
    if text is None:
        text = []
    if children is None:
        children = []
    
    # By setting an empty rich text we prevent the "Empty quote" line from showing up at all
    rich_text_content = text if len(text) > 0 else [rich_text("")]
    
    result: Block = {
        "object": "block",
        "type": "quote",
        "quote": {"rich_text": rich_text_content},
    }
    
    if children:
        result["quote"]["children"] = children
    
    return result


def image(url: str) -> Block:
    """Create an image block."""
    return {
        "object": "block",
        "type": "image",
        "image": {"type": "external", "external": {"url": url}},
    }


def table_of_contents() -> Block:
    """Create a table of contents block."""
    return {"object": "block", "type": "table_of_contents", "table_of_contents": {}}


def heading_one(text: List[RichText]) -> Block:
    """Create a heading 1 block."""
    return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": text}}


def heading_two(text: List[RichText]) -> Block:
    """Create a heading 2 block."""
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": text}}


def heading_three(text: List[RichText]) -> Block:
    """Create a heading 3 block."""
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": text}}


def bulleted_list_item(
    text: List[RichText], children: Optional[List[Block]] = None
) -> Block:
    """Create a bulleted list item block."""
    if children is None:
        children = []
    
    result: Block = {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": text},
    }
    
    if children:
        result["bulleted_list_item"]["children"] = children
    
    return result


def numbered_list_item(
    text: List[RichText], children: Optional[List[Block]] = None
) -> Block:
    """Create a numbered list item block."""
    if children is None:
        children = []
    
    result: Block = {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": text},
    }
    
    if children:
        result["numbered_list_item"]["children"] = children
    
    return result


def to_do(
    checked: bool, text: List[RichText], children: Optional[List[Block]] = None
) -> Block:
    """Create a to-do block."""
    if children is None:
        children = []
    
    result: Block = {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": text, "checked": checked},
    }
    
    if children:
        result["to_do"]["children"] = children
    
    return result


def table(children: List[TableRowBlock], table_width: int) -> Block:
    """Create a table block."""
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": True,
            "children": children if children else [],
        },
    }


def table_row(cells: Optional[List[List[RichText]]] = None) -> TableRowBlock:
    """Create a table row block."""
    if cells is None:
        cells = []
    
    return {
        "object": "block",
        "type": "table_row",
        "table_row": {"cells": cells if cells else []},
    }


def equation(value: str) -> Block:
    """Create an equation block."""
    return {"type": "equation", "equation": {"expression": value}}


def callout(
    text: Optional[List[RichText]] = None,
    emoji: EmojiRequest = "👍",
    color: ApiColor = "default",
    children: Optional[List[Block]] = None,
) -> Block:
    """Create a callout block.
    
    Args:
        text: Rich text for the callout (empty list by default)
        emoji: Emoji icon for the callout
        color: Background color for the callout
        children: Child blocks (empty list by default)
        
    Returns:
        A Notion callout block
    """
    if text is None:
        text = []
    if children is None:
        children = []
    
    rich_text_content = text if len(text) > 0 else [rich_text("")]
    
    result: Block = {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": rich_text_content,
            "icon": {"type": "emoji", "emoji": emoji},
            "color": color,
        },
    }
    
    if children:
        result["callout"]["children"] = children
    
    return result

