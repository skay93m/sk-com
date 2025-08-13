# Git Flow Scenarios Manual: When to Use `git cz bump`

## Overview
This manual covers 10 common development scenarios and explains when to use `git cz bump` versus traditional Git Flow commands. The key principle: **`git cz bump` should be used when you're ready to create a release version**, not during active development.

---

## Scenario 1: 🐛 Critical Bug Discovered in Production

**Situation**: Production is broken, users are affected, immediate fix needed.

### Steps:
```bash
# 1. Start hotfix from main (production)
git checkout main
git pull origin main
git flow hotfix start v0.4.1

# 2. Fix the bug with conventional commits
git add .
git commit -m "fix(critical): resolve payment processing error"

# 3. Finish hotfix (merges to main and develop, creates tag)
git flow hotfix finish v0.4.1

# 4. Push everything
git push origin main develop --tags
```

### ❌ **DON'T use `git cz bump`** - Git Flow hotfix already handles versioning and tagging

---

## Scenario 2: 🚀 Developing a New Major Release

**Situation**: Planning v1.0.0 with multiple new features.

### Steps:
```bash
# 1. Develop features normally
git flow feature start user-authentication
# ... work on feature ...
git commit -m "feat(auth): add login system"
git flow feature finish user-authentication

git flow feature start payment-integration
# ... work on feature ...
git commit -m "feat(payment): integrate Stripe payments"
git flow feature finish payment-integration

# 2. When ALL features are complete and ready for release
git checkout develop
uv run git cz bump  # 🟢 USE HERE - analyzes all feat: commits

# 3. Merge to main for release
git checkout main
git merge develop
git push origin main develop --tags
```

### ✅ **USE `git cz bump`** - After all features are complete, to create the final release version

---

## Scenario 3: 🧪 Trying Out Experimental Ideas

**Situation**: Want to experiment with a new UI framework, unsure if it will be kept.

### Steps:
```bash
# 1. Create experimental feature branch
git flow feature start experimental-ui-redesign

# 2. Work and commit (use conventional commits for consistency)
git commit -m "feat(ui): experiment with new component library"
git commit -m "refactor(ui): restructure layout components"

# 3a. If experiment is successful - finish normally
git flow feature finish experimental-ui-redesign
# Continue to scenario 2 or 4 for versioning

# 3b. If experiment fails - abandon the branch
git checkout develop
git branch -D feature/experimental-ui-redesign
```

### ❌ **DON'T use `git cz bump`** - Only during experimentation. Use it later if the experiment becomes a release.

---

## Scenario 4: 📦 Small Feature Release (Minor Version)

**Situation**: Completed a single feature, ready to release immediately.

### Steps:
```bash
# 1. Feature is already finished and merged to develop
git checkout develop

# 2. Use commitizen to create version and tag
uv run git cz bump  # 🟢 USE HERE - creates v0.5.0 from v0.4.0

# 3. Merge to main and deploy
git checkout main
git merge develop
git push origin main develop --tags
```

### ✅ **USE `git cz bump`** - When feature is complete and ready for immediate release

---

## Scenario 5: 🔧 Multiple Small Bug Fixes

**Situation**: Several minor bugs found, fixed together in one release.

### Steps:
```bash
# 1. Create feature branch for bug fixes
git flow feature start bug-fixes-batch

# 2. Fix bugs with proper commit messages
git commit -m "fix(ui): correct button alignment on mobile"
git commit -m "fix(api): handle null response in user profile"
git commit -m "fix(form): validate email format properly"

# 3. Finish feature
git flow feature finish bug-fixes-batch

# 4. Create patch release
git checkout develop
uv run git cz bump  # 🟢 USE HERE - creates v0.4.1 (patch version)

# 5. Deploy
git checkout main
git merge develop
git push origin main develop --tags
```

### ✅ **USE `git cz bump`** - After all fixes are complete and ready for release

---

## Scenario 6: 📚 Documentation and Non-Code Changes

**Situation**: Updated documentation, README, or configuration files only.

### Steps:
```bash
# 1. Create feature branch
git flow feature start update-documentation

# 2. Make changes with appropriate commits
git commit -m "docs: update installation instructions"
git commit -m "docs: add API usage examples"
git commit -m "chore: update dependencies in requirements.txt"

# 3. Finish feature
git flow feature finish update-documentation

# 4. Check if version bump is needed
uv run git cz bump --dry-run

# If no version change suggested (docs/chore don't bump version):
# Just merge to main without versioning
git checkout main
git merge develop
git push origin main develop

# If changes include fixes or features, then use cz bump
```

### ⚠️ **CONDITIONAL** - Only if the changes include `feat:` or `fix:` commits

---

## Scenario 7: 🎯 Preparing for Scheduled Release

**Situation**: Working towards a planned release date with multiple features.

### Steps:
```bash
# 1. Multiple features developed over time
git flow feature start feature-a
# ... finish feature-a

git flow feature start feature-b  
# ... finish feature-b

git flow feature start feature-c
# ... finish feature-c

# 2. Week before release - create release branch
git flow release start v1.2.0

# 3. In release branch - final preparations
git commit -m "chore: update version numbers in documentation"
git commit -m "docs: update CHANGELOG for v1.2.0"
git commit -m "test: add integration tests for new features"

# 4. Finish release
git flow release finish v1.2.0
git push origin main develop --tags
```

