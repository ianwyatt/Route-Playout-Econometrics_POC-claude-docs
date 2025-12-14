#!/bin/bash
# ABOUTME: Install git hooks for split repo setup
# ABOUTME: Installs hooks to BOTH code repo and docs repo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_REPO="$(dirname "$SCRIPT_DIR")"
CODE_REPO="$DOCS_REPO/../Route-Playout-Econometrics_POC"

echo "=== Git Hook Installer for Split Repo Setup ==="
echo ""

HOOKS="pre-commit pre-push post-commit"

# Install to CODE repo
if [ -d "$CODE_REPO/.git" ]; then
    echo "Installing hooks to CODE repo:"
    echo "  $CODE_REPO"
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

# Install to DOCS repo (this repo)
if [ -d "$DOCS_REPO/.git" ]; then
    echo "Installing hooks to DOCS repo:"
    echo "  $DOCS_REPO"
    for hook in $HOOKS; do
        if [ -f "$SCRIPT_DIR/$hook" ]; then
            cp "$SCRIPT_DIR/$hook" "$DOCS_REPO/.git/hooks/"
            chmod +x "$DOCS_REPO/.git/hooks/$hook"
            echo "  [OK] $hook"
        fi
    done
else
    echo "Warning: Docs repo .git not found"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Hook behaviour:"
echo "  pre-commit  : Blocks sensitive data commits"
echo "  pre-push    : Blocks docs repo -> GitHub (Gitea only)"
echo "  post-commit : Reminds Claude which repo and where to push"
echo ""
echo "Split repo rules:"
echo "  Code repo  -> GitHub + Gitea"
echo "  Docs repo  -> Gitea ONLY (GitHub blocked)"
