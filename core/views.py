"""Adapt published Markdown content to Folio page contracts."""

import folio
from django.conf import settings
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from django.views.generic import View
from folio.contracts import (
    Homepage, HomepageNoteItem, ProvenanceEntry, Reading, ReadingRelation, SocialLink,
)

from .context_processors import BIO
from .posts import get_all_posts, get_post_by_slug


SOCIALS = (
    SocialLink("Email", "mailto:syafiq@syafiqkay.com", "email", "Email", external=False),
    SocialLink("GitHub", "https://github.com/skay93m", "github", "GitHub"),
    SocialLink("LinkedIn", "https://www.linkedin.com/in/syafiqkay/", "linkedin", "LinkedIn"),
    SocialLink("ResearchGate", "https://www.researchgate.net/profile/Syafiq-Kay", "researchgate", "ResearchGate"),
    SocialLink("ORCID", "https://orcid.org/0000-0001-8799-3188", "orcid", "ORCID"),
)
SHARED_PAGE = {
    "socials": SOCIALS,
    "footer_copyright": "© 2026 Syafiq Kay",
    "footer_source_url": "https://github.com/skay93m/sk-com",
    "footer_source_label": "open source",
    "footer_note": "I build in public and welcome corrections.",
    "home_href": "/",
    "home_aria_label": "Syafiq Kay home",
    "lang": "en-GB",
    "include_scripts": False,
    "show_theme_toggle": False,
}


def _homepage_note(note):
    return HomepageNoteItem(
        slug=note["slug"],
        title=note["title"],
        date=f"{note['date']:%d %B %Y}, {note['read_time']}",
        summary=note["description"] or "",
        href=reverse("core:note-detail", args=[note["slug"]]),
    )


class HomeView(View):
    def get(self, request):
        notes = get_all_posts()
        page = Homepage(
            author_name="Syafiq Kay",
            headline=BIO["tagline"],
            statement_paragraphs=tuple(BIO["paragraphs"]),
            now_heading="Now",
            now_paragraphs=("Working as a pharmacist in London while reading the MSc in Mental Health, Ethics and Law at King's College London and studying for CompTIA Network+.",),
            notes_heading="Notes",
            notes_intro="Ideas, statutory arguments, and operational problems I work through across pharmacy, health law, and software.",
            notes=tuple(_homepage_note(note) for note in notes if note["type"] == "note"),
            long_form_heading="Long-form notes",
            long_form_notes=tuple(_homepage_note(note) for note in notes if note["type"] == "essay"),
            long_form_paragraphs=("Longer essays on clinical systems, mental health law, and technical work will be added here as they mature.",),
            meta_description=BIO["tagline"],
            canonical_url="https://syafiqkay.com/",
            **SHARED_PAGE,
        )
        return folio.render(request, page, extra_context={"page_title": "Syafiq Kay"})


def _relations(links):
    return tuple(
        ReadingRelation(title=link["title"], href=link["href"], external=bool(link.get("external", False)))
        for link in links
    )


class NoteDetailView(View):
    def get(self, request, slug):
        note = get_post_by_slug(slug)
        if note is None:
            raise Http404
        provenance = []
        if note["ai_disclosure"]:
            provenance.append(ProvenanceEntry("AI contribution", note["ai_disclosure"]))
        provenance.append(ProvenanceEntry("Revision history", f"{note['date']:%d %B %Y}: Published."))
        page = Reading(
            eyebrow="Essay" if note["type"] == "essay" else "Note",
            title=note["title"],
            meta=(f"{note['date']:%d %B %Y}", note["author"], note["read_time"]),
            abstract=note["description"] or "",
            body_html=note["body_html"],
            provenance=tuple(provenance),
            backlinks=_relations(note.get("backlinks", ())),
            similar_links=_relations(note.get("similar_links", ())),
            back_href="/",
            standalone_header=True,
            show_print_action=False,
            show_progress=False,
            meta_description=note["description"] or BIO["tagline"],
            canonical_url=f"https://syafiqkay.com/notes/{note['slug']}/",
            author_meta=note["author"],
            citation_date=f"{note['date']:%Y/%m/%d}",
            **SHARED_PAGE,
        )
        return folio.render(request, page, extra_context={"page_title": f"{note['title']} · Syafiq Kay"})


@method_decorator(cache_control(max_age=86400), name='dispatch')
class RobotsTxtView(View):
    def get(self, request):
        robots_path = settings.BASE_DIR / 'robots.txt'
        content = None
        if robots_path.exists():
            try:
                content = robots_path.read_text()
            except OSError:
                pass

        if not content:
            content = (
                "User-agent: *\n"
                "Disallow: /admin/\n"
                "Crawl-delay: 1\n"
            )
        return HttpResponse(content, content_type='text/plain')