### ❌ **DON'T use `git cz bump`** - Traditional Git Flow release handles this better for scheduled releases

---

## Scenario 8: 🔄 Continuous Development (Trunk-based)

**Situation**: Small frequent releases, deploying features as soon as they're ready.

### Steps:
```bash
# Daily/weekly cycle:

# 1. Develop small feature
git flow feature start quick-improvement
git commit -m "feat(ux): add loading spinner to forms"
git flow feature finish quick-improvement

# 2. Immediately release
git checkout develop
uv run git cz bump  # 🟢 USE HERE - frequent small releases

# 3. Deploy
git checkout main  
git merge develop
git push origin main develop --tags

# Repeat cycle...
```

### ✅ **USE `git cz bump`** - Perfect for frequent, small releases

---

## Scenario 9: 🚨 Emergency Rollback Needed

**Situation**: Latest release has issues, need to rollback and fix.

### Steps:
```bash
# 1. Immediate rollback (deploy previous tag)
# Deploy v0.4.0 instead of v0.5.0 in production

# 2. Create hotfix from the problematic commit
git checkout v0.5.0  # the problematic release
git flow hotfix start v0.5.1

# 3. Fix the issue
git commit -m "fix(critical): resolve data corruption in user profiles"

# 4. Finish hotfix
git flow hotfix finish v0.5.1
git push origin main develop --tags

# 5. Deploy fixed version
```

### ❌ **DON'T use `git cz bump`** - Hotfix workflow handles versioning

---

## Scenario 10: 🎨 Long-running Feature Development

**Situation**: Large feature taking weeks/months, needs intermediate saves.

### Steps:
```bash
# 1. Start long-running feature
git flow feature start major-ui-overhaul

# 2. Work in phases with good commit messages
git commit -m "feat(ui): redesign header component"
git commit -m "feat(ui): implement new navigation system"
git commit -m "refactor(ui): extract common styling utilities"
# ... continue for weeks ...

# 3. Periodically sync with develop (optional)
git checkout develop
git pull origin develop
git checkout feature/major-ui-overhaul
git merge develop  # resolve conflicts if any

# 4. When feature is COMPLETELY done
git flow feature finish major-ui-overhaul

# 5. Ready for release
git checkout develop
uv run git cz bump  # 🟢 USE HERE - feature is complete

# 6. Release
git checkout main
git merge develop
git push origin main develop --tags
```

### ✅ **USE `git cz bump`** - Only when the entire feature is complete and ready for release

---

## 🎯 Decision Matrix: When to Use `git cz bump`

| Scenario | Use `git cz bump`? | Alternative | Timing |
|----------|-------------------|-------------|---------|
| **Production Bug** | ❌ No | `git flow hotfix` | Immediate |
| **Major Release** | ✅ Yes | N/A | After all features complete |
| **Experiments** | ❌ No | N/A | Never (until experiment becomes feature) |
| **Small Feature** | ✅ Yes | N/A | After feature complete |
| **Bug Fixes Batch** | ✅ Yes | N/A | After all fixes complete |
| **Documentation** | ⚠️ Maybe | Direct merge | Only if includes feat/fix |
| **Scheduled Release** | ❌ No | `git flow release` | Traditional release cycle |
| **Continuous Development** | ✅ Yes | N/A | After each small feature |
| **Emergency Rollback** | ❌ No | `git flow hotfix` | Immediate |
| **Long-running Feature** | ✅ Yes | N/A | After feature complete |

## 🔑 Key Principles

### ✅ **USE `git cz bump` when:**
- Feature development is **complete**
- Ready to **create a release version**
- Want **automated version calculation**
- Following **continuous delivery** approach
- All changes are **tested and ready for production**

### ❌ **DON'T use `git cz bump` when:**
- Still **actively developing**
- Need **emergency fixes** (use hotfix)
- Following **traditional release cycles** (use git flow release)
- Changes are **experimental**
- Working on **long-running features** (use when complete)

### ⚠️ **Key Timing Rule:**
**`git cz bump` should be the LAST step before merging to main/production, not during development.**

---

## 🛠️ Quick Reference Commands

```bash
# Check what version bump would happen (without doing it)
uv run git cz bump --dry-run

# Check current version
uv run git cz version

# Manual version bump (if automatic detection fails)
uv run git cz bump --increment PATCH|MINOR|MAJOR

# See what commits would trigger version bump
git log --oneline --grep="^feat\|^fix\|^feat!\|^fix!" <last-tag>..HEAD
```

---

## 📋 Pre-Release Checklist

Before running `git cz bump`, ensure:

- [ ] All intended features are merged to develop
- [ ] All tests are passing
- [ ] Documentation is updated
- [ ] CHANGELOG.md is ready (cz bump will update it)
- [ ] No experimental/incomplete code in develop
- [ ] Ready to deploy to production

**Remember**: `git cz bump` creates a permanent version tag. Make sure you're truly ready for release!
