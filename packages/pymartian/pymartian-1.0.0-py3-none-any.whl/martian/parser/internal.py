"""Core parser for converting Markdown AST to Notion blocks."""

import os
import re
from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union
from urllib.parse import urlparse

from ..markdown.types import (
    Blockquote,
    Break,
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
    Strong,
    Table,
    TableCell,
    TableRow,
    Text,
)
from ..notion import blocks as notion
from ..notion.blocks import Block, RichText
from ..notion.common import LIMITS
from ..notion.utils import parse_callout_emoji, parse_code_language
from ..notion.common import GFM_ALERT_MAP, is_gfm_alert_type, is_supported_code_lang


def ensure_length(text: str, copy: Optional[Dict[str, Any]] = None) -> List[RichText]:
    """Split text into chunks of max 2000 characters.
    
    Args:
        text: The text to split
        copy: Options to pass to rich_text
        
    Returns:
        List of RichText objects
    """
    if copy is None:
        copy = {}
    
    # Split into chunks of 2000 characters
    chunks = []
    for i in range(0, len(text), 2000):
        chunks.append(text[i:i+2000])
    
    return [notion.rich_text(chunk, copy) for chunk in chunks]


def ensure_code_block_language(lang: Optional[str]) -> Optional[str]:
    """Ensure code block language is supported by Notion.
    
    Args:
        lang: The language identifier
        
    Returns:
        Notion supported language or None
    """
    if lang:
        lang_lower = lang.lower()
        # First try to map the language (handles aliases like "ts" -> "typescript", "java" -> "java/c/c++/c#")
        parsed = parse_code_language(lang_lower)
        if parsed and is_supported_code_lang(parsed):
            return parsed
        # If no mapping, check if it's already a supported language
        elif is_supported_code_lang(lang_lower):
            return lang_lower
        else:
            return "plain text"
    return None


def parse_inline(
    element: PhrasingContent, options: Optional[Dict[str, Any]] = None
) -> List[RichText]:
    """Parse inline/phrasing content to Notion RichText.
    
    Args:
        element: The markdown AST phrasing content element
        options: Rich text options (annotations, url)
        
    Returns:
        List of Notion RichText objects
    """
    if options is None:
        options = {}
    
    copy = {
        "annotations": {
            **options.get("annotations", {})
        },
        "url": options.get("url"),
    }
    
    element_type = element.get("type")
    
    if element_type == "text":
        text_elem = element  # type: Text
        return ensure_length(text_elem["value"], copy)
    
    elif element_type == "delete":
        delete_elem = element  # type: Delete
        copy["annotations"]["strikethrough"] = True
        return [
            rt
            for child in delete_elem["children"]
            for rt in parse_inline(child, copy)
        ]
    
    elif element_type == "emphasis":
        emphasis_elem = element  # type: Emphasis
        copy["annotations"]["italic"] = True
        return [
            rt
            for child in emphasis_elem["children"]
            for rt in parse_inline(child, copy)
        ]
    
    elif element_type == "strong":
        strong_elem = element  # type: Strong
        copy["annotations"]["bold"] = True
        return [
            rt
            for child in strong_elem["children"]
            for rt in parse_inline(child, copy)
        ]
    
    elif element_type == "link":
        link_elem = element  # type: Link
        copy["url"] = link_elem["url"]
        return [
            rt
            for child in link_elem["children"]
            for rt in parse_inline(child, copy)
        ]
    
    elif element_type == "inlineCode":
        code_elem = element  # type: InlineCode
        copy["annotations"]["code"] = True
        return [notion.rich_text(code_elem["value"], copy)]
    
    elif element_type == "inlineMath":
        math_elem = element  # type: InlineMath
        return [notion.rich_text(math_elem["value"], {**copy, "type": "equation"})]
    
    else:
        return []


def parse_image(image: Image, options: "BlocksOptions") -> Block:
    """Parse image node to Notion block.
    
    Args:
        image: The markdown image node
        options: Parsing options
        
    Returns:
        Notion image block or paragraph with URL as text
    """
    allowed_types = [
        ".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff",
        ".bmp", ".svg", ".heic", ".webp"
    ]
    
    def deal_with_error() -> Block:
        return notion.paragraph([notion.rich_text(image["url"])])
    
    try:
        if options.get("strictImageUrls", True):
            parsed_url = urlparse(image["url"])
            file_type = os.path.splitext(parsed_url.path)[1].lower()
            if file_type in allowed_types:
                return notion.image(image["url"])
            else:
                return deal_with_error()
        else:
            return notion.image(image["url"])
    except Exception:
        return deal_with_error()


