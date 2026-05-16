"""
Tests for core/views.py

These are integration tests — they go through Django's URL routing, views,
and templates. pytest-django's `client` fixture provides a test HTTP client.

Concept: you are testing behaviour from the outside in, the same way a user
(or a browser) would. If the URL returns 200, the view and template wired up
correctly. If it returns 404, the not-found path is working.

Run with:  uv run pytest core/tests/test_views.py -v
"""
import pytest


# ---------------------------------------------------------------------------
# Public pages — smoke tests (do they respond at all?)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_writings_page_returns_200(client):
    response = client.get("/writings/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_labs_page_returns_200(client):
    response = client.get("/labs/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_cv_page_returns_200(client):
    response = client.get("/cv/")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Post detail — valid and invalid slug
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_known_post_slug_returns_200(client):
    # Depends on hello-world.md existing in content/posts/.
    response = client.get("/writings/hello-world/")
    assert response.status_code == 200


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
