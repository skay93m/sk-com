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

## New lab

Labs are network/security write-ups published at `/labs/<slug>/`. They follow the same publish-by-push workflow as posts but live in a separate directory and support additional metadata fields.

1. Export your topology diagram from Cisco Packet Tracer: **File → Export → As Image**
2. Save the image to `static/labs/<your-slug>/topology.png` (create the folder if needed)
3. Optionally save the `.pkt` file to `static/labs/<your-slug>/lab.pkt` for recruiters to download
4. Create a `.md` file in `content/labs/`:

```markdown
---
title: VLAN Segmentation on a Cisco Switch
date: 2026-05-16
slug: vlan-segmentation-cisco
type: lab
tools:
  - Cisco Packet Tracer
  - Cisco IOS CLI
objectives:
  - Configure VLANs 10, 20, 30 on a 2960 switch
  - Verify inter-VLAN isolation
skills:
  - VLANs
  - Cisco IOS
  - Network segmentation
---

## Topology

![Network topology](/static/labs/vlan-segmentation-cisco/topology.png)

## Overview

Write your explanation here in markdown.
```

**Field rules:**
- `title`, `date`, `slug`, `type: lab` are all **required** — any missing field silently skips the file
- `tools`, `objectives`, `skills` are **optional** lists — omit any you don't need
- `slug` must be `[a-zA-Z0-9_-]` only and matches the folder name under `static/labs/`
- Do **not** change `slug` after publishing — it will break the URL

5. Commit and push:

```bash
git add content/labs/your-filename.md static/labs/your-slug/
git commit -m "feat: add lab — Your Lab Title"
git push
```

Render redeploys automatically. Lab is live in 2–3 minutes at `/labs/<slug>/`.

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

---

## Projects page (future work)

A dedicated section for active experiments, structured as a lab notebook. Each experiment would have a defined aim, hypothesis, method, and running log of observations — mirroring the scientific method applied to career exploration. This is distinct from the CV's active experiments section: the CV shows the summary, the projects page shows the working notes.

Feature branch: `feature/projects`

---

## Tools page (future work)

A collection of small, self-contained clinical and professional tools accessible from any browser. Each tool lives at `/tools/<tool-name>/` and is built as a Django view with a minimal form and output — no external dependencies, no accounts required.

**Planned tools:**

- **Emergency contraception consultation aid**
 — takes last menstrual period date, average cycle length, and next expected period; estimates ovulation window; visualises the menstrual cycle with EHC options and their effectiveness windows explained in plain language. Designed to support patient consultations at the counter.

When building a new tool:
- Add the view to `core/views.py`
- Add the URL to `core/urls.py` under `tools/<tool-name>/`
- Add the template to `core/templates/tools/`
- Any JavaScript needed for visualisation should be minimal and inline — no npm, no build step

Feature branch: `feature/tools`
