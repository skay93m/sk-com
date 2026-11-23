"""
Tests for core/views.py

These are integration tests — they go through Django's URL routing, views,
and templates. pytest-django's `client` fixture provides a test HTTP client.

Run with:  uv run pytest core/tests/test_views.py -v
"""
from datetime import date

import pytest
from django.utils.html import escape

from core.context_processors import BIO
from core.tests.constants import (
    AI_CONTRIBUTION_SUMMARY,
    FORBIDDEN_AI_DISCLOSURE_TEXT,
    REVISION_HISTORY_SUMMARY,
)
from core.tests.helpers import (
    assert_hello_world_rendering,
    assert_no_boundary_copy,
    assert_note_provenance_contract,
    split_provenance_and_body,
)
from core.urls import LEGACY_REDIRECT_PATHS


# ---------------------------------------------------------------------------
# Public pages — smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    expected_meta = f'<meta name="description" content="{escape(BIO["tagline"])}">'.encode()
    assert expected_meta in response.content


@pytest.mark.django_db
def test_writings_page_returns_200(client):
    response = client.get("/writings/")
    assert response.status_code == 200
    assert b"Why this site exists, and why a simple text-file workflow might last." in response.content
    assert b" min read" in response.content
    assert response.content.index(b"Hello World") < response.content.index(
        b"Why this site exists, and why a simple text-file workflow might last."
    )


@pytest.mark.django_db
def test_writings_page_heading_and_title(client):
    response = client.get("/writings/")
    assert response.status_code == 200
    assert b"<h1>Writing</h1>" in response.content
    assert "<title>Writing · Syafiq Kay</title>" in response.content.decode()


@pytest.mark.django_db
def test_homepage_shows_writing_metadata(client):
    response = client.get("/")
    assert b"Why this site exists, and why a simple text-file workflow might last." in response.content
    assert b" min read" in response.content
    assert response.content.index(b"Hello World") < response.content.index(
        b"Why this site exists, and why a simple text-file workflow might last."
    )


@pytest.mark.django_db
@pytest.mark.parametrize("slug", LEGACY_REDIRECT_PATHS)
def test_stage_one_legacy_redirects(client, slug):
    response = client.get(f"/{slug}/")
    assert response.status_code == 302
    assert response["Location"] == "/"


# ---------------------------------------------------------------------------
# Post detail — valid and invalid slug
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_known_post_slug_returns_200(client):
    # Depends on hello-world.md existing in content/posts/.
    response = client.get("/writings/hello-world/")
    assert response.status_code == 200
    assert b"article-notebook" in response.content
    assert (
        b'<meta name="description" content="Why this site exists, and why a simple text-file workflow might last.">'
        in response.content
    )
    assert b"Why this site exists, and why a simple text-file workflow might last." in response.content
    assert b" min read" in response.content


@pytest.mark.django_db
def test_post_detail_without_description_falls_back_to_tagline(client, monkeypatch):
    dummy_post = {
        "title": "No Description Post",
        "description": None,
        "read_time": "1 min read",
        "date": date(2026, 1, 1),
        "slug": "no-description",
        "type": "article",
        "author": "Syafiq Kay",
        "ai_disclosure": None,
        "body_html": "<p>Body</p>",
    }
    monkeypatch.setattr(
        "core.views.get_post_by_slug",
        lambda slug: dummy_post if slug == "no-description" else None,
    )
    response = client.get("/writings/no-description/")
    assert response.status_code == 200
    expected_meta = f'<meta name="description" content="{escape(BIO["tagline"])}">'.encode()
    assert expected_meta in response.content
    assert AI_CONTRIBUTION_SUMMARY not in response.content.decode()


@pytest.mark.django_db
def test_unknown_post_slug_returns_404(client):
    response = client.get("/writings/this-post-does-not-exist/")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Lab detail — valid and invalid slug
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_lab_detail_renders_with_shell_and_home_link(client, tmp_path, settings):
    settings.CONTENT_DIR = tmp_path
    labs_dir = tmp_path / "labs"
    labs_dir.mkdir()
    (labs_dir / "sample-lab.md").write_text(
        "---\n"
        "title: Sample Lab\n"
        "date: 2026-05-16\n"
        "slug: sample-lab\n"
        "type: lab\n"
        "project: comptia-network-plus\n"
        "author: Syafiq Kay\n"
        "skills:\n"
        "  - VLANs\n"
        "---\n\n"
        "Lab notes.\n",
        encoding="utf-8",
    )
    response = client.get("/labs/sample-lab/")
    assert response.status_code == 200
    html = response.content.decode()
    assert "sk-spatial-shell" in html
    assert "Sample Lab" in html
    assert "Back to homepage" in html
    assert 'href="/labs/"' not in html


