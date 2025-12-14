# Session Handover: Split Repo Setup

**Date:** 14 December 2025
**Focus:** Repository restructuring and documentation audit

---

## Summary

Established a split repo setup to keep Claude working docs off GitHub, reorganised folder structure, and completed documentation audit.

---

## What Was Done

### 1. Documentation Audit
- Updated `docs/01-architecture.md` with ASCII diagram and current performance numbers
- Updated `docs/02-ui-guide.md` with startstream notes
- Updated `docs/04-cache-integration.md` - Phase 7 → December 2025 performance
- Trimmed `docs/06-campaign-indicators.md` from 499 to 101 lines (removed changelog)
- Updated `README.md` - removed emojis, added overlap demo, cleaned up
- Updated `CLAUDE.md` - fixed doc paths, cache-first wording, added performance table

### 2. Split Repo Setup
Created separate Gitea-only repo for Claude docs:

| Repo | Purpose | Remote |
|------|---------|--------|
| `Route-Playout-Econometrics_POC` | Application code | GitHub + Gitea |
| `Route-Playout-Econometrics_POC-claude-docs` | Claude docs | Gitea only |

**Implementation:**
- Created new Gitea repo for Claude docs
- Moved all content from `Claude/` and `.claude/` to new repo
- Created symlinks in code repo pointing to sibling docs repo
- Added `.claude/` and `Claude/` to code repo's `.gitignore`
- Created stub `CLAUDE.md` in code repo for public viewing

### 3. Folder Reorganisation
New structure in claude-docs repo:
```
├── CLAUDE.md        # Main instructions (moved from code repo)
├── SETUP.md         # New machine setup guide
├── config/          # hooks.json, settings, gitignore template
├── hooks/           # Git hooks + installer
├── skills/          # Claude Code skills
├── handover/        # Session handovers (renamed from Handover)
├── todo/            # Task tracking (renamed from ToDo)
├── docs/            # Working documentation (renamed from Documentation)
├── reference/       # Merged: Solutions, Streamlit Reference, research files
└── archive/         # Old content (renamed from Archive)
```

### 4. Claude Code Skills
Created 4 skills wrapping existing utility scripts:
- `check-cache` - Cache status and coverage
- `query-database` - Query MS-01 for playout data
- `test-route-api` - Route API connectivity tests
- `test-space-api` - SPACE API entity lookups

### 5. Git Hooks
Copied hooks to docs repo with installer:
- `hooks/pre-commit` - Blocks sensitive data
- `hooks/pre-push` - Final checks, symlink-aware
- `hooks/install.sh` - Installs hooks to code repo

### 6. Repo Descriptions Updated
- **GitHub:** "OOH campaign analytics linking playout data to Route audiences for econometric modelling"
- **Gitea (code):** Update manually to "GitHub mirror - OOH playout/Route audience analytics"
- **Gitea (docs):** Update manually to "Claude Code config and dev docs (private)"

---

## New Machine Setup

See `SETUP.md` for complete instructions. Quick version:

```bash
cd ~/PycharmProjects
git clone https://github.com/ianwyatt/Route-Playout-Econometrics_POC.git
git clone https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC-claude-docs.git

cd Route-Playout-Econometrics_POC
git remote add zimacube https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC.git
ln -s ../Route-Playout-Econometrics_POC-claude-docs .claude
ln -s ../Route-Playout-Econometrics_POC-claude-docs Claude
../Route-Playout-Econometrics_POC-claude-docs/hooks/install.sh
uv sync
```

---

## Daily Workflow

**Code changes:**
```bash
git add . && git commit -m "message"
git push origin main && git push zimacube main
```

**Claude docs:**
```bash
cd .claude  # or cd ../Route-Playout-Econometrics_POC-claude-docs
git add . && git commit -m "message" && git push
```

---

## Files Changed

### Code Repo (GitHub + Gitea)
- `.gitignore` - Added `.claude/` and `Claude/`
- `CLAUDE.md` - Replaced with minimal stub
- `README.md` - Added "Check Gitea" hint, removed emojis
- `docs/01-architecture.md` - ASCII diagram, performance, MVs list
- `docs/02-ui-guide.md` - startstream note, date
- `docs/04-cache-integration.md` - December 2025 performance
- `docs/06-campaign-indicators.md` - Trimmed to 101 lines

### Claude Docs Repo (Gitea only)
- New repo created with all Claude working docs
- Folder structure reorganised (lowercase, merged dirs)
- `CLAUDE.md` moved here with updated structure
- `SETUP.md` improved with quick start guide
- Skills, hooks, config added

---

## Outstanding Items

- Update Gitea repo descriptions manually (API needs auth token)
- Consider archiving old handover files after confirming new structure works

---

## Key Commits

**Code repo:**
- `7347131` - docs: simplify CLAUDE.md, add Gitea hint to README

**Claude docs repo:**
- `710f471` - Improve SETUP.md with complete quick start guide
- `23e963a` - Reorganise folder structure, add CLAUDE.md
