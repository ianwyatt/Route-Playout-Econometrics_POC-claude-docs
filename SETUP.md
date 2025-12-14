# New Machine Setup

Complete setup for Route Playout Econometrics POC development environment.

## Quick Start

```bash
# 1. Clone both repos as siblings
cd ~/PycharmProjects
git clone https://github.com/ianwyatt/Route-Playout-Econometrics_POC.git
git clone https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC-claude-docs.git

# 2. Add Gitea mirror remote to code repo
cd Route-Playout-Econometrics_POC
git remote add zimacube https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC.git

# 3. Create symlinks
ln -s ../Route-Playout-Econometrics_POC-claude-docs .claude
ln -s ../Route-Playout-Econometrics_POC-claude-docs Claude

# 4. Install git hooks
../Route-Playout-Econometrics_POC-claude-docs/hooks/install.sh

# 5. Install Python dependencies
uv sync
cp .env.example .env
# Edit .env with database credentials
```

## Verify Setup

```bash
ls -la .claude Claude    # Should show symlinks -> ../Route-Playout-Econometrics_POC-claude-docs
git status               # .claude and Claude should NOT appear (gitignored)
git remote -v            # Should show origin (GitHub) and zimacube (Gitea)
```

## Daily Workflow

**Code changes** (GitHub + Gitea mirror):
```bash
git add . && git commit -m "message"
git push origin main && git push zimacube main
```

**Claude docs** (Gitea only):
```bash
cd ../Route-Playout-Econometrics_POC-claude-docs
git add . && git commit -m "message" && git push
```

## Troubleshooting

**Symlinks not working?**
```bash
# Remove and recreate
rm .claude Claude
ln -s ../Route-Playout-Econometrics_POC-claude-docs .claude
ln -s ../Route-Playout-Econometrics_POC-claude-docs Claude
```

**Git hooks not running?**
```bash
../Route-Playout-Econometrics_POC-claude-docs/hooks/install.sh
ls -la .git/hooks/pre-*   # Should show pre-commit and pre-push
```

**.gitignore missing Claude dirs?**
```bash
# Should already be in .gitignore, but if not:
echo ".claude/" >> .gitignore
echo "Claude/" >> .gitignore
```
