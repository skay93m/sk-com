"""
Tests for core/labs.py

Run with:  uv run pytest core/tests/test_labs.py -v
"""
from datetime import date

import pytest

from core.labs import (
    LAB_REQUIRED_FIELDS,
    _parse_lab_file,
    get_all_labs,
    get_lab_by_slug,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_lab_file(tmp_path, content, filename="test_lab.md"):
    f = tmp_path / filename
    f.write_text(content, encoding="utf-8")
    return f


VALID_LAB = """\
---
title: VLAN Segmentation
date: 2026-05-16
slug: vlan-segmentation
type: lab
project: comptia-network-plus
author: Syafiq Kay
tools:
  - Cisco Packet Tracer
  - Cisco IOS CLI
objectives:
  - Configure VLANs 10 and 20
  - Verify inter-VLAN isolation
skills:
  - VLANs
  - Cisco IOS
---

## Topology

Body text here.
"""

MINIMAL_LAB = """\
---
title: Minimal Lab
date: 2026-05-16
slug: minimal-lab
type: lab
project: comptia-network-plus
author: Syafiq Kay
---

Body.
"""


# ---------------------------------------------------------------------------
# _parse_lab_file — unit tests (no Django, no filesystem beyond tmp_path)
# ---------------------------------------------------------------------------

def test_valid_lab_with_metadata_is_parsed(tmp_path):
    path = make_lab_file(tmp_path, VALID_LAB)
    result = _parse_lab_file(path)

    assert result is not None
    assert result["title"] == "VLAN Segmentation"
    assert result["slug"] == "vlan-segmentation"
    assert result["type"] == "lab"
    assert result["project"] == "comptia-network-plus"
    assert result["author"] == "Syafiq Kay"
    assert result["date"] == date(2026, 5, 16)
    assert result["tools"] == ["Cisco Packet Tracer", "Cisco IOS CLI"]
    assert result["objectives"] == ["Configure VLANs 10 and 20", "Verify inter-VLAN isolation"]
    assert result["skills"] == ["VLANs", "Cisco IOS"]
    assert "Body text" in result["body_html"]


def test_valid_lab_without_optional_fields_is_parsed(tmp_path):
    path = make_lab_file(tmp_path, MINIMAL_LAB)
    result = _parse_lab_file(path)

    assert result is not None
    assert result["project"] == "comptia-network-plus"
    assert result["tools"] == []
    assert result["objectives"] == []
    assert result["skills"] == []


@pytest.mark.parametrize("missing_field", LAB_REQUIRED_FIELDS)
def test_lab_missing_required_field_returns_none(tmp_path, missing_field):
    lines = [
        "---",
        "title: VLAN Segmentation",
        "date: 2026-05-16",
        "slug: vlan-segmentation",
        "type: lab",
        "project: comptia-network-plus",
        "author: Syafiq Kay",
        "---",
        "",
        "Body.",
    ]
    lines = [l for l in lines if not l.startswith(missing_field + ":")]
    path = make_lab_file(tmp_path, "\n".join(lines))

    assert _parse_lab_file(path) is None


def test_lab_wrong_author_returns_none(tmp_path):
    content = VALID_LAB.replace("author: Syafiq Kay", "author: Someone Else")
    path = make_lab_file(tmp_path, content)
    assert _parse_lab_file(path) is None


@pytest.mark.parametrize("post_type,should_parse", [
    ("lab", True),
    ("blog", False),
    ("article", False),
    ("draft", False),
])
def test_lab_type_validation(tmp_path, post_type, should_parse):
    content = MINIMAL_LAB.replace("type: lab", f"type: {post_type}")
    path = make_lab_file(tmp_path, content)
    result = _parse_lab_file(path)

    if should_parse:
        assert result is not None
    else:
        assert result is None


@pytest.mark.parametrize("header", ["", "just a string", "- a\n- list"])
def test_lab_with_non_mapping_frontmatter_returns_none(tmp_path, header):
    path = make_lab_file(tmp_path, f"---\n{header}\n---\n\nBody.\n")

    assert _parse_lab_file(path) is None


# ---------------------------------------------------------------------------
# get_all_labs / get_lab_by_slug — integration
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_all_labs_returns_list():
    result = get_all_labs()
    assert isinstance(result, list)


@pytest.mark.django_db
def test_labs_are_sorted_newest_first():
    labs = get_all_labs()
    dates = [l["date"] for l in labs]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_get_lab_by_slug_unknown_returns_none():
    result = get_lab_by_slug("this-lab-does-not-exist")
    assert result is None
