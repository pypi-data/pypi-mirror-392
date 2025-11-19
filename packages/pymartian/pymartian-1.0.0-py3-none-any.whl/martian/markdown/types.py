"""Markdown AST type definitions.

From https://github.com/syntax-tree/mdast
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


class Node(TypedDict, total=False):
    """Base AST node."""
    type: str


class Parent(TypedDict, total=False):
    """Parent node with children."""
    children: List[Any]


class Literal(TypedDict, total=False):
    """Literal node with value."""
    value: str


class Root(TypedDict):
    """Root node."""
    type: Literal["root"]
    children: List["FlowContent"]


class Paragraph(TypedDict):
    """Paragraph node."""
    type: Literal["paragraph"]
    children: List["PhrasingContent"]


class Heading(TypedDict):
    """Heading node."""
    type: Literal["heading"]
    depth: Literal[1, 2, 3, 4, 5, 6]
    children: List["PhrasingContent"]


class ThematicBreak(TypedDict):
    """Thematic break node (horizontal rule)."""
    type: Literal["thematicBreak"]


class Blockquote(TypedDict):
    """Blockquote node."""
    type: Literal["blockquote"]
    children: List["FlowContent"]


class List(TypedDict, total=False):
    """List node."""
    type: Literal["list"]
    ordered: Optional[bool]
    start: Optional[int]
    spread: Optional[bool]
    children: List["ListItem"]


class ListItem(TypedDict, total=False):
    """List item node."""
    type: Literal["listitem"]
    checked: Optional[bool]
    spread: Optional[bool]
    children: List["FlowContent"]


class HTML(TypedDict):
    """HTML node."""
    type: Literal["html"]
    value: str


class Code(TypedDict, total=False):
    """Code block node."""
    type: Literal["code"]
    lang: Optional[str]
    meta: Optional[str]
    value: str


class Math(TypedDict):
    """Math block node."""
    type: Literal["math"]
    value: str


class Definition(TypedDict):
    """Definition node."""
    type: Literal["definition"]


class Text(TypedDict):
    """Text node."""
    type: Literal["text"]
    value: str


class Emphasis(TypedDict):
    """Emphasis node (italic)."""
    type: Literal["emphasis"]
    children: List["PhrasingContent"]


class Strong(TypedDict):
    """Strong node (bold)."""
    type: Literal["strong"]
    children: List["PhrasingContent"]


class Delete(TypedDict):
    """Delete node (strikethrough)."""
    type: Literal["delete"]
    children: List["PhrasingContent"]


class InlineCode(TypedDict):
    """Inline code node."""
    type: Literal["inlineCode"]
    value: str


class InlineMath(TypedDict):
    """Inline math node."""
    type: Literal["inlineMath"]
    value: str


class Break(TypedDict):
    """Line break node."""
    type: Literal["break"]


class Resource(TypedDict, total=False):
    """Resource with URL."""
    url: str
    title: Optional[str]


class Link(TypedDict):
    """Link node."""
    type: Literal["link"]
    url: str
    title: Optional[str]
    children: List["StaticPhrasingContent"]


class Image(TypedDict, total=False):
    """Image node."""
    type: Literal["image"]
    url: str
    title: Optional[str]


class LinkReference(TypedDict):
    """Link reference node."""
    type: Literal["linkReference"]
    children: List["StaticPhrasingContent"]


class ImageReference(TypedDict):
    """Image reference node."""
    type: Literal["imageReference"]


class Table(TypedDict, total=False):
    """Table node."""
    type: Literal["table"]
    align: Optional[List[Optional[Literal["left", "right", "center"]]]]
    children: List["TableRow"]


class TableRow(TypedDict):
    """Table row node."""
    type: Literal["tableRow"]
    children: List["TableCell"]


class TableCell(TypedDict):
    """Table cell node."""
    type: Literal["tableCell"]
    children: List["PhrasingContent"]


# Union types for content
StaticPhrasingContent = Union[
    Image,
    Break,
    Emphasis,
    HTML,
    ImageReference,
    InlineCode,
    Strong,
    Text,
    Delete,
    InlineMath,
]

PhrasingContent = Union[Link, LinkReference, StaticPhrasingContent]

Content = Union[Definition, Paragraph]

ListContent = ListItem

FlowContent = Union[
    Blockquote,
    Code,
    Heading,
    HTML,
    List,
    Image,
    ImageReference,
    ThematicBreak,
    Content,
    Table,
    Math,
]

TableContent = TableRow

RowContent = TableCell

MdastContent = Union[FlowContent, ListContent, PhrasingContent, TableContent, RowContent]

