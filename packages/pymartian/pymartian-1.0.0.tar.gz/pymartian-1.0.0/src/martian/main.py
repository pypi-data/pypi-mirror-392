"""Main entry point for Martian markdown parser."""

from typing import List, Optional

from markdown_it import MarkdownIt
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from .markdown.types import Root
from .notion.blocks import Block, RichText
from .parser.internal import BlocksOptions, RichTextOptions, parse_blocks, parse_rich_text


def _markdown_it_to_mdast(tokens: list) -> Root:
    """Convert markdown-it tokens to mdast-compatible AST.
    
    Args:
        tokens: markdown-it token list
        
    Returns:
        mdast Root node
    """
    from .markdown.types import (
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
        Strong,
        Table,
        TableCell,
        TableRow,
        Text,
        ThematicBreak,
    )
    
    def process_tokens(tokens: list, start: int = 0, end: Optional[int] = None) -> tuple:
        """Process tokens and return (nodes, next_index)."""
        if end is None:
            end = len(tokens)
        
        nodes = []
        i = start
        
        while i < end:
            token = tokens[i]
            token_type = token.type
            
            # Paragraph
            if token_type == "paragraph_open":
                i, paragraph_node = process_paragraph(tokens, i)
                nodes.append(paragraph_node)
            
            # Heading
            elif token_type == "heading_open":
                i, heading_node = process_heading(tokens, i)
                nodes.append(heading_node)
            
            # Code block
            elif token_type == "fence" or token_type == "code_block":
                code_node: Code = {
                    "type": "code",
                    "value": token.content,
                }
                if token.info:
                    code_node["lang"] = token.info.strip()
                nodes.append(code_node)
                i += 1
            
            # Math block
            elif token_type == "math_block" or token_type == "display_math":
                math_node: Math = {
                    "type": "math",
                    "value": token.content,
                }
                nodes.append(math_node)
                i += 1
            
            # Blockquote
            elif token_type == "blockquote_open":
                i, blockquote_node = process_blockquote(tokens, i)
                nodes.append(blockquote_node)
            
            # List
            elif token_type == "bullet_list_open" or token_type == "ordered_list_open":
                i, list_node = process_list(tokens, i)
                nodes.append(list_node)
            
            # Table
            elif token_type == "table_open":
                i, table_node = process_table(tokens, i)
                nodes.append(table_node)
            
            # Thematic break (hr)
            elif token_type == "hr":
                thematic_break: ThematicBreak = {"type": "thematicBreak"}
                nodes.append(thematic_break)
                i += 1
            
            # Image (standalone)
            elif token_type == "image":
                image_node: Image = {
                    "type": "image",
                    "url": token.attrGet("src") or "",
                }
                if token.attrGet("title"):
                    image_node["title"] = token.attrGet("title")
                nodes.append(image_node)
                i += 1
            
            else:
                i += 1
        
        return nodes, i
    
    def process_inline(tokens: list, start: int, end: int) -> list:
        """Process inline tokens."""
        nodes = []
        i = start
        
        while i < end:
            token = tokens[i]
            token_type = token.type
            
            # Text
            if token_type == "text":
                text_node: Text = {"type": "text", "value": token.content}
                nodes.append(text_node)
                i += 1
            
            # Code inline
            elif token_type == "code_inline":
                code_node: InlineCode = {"type": "inlineCode", "value": token.content}
                nodes.append(code_node)
                i += 1
            
            # Math inline
            elif token_type == "math_inline" or token_type == "inline_math":
                math_node: InlineMath = {"type": "inlineMath", "value": token.content}
                nodes.append(math_node)
                i += 1
            
            # Strong (bold)
            elif token_type == "strong_open":
                # Find matching close
                j = i + 1
                depth = 1
                while j < end and depth > 0:
                    if tokens[j].type == "strong_open":
                        depth += 1
                    elif tokens[j].type == "strong_close":
                        depth -= 1
                    j += 1
                
                children = process_inline(tokens, i + 1, j - 1)
                strong_node: Strong = {"type": "strong", "children": children}
                nodes.append(strong_node)
                i = j
            
            # Emphasis (italic)
            elif token_type == "em_open":
                # Find matching close
                j = i + 1
                depth = 1
                while j < end and depth > 0:
                    if tokens[j].type == "em_open":
                        depth += 1
                    elif tokens[j].type == "em_close":
                        depth -= 1
                    j += 1
                
                children = process_inline(tokens, i + 1, j - 1)
                em_node: Emphasis = {"type": "emphasis", "children": children}
                nodes.append(em_node)
                i = j
            
            # Strikethrough (delete)
            elif token_type == "s_open":
                # Find matching close
                j = i + 1
                depth = 1
                while j < end and depth > 0:
                    if tokens[j].type == "s_open":
                        depth += 1
                    elif tokens[j].type == "s_close":
                        depth -= 1
                    j += 1
                
                children = process_inline(tokens, i + 1, j - 1)
                del_node: Delete = {"type": "delete", "children": children}
                nodes.append(del_node)
                i = j
            
            # Link
            elif token_type == "link_open":
                # Find matching close
                j = i + 1
                depth = 1
                while j < end and depth > 0:
                    if tokens[j].type == "link_open":
                        depth += 1
                    elif tokens[j].type == "link_close":
                        depth -= 1
                    j += 1
                
                children = process_inline(tokens, i + 1, j - 1)
                link_node: Link = {
                    "type": "link",
                    "url": token.attrGet("href") or "",
                    "children": children,
                }
                if token.attrGet("title"):
                    link_node["title"] = token.attrGet("title")
                nodes.append(link_node)
                i = j
            
            # Image
            elif token_type == "image":
                image_node: Image = {
                    "type": "image",
                    "url": token.attrGet("src") or "",
                }
                if token.attrGet("title"):
                    image_node["title"] = token.attrGet("title")
                nodes.append(image_node)
                i += 1
            
            # Hardbreak
            elif token_type == "hardbreak":
                break_node = {"type": "break"}
                nodes.append(break_node)
                i += 1
            
            # Softbreak (treat as text with newline)
            elif token_type == "softbreak":
                text_node = {"type": "text", "value": "\n"}
                nodes.append(text_node)
                i += 1
            
            else:
                i += 1
        
        # Merge consecutive text nodes
        merged_nodes = []
        for node in nodes:
            if (
                node.get("type") == "text"
                and merged_nodes
                and merged_nodes[-1].get("type") == "text"
            ):
                # Merge with previous text node
                merged_nodes[-1]["value"] += node["value"]
            else:
                merged_nodes.append(node)
        
        return merged_nodes
    
    def process_paragraph(tokens: list, start: int) -> tuple:
        """Process paragraph tokens."""
        i = start + 1  # Skip paragraph_open
        inline_token = tokens[i]
        i += 1  # Skip inline token
        i += 1  # Skip paragraph_close
        
        children = []
        if inline_token.children:
            children = process_inline(inline_token.children, 0, len(inline_token.children))
        
        paragraph_node: Paragraph = {"type": "paragraph", "children": children}
        return i, paragraph_node
    
    def process_heading(tokens: list, start: int) -> tuple:
        """Process heading tokens."""
        heading_open = tokens[start]
        depth = int(heading_open.tag[1])  # h1 -> 1, h2 -> 2, etc.
        
        i = start + 1
        inline_token = tokens[i]
        i += 1  # Skip inline token
        i += 1  # Skip heading_close
        
        children = []
        if inline_token.children:
            children = process_inline(inline_token.children, 0, len(inline_token.children))
        
        heading_node: Heading = {
            "type": "heading",
            "depth": depth,  # type: ignore
            "children": children,
        }
        return i, heading_node
    
    def process_blockquote(tokens: list, start: int) -> tuple:
        """Process blockquote tokens."""
        i = start + 1  # Skip blockquote_open
        
        # Find matching close
        depth = 1
        j = i
        while j < len(tokens) and depth > 0:
            if tokens[j].type == "blockquote_open":
                depth += 1
            elif tokens[j].type == "blockquote_close":
                depth -= 1
            j += 1
        
        children, _ = process_tokens(tokens, i, j - 1)
        
        blockquote_node: Blockquote = {"type": "blockquote", "children": children}
        return j, blockquote_node
    
    def process_list(tokens: list, start: int) -> tuple:
        """Process list tokens."""
        list_open = tokens[start]
        is_ordered = list_open.type == "ordered_list_open"
        
        i = start + 1
        
        # Find matching close
        depth = 1
        j = i
        while j < len(tokens) and depth > 0:
            if tokens[j].type in ["bullet_list_open", "ordered_list_open"]:
                depth += 1
            elif tokens[j].type in ["bullet_list_close", "ordered_list_close"]:
                depth -= 1
            j += 1
        
        # Process list items
        items = []
        k = i
        while k < j - 1:
            if tokens[k].type == "list_item_open":
                k, item = process_list_item(tokens, k)
                items.append(item)
            else:
                k += 1
        
        list_node: ListNode = {
            "type": "list",
            "ordered": is_ordered,
            "children": items,
        }
        if is_ordered:
            list_node["start"] = 0
        
        return j, list_node
    
    def process_list_item(tokens: list, start: int) -> tuple:
        """Process list item tokens."""
        list_item_open = tokens[start]
        
        # Check for checkbox (tasklists plugin adds class="task-list-item")
        checked = None
        if hasattr(list_item_open, "attrGet"):
            checkbox_attr = list_item_open.attrGet("class")
            if checkbox_attr and "task-list-item" in checkbox_attr:
                # Look for checkbox in content (html_inline token)
                # tasklists_plugin adds <input class="task-list-item-checkbox" checked="checked"> or disabled="disabled"
                if start + 1 < len(tokens):
                    next_token = tokens[start + 1]
                    if next_token.type == "paragraph_open" and start + 2 < len(tokens):
                        inline_token = tokens[start + 2]
                        if inline_token.children and len(inline_token.children) > 0:
                            first_child = inline_token.children[0]
                            if first_child.type == "html_inline":
                                html_content = first_child.content
                                if 'checked="checked"' in html_content or 'checked=""' in html_content:
                                    checked = True
                                elif 'disabled="disabled"' in html_content or 'disabled=""' in html_content:
                                    checked = False
                                # Remove the html_inline token from children
                                inline_token.children = inline_token.children[1:]
                                # Trim leading space from next text node if present
                                if inline_token.children and inline_token.children[0].type == "text":
                                    inline_token.children[0].content = inline_token.children[0].content.lstrip()
        
        i = start + 1
        
        # Find matching close
        depth = 1
        j = i
        while j < len(tokens) and depth > 0:
            if tokens[j].type == "list_item_open":
                depth += 1
            elif tokens[j].type == "list_item_close":
                depth -= 1
            j += 1
        
        children, _ = process_tokens(tokens, i, j - 1)
        
        item_node: ListItem = {"type": "listitem", "children": children}
        if checked is not None:
            item_node["checked"] = checked
        
        return j, item_node
    
    def process_table(tokens: list, start: int) -> tuple:
        """Process table tokens."""
        i = start + 1  # Skip table_open
        
        # Find matching close
        depth = 1
        j = i
        while j < len(tokens) and depth > 0:
            if tokens[j].type == "table_open":
                depth += 1
            elif tokens[j].type == "table_close":
                depth -= 1
            j += 1
        
        # Process table rows
        rows = []
        k = i
        while k < j - 1:
            if tokens[k].type == "tr_open":
                k, row = process_table_row(tokens, k)
                rows.append(row)
            else:
                k += 1
        
        table_node: Table = {"type": "table", "children": rows}
        return j, table_node
    
    def process_table_row(tokens: list, start: int) -> tuple:
        """Process table row tokens."""
        i = start + 1  # Skip tr_open
        
        # Find matching close
        depth = 1
        j = i
        while j < len(tokens) and depth > 0:
            if tokens[j].type == "tr_open":
                depth += 1
            elif tokens[j].type == "tr_close":
                depth -= 1
            j += 1
        
        # Process table cells
        cells = []
        k = i
        while k < j - 1:
            if tokens[k].type in ["th_open", "td_open"]:
                k, cell = process_table_cell(tokens, k)
                cells.append(cell)
            else:
                k += 1
        
        row_node: TableRow = {"type": "tableRow", "children": cells}
        return j, row_node
    
    def process_table_cell(tokens: list, start: int) -> tuple:
        """Process table cell tokens."""
        cell_open = tokens[start]
        i = start + 1
        inline_token = tokens[i]
        i += 1  # Skip inline token
        i += 1  # Skip th_close or td_close
        
        children = []
        if inline_token.children:
            children = process_inline(inline_token.children, 0, len(inline_token.children))
        
        cell_node: TableCell = {"type": "tableCell", "children": children}
        return i, cell_node
    
    # Process all tokens
    children, _ = process_tokens(tokens)
    
    root: Root = {"type": "root", "children": children}
    return root


