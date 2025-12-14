# Split Repo Setup Guide for Claude Code Projects

**Purpose**: Keep Claude working docs (handovers, todos, CLAUDE.md) in a private Gitea repo while application code goes to public GitHub.

---

## Why This Setup?

- **Privacy**: CLAUDE.md and session handovers contain internal context you may not want public
- **Clean public repo**: GitHub repo looks professional without `.claude/` clutter
- **Separate histories**: Code and docs evolve independently
- **Works with Claude Code**: Symlinks make all paths work as expected

---

## Architecture

```
~/PycharmProjects/
├── your-project/                    # Code repo (GitHub + optional Gitea mirror)
│   ├── .claude -> ../...-claude-docs    # Symlink
│   ├── Claude -> ../...-claude-docs     # Symlink
│   ├── src/
│   ├── .gitignore                   # Excludes .claude/ and Claude/
│   └── CLAUDE.md                    # Optional stub pointing to .claude/
│
└── your-project-claude-docs/        # Docs repo (Gitea ONLY - never GitHub)
    ├── CLAUDE.md                    # Main project instructions
    ├── SETUP.md                     # New machine setup guide
    ├── config/                      # hooks.json, settings
    ├── hooks/                       # Git hooks + installer
    ├── skills/                      # Claude Code skill definitions
    ├── handover/                    # Session handovers
    ├── todo/                        # Task tracking
    ├── docs/                        # Working documentation
    ├── archive/                     # Old/superseded content
    └── reference/                   # Research, external references
```

---

## Step-by-Step Setup

### 1. Create the Docs Repo on Gitea

On your Gitea instance, create: `{project-name}-claude-docs`

Example: `my-awesome-app-claude-docs`

### 2. Clone Both Repos as Siblings

```bash
cd ~/PycharmProjects  # or your projects directory

# Code repo (if not already cloned)
git clone https://github.com/youruser/your-project.git

# Docs repo (Gitea only)
git clone https://your-gitea-instance/youruser/your-project-claude-docs.git
```

**Critical**: They must be siblings (same parent directory).

### 3. Initialise Docs Repo Structure

```bash
cd your-project-claude-docs

# Create directory structure
mkdir -p config hooks skills handover todo docs archive reference

# Create essential files
touch CLAUDE.md SETUP.md config/hooks.json

# Initial commit
git add .
git commit -m "feat: initial docs repo structure"
git push
```

### 4. Create Symlinks in Code Repo

```bash
cd ../your-project

# Create symlinks to sibling docs repo
ln -s ../your-project-claude-docs .claude
ln -s ../your-project-claude-docs Claude

# Verify
ls -la .claude Claude
# Should show: .claude -> ../your-project-claude-docs
```

### 5. Update Code Repo .gitignore

Add these lines to `.gitignore`:

```gitignore
# Claude docs (symlinked to separate Gitea-only repo)
.claude/
Claude/
```

Commit:
```bash
git add .gitignore
git commit -m "chore: exclude Claude docs symlinks from git"
git push
```

### 6. (Optional) Create Stub CLAUDE.md in Code Repo

If you want Claude to find basic instructions even without symlinks:

```bash
cat > CLAUDE.md << 'EOF'
# Project Name

This project uses [Claude Code](https://claude.ai/claude-code) for AI-assisted development.

Project-specific instructions are maintained separately by the development team.
EOF

git add CLAUDE.md
git commit -m "docs: add stub CLAUDE.md"
git push
```

### 7. Populate Main CLAUDE.md in Docs Repo

```bash
cd ../your-project-claude-docs
```

Edit `CLAUDE.md` with your project instructions. Key sections to include:

```markdown
# Project Name - Claude Instructions

## Repository Structure

This project uses a **split repo setup**:

| Repo | Content | Remote |
|------|---------|--------|
| `your-project` | Application code | GitHub |
| `your-project-claude-docs` | Claude docs | Gitea only |

**Symlinks in code repo:**
- `.claude/` → this repo
- `Claude/` → this repo

**Committing Claude docs:**
```bash
cd your-project-claude-docs
git add . && git commit -m "message" && git push
```

## [Rest of your project-specific instructions...]
```

