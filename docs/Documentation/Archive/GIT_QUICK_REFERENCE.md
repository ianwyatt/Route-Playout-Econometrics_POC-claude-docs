# Git Quick Reference Card

**Keep this open in your terminal!**

---

## Daily Commands

### Start Your Day
```bash
git checkout dev          # Switch to dev branch
git pull origin dev       # Get latest
```

### Work & Commit
```bash
git status                # See what changed
git add .                 # Stage all changes
git commit -m "fix: description"
git push origin dev       # Backup to GitHub
```

### Check Where You Are
```bash
git branch                # Which branch? (* = current)
git status                # Detailed status
```

---

## Demo Time

### Before Demo (Use Main)
```bash
git checkout main         # Switch to stable
git pull origin main      # Get latest
streamlit run src/ui/app.py --server.port 8504
```

### Tag Before Important Demo
```bash
git checkout main
git tag -a demo-oct-25 -m "Board meeting version"
git push --tags
```

---

## Merge dev → main

### When Feature Complete
```bash
# 1. Finish on dev
git checkout dev
git push origin dev

# 2. Switch to main
git checkout main
git pull origin main

# 3. Merge
git merge dev

# 4. Test it!
streamlit run src/ui/app.py

# 5. Push
git push origin main

# 6. Back to dev
git checkout dev
```

---

## Rollback to Tag

### If Main Breaks Before Demo
```bash
git tag -l                # List tags
git checkout demo-oct-25  # Go to safe version
streamlit run src/ui/app.py
# Demo successful!
git checkout main         # Back to latest
```

---

## Emergency Commands

### Accidentally on Wrong Branch?
```bash
git branch                # Check where you are
git checkout dev          # Switch to dev
```

### Undo Last Commit (Not Pushed)
```bash
git reset --soft HEAD~1   # Keep changes
# or
git reset --hard HEAD~1   # Discard changes (careful!)
```

### Merge Conflict?
```bash
git status                # See conflicted files
git merge --abort         # Cancel merge, ask for help
```

### Start Fresh (Lose Uncommitted Work)
```bash
git checkout dev
git reset --hard origin/dev
```

---

## Branch Rules

| Branch | Purpose | Rule |
|--------|---------|------|
| `main` | Demos | ❌ No direct development |
| `dev` | Work | ✅ All coding here |

**Golden Rule**: Work on `dev`, demo from `main`

---

## Tag Format

```bash
demo-event-date           # demo-board-oct-25
v1.0-feature-name         # v1.0-reach-complete
stable-before-change      # stable-before-refactor
```

---

## Current State

```
main  ← v1.0-reach-caching-complete (demo-ready)
dev   ← Start datetime bug fix here
```

---

## Need Help?

**Check status**:
```bash
git status
git branch
git log --oneline -5
```

**See full workflow**: `Claude/Documentation/GIT_WORKFLOW.md`

---

**Remember**: When in doubt, `git status` and `git branch`!