def markdown_to_blocks(body: str, options: Optional[BlocksOptions] = None) -> List[Block]:
    """Parse Markdown content into Notion Blocks.
    
    Args:
        body: Any Markdown or GFM content
        options: Additional parsing options
        
    Returns:
        List of Notion Block objects
    """
    # Create markdown-it parser with plugins
    md = MarkdownIt("commonmark", {"html": False})
    md.enable(["table", "strikethrough"])
    md.disable(["linkify"])
    
    # Add plugins
    md.use(tasklists_plugin)
    md.use(dollarmath_plugin)
    
    # Parse to tokens
    tokens = md.parse(body)
    
    # Convert to mdast
    root = _markdown_it_to_mdast(tokens)
    
    # Parse to Notion blocks
    return parse_blocks(root, options)


def markdown_to_rich_text(
    text: str, options: Optional[RichTextOptions] = None
) -> List[RichText]:
    """Parse inline Markdown content into Notion RichText objects.
    
    Only supports plain text, italics, bold, strikethrough, inline code, and hyperlinks.
    
    Args:
        text: Any inline Markdown or GFM content
        options: Additional parsing options
        
    Returns:
        List of Notion RichText objects
    """
    # Create markdown-it parser with plugins
    md = MarkdownIt("commonmark", {"html": False})
    md.enable(["strikethrough"])
    md.disable(["linkify"])
    
    # Parse to tokens
    tokens = md.parse(text)
    
    # Convert to mdast
    root = _markdown_it_to_mdast(tokens)
    
    # Parse to Notion rich text
    return parse_rich_text(root, options)