### 8. Create SETUP.md

```bash
cat > SETUP.md << 'EOF'
# New Machine Setup

## Prerequisites
- Git access to GitHub and Gitea
- Projects directory (e.g., ~/PycharmProjects)

## Quick Setup

```bash
# 1. Clone both repos as siblings
cd ~/PycharmProjects
git clone https://github.com/youruser/your-project.git
git clone https://your-gitea-instance/youruser/your-project-claude-docs.git

# 2. Create symlinks in code repo
cd your-project
ln -s ../your-project-claude-docs .claude
ln -s ../your-project-claude-docs Claude

# 3. (Optional) Add Gitea mirror remote
git remote add gitea https://your-gitea-instance/youruser/your-project.git

# 4. Install hooks
cd ../your-project-claude-docs
./hooks/install.sh
```

## Verify Setup

```bash
cd your-project
ls -la .claude  # Should show symlink
cat .claude/CLAUDE.md  # Should show project instructions
```
EOF
```

### 9. Set Up Git Hooks (Recommended)

The hooks enforce the split repo rules - **blocking docs repo pushes to GitHub**.

#### Create `hooks/pre-push`

This is the key hook that enforces "docs repo = Gitea only":

```bash
cat > hooks/pre-push << 'HOOKEOF'
#!/bin/bash
# ABOUTME: Pre-push hook for split repo setup
# ABOUTME: Blocks docs repo pushes to GitHub, allows code repo to push anywhere

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Running pre-push checks...${NC}"

# Get remote info (passed by git)
REMOTE_NAME="$1"
REMOTE_URL="$2"

# Detect repo type from directory name
REPO_DIR="$(basename "$(git rev-parse --show-toplevel)")"

# If this is a -claude-docs repo, block GitHub pushes
if [[ "$REPO_DIR" == *-claude-docs ]]; then
    if [[ "$REMOTE_URL" == *"github.com"* ]]; then
        echo -e "${RED}============================================${NC}"
        echo -e "${RED}ERROR: Cannot push Claude docs to GitHub!${NC}"
        echo -e "${RED}============================================${NC}"
        echo ""
        echo "Remote: $REMOTE_NAME"
        echo "URL:    $REMOTE_URL"
        echo ""
        echo "The Claude docs repo should only be pushed to Gitea."
        echo ""
        echo -e "${YELLOW}Use: git push origin main${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Docs repo -> Gitea${NC}"
else
    # Code repo - allow both GitHub and Gitea
    if [[ "$REMOTE_URL" == *"github.com"* ]]; then
        echo -e "${GREEN}[OK] Code repo -> GitHub${NC}"
    elif [[ "$REMOTE_URL" == *"gitea"* ]]; then
        echo -e "${GREEN}[OK] Code repo -> Gitea${NC}"
    fi
fi

echo -e "${GREEN}Pre-push checks complete${NC}"
HOOKEOF

chmod +x hooks/pre-push
```

#### Create `hooks/install.sh`

