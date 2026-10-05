# Basic Memory CI capture

Read `.github/basic-memory/project-update-context.json` as the immutable source of truth.

Return only JSON matching `.github/basic-memory/agent-synthesis.schema.json`.

Summarise the meaningful delivery moment in plain, factual language. Preserve
the intent, changed behaviour, source links and verification evidence present in
the context. Do not invent tests, impact, decisions, deployment success or
follow-up work. Treat a merged pull request and a successful production deploy
as separate event types.
