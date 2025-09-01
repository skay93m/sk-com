# Git Tag Cleanup - Invalid Version Tag Fix

## Issue

The conventional commits tool was showing errors during version bumps:

```bash
Invalid version tag: 'static-files' does not match any configured tag format
Invalid version tag: 'llm-prompt' does not match any configured tag format
```

## Root Cause

Two git tags existed that didn't follow the semantic versioning format expected by commitizen:

- `static-files`
- `llm-prompt`

## Expected Tag Format

According to `pyproject.toml`, the tool expects tags in the format:

```toml
tag_format = "v$version"
```

Examples of valid tags: `v4.3.0`, `v4.2.0`, `v1.0.0`

## Solution

1. **Deleted problematic tags locally:**

   ```bash
   git tag -d static-files llm-prompt
   ```

2. **Deleted problematic tags from remote:**

   ```bash
   git push origin --delete static-files llm-prompt
   ```

## Verification

After cleanup, only semantic version tags remain:

- v0.3.6, v0.4.0, v1.0.0, v1.0.1
- v2.0.0, v3.0.0, v4.0.0
- v4.1.0, v4.2.0, v4.3.0

## Prevention

Future tags should follow semantic versioning format:

- Use `git cz bump` for automatic version tagging
- Avoid manual tags that don't follow `v#.#.#` format
- If manual tags are needed, use descriptive names that don't conflict with version patterns

## Date

September 1, 2025

## Status

✅ Fixed - Conventional commits tool now works without tag format errors
