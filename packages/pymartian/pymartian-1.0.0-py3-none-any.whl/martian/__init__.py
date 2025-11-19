"""Martian: Markdown to Notion Parser.

Convert Markdown and GitHub Flavoured Markdown to Notion API Blocks and RichText.
"""

from .main import markdown_to_blocks, markdown_to_rich_text

__version__ = "1.2.4"
__all__ = ["markdown_to_blocks", "markdown_to_rich_text"]

