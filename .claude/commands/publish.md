# /publish — Publish a note or essay

Given a markdown file (path or pasted content), publish it to `content/notes/`
on a new branch ready for review. Never merge to main or create a PR — the user
does that themselves after reviewing the branch.

## Inputs

The user will either:

- Paste the markdown content directly, or
- Provide a file path to an existing draft

If it's a file path, read it first. If it's pasted content, treat it as the file body.

If the user provides both a file path and pasted markdown in the same message, stop and
ask which one to use — do not guess. Proceeding with the wrong source could publish
stale content.

## Step 1 — Parse and validate frontmatter

The file must begin with a YAML frontmatter block (`---` ... `---`).
Extract the frontmatter and validate the required and optional fields.

### Notes and essays (`type: note` or `type: essay`)

Required fields:

| Field    | Rule                                                                                    |
|----------|-----------------------------------------------------------------------------------------|
| `title`  | Any non-empty string                                                                    |
| `date`   | `YYYY-MM-DD`                                                                            |
| `slug`   | Only `[a-zA-Z0-9_-]` — this becomes the URL (`/notes/<slug>/`)                          |
| `type`   | Must be `note` or `essay` (legacy `blog` -> `note` and `article` -> `essay` also work)  |
| `author` | Must be `Syafiq Kay` — used in citation meta tags                                       |

Optional fields:

| Field           | Rule                                                                                    |
|-----------------|-----------------------------------------------------------------------------------------|
| `description`   | One sentence, shown on listings and used as the page abstract and meta description      |
| `read_time`     | Overrides the value computed from word count, for example `4 min read`                  |
| `ai_disclosure` | Optional AI-use disclosure shown in Reading provenance when set; omit unless explicitly supplied (no AI contribution dropdown or boilerplate fallback is rendered when omitted or blank) |
| `backlinks`     | Optional list of `{title, href, external?}` links shown in Reading relations            |
| `similar_links` | Optional list of `{title, href, external?}` links shown in Reading relations            |

### Validation failures

If any required field is missing or invalid (including retired types like `lab` or `draft`),
stop immediately and tell the user exactly what is wrong. Do not proceed to git operations.
Give a corrected frontmatter block if the fix is obvious (e.g. wrong date format, invalid type value).

## Step 2 — Check for conflicts

Before creating the branch:

1. Read `content/notes/` and confirm no file already uses this filename or `slug`.
   If a file or slug already exists, tell the user and stop — do not overwrite.
2. Run `git branch --list publish/<slug>` (both local and remote via
   `git ls-remote --heads origin`). If the branch already exists, tell the user and
   stop.

## Step 3 — Create the branch from main

```bash
git fetch origin main
git checkout -b publish/<slug> origin/main
```

Do not branch from the currently checked-out branch — always branch from `origin/main`.

## Step 4 — Write the file

Destination: `content/notes/<slug>.md`.

Write the content exactly as provided. Do not alter the frontmatter or body.

## Step 5 — Commit and push

```bash
git add content/notes/<slug>.md
git commit -m "feat: add note — <title>"   # or "feat: add essay — <title>"
git push -u origin publish/<slug>
```

Use the `title` value from frontmatter in the commit message.

Do NOT:

- Stage anything other than the single content file
- Push to main
- Create a pull request
- Open a browser

## Step 6 — Report back

Tell the user:

- Branch name (e.g. `publish/hello-world`)
- File written (e.g. `content/notes/hello-world.md`)
- The URL it will appear at once merged (e.g. `/notes/hello-world/`)
- How to create the PR when ready: `gh pr create` or via GitHub web

Keep the report short — one line per item.

## Publishing rules reference

These are the constraints enforced by `core/posts.py` and Folio's `Reading` contract when loading content.
A file that violates them will be silently skipped or rejected — it will not render on the site.

- **Notes directory:** `content/notes/` — served at `/notes/<slug>/`
- **Allowed types:** `note`, `essay` (legacy `blog` maps to `note`, `article` maps to `essay`); `draft`, `lab`, or anything else is skipped
- **Author:** required on all entries; must be `Syafiq Kay`
- **Date:** parsed as `date` object; strings and YAML dates both accepted; invalid dates silently skip the file
- **Slug:** used as-is in the URL; Django's slug URL converter requires `[a-zA-Z0-9_-]`
- **Filename:** does not matter for URL routing — `slug` in frontmatter is the canonical URL
- **Faux-serif tags:** avoid Markdown `*emphasis*`/`**bold**` or raw `<em>`/`<strong>`/`<i>`/`<b>` tags in abstracts and bodies (`folio.contracts.Reading` rejects faux-serif tags)
- **Server cache:** notes are cached in memory after first load; Render re-deploys on push which resets the cache
