"""Shared assertion and HTML-splitting helpers for view and static-export tests."""

import re
from typing import Optional

from django.utils.html import escape

from core.tests.constants import (
    AI_CONTRIBUTION_LABEL,
    AI_CONTRIBUTION_SUMMARY,
    FORBIDDEN_AI_DISCLOSURE_TEXT,
    FORBIDDEN_BOUNDARY_TEXT,
    HELLO_WORLD_AI_DISCLOSURE,
    REVISION_HISTORY_SUMMARY,
)


def assert_no_boundary_copy(html: str) -> None:
    """Assert removed Stage 1 boundary copy and class names do not appear in HTML."""
    for forbidden in FORBIDDEN_BOUNDARY_TEXT:
        assert forbidden not in html


def _find_matching_div_end(html: str, start: int) -> int:
    depth = 0
    for tag in re.finditer(r"<(/)?div\b[^>]*>", html[start:]):
        depth += -1 if tag.group(1) else 1
        if depth == 0:
            return start + tag.end()
    raise AssertionError('Unclosed <div class="article-provenance"> element')


def split_provenance_and_body(html: str) -> tuple[str, str]:
    """Return the raw HTML of .article-provenance and the Markdown body that follows it."""
    start = html.find('<div class="article-provenance">')
    assert start != -1
    provenance_end = _find_matching_div_end(html, start)
    body_start = html.find('<div class="sk-reading-body">', provenance_end)
    assert body_start != -1
    body_end = _find_matching_div_end(html, body_start)
    return html[start:provenance_end], html[body_start:body_end]


def assert_note_provenance_contract(html: str, ai_disclosure: Optional[str]) -> str:
    """Assert Reading provenance contract for a note and return its article body HTML."""
    provenance_html, body_html = split_provenance_and_body(html)
    assert REVISION_HISTORY_SUMMARY in provenance_html
    assert FORBIDDEN_AI_DISCLOSURE_TEXT not in html
    assert_no_boundary_copy(html)
    if ai_disclosure:
        expected_disclosure = (
            f"<details>{AI_CONTRIBUTION_SUMMARY}<p>{escape(ai_disclosure)}</p></details>"
        )
        assert re.sub(r">\s+<", "><", expected_disclosure) in re.sub(r">\s+<", "><", provenance_html)
    else:
        assert AI_CONTRIBUTION_SUMMARY not in html
        assert AI_CONTRIBUTION_LABEL not in provenance_html
    return body_html


def assert_hello_world_rendering(html: str) -> None:
    """Assert hello-world renders its AI disclosure only in provenance with a clean body."""
    body_html = assert_note_provenance_contract(html, HELLO_WORLD_AI_DISCLOSURE)
    assert "<hr" not in body_html
    assert "<em>" not in body_html
    assert escape(HELLO_WORLD_AI_DISCLOSURE) not in body_html
    assert html.count(escape(HELLO_WORLD_AI_DISCLOSURE)) == 1