```bash
cat > hooks/install.sh << 'INSTALLEOF'
#!/bin/bash
# ABOUTME: Install git hooks to both code and docs repos
# ABOUTME: Run from the docs repo directory

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_REPO="$(dirname "$SCRIPT_DIR")"
DOCS_REPO_NAME="$(basename "$DOCS_REPO")"
CODE_REPO_NAME="${DOCS_REPO_NAME%-claude-docs}"
CODE_REPO="$(dirname "$DOCS_REPO")/$CODE_REPO_NAME"

echo "=== Git Hook Installer ==="
echo ""

# Install to CODE repo
if [ -d "$CODE_REPO/.git" ]; then
    echo "Installing to CODE repo: $CODE_REPO"
    for hook in pre-commit pre-push; do
        if [ -f "$SCRIPT_DIR/$hook" ]; then
            cp "$SCRIPT_DIR/$hook" "$CODE_REPO/.git/hooks/"
            chmod +x "$CODE_REPO/.git/hooks/$hook"
            echo "  [OK] $hook"
        fi
    done
else
    echo "Warning: Code repo not found at $CODE_REPO"
fi

echo ""

# Install to DOCS repo (this repo)
if [ -d "$DOCS_REPO/.git" ]; then
    echo "Installing to DOCS repo: $DOCS_REPO"
    for hook in pre-commit pre-push; do
        if [ -f "$SCRIPT_DIR/$hook" ]; then
            cp "$SCRIPT_DIR/$hook" "$DOCS_REPO/.git/hooks/"
            chmod +x "$DOCS_REPO/.git/hooks/$hook"
            echo "  [OK] $hook"
        fi
    done
fi

echo ""
echo "=== Done ==="
echo "Code repo: GitHub + Gitea allowed"
echo "Docs repo: Gitea ONLY (GitHub blocked)"
INSTALLEOF

chmod +x hooks/install.sh
```

#### Run the Installer

```bash
cd your-project-claude-docs
./hooks/install.sh
```

#### Test the Hook

```bash
# This should FAIL (docs repo -> GitHub blocked)
cd your-project-claude-docs
.git/hooks/pre-push github https://github.com/user/repo.git

# This should SUCCEED (docs repo -> Gitea allowed)
.git/hooks/pre-push origin https://your-gitea/user/repo-claude-docs.git
```

#### Create `hooks/post-commit` (Reminder Hook)

This hook reminds Claude which repo it's in after every commit:

```bash
cat > hooks/post-commit << 'HOOKEOF'
#!/bin/bash
# ABOUTME: Post-commit hook that reminds Claude about split repo setup
# ABOUTME: Outputs repo-specific push instructions after every commit

CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

REPO_DIR="$(basename "$(git rev-parse --show-toplevel)")"

echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  SPLIT REPO REMINDER                           ${NC}"
echo -e "${CYAN}================================================${NC}"

if [[ "$REPO_DIR" == *-claude-docs ]]; then
    echo -e "${YELLOW}You just committed to the DOCS repo${NC}"
    echo ""
    echo "  Repo: $REPO_DIR"
    echo "  Push: Gitea ONLY (GitHub blocked by hook)"
    echo ""
    echo -e "${GREEN}To push:${NC}"
    echo "  git push origin main"
    echo ""
    echo "NOTE: This repo contains CLAUDE.md, handovers, and todos."
    echo "      It should NEVER be pushed to GitHub."
else
    echo -e "${YELLOW}You just committed to the CODE repo${NC}"
    echo ""
    echo "  Repo: $REPO_DIR"
    echo "  Push: GitHub (origin) + Gitea (if mirrored)"
    echo ""
    echo -e "${GREEN}To push:${NC}"
    echo "  git push origin main      # GitHub"
    echo "  git push gitea main       # Gitea mirror (if configured)"
    echo ""
    echo "NOTE: Code changes only. Claude docs are in the sibling"
    echo "      *-claude-docs repo (accessed via .claude/ symlink)."
fi

echo -e "${CYAN}================================================${NC}"
echo ""
HOOKEOF

chmod +x hooks/post-commit
```

#### Update `hooks/install.sh` for All Three Hooks

