# /publish — Publish a blog post or lab write-up

Given a markdown file (path or pasted content), publish it to the correct content
directory on a new branch ready for review. Never merge to main or create a PR —
the user does that themselves after reviewing the branch.

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
Extract the frontmatter and check the `type` field to determine what is being published.

### Posts (`type: blog` or `type: article`)

Required fields:

| Field    | Rule                                                            |
|----------|-----------------------------------------------------------------|
| `title`  | Any non-empty string                                            |
| `date`   | `YYYY-MM-DD`                                                    |
| `slug`   | Only `[a-zA-Z0-9_-]` — this becomes the URL                    |
| `type`   | Must be `blog` or `article` (not `lab`, `draft`, `note`, etc.) |
| `author` | Must be `Syafiq Kay` — used in citation meta tags              |

### Labs (`type: lab`)

Required fields:

| Field     | Rule                                               |
|-----------|----------------------------------------------------|
| `title`   | Any non-empty string                               |
| `date`    | `YYYY-MM-DD`                                       |
| `slug`    | Only `[a-zA-Z0-9_-]`                              |
| `type`    | Must be `lab`                                      |
| `project` | Must match a slug in `content/labs/projects.yaml` |
| `author`  | Must be `Syafiq Kay` — used in citation meta tags |

**Optional lab fields** (include if present, ignore if absent):

- `tools` — list of tool names used
- `objectives` — list of learning objectives
- `skills` — list of skills demonstrated (shown as badges on /labs/)

Always read `content/labs/projects.yaml` for the authoritative list of valid project slugs.
The list below is illustrative only and will go out of date as projects are added:

- `comptia-network-plus`
- `comptia-security-plus`
- `actuarial-statistics`
- `clinical-pharmacy`

If the `project` slug is not in `projects.yaml`, **stop and tell the user**. Do not
create the branch. They either need to fix the slug or add the project to
`content/labs/projects.yaml` first.

### Validation failures

If any required field is missing or invalid, stop immediately and tell the user exactly
what is wrong. Do not proceed to git operations. Give a corrected frontmatter block if
the fix is obvious (e.g. wrong date format, invalid type value).

## Step 2 — Check for conflicts

Before creating the branch:

1. Read `content/posts/` or `content/labs/` and confirm no file already uses this slug.
   If a file exists, tell the user and stop — do not overwrite.
2. Run `git branch --list post/<slug>` or `git branch --list lab/<slug>` (both local and
   remote via `git ls-remote --heads origin`). If the branch already exists, tell the
   user and stop.

## Step 3 — Create the branch from main

```bash
git fetch origin main
git checkout -b post/<slug> origin/main    # for posts
git checkout -b lab/<slug> origin/main     # for labs
```

Do not branch from the currently checked-out branch — always branch from `origin/main`.

## Step 4 — Write the file

| Type | Destination               |
|------|---------------------------|
| Post | `content/posts/<slug>.md` |
| Lab  | `content/labs/<slug>.md`  |

Write the content exactly as provided. Do not alter the frontmatter or body.

## Step 5 — Commit and push

```bash
git add content/posts/<slug>.md        # or content/labs/<slug>.md
git commit -m "feat: add post — <title>"   # or "feat: add lab — <title>"
git push -u origin post/<slug>             # or lab/<slug>
```

Use the `title` value from frontmatter in the commit message.

Do NOT:

- Stage anything other than the single content file
- Push to main
- Create a pull request
- Open a browser

## Step 6 — Report back

Tell the user:

- Branch name (e.g. `post/hello-world`)
- File written (e.g. `content/posts/hello-world.md`)
- The URL it will appear at once merged (e.g. `/writings/hello-world/` or `/labs/hello-world/`)
- How to create the PR when ready: `gh pr create` or via GitHub web

Keep the report short — one line per item.

## Publishing rules reference

These are the constraints enforced by `core/posts.py` and `core/labs.py` at render time.
A file that violates them will be silently skipped — it will not appear on the site.

- **Posts directory:** `content/posts/` — served at `/writings/<slug>/`
- **Labs directory:** `content/labs/` — served at `/labs/<slug>/`
- **Allowed post types:** `blog`, `article` — `draft`, `note`, `lab`, or anything else is skipped
- **Lab type:** must be exactly `lab`
- **Author:** required on all posts and labs; must be `Syafiq Kay`
- **Lab project:** must match a slug in `content/labs/projects.yaml` — unknown slugs are excluded from `/labs/` grouping
- **Date:** parsed as `date` object; strings and YAML dates both accepted; invalid dates silently skip the file
- **Slug:** used as-is in the URL; Django's slug URL converter requires `[a-zA-Z0-9_-]`
- **Filename:** does not matter — slug in frontmatter is the canonical URL
- **Server cache:** posts and labs are cached in memory after first load; Render re-deploys on push which resets the cache