def parse_paragraph(element: Paragraph, options: "BlocksOptions") -> List[Block]:
    """Parse paragraph node to Notion blocks.
    
    Args:
        element: The markdown paragraph node
        options: Parsing options
        
    Returns:
        List of Notion blocks (paragraphs and images)
    """
    # Check for legacy TOC syntax
    if len(element["children"]) > 2:
        first_child = element["children"][0]
        if (
            first_child.get("type") == "text"
            and first_child.get("value") == "[["  # type: ignore
        ):
            second_child = element["children"][1]
            if second_child.get("type") == "emphasis":
                emphasis_child = second_child["children"][0]  # type: ignore
                if (
                    emphasis_child.get("type") == "text"
                    and emphasis_child.get("value") == "TOC"  # type: ignore
                ):
                    return [notion.table_of_contents()]
    
    # Notion doesn't deal with inline images
    images: List[Block] = []
    paragraphs: List[List[RichText]] = []
    current_paragraph: List[RichText] = []
    
    def push_paragraph() -> None:
        if len(current_paragraph) > 0:
            paragraphs.append(current_paragraph.copy())
            current_paragraph.clear()
    
    for item in element["children"]:
        if item.get("type") == "image":
            images.append(parse_image(item, options))  # type: ignore
            continue
        
        if item.get("type") == "break":
            push_paragraph()
            continue
        
        rich_text_list = parse_inline(item)
        current_paragraph.extend(rich_text_list)
    
    push_paragraph()
    
    return [notion.paragraph(p) for p in paragraphs] + images


def parse_blockquote(element: Blockquote, options: "BlocksOptions") -> Block:
    """Parse blockquote node to Notion block.
    
    Args:
        element: The markdown blockquote node
        options: Parsing options
        
    Returns:
        Notion quote or callout block
    """
    first_child = element["children"][0] if element["children"] else None
    first_text_node = None
    
    if first_child and first_child.get("type") == "paragraph":
        paragraph_children = first_child["children"]  # type: ignore
        if paragraph_children:
            first_text_node = paragraph_children[0]
    
    if first_text_node and first_text_node.get("type") == "text":
        # Helper to parse subsequent blocks
        def parse_subsequent_blocks() -> List[Block]:
            if len(element["children"]) > 1:
                return [
                    block
                    for child in element["children"][1:]
                    for block in parse_node(child, options)
                ]
            return []
        
        # Check for GFM alert syntax
        first_line = first_text_node["value"].split("\n")[0]  # type: ignore
        gfm_match = re.match(
            r"^(?:\\\[|\[)!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]$", first_line
        )
        
        if gfm_match and is_gfm_alert_type(gfm_match.group(1)):
            alert_type = gfm_match.group(1)
            alert_config = GFM_ALERT_MAP[alert_type]
            display_type = alert_type.capitalize()
            
            children = []
            content_lines = first_text_node["value"].split("\n")[1:]  # type: ignore
            
            if content_lines:
                content_text = "\n".join(content_lines)
                if content_text.strip():
                    children.append(
                        notion.paragraph(parse_inline({"type": "text", "value": content_text}))
                    )
            
            children.extend(parse_subsequent_blocks())
            
            return notion.callout(
                [notion.rich_text(display_type)],
                alert_config["emoji"],
                alert_config["color"],
                children,
            )
        
        # Check for emoji syntax if enabled
        if options.get("enableEmojiCallouts"):
            emoji_data = parse_callout_emoji(first_text_node["value"])  # type: ignore
            if emoji_data:
                paragraph = first_child  # type: Paragraph
                text_without_emoji = (
                    first_text_node["value"][len(emoji_data["emoji"]):].lstrip()  # type: ignore
                )
                
                # Process inline content from first paragraph
                rich_text_list = []
                for i, child in enumerate(paragraph["children"]):
                    if i == 0:  # First child (the text node with emoji)
                        if text_without_emoji:
                            rich_text_list.extend(
                                parse_inline({"type": "text", "value": text_without_emoji})
                            )
                    else:
                        rich_text_list.extend(parse_inline(child))
                
                return notion.callout(
                    rich_text_list,
                    emoji_data["emoji"],
                    emoji_data["color"],
                    parse_subsequent_blocks(),
                )
    
    # Default: regular blockquote
    children = [
        block for child in element["children"] for block in parse_node(child, options)
    ]
    return notion.blockquote([], children)


