# Git Flow and Versioning Guide

## Overview
This project uses Git Flow workflow with automated versioning via Commitizen and follows semantic versioning with "v" prefix.

## Git Flow Workflow

### 1. Feature Development
```bash
# Start a new feature
git flow feature start <feature-name>

# Work on your feature...
# Make commits using conventional commit format

# Finish the feature (merges to develop)
git flow feature finish <feature-name>
```

### 2. Release Process

#### Option A: Using Commitizen (Recommended)
```bash
# On develop branch, after features are merged
uv run git cz bump

# This will:
# - Analyze conventional commits
# - Bump version automatically
# - Update CHANGELOG.md
# - Create a commit and tag

# Then merge to main (since versioning is done)
git checkout main
git merge develop
git push origin main
git push origin develop
git push --tags
```

#### Option B: Traditional Git Flow Release
```bash
# Start a release
git flow release start <version>

# Prepare release (update docs, fix bugs)
# ...

# Finish release (merges to main and develop, creates tag)
git flow release finish <version>
git push origin main
git push origin develop
git push --tags
```

### 3. Hotfixes
```bash
# Start hotfix from main
git flow hotfix start <version>

# Fix the issue...

# Finish hotfix (merges to main and develop)
git flow hotfix finish <version>
git push origin main
git push origin develop
git push --tags
```

## Conventional Commits

Use conventional commit format for automatic version detection:

- `feat:` - New feature (minor version bump)
- `fix:` - Bug fix (patch version bump)
- `feat!:` or `fix!:` - Breaking change (major version bump)
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Build/tool changes

### Examples:
```bash
git commit -m "feat(auth): add user login functionality"
git commit -m "fix(ui): resolve button alignment issue"
git commit -m "feat!: change API response format"
```

## Versioning Configuration

### Commitizen Settings (pyproject.toml)
```toml
[tool.commitizen]
name = "cz_conventional_commits"
tag_format = "v$version"              # Creates tags like v1.2.3
version_scheme = "pep440"
version_provider = "uv"
update_changelog_on_bump = true
major_version_zero = true
```

### Tag Format
- **Format**: `v{major}.{minor}.{patch}` (e.g., v1.2.3)
- **Semantic Versioning**: 
  - Major: Breaking changes
  - Minor: New features (backward compatible)
  - Patch: Bug fixes

## Commands Reference

### Commitizen Commands
```bash
# Check what the next version would be
uv run git cz bump --dry-run

# Bump version automatically
uv run git cz bump

# Create changelog
uv run git cz changelog

# Check commit format
uv run git cz check --rev-range HEAD~1..HEAD
```

### Git Flow Commands
```bash
# Initialize git flow
git flow init

# Feature workflow
git flow feature start <name>
git flow feature finish <name>

# Release workflow
git flow release start <version>
git flow release finish <version>

# Hotfix workflow
git flow hotfix start <version>
git flow hotfix finish <version>
```

### Tag Management
```bash
# List all tags
git tag --list

# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push --delete origin v1.0.0

# Push all tags
git push --tags
```

## Branch Strategy

- **main**: Production-ready code, tagged releases
- **develop**: Integration branch for features
- **feature/**: Individual feature development
- **release/**: Release preparation (optional with commitizen)
- **hotfix/**: Critical fixes for production

## Deployment

1. Code is deployed from the `main` branch
2. Tags represent deployable versions
3. Use the latest tag for production deployment
4. Environment-specific configurations should be handled via environment variables

## Best Practices

1. **Always use conventional commits** for automatic versioning
2. **Test thoroughly** before merging to develop
3. **Keep feature branches small** and focused
4. **Update documentation** with new features
5. **Review CHANGELOG.md** before releases
6. **Use descriptive commit messages** beyond the conventional format
7. **Squash commits** if needed to maintain clean history

## Troubleshooting

### Tag Already Exists Error
If `git cz bump` creates a tag and then `git flow release start` fails:
```bash
# Option 1: Use direct merge (recommended)
git checkout main
git merge develop
git push origin main develop --tags

# Option 2: Use next patch version
git flow release start <next-patch-version>
```

### Version Conflicts
If versions get out of sync:
```bash
# Check current version
uv run git cz version

# Manually set version in pyproject.toml
# Then run: uv run git cz bump --increment MANUAL
```

### Cleaning Up Tags
```bash
# List all tags
git tag -l

# Delete old tags locally
git tag -d old-tag-name

# Delete old tags from remote
git push --delete origin old-tag-name

# Push new tags
git push --tags
```