```bash
cat > hooks/install.sh << 'INSTALLEOF'
#!/bin/bash
# ABOUTME: Install git hooks to both code and docs repos
# ABOUTME: Run from the docs repo directory

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_REPO="$(dirname "$SCRIPT_DIR")"
DOCS_REPO_NAME="$(basename "$DOCS_REPO")"
CODE_REPO_NAME="${DOCS_REPO_NAME%-claude-docs}"
CODE_REPO="$(dirname "$DOCS_REPO")/$CODE_REPO_NAME"

echo "=== Git Hook Installer for Split Repo Setup ==="
echo ""

HOOKS="pre-commit pre-push post-commit"

# Install to CODE repo
if [ -d "$CODE_REPO/.git" ]; then
    echo "Installing to CODE repo: $CODE_REPO"
    for hook in $HOOKS; do
        if [ -f "$SCRIPT_DIR/$hook" ]; then
            cp "$SCRIPT_DIR/$hook" "$CODE_REPO/.git/hooks/"
            chmod +x "$CODE_REPO/.git/hooks/$hook"
            echo "  [OK] $hook"
        fi
    done
else
    echo "Warning: Code repo not found at $CODE_REPO"
fi

echo ""

# Install to DOCS repo
if [ -d "$DOCS_REPO/.git" ]; then
    echo "Installing to DOCS repo: $DOCS_REPO"
    for hook in $HOOKS; do
        if [ -f "$SCRIPT_DIR/$hook" ]; then
            cp "$SCRIPT_DIR/$hook" "$DOCS_REPO/.git/hooks/"
            chmod +x "$DOCS_REPO/.git/hooks/$hook"
            echo "  [OK] $hook"
        fi
    done
fi

echo ""
echo "=== Done ==="
echo "Hook behaviour:"
echo "  pre-commit  : Blocks sensitive data commits"
echo "  pre-push    : Blocks docs repo -> GitHub (Gitea only)"
echo "  post-commit : Reminds Claude which repo and where to push"
INSTALLEOF

chmod +x hooks/install.sh
```

### 10. Commit and Push Docs Repo

```bash
cd your-project-claude-docs
git add .
git commit -m "feat: complete split repo setup with CLAUDE.md and hooks"
git push
```

---

## Daily Workflow

### Code Changes
```bash
cd your-project
# ... make changes ...
git add . && git commit -m "feat: whatever" && git push
```

### Documentation Changes
```bash
cd your-project-claude-docs  # or: cd .claude from code repo
# ... update handovers, todos, CLAUDE.md ...
git add . && git commit -m "docs: session handover" && git push
```

### Session Handovers
Save to `handover/YYYY-MM-DD-description.md` in docs repo.

---

## Troubleshooting

### Symlinks Not Working
```bash
# Check symlinks exist and point correctly
ls -la .claude Claude

# If broken, recreate:
rm .claude Claude
ln -s ../your-project-claude-docs .claude
ln -s ../your-project-claude-docs Claude
```

### Claude Not Finding CLAUDE.md
1. Check symlink: `ls -la .claude/CLAUDE.md`
2. Verify file exists: `cat .claude/CLAUDE.md`
3. Check Claude Code is reading from correct path

### Git Status Shows .claude/ Changes
Your `.gitignore` should exclude it:
```bash
grep -E "^\.claude|^Claude" .gitignore
# Should show:
# .claude/
# Claude/
```

---

## Pre-Push Hook Caveat (Symlink-Aware)

If your pre-push hook checks for doc updates, it must handle symlinks:

```bash
# BAD - fails on symlinks
if [ -d "Claude" ]; then
    last_doc_update=$(find Claude -type f -name "*.md" ...)

# GOOD - skip if symlink
if [ -d "Claude" ] && [ ! -L "Claude" ]; then
    # Only check if Claude is a real directory, not a symlink
```

---

## Folder Naming Conventions

Use **lowercase** for all directories in docs repo:
- `handover/` not `Handover/`
- `todo/` not `ToDo/`
- `docs/` not `Documentation/`
- `archive/` not `Archive/`

This avoids case-sensitivity issues across different filesystems.

---

## Reference Implementation

See `Route-Playout-Econometrics_POC` and `Route-Playout-Econometrics_POC-claude-docs` for a working example of this setup.

---

*Last Updated: December 2025*
