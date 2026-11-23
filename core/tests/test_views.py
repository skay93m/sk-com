"""
Tests for core/views.py

These are integration tests — they go through Django's URL routing, views,
and templates. pytest-django's `client` fixture provides a test HTTP client.

Concept: you are testing behaviour from the outside in, the same way a user
(or a browser) would. If the URL returns 200, the view and template wired up
correctly. If it returns 404, the not-found path is working.

Run with:  uv run pytest core/tests/test_views.py -v
"""
from datetime import date

import pytest


# ---------------------------------------------------------------------------
# Public pages — smoke tests (do they respond at all?)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert (
        b'<meta name="description" content="I solve problems using analytical thinking and drawing insights from various perspectives.">'
        in response.content
    )


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
def test_labs_page_redirects(client):
    response = client.get("/labs/")
    assert response.status_code == 302
    assert response["Location"] == "/"


@pytest.mark.django_db
def test_cv_page_redirects(client):
    response = client.get("/cv/")
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
        "body_html": "<p>Body</p>",
    }
    monkeypatch.setattr(
        "core.views.get_post_by_slug",
        lambda slug: dummy_post if slug == "no-description" else None,
    )
    response = client.get("/writings/no-description/")
    assert response.status_code == 200
    assert (
        b'<meta name="description" content="I solve problems using analytical thinking and drawing insights from various perspectives.">'
        in response.content
    )


@pytest.mark.django_db
def test_unknown_post_slug_returns_404(client):
    response = client.get("/writings/this-post-does-not-exist/")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Lab detail — valid and invalid slug
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_unknown_lab_slug_returns_404(client):
    response = client.get("/labs/this-lab-does-not-exist/")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Robots.txt
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_robots_txt_returns_200(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/plain"

@pytest.mark.parametrize("path", ["/about/", "/writing/"])
def test_stage_one_legacy_redirects(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert response["Location"] == "/"


def test_stage_one_homepage_contract(client):
    html = client.get("/").content.decode()
    for text in ["sk-spatial-shell", "Long-form notes", "King's College London", "clinical advice", 'aria-label="LinkedIn"', 'aria-label="GitHub"']:
        assert text in html
    assert "<script" not in html
    assert "<hr" not in html


def test_query_note_reading_contract(client):
    response = client.get("/", {"note": "hello-world"})
    assert response.status_code == 200
    html = response.content.decode()
    assert 'class="abstract"' in html
    assert 'class="article-provenance"' in html
    assert "Back to homepage" in html
    assert "sk-reading-relations" not in html
    assert client.get("/", {"note": "missing"}).status_code == 404
