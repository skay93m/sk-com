# Workflow Guide — syafiqkay.com

## New post

1. Create a new `.md` file in `content/posts/`
2. Add frontmatter at the top — all four fields are required:

```markdown
---
title: Your Post Title
date: 2026-05-01
slug: your-post-slug
type: blog
---

Your writing goes here.
```

- `date` — `YYYY-MM-DD`
- `slug` — letters, numbers, hyphens only; becomes the URL (`/writings/your-post-slug/`)
- `type` — `blog` or `article`; any other value causes the post to be silently skipped

3. Commit and push straight to `main`:

```bash
git add content/posts/your-post-title.md
git commit -m "feat: add post — Your Post Title"
git push
```

Render redeploys automatically. Post is live in 2–3 minutes.

---

## Edit existing post

1. Open the relevant `.md` file in `content/posts/`
2. Make your edits — do not change the `slug` (it will break the existing URL)
3. Commit and push straight to `main`:

```bash
git add content/posts/your-post-title.md
git commit -m "fix: update post — Your Post Title"
git push
```

---

## CV updates

The CV is a Django template, not a markdown file.

1. Edit `core/templates/cv.html` directly
2. Commit and push straight to `main`:

```bash
git add core/templates/cv.html
git commit -m "chore: update CV"
git push
```

For bio text (the paragraph that appears on both the homepage and CV), edit `core/context_processors.py` instead.

---

## Pagination (future work)

When the post list grows long enough to need pagination, this is a **feature branch** — it touches views, templates, and URL structure.

```bash
git checkout -b feature/pagination
# make changes
git push -u origin feature/pagination
# open pull request on GitHub → merge → Render redeploys
```

Rule of thumb: content changes (posts, CV) go straight to `main`. Code changes (templates, views, settings) go via a feature branch and pull request.
