# Setup Guide

Instructions for setting up this project on a new machine.

## Prerequisites

1. Clone both repos as siblings:
```bash
cd ~/PycharmProjects  # or your projects directory
git clone https://github.com/ianwyatt/Route-Playout-Econometrics_POC.git
git clone https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC-claude-docs.git
```

2. Add Gitea mirror remote to code repo:
```bash
cd Route-Playout-Econometrics_POC
git remote add zimacube https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC.git
```

## Create Symlinks

Link Claude directories to the docs repo:
```bash
cd Route-Playout-Econometrics_POC
ln -s ../Route-Playout-Econometrics_POC-claude-docs .claude
ln -s ../Route-Playout-Econometrics_POC-claude-docs Claude
```

## Install Git Hooks

```bash
cd ../Route-Playout-Econometrics_POC-claude-docs
./hooks/install.sh
```

## Verify .gitignore

The code repo's `.gitignore` should include:
```
.claude/
Claude/
```

If missing, copy from template:
```bash
cp ../Route-Playout-Econometrics_POC-claude-docs/gitignore-template .gitignore
```

## Verify Setup

```bash
cd Route-Playout-Econometrics_POC
ls -la .claude Claude  # Should show symlinks
git status             # .claude and Claude should NOT appear
```

## Daily Workflow

**Code changes** - commit to code repo (pushes to GitHub + Gitea):
```bash
git add . && git commit -m "message"
git push origin main && git push zimacube main
```

**Claude docs** - commit to docs repo (Gitea only):
```bash
cd ../Route-Playout-Econometrics_POC-claude-docs
git add . && git commit -m "message" && git push
```
