"""
Tests for core/labs.py

Run with:  uv run pytest core/tests/test_labs.py -v
"""
from datetime import date
from pathlib import Path

import pytest
import yaml

from core.labs import (
    _parse_lab_file,
    get_all_labs,
    get_lab_by_slug,
    get_labs_grouped_by_project,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_lab_file(tmp_path, content, filename="test_lab.md"):
    f = tmp_path / filename
    f.write_text(content, encoding="utf-8")
    return f


def make_projects_yaml(labs_dir: Path, projects: list):
    labs_dir.mkdir(parents=True, exist_ok=True)
    (labs_dir / "projects.yaml").write_text(
        yaml.dump(projects), encoding="utf-8"
    )


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

# Concept: happy path — all fields including optional metadata.
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


# Concept: optional fields absent — parse fine with empty lists.
def test_valid_lab_without_optional_fields_is_parsed(tmp_path):
    path = make_lab_file(tmp_path, MINIMAL_LAB)
    result = _parse_lab_file(path)

    assert result is not None
    assert result["project"] == "comptia-network-plus"
    assert result["tools"] == []
    assert result["objectives"] == []
    assert result["skills"] == []


# Concept: boundary condition — every required field, including project, must be present.
@pytest.mark.parametrize("missing_field", ["title", "date", "slug", "type", "project", "author"])
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


# Concept: valid/invalid enum — only type: lab is accepted.
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


# ---------------------------------------------------------------------------
# get_labs_grouped_by_project — integration using settings fixture
#
# Concept: the settings fixture (from pytest-django) lets you override Django
# settings for a single test. Here we point CONTENT_DIR at tmp_path so we
# can control exactly which labs and projects exist without touching real files.
# ---------------------------------------------------------------------------

PROJECTS = [
    {"slug": "comptia-network-plus", "name": "CompTIA Network+", "description": "Networking labs."},
    {"slug": "clinical-pharmacy",    "name": "Clinical Pharmacy",  "description": "Clinical cases."},
]


def _write_lab(labs_dir: Path, slug: str, project: str, date_str: str, filename=None):
    content = f"""\
---
title: Lab {slug}
date: {date_str}
slug: {slug}
type: lab
project: {project}
author: Syafiq Kay
---

Body.
"""
    (labs_dir / (filename or f"{slug}.md")).write_text(content, encoding="utf-8")


# Concept: correct structure — grouped result has name, description, and labs list.
@pytest.mark.django_db
def test_get_labs_grouped_returns_correct_structure(tmp_path, settings):
    settings.CONTENT_DIR = tmp_path
    labs_dir = tmp_path / "labs"
    labs_dir.mkdir()
    make_projects_yaml(labs_dir, PROJECTS)
    _write_lab(labs_dir, "vlan-lab", "comptia-network-plus", "2026-05-16")

    result = get_labs_grouped_by_project()

    assert len(result) == 1
    project = result[0]
    assert project["slug"] == "comptia-network-plus"
    assert project["name"] == "CompTIA Network+"
    assert "description" in project
    assert len(project["labs"]) == 1
    assert project["labs"][0]["slug"] == "vlan-lab"


# Concept: ordering — project with the most recent lab comes first.
@pytest.mark.django_db
def test_projects_sorted_by_most_recent_lab(tmp_path, settings):
    settings.CONTENT_DIR = tmp_path
    labs_dir = tmp_path / "labs"
    labs_dir.mkdir()
    make_projects_yaml(labs_dir, PROJECTS)
    _write_lab(labs_dir, "old-lab",    "comptia-network-plus", "2026-01-01")
    _write_lab(labs_dir, "recent-lab", "clinical-pharmacy",    "2026-05-16")

    result = get_labs_grouped_by_project()

    assert result[0]["slug"] == "clinical-pharmacy"
    assert result[1]["slug"] == "comptia-network-plus"


# Concept: empty state — a project defined in YAML with no matching labs is hidden.
@pytest.mark.django_db
def test_project_with_no_labs_not_included(tmp_path, settings):
    settings.CONTENT_DIR = tmp_path
    labs_dir = tmp_path / "labs"
    labs_dir.mkdir()
    make_projects_yaml(labs_dir, PROJECTS)
    _write_lab(labs_dir, "vlan-lab", "comptia-network-plus", "2026-05-16")
    # clinical-pharmacy has no labs

    result = get_labs_grouped_by_project()

    slugs = [p["slug"] for p in result]
    assert "comptia-network-plus" in slugs
    assert "clinical-pharmacy" not in slugs


# Concept: validation at load time — a lab whose project slug is not in projects.yaml
# is silently excluded from the grouped output. The parser accepts any non-empty
# project string; the grouping function enforces the allow-list.
@pytest.mark.django_db
def test_lab_with_unknown_project_excluded_from_grouping(tmp_path, settings):
    settings.CONTENT_DIR = tmp_path
    labs_dir = tmp_path / "labs"
    labs_dir.mkdir()
    make_projects_yaml(labs_dir, PROJECTS)
    _write_lab(labs_dir, "orphan-lab", "unknown-project", "2026-05-16")

    result = get_labs_grouped_by_project()

    assert result == []


# ---------------------------------------------------------------------------
# get_all_labs / get_lab_by_slug — basic integration
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
