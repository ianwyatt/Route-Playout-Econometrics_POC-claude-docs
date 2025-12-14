#!/bin/bash
# ABOUTME: Install git hooks for Route Playout Econometrics POC
# ABOUTME: Run from the claude-docs repo to install hooks in the code repo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE_REPO="$(dirname "$SCRIPT_DIR")/../Route-Playout-Econometrics_POC"

if [ ! -d "$CODE_REPO/.git" ]; then
    echo "Error: Code repo not found at $CODE_REPO"
    echo "Expected sibling directory: Route-Playout-Econometrics_POC"
    exit 1
fi

echo "Installing hooks to $CODE_REPO/.git/hooks/"

cp "$SCRIPT_DIR/pre-commit" "$CODE_REPO/.git/hooks/pre-commit"
cp "$SCRIPT_DIR/pre-push" "$CODE_REPO/.git/hooks/pre-push"

chmod +x "$CODE_REPO/.git/hooks/pre-commit"
chmod +x "$CODE_REPO/.git/hooks/pre-push"

echo "Done. Installed:"
ls -la "$CODE_REPO/.git/hooks/pre-commit" "$CODE_REPO/.git/hooks/pre-push"
