"""Public route tests use isolated Markdown notes."""
import pytest
from django.utils.html import escape

from core.context_processors import BIO
from core.tests.helpers import assert_note_provenance_contract
from core.urls import LEGACY_REDIRECT_PATHS


@pytest.fixture
def note_file(tmp_path, settings):
    settings.CONTENT_DIR = tmp_path
    notes = tmp_path / "notes"
    notes.mkdir()
    path = notes / "sample.md"
    path.write_text("---\ntitle: Sample note\ndate: 2026-05-16\nslug: sample\ntype: note\nauthor: Syafiq Kay\ndescription: A sample summary.\nai_disclosure: Grammar assistance.\n---\n\nA body with [a link](https://example.org).\n")
    return path


def test_homepage_lists_notes(client, note_file):
    response = client.get("/")
    assert response.status_code == 200
    html = response.content.decode()
    assert '<title>Syafiq Kay</title>' in html
    assert 'href="/notes/sample/"' in html
    assert "A sample summary." in html
    assert "16 May 2026, 1 min read" in html
    for paragraph in BIO["paragraphs"]:
        assert escape(paragraph) in html
    for label in ("Email", "GitHub", "LinkedIn", "ResearchGate", "ORCID"):
        assert f'aria-label="{label}"' in html
    assert "<script" not in html
    assert "<hr" not in html


@pytest.mark.parametrize("kind,eyebrow", [("note", "Note"), ("essay", "Essay"), ("blog", "Note"), ("article", "Essay")])
def test_reading_renders_markdown_and_metadata(client, note_file, kind, eyebrow):
    note_file.write_text(note_file.read_text().replace("type: note", f"type: {kind}"))
    response = client.get("/notes/sample/")
    assert response.status_code == 200
    html = response.content.decode()
    body = assert_note_provenance_contract(html, "Grammar assistance.")
    assert '<a href="https://example.org">a link</a>' in body
    assert "Grammar assistance." not in body
    assert f'class="eyebrow">{eyebrow}</div>' in html
    assert '<html lang="en-GB"' in html
    assert 'name="description" content="A sample summary."' in html
    assert 'rel="canonical" href="https://syafiqkay.com/notes/sample/"' in html
    assert 'name="citation_author" content="Syafiq Kay"' in html
    assert 'name="citation_date" content="2026/05/16"' in html
    assert '<title>Sample note · Syafiq Kay</title>' in html
    assert "sk-reading-relations" not in html
    assert "<script" not in html


@pytest.mark.parametrize("value", ["", "ai_disclosure: ''", "ai_disclosure: '   '"])
def test_optional_disclosure_and_description(client, note_file, value):
    note_file.write_text(note_file.read_text().replace("ai_disclosure: Grammar assistance.", value).replace("description: A sample summary.", ""))
    html = client.get("/notes/sample/").content.decode()
    assert_note_provenance_contract(html, None)
    assert f'name="description" content="{escape(BIO["tagline"])}"' in html
    assert 'class="abstract"' not in html


@pytest.mark.parametrize("slug", LEGACY_REDIRECT_PATHS)
def test_legacy_redirects(client, slug):
    response = client.get(f"/{slug}/")
    assert response.status_code == 302
    assert response["Location"] == "/"


def test_retired_detail_redirects(client):
    for path in ("/writings/sample/", "/labs/sample/"):
        response = client.get(path)
        assert response.status_code == 302
        assert response["Location"] == "/"


def test_missing_note_and_admin_are_unavailable(client, note_file):
    assert client.get("/notes/missing/").status_code == 404
    assert client.get("/admin/").status_code == 404


def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/plain"


def test_essays_appear_in_long_form_section(client, note_file):
    note_file.write_text(note_file.read_text().replace("type: note", "type: essay"))
    html = client.get("/").content.decode()
    before, after = html.split("<h2>Long-form notes</h2>")
    assert 'href="/notes/sample/"' not in before
    assert 'href="/notes/sample/"' in after
    assert "A sample summary." in after


def test_reading_relations_from_frontmatter(client, note_file):
    note_file.write_text(note_file.read_text().replace(
        "description: A sample summary.",
        "backlinks: [{title: Related note, href: /notes/related/}]\nsimilar_links: [{title: External essay, href: 'https://example.org/essay', external: true}]"
    ))
    html = client.get("/notes/sample/").content.decode()
    assert 'class="sk-reading-relations"' in html
    assert '<a href="/notes/related/">Related note</a>' in html
    assert '<a href="https://example.org/essay" target="_blank" rel="noopener noreferrer">External essay</a>' in html
