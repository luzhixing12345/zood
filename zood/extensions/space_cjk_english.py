#!/usr/bin/env python3
"""
Add spaces between adjacent Chinese and English text in a Markdown file.

By default, the formatted Markdown is written to stdout. Use --in-place to
rewrite the input file.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CJK = r"\u4e00-\u9fff"
ENGLISH = r"A-Za-z0-9"

CJK_BEFORE_ENGLISH = re.compile(rf"([{CJK}])([{ENGLISH}])")
ENGLISH_BEFORE_CJK = re.compile(rf"([{ENGLISH}])([{CJK}])")
INLINE_CODE = re.compile(r"(`+)(.*?)(\1)")
FENCE_START = re.compile(r"^\s*(```|~~~)")


def add_spaces_to_text(text: str) -> str:
    text = CJK_BEFORE_ENGLISH.sub(r"\1 \2", text)
    return ENGLISH_BEFORE_CJK.sub(r"\1 \2", text)


def format_non_code_line(line: str) -> str:
    parts: list[str] = []
    last_end = 0

    for match in INLINE_CODE.finditer(line):
        parts.append(add_spaces_to_text(line[last_end : match.start()]))
        parts.append(match.group(0))
        last_end = match.end()

    parts.append(add_spaces_to_text(line[last_end:]))
    return "".join(parts)


def format_markdown(text: str) -> str:
    lines = text.splitlines(keepends=True)
    formatted_lines: list[str] = []
    in_fence = False
    fence_marker = ""

    for line in lines:
        fence_match = FENCE_START.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            formatted_lines.append(line)
            continue

        if in_fence:
            formatted_lines.append(line)
        else:
            formatted_lines.append(format_non_code_line(line))

    return "".join(formatted_lines)