def parse_heading(element: Heading) -> Block:
    """Parse heading node to Notion block.
    
    Args:
        element: The markdown heading node
        
    Returns:
        Notion heading block
    """
    text = [rt for child in element["children"] for rt in parse_inline(child)]
    
    depth = element["depth"]
    if depth == 1:
        return notion.heading_one(text)
    elif depth == 2:
        return notion.heading_two(text)
    else:
        return notion.heading_three(text)


def parse_code(element: Code) -> Block:
    """Parse code block node to Notion block.
    
    Args:
        element: The markdown code node
        
    Returns:
        Notion code block
    """
    # Remove trailing newline if present (markdown-it adds it)
    code_value = element["value"]
    if code_value.endswith("\n"):
        code_value = code_value[:-1]
    
    text = ensure_length(code_value)
    lang = ensure_code_block_language(element.get("lang"))
    return notion.code(text, lang or "plain text")


def parse_list(element: ListNode, options: "BlocksOptions") -> List[Block]:
    """Parse list node to Notion blocks.
    
    Args:
        element: The markdown list node
        options: Parsing options
        
    Returns:
        List of Notion list item blocks
    """
    blocks = []
    
    for item in element["children"]:
        item_children = item["children"].copy()
        if not item_children or item_children[0].get("type") != "paragraph":
            continue
        
        paragraph = item_children.pop(0)  # type: Paragraph
        text = [
            rt for child in paragraph["children"] for rt in parse_inline(child)
        ]
        
        # Process remaining children
        parsed_children = [
            block
            for child in item_children
            for block in parse_node(child, options)
        ]
        
        # Determine list item type
        if element.get("start") is not None:
            blocks.append(notion.numbered_list_item(text, parsed_children))
        elif item.get("checked") is not None:
            blocks.append(notion.to_do(item["checked"], text, parsed_children))
        else:
            blocks.append(notion.bulleted_list_item(text, parsed_children))
    
    return blocks


def parse_table_cell(node: TableCell) -> List[RichText]:
    """Parse table cell to rich text.
    
    Args:
        node: The markdown table cell node
        
    Returns:
        List of rich text objects
    """
    return [rt for child in node["children"] for rt in parse_inline(child)]


def parse_table_row(node: TableRow) -> Any:
    """Parse table row to Notion table row.
    
    Args:
        node: The markdown table row node
        
    Returns:
        Notion table row block
    """
    cells = [parse_table_cell(child) for child in node["children"]]
    return notion.table_row(cells)


def parse_table(node: Table) -> List[Block]:
    """Parse table node to Notion table block.
    
    Args:
        node: The markdown table node
        
    Returns:
        List containing a single Notion table block
    """
    table_width = len(node["children"][0]["children"]) if node["children"] else 0
    table_rows = [parse_table_row(child) for child in node["children"]]
    return [notion.table(table_rows, table_width)]


def parse_math(node: Math) -> Block:
    """Parse math block node to Notion equation block.
    
    Args:
        node: The markdown math node
        
    Returns:
        Notion equation block
    """
    # Convert newlines to KaTeX format
    # First strip leading/trailing whitespace, then replace internal newlines
    math_value = node["value"].strip()
    text_with_katex_newlines = math_value.replace("\n", "\\\\\n")
    return notion.equation(text_with_katex_newlines)


