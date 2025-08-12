# Readme

```sh
alias urm="uv run manage.py"
```

12 August 2025:

```bash
@skay93m ➜ /workspaces/sk-com (develop) $ git flow release start v1.0.0
Switched to a new branch 'release/v1.0.0'

Summary of actions:
- A new branch 'release/v1.0.0' was created, based on 'develop'
- You are now on branch 'release/v1.0.0'

Follow-up actions:
- Bump the version number now!
- Start committing last-minute fixes in preparing your release
- When done, run:

     git flow release finish 'v1.0.0'
```

DOD:
    - Dockerfile config - partially done - need testing
    - secrets variables - 
    - setup https
    - database
    - static files

## First deployment

@skay93m ➜ /workspaces/sk-com (main) $ uv run git flow hotfix start fix-render-deployment
Switched to a new branch 'hotfix/fix-render-deployment'

Summary of actions:
- A new branch 'hotfix/fix-render-deployment' was created, based on 'main'
- You are now on branch 'hotfix/fix-render-deployment'

Follow-up actions:
- Start committing your hot fixes
- Bump the version number now!
- When done, run:

     `git flow hotfix finish 'fix-render-deployment'`

## Hotfix: Bad Request (CSRF)

@skay93m ➜ /workspaces/sk-com (main) $ uv run git flow hotfix start bad-request
- Fixed CSRF verification issues
- Configured production and development environments
- Added PostgreSQL support for both environments
- When done, run: `git flow hotfix finish 'bad-request'`

## Issue List

### Static Files Issues
```
#12 2.838 ?: (staticfiles.W004) The directory '/app/home/static' in the STATICFILES_DIRS setting does not exist.
#12 2.838 ?: (staticfiles.W004) The directory '/app/sk/static' in the STATICFILES_DIRS setting does not exist.
```

### Resolved Issues
1. ✅ CSRF configuration - Fixed in bad-request hotfix
