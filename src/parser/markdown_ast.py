"""Minimal markdown AST parser for agent config sources."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence


@dataclass(frozen=True)
class HeadingNode:
    level: int
    text: str
    raw_line: str
    line_start: int
    line_end: int


@dataclass(frozen=True)
class ParagraphNode:
    lines: Sequence[str]
    line_start: int
    line_end: int


@dataclass(frozen=True)
class ListItemNode:
    lines: Sequence[str]
    line_start: int
    line_end: int


@dataclass(frozen=True)
class ListBlockNode:
    ordered: bool
    items: Sequence[ListItemNode]
    line_start: int
    line_end: int


@dataclass(frozen=True)
class CodeBlockNode:
    fence: str
    info: str | None
    lines: Sequence[str]
    line_start: int
    line_end: int
    opening_line: str
    closing_line: str | None


@dataclass(frozen=True)
class BlankLineNode:
    lines: Sequence[str]
    line_start: int
    line_end: int


MarkdownNode = (
    HeadingNode
    | ParagraphNode
    | ListBlockNode
    | ListItemNode
    | CodeBlockNode
    | BlankLineNode
)


_FENCE_RE = re.compile(r"^\s*(```+|~~~+)\s*(.*)$")
_HEADING_RE = re.compile(r"^\s*(#{1,6})\s*(.*)$")
_LIST_RE = re.compile(r"^\s*([-+*]|\d+[.)])\s+.*$")
_ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+.*$")


def parse_markdown(source: str | Iterable[str]) -> list[MarkdownNode]:
    lines = _coerce_lines(source)
    nodes: list[MarkdownNode] = []
    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]
        stripped = line.rstrip("\n")

        if stripped.strip() == "":
            i = _consume_blank_lines(lines, i, nodes)
            continue

        fence_match = _FENCE_RE.match(stripped)
        if fence_match:
            i = _consume_code_block(lines, i, nodes, fence_match)
            continue

        heading_match = _HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            nodes.append(
                HeadingNode(level=level, text=text, raw_line=line, line_start=i + 1, line_end=i + 2)
            )
            i += 1
            continue

        if _LIST_RE.match(stripped):
            i = _consume_list_block(lines, i, nodes)
            continue

        i = _consume_paragraph(lines, i, nodes)

    return nodes


def _coerce_lines(source: str | Iterable[str]) -> list[str]:
    if isinstance(source, str):
        return source.splitlines(keepends=True)
    return list(source)


def _consume_blank_lines(lines: list[str], start: int, nodes: list[MarkdownNode]) -> int:
    i = start
    blank_lines: list[str] = []
    while i < len(lines) and lines[i].strip() == "":
        blank_lines.append(lines[i])
        i += 1
    nodes.append(BlankLineNode(lines=blank_lines, line_start=start + 1, line_end=i + 1))
    return i


def _consume_code_block(
    lines: list[str],
    start: int,
    nodes: list[MarkdownNode],
    fence_match: re.Match[str],
) -> int:
    fence = fence_match.group(1)
    info = fence_match.group(2).strip() or None
    opening_line = lines[start]
    code_lines: list[str] = []
    i = start + 1
    closing_line: str | None = None

    while i < len(lines):
        current = lines[i]
        current_stripped = current.rstrip("\n")
        if current_stripped.lstrip().startswith(fence):
            closing_line = current
            break
        code_lines.append(current)
        i += 1

    if closing_line is None:
        nodes.append(
            CodeBlockNode(
                fence=fence,
                info=info,
                lines=code_lines,
                line_start=start + 1,
                line_end=len(lines) + 1,
                opening_line=opening_line,
                closing_line=None,
            )
        )
        return len(lines)

    nodes.append(
        CodeBlockNode(
            fence=fence,
            info=info,
            lines=code_lines,
            line_start=start + 1,
            line_end=i + 2,
            opening_line=opening_line,
            closing_line=closing_line,
        )
    )
    return i + 1


def _consume_list_block(lines: list[str], start: int, nodes: list[MarkdownNode]) -> int:
    items: list[ListItemNode] = []
    i = start
    ordered = _ORDERED_RE.match(lines[i].rstrip("\n")) is not None
    while i < len(lines):
        current = lines[i]
        current_stripped = current.rstrip("\n")
        if current_stripped.strip() == "":
            break
        if _FENCE_RE.match(current_stripped) or _HEADING_RE.match(current_stripped):
            break
        if _LIST_RE.match(current_stripped):
            item_start = i
            item_lines = [lines[i]]
            i += 1
            while i < len(lines):
                continuation = lines[i]
                continuation_stripped = continuation.rstrip("\n")
                if continuation_stripped.strip() == "":
                    break
                if _FENCE_RE.match(continuation_stripped) or _HEADING_RE.match(
                    continuation_stripped
                ):
                    break
                if _LIST_RE.match(continuation_stripped):
                    break
                if continuation.startswith((" ", "\t")):
                    item_lines.append(continuation)
                    i += 1
                    continue
                break
            items.append(
                ListItemNode(
                    lines=item_lines,
                    line_start=item_start + 1,
                    line_end=item_start + len(item_lines) + 1,
                )
            )
            continue
        break
    nodes.append(ListBlockNode(ordered=ordered, items=items, line_start=start + 1, line_end=i + 1))
    return i


def _consume_paragraph(lines: list[str], start: int, nodes: list[MarkdownNode]) -> int:
    i = start
    paragraph_lines: list[str] = []
    while i < len(lines):
        current = lines[i]
        current_stripped = current.rstrip("\n")
        if current_stripped.strip() == "":
            break
        if _FENCE_RE.match(current_stripped) or _HEADING_RE.match(current_stripped):
            break
        if _LIST_RE.match(current_stripped):
            break
        paragraph_lines.append(current)
        i += 1
    if paragraph_lines:
        nodes.append(
            ParagraphNode(
                lines=paragraph_lines,
                line_start=start + 1,
                line_end=start + len(paragraph_lines) + 1,
            )
        )
    return i
