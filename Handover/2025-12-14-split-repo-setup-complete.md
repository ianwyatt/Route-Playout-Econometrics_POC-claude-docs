# Session Handover: Split Repo Setup Complete

**Date**: 14 December 2025
**Session Focus**: Documentation audit, split repo setup, CLAUDE.md migration, folder reorganisation

---

## Summary of Work Completed

### 1. Documentation Audit
- Added ASCII architecture diagram to `docs/01-architecture.md` (tree-style format)
- Updated performance numbers to December 2025
- Documented `startstream` shell function
- Trimmed `docs/06-campaign-indicators.md` from 499 → 101 lines (removed changelog content)
- Restored overlap demo content to README (user caught accidental removal)
- Removed emojis from README UI table (user preference)

### 2. Split Repo Setup (COMPLETE)
Created separate Gitea-only repo for Claude docs:

**Repos:**
| Repo | Location | Remote |
|------|----------|--------|
| Code | `Route-Playout-Econometrics_POC` | GitHub + Gitea mirror |
| Docs | `Route-Playout-Econometrics_POC-claude-docs` | Gitea ONLY |

**Symlinks in code repo:**
```
.claude -> ../Route-Playout-Econometrics_POC-claude-docs
Claude -> ../Route-Playout-Econometrics_POC-claude-docs
```

### 3. CLAUDE.md Migration
- Moved main CLAUDE.md from code repo to docs repo
- Created stub CLAUDE.md in code repo (just points to .claude/)
- Updated path references in CLAUDE.md for new location

### 4. Folder Reorganisation
Renamed all folders to lowercase, consolidated loose files:

**Final docs repo structure:**
```
Route-Playout-Econometrics_POC-claude-docs/
├── CLAUDE.md                 # Main project instructions
├── SETUP.md                  # New machine setup guide
├── config/
│   ├── hooks.json
│   ├── settings.local.json
│   └── gitignore-template
├── hooks/
│   ├── install.sh
│   ├── pre-commit
│   └── pre-push
├── skills/
│   ├── check-cache/SKILL.md
│   ├── query-database/SKILL.md
│   ├── test-route-api/SKILL.md
│   └── test-space-api/SKILL.md
├── handover/                 # 71+ session handovers
├── todo/                     # Task tracking files
├── docs/                     # Working documentation
│   ├── Deployment_Planning/
│   ├── MS01_Migration_Plan/
│   └── Project_Reorganization/
├── archive/                  # Old/superseded content
└── reference/
    ├── SPLIT_REPO_SETUP_GUIDE.md    # NEW - guide for other projects
    ├── research_*.md files
    ├── SECURITY_ALERT.md
    └── Streamlit reference files
```

### 5. Hooks System
- Fixed pre-push hook integer expression error (symlink-aware check)
- Created `hooks/install.sh` for easy setup on new machines
- Hooks prevent credential commits and enforce naming conventions
- **Split repo enforcement** - pre-push hook blocks docs repo pushes to GitHub
- **Post-commit reminder** - shows Claude which repo it's in and where to push

**Three hooks installed to both repos:**
| Hook | Purpose |
|------|---------|
| `pre-commit` | Blocks sensitive data commits |
| `pre-push` | Blocks docs repo → GitHub (Gitea only) |
| `post-commit` | Reminds Claude about split repo rules after every commit |

---

## Important Files and Locations

### Code Repo (`Route-Playout-Econometrics_POC`)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Stub pointing to .claude/ |
| `.gitignore` | Excludes .claude/ and Claude/ |
| `docs/01-architecture.md` | Main architecture doc with ASCII diagram |
| `docs/06-campaign-indicators.md` | Campaign status indicators reference |
| `README.md` | Project overview (no emojis, has overlap demo) |
| `src/ui/app.py` | Main Streamlit application |

### Docs Repo (`Route-Playout-Econometrics_POC-claude-docs`)

| File | Purpose |
|------|---------|
| `CLAUDE.md` | **MAIN** project instructions for Claude |
| `SETUP.md` | New machine setup guide |
| `config/hooks.json` | Hook configuration |
| `config/gitignore-template` | Template for new projects |
| `hooks/install.sh` | Hook installer script |
| `reference/SPLIT_REPO_SETUP_GUIDE.md` | Guide for setting up split repos in other projects |

### Key Paths for Claude

| What | Path |
|------|------|
| Session handovers | `handover/` |
| Task tracking | `todo/` |
| Working docs | `docs/` |
| Archive | `archive/` |
| Skills | `skills/` |
| Reference material | `reference/` |

---

## Git Commits This Session

### Code Repo
| Hash | Description |
|------|-------------|
| `6a066a7` | docs: main documentation updates (architecture, README) |
| `4d65832` | docs: trim campaign indicators (499→101 lines) |
| `3862c42` | chore: add gitignore for Claude symlinks |
| `4058769` | docs: add split repo structure to CLAUDE.md |
| `70adac8` | docs: add SETUP.md reference |

### Docs Repo
| Hash | Description |
|------|-------------|
| `9f2e713` | feat: initial docs repo structure |
| `72be82a` | feat: add hooks and installer |
| `b28bfc0` | docs: add SETUP.md and gitignore template |
| *pending* | Folder reorganisation + CLAUDE.md move |

---

## Pending Actions

### Must Do (Before Pushing)
1. **Commit docs repo reorganisation** - folder renames and CLAUDE.md move are uncommitted
2. **Verify stub CLAUDE.md in code repo** - check it exists and is committed

### Commands to Complete
```bash
# Commit docs repo changes
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC-claude-docs
git add .
git status  # Review changes
git commit -m "refactor: reorganise folders, migrate CLAUDE.md from code repo"
git push

# Verify code repo stub (if needed)
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
cat CLAUDE.md
git status
```

---

## Key Learnings / Notes for Next Session

### User Preferences
- **Hates emojis** - don't add to docs or code
- **README is "first port of call"** - keep clean and focused
- **Overlap demo is important** - campaigns 16879/16882 demonstrate key feature
- **CLAUDE.md in public repo "looks odd"** - hence the split repo setup
- **British English spelling** - colour, analyse, organisation, etc.
- **Address as "Doctor Biz"**

### Technical Notes
- **Symlinks**: `.claude` and `Claude` both point to sibling docs repo
- **Pre-push hook**: Must check `[ ! -L "Claude" ]` to avoid integer expression error on symlinks
- **Unicode box art**: Don't attempt - use tree-style ASCII instead (3 failed attempts this session)
- **Shell cwd**: Resets unpredictably - always explicit `cd` before git commands

### Demo Campaigns
- `16699`, `16879`, `18409` - "board demo" campaigns
- `16879` & `16882` - overlap demonstration (same frame, different campaigns)

### Startstream Command
User has shell function in `~/.zshrc`:
```bash
startstream           # MS01 database, normal mode
startstream demo      # MS01 database, demo mode (anonymised brands)
startstream local     # Local database
startstream local demo
```

---

## Remotes Reference

### Code Repo
```
origin   → https://github.com/ianwyatt/Route-Playout-Econometrics_POC.git
zimacube → https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC.git
```

### Docs Repo
```
origin → https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC-claude-docs.git
```

---

## For Other Projects

Created comprehensive guide at:
`reference/SPLIT_REPO_SETUP_GUIDE.md`

This can be used as a template for setting up split repos in other Claude Code projects.

---

*Handover prepared: 14 December 2025*
