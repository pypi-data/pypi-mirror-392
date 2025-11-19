"""Notion API common types and constants."""

import re
from typing import Any, Callable, Dict, Literal, Optional, TypedDict, Union

# Type aliases
EmojiRequest = str
ApiColor = Literal[
    "default",
    "gray",
    "brown",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink",
    "red",
    "gray_background",
    "brown_background",
    "orange_background",
    "yellow_background",
    "green_background",
    "blue_background",
    "purple_background",
    "pink_background",
    "red_background",
]


class Limits:
    """Notion API limits.
    
    See https://developers.notion.com/reference/request-limits#limits-for-property-values
    """

    PAYLOAD_BLOCKS = 1000
    RICH_TEXT_ARRAYS = 100
    RICH_TEXT = {"TEXT_CONTENT": 2000, "LINK_URL": 1000, "EQUATION_EXPRESSION": 1000}


LIMITS = Limits()


class RichTextAnnotations(TypedDict, total=False):
    """Rich text annotations."""

    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str


class RichTextOptions(TypedDict, total=False):
    """Options for creating rich text."""

    type: Literal["text", "equation"]
    annotations: RichTextAnnotations
    url: Optional[str]


class TextContent(TypedDict, total=False):
    """Text content."""

    content: str
    link: Optional[Dict[str, str]]


class EquationContent(TypedDict):
    """Equation content."""

    expression: str


class RichTextText(TypedDict):
    """Rich text object for text."""

    type: Literal["text"]
    annotations: RichTextAnnotations
    text: TextContent


class RichTextEquation(TypedDict):
    """Rich text object for equation."""

    type: Literal["equation"]
    annotations: RichTextAnnotations
    equation: EquationContent


RichText = Union[RichTextText, RichTextEquation]


def is_valid_url(url: Optional[str]) -> bool:
    """Check if URL is valid."""
    if not url or url == "":
        return False
    url_regex = re.compile(r"^https?://.+", re.IGNORECASE)
    return bool(url_regex.match(url))


def rich_text(content: str, options: Optional[RichTextOptions] = None) -> RichText:
    """Create a rich text object.
    
    Args:
        content: The text content or equation expression
        options: Optional formatting options
        
    Returns:
        A Notion RichText object
    """
    if options is None:
        options = {}

    annotations: RichTextAnnotations = {
        "bold": False,
        "strikethrough": False,
        "underline": False,
        "italic": False,
        "code": False,
        "color": "default",
    }

    if "annotations" in options and options["annotations"]:
        annotations.update(options["annotations"])

    if options.get("type") == "equation":
        return {
            "type": "equation",
            "annotations": annotations,
            "equation": {"expression": content},
        }
    else:
        text_obj: TextContent = {"content": content}
        if is_valid_url(options.get("url")):
            text_obj["link"] = {"type": "url", "url": options["url"]}

        return {"type": "text", "annotations": annotations, "text": text_obj}


# Supported code block languages
SUPPORTED_CODE_BLOCK_LANGUAGES = (
    "abap",
    "arduino",
    "bash",
    "basic",
    "c",
    "clojure",
    "coffeescript",
    "c++",
    "c#",
    "css",
    "dart",
    "diff",
    "docker",
    "elixir",
    "elm",
    "erlang",
    "flow",
    "fortran",
    "f#",
    "gherkin",
    "glsl",
    "go",
    "graphql",
    "groovy",
    "haskell",
    "html",
    "java",
    "javascript",
    "json",
    "julia",
    "kotlin",
    "latex",
    "less",
    "lisp",
    "livescript",
    "lua",
    "makefile",
    "markdown",
    "markup",
    "matlab",
    "mermaid",
    "nix",
    "objective-c",
    "ocaml",
    "pascal",
    "perl",
    "php",
    "plain text",
    "powershell",
    "prolog",
    "protobuf",
    "python",
    "r",
    "reason",
    "ruby",
    "rust",
    "sass",
    "scala",
    "scheme",
    "scss",
    "shell",
    "sql",
    "swift",
    "typescript",
    "vb.net",
    "verilog",
    "vhdl",
    "visual basic",
    "webassembly",
    "xml",
    "yaml",
    "java/c/c++/c#",
)

SupportedCodeLang = Literal[
    "abap",
    "arduino",
    "bash",
    "basic",
    "c",
    "clojure",
    "coffeescript",
    "c++",
    "c#",
    "css",
    "dart",
    "diff",
    "docker",
    "elixir",
    "elm",
    "erlang",
    "flow",
    "fortran",
    "f#",
    "gherkin",
    "glsl",
    "go",
    "graphql",
    "groovy",
    "haskell",
    "html",
    "java",
    "javascript",
    "json",
    "julia",
    "kotlin",
    "latex",
    "less",
    "lisp",
    "livescript",
    "lua",
    "makefile",
    "markdown",
    "markup",
    "matlab",
    "mermaid",
    "nix",
    "objective-c",
    "ocaml",
    "pascal",
    "perl",
    "php",
    "plain text",
    "powershell",
    "prolog",
    "protobuf",
    "python",
    "r",
    "reason",
    "ruby",
    "rust",
    "sass",
    "scala",
    "scheme",
    "scss",
    "shell",
    "sql",
    "swift",
    "typescript",
    "vb.net",
    "verilog",
    "vhdl",
    "visual basic",
    "webassembly",
    "xml",
    "yaml",
    "java/c/c++/c#",
]


def is_supported_code_lang(lang: str) -> bool:
    """Check if a code language is supported by Notion."""
    return lang in SUPPORTED_CODE_BLOCK_LANGUAGES


# GFM Alert types
SUPPORTED_GFM_ALERT_TYPES = ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION")

GfmAlertType = Literal["NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"]


def is_gfm_alert_type(type_str: str) -> bool:
    """Check if a string is a valid GFM alert type."""
    return type_str in SUPPORTED_GFM_ALERT_TYPES


class GfmAlertConfig(TypedDict):
    """GFM alert configuration."""

    emoji: EmojiRequest
    color: ApiColor


GFM_ALERT_MAP: Dict[str, GfmAlertConfig] = {
    "NOTE": {"emoji": "📘", "color": "blue_background"},
    "TIP": {"emoji": "💡", "color": "green_background"},
    "IMPORTANT": {"emoji": "☝️", "color": "purple_background"},
    "WARNING": {"emoji": "⚠️", "color": "yellow_background"},
    "CAUTION": {"emoji": "❗", "color": "red_background"},
}

SUPPORTED_EMOJI_COLOR_MAP: Dict[str, ApiColor] = {
    "👍": "green_background",
    "📘": "blue_background",
    "🚧": "yellow_background",
    "❗": "red_background",
}


class TableRowBlock(TypedDict):
    """Table row block."""

    type: Literal["table_row"]
    object: Literal["block"]
    table_row: Dict[str, Any]

