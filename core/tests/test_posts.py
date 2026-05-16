"""
Tests for core/posts.py

TDD approach: each test describes a behaviour the system must have.
Write a test, watch it fail (Red), make it pass (Green), tidy up (Refactor).

Run with:  uv run pytest core/tests/test_posts.py -v
"""
from datetime import date

import pytest

from core.posts import _parse_post_file, get_all_posts, get_post_by_slug


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_post_file(tmp_path, content):
    """Write content to a temp .md file and return the Path."""
    f = tmp_path / "test_post.md"
    f.write_text(content, encoding="utf-8")
    return f


VALID_POST = """\
---
title: Test Post
date: 2026-01-15
slug: test-post
type: blog
---

This is the body.
"""


# ---------------------------------------------------------------------------
# _parse_post_file — unit tests (no Django, no HTTP)
# ---------------------------------------------------------------------------

# Concept: happy path — confirm a valid file returns the fields you expect.
def test_valid_post_is_parsed(tmp_path):
    path = make_post_file(tmp_path, VALID_POST)
    result = _parse_post_file(path)

    assert result is not None
    assert result["title"] == "Test Post"
    assert result["slug"] == "test-post"
    assert result["type"] == "blog"
    assert result["date"] == date(2026, 1, 15)
    assert "This is the body" in result["body_html"]


# Concept: boundary condition — what happens when a required field is absent?
# Each missing field is its own test so failures are easy to diagnose.
@pytest.mark.parametrize("missing_field", ["title", "date", "slug", "type"])
def test_post_missing_required_field_returns_none(tmp_path, missing_field):
    lines = [
        "---",
        "title: Test Post",
        "date: 2026-01-15",
        "slug: test-post",
        "type: blog",
        "---",
        "",
        "Body.",
    ]
    # Remove the line that starts with the missing field
    lines = [l for l in lines if not l.startswith(missing_field + ":")]
    path = make_post_file(tmp_path, "\n".join(lines))

    assert _parse_post_file(path) is None


# Concept: valid/invalid enum — the type field has a fixed set of allowed values.
@pytest.mark.parametrize("post_type,should_parse", [
    ("blog", True),
    ("article", True),
    ("draft", False),
    ("note", False),
    ("", False),
])
def test_post_type_validation(tmp_path, post_type, should_parse):
    content = VALID_POST.replace("type: blog", f"type: {post_type}")
    path = make_post_file(tmp_path, content)
    result = _parse_post_file(path)

    if should_parse:
        assert result is not None
    else:
        assert result is None


# Concept: input normalisation — dates can arrive as strings or YAML date objects;
# the parser should always return a Python date.
@pytest.mark.parametrize("date_value,expected", [
    ("2026-01-15", date(2026, 1, 15)),
    ("2026-01-15T00:00:00", date(2026, 1, 15)),  # ISO datetime string
])
def test_date_normalisation(tmp_path, date_value, expected):
    content = VALID_POST.replace("date: 2026-01-15", f"date: {date_value}")
    path = make_post_file(tmp_path, content)
    result = _parse_post_file(path)

    assert result is not None
    assert result["date"] == expected


# Concept: invalid input — a malformed date should not crash; return None instead.
def test_invalid_date_returns_none(tmp_path):
    content = VALID_POST.replace("date: 2026-01-15", "date: not-a-date")
    path = make_post_file(tmp_path, content)

    assert _parse_post_file(path) is None


# Concept: graceful degradation — a file with no frontmatter at all is skipped silently.
def test_post_without_frontmatter_returns_none(tmp_path):
    path = make_post_file(tmp_path, "Just plain text, no frontmatter.")

    assert _parse_post_file(path) is None


# ---------------------------------------------------------------------------
# get_all_posts — integration (reads from content/posts/ via Django settings)
# ---------------------------------------------------------------------------

# Concept: return type contract — the function always returns a list, never raises.
@pytest.mark.django_db
def test_get_all_posts_returns_list():
    result = get_all_posts()
    assert isinstance(result, list)


# Concept: ordering — posts should be newest-first.
@pytest.mark.django_db
def test_posts_are_sorted_newest_first():
    posts = get_all_posts()
    dates = [p["date"] for p in posts]
    assert dates == sorted(dates, reverse=True)


# ---------------------------------------------------------------------------
# get_post_by_slug — integration
# ---------------------------------------------------------------------------

# Concept: return value contract — unknown slug returns None, not an exception.
@pytest.mark.django_db
def test_get_post_by_slug_unknown_returns_none():
    result = get_post_by_slug("this-slug-does-not-exist")
    assert result is None


# Concept: lookup correctness — known slug returns the matching post.
@pytest.mark.django_db
def test_get_post_by_slug_known_returns_post():
    # This test depends on hello-world.md existing in content/posts/.
    # If you remove that file, update this test to use a slug that exists.
    result = get_post_by_slug("hello-world")
    assert result is not None
    assert result["slug"] == "hello-world"