def parse_node(node: FlowContent, options: "BlocksOptions") -> List[Block]:
    """Parse a markdown flow content node to Notion blocks.
    
    Args:
        node: The markdown AST node
        options: Parsing options
        
    Returns:
        List of Notion blocks
    """
    node_type = node.get("type")
    
    if node_type == "heading":
        return [parse_heading(node)]  # type: ignore
    
    elif node_type == "paragraph":
        return parse_paragraph(node, options)  # type: ignore
    
    elif node_type == "code":
        return [parse_code(node)]  # type: ignore
    
    elif node_type == "blockquote":
        return [parse_blockquote(node, options)]  # type: ignore
    
    elif node_type == "list":
        return parse_list(node, options)  # type: ignore
    
    elif node_type == "table":
        return parse_table(node)  # type: ignore
    
    elif node_type == "math":
        return [parse_math(node)]  # type: ignore
    
    elif node_type == "thematicBreak":
        return [notion.divider()]
    
    else:
        return []


class NotionLimitsOptions(TypedDict, total=False):
    """Options for handling Notion limits."""
    
    truncate: bool
    onError: Optional[Callable[[Exception], None]]


class CommonOptions(TypedDict, total=False):
    """Options common to all parsing methods."""
    
    notionLimits: NotionLimitsOptions


class BlocksOptions(CommonOptions, total=False):
    """Options for parsing blocks."""
    
    strictImageUrls: bool
    enableEmojiCallouts: bool


def parse_blocks(root: Root, options: Optional[BlocksOptions] = None) -> List[Block]:
    """Parse markdown AST root to Notion blocks.
    
    Args:
        root: The markdown AST root node
        options: Parsing options
        
    Returns:
        List of Notion blocks
    """
    if options is None:
        options = {}
    
    parsed = [block for item in root["children"] for block in parse_node(item, options)]
    
    truncate = options.get("notionLimits", {}).get("truncate", True)
    limit_callback = options.get("notionLimits", {}).get("onError", lambda e: None)
    
    if len(parsed) > LIMITS.PAYLOAD_BLOCKS:
        limit_callback(
            Exception(
                f"Resulting blocks array exceeds Notion limit ({LIMITS.PAYLOAD_BLOCKS})"
            )
        )
    
    return parsed[: LIMITS.PAYLOAD_BLOCKS] if truncate else parsed


class RichTextOptions(CommonOptions, total=False):
    """Options for parsing rich text."""
    
    nonInline: Literal["ignore", "throw"]


def parse_rich_text(
    root: Root, options: Optional[RichTextOptions] = None
) -> List[RichText]:
    """Parse markdown AST root to Notion rich text.
    
    Args:
        root: The markdown AST root node
        options: Parsing options
        
    Returns:
        List of Notion RichText objects
    """
    if options is None:
        options = {}
    
    rich_texts: List[RichText] = []
    
    for child in root["children"]:
        if child.get("type") == "paragraph":
            paragraph = child  # type: Paragraph
            for phrasing_child in paragraph["children"]:
                rich_texts.extend(parse_inline(phrasing_child))
        elif options.get("nonInline") == "throw":
            raise Exception(f"Unsupported markdown element: {child}")
    
    truncate = options.get("notionLimits", {}).get("truncate", True)
    limit_callback = options.get("notionLimits", {}).get("onError", lambda e: None)
    
    if len(rich_texts) > LIMITS.RICH_TEXT_ARRAYS:
        limit_callback(
            Exception(
                f"Resulting richTexts array exceeds Notion limit ({LIMITS.RICH_TEXT_ARRAYS})"
            )
        )
    
    # Truncate or keep full array
    result = (
        rich_texts[: LIMITS.RICH_TEXT_ARRAYS] if truncate else rich_texts
    )
    
    # Check text content limits
    for rt in result:
        if rt["type"] != "text":
            continue
        
        text_content = rt["text"]["content"]
        if len(text_content) > LIMITS.RICH_TEXT["TEXT_CONTENT"]:
            limit_callback(
                Exception(
                    f"Resulting text content exceeds Notion limit ({LIMITS.RICH_TEXT['TEXT_CONTENT']})"
                )
            )
            if truncate:
                rt["text"]["content"] = (
                    text_content[: LIMITS.RICH_TEXT["TEXT_CONTENT"] - 3] + "..."
                )
        
        if rt["text"].get("link") and rt["text"]["link"].get("url"):
            url = rt["text"]["link"]["url"]
            if len(url) > LIMITS.RICH_TEXT["LINK_URL"]:
                limit_callback(
                    Exception(
                        f"Resulting text URL exceeds Notion limit ({LIMITS.RICH_TEXT['LINK_URL']})"
                    )
                )
    
    return result