@pytest.mark.django_db
def test_unknown_lab_slug_returns_404(client):
    response = client.get("/labs/this-lab-does-not-exist/")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Robots.txt & Stage 1 contracts
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_robots_txt_returns_200(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/plain"


STAGE_ONE_STATEMENT_PARAGRAPHS = (
    "Eight years of clinical pharmacy across community, acute hospital, and mental health settings taught me one lesson that rarely appears in policy papers: healthcare design often diverges from what clinicians face on the ground. I study that gap across EPMA, Epic, and electronic health records to spot system-related safety risks, improve structured prescribing data, and strengthen medicines optimisation.",
    "My background deliberately crosses disciplines. I extracted clinical insights from electronic health records at South London and Maudsley NHS Trust, coded adverse events across clinical trials at Femtogenix to spot toxicity patterns, and gathered cross-agency evidence for patients at Rethink. Legal training through the GDL, an MSc in Mental Health, Ethics and Law at King's College London, and programming self-taught during my MPharm research run alongside that clinical work.",
    "Right now I investigate psychiatric prescribing, evidence heterogeneity, and healthcare law: specifically whether the Mental Health Act 1983 accounts for the limits of population-level evidence when applied to individual patients. Open to conversations on healthcare policy, research collaboration, and analytical roles across health and the public sector.",
)


def test_stage_one_homepage_contract(client):
    html = client.get("/").content.decode()
    for text in [
        "sk-spatial-shell",
        "Long-form notes",
        "King's College London",
        'aria-label="LinkedIn"',
        'aria-label="GitHub"',
        'aria-label="Email"',
        'aria-label="ResearchGate"',
        'aria-label="ORCID"',
    ]:
        assert text in html
    assert len(BIO["paragraphs"]) == 3
    for paragraph in STAGE_ONE_STATEMENT_PARAGRAPHS:
        assert escape(paragraph) in html
    assert_no_boundary_copy(html)
    assert "<script" not in html
    assert "<hr" not in html
    assert "?note=" not in html


def test_query_note_ignored_on_homepage(client):
    response = client.get("/", {"note": "hello-world"})
    assert response.status_code == 200
    html = response.content.decode()
    assert "Long-form notes" in html
    assert 'class="article-provenance"' not in html


@pytest.mark.parametrize("slug", ["hello-world", "controlled-drugs-indelible-ink"])
def test_reading_mode_note_contract(client, slug):
    response = client.get(f"/writings/{slug}/")
    assert response.status_code == 200
    html = response.content.decode()
    assert "sk-view-reading" in html
    assert 'class="abstract"' in html
    provenance_html, _ = split_provenance_and_body(html)
    assert REVISION_HISTORY_SUMMARY in provenance_html
    assert "Published by Syafiq Kay." in html
    assert "Back to homepage" in html
    assert_no_boundary_copy(html)
    assert FORBIDDEN_AI_DISCLOSURE_TEXT not in html
    assert "sk-reading-relations" not in html
    assert "<script" not in html


def test_hello_world_renders_ai_disclosure_without_duplicate_footer(client):
    html = client.get("/writings/hello-world/").content.decode()
    assert_hello_world_rendering(html)


def test_controlled_drugs_omits_ai_contribution_disclosure(client):
    html = client.get("/writings/controlled-drugs-indelible-ink/").content.decode()
    assert_note_provenance_contract(html, None)


def test_reading_relations_shown_when_populated(client, monkeypatch):
    dummy_post = {
        "title": "Linked Note",
        "description": "Summary.",
        "read_time": "1 min read",
        "date": date(2026, 5, 16),
        "slug": "linked-note",
        "type": "article",
        "author": "Syafiq Kay",
        "ai_disclosure": None,
        "body_html": "<p>Body</p>",
        "backlinks": [{"href": "/writings/hello-world/", "title": "Hello World"}],
        "similar_links": [],
    }
    monkeypatch.setattr(
        "core.views.get_post_by_slug",
        lambda slug: dummy_post if slug == "linked-note" else None,
    )
    html = client.get("/writings/linked-note/").content.decode()
    assert 'class="sk-reading-relations"' in html
    assert "Backlinks" in html
    assert "Hello World" in html
