# Route Playout Econometrics POC - Project Specification

```
╔════════════════════════════════════════════════════════════════════════╗
║                    SPLIT REPOSITORY SETUP                              ║
║                                                                        ║
║  CODE REPO: Route-Playout-Econometrics_POC                             ║
║    - Push to: GitHub (origin) + Gitea (zimacube)                       ║
║    - Contains: Application source code                                 ║
║                                                                        ║
║  DOCS REPO: Route-Playout-Econometrics_POC-claude-docs  (THIS REPO)    ║
║    - Push to: Gitea ONLY - NEVER PUSH TO GITHUB                        ║
║    - Contains: CLAUDE.md, handovers, todos, session docs               ║
║                                                                        ║
║  The code repo has symlinks (.claude/ and Claude/) pointing here.      ║
║  Pre-push hooks enforce these rules automatically.                     ║
╚════════════════════════════════════════════════════════════════════════╝
```

---

## CRITICAL: Two Separate Repos

| Repo | What Goes Here | Where to Push |
|------|----------------|---------------|
| **Code repo** | Python, Streamlit, src/, tests/ | GitHub + Gitea |
| **Docs repo** (this one) | CLAUDE.md, handovers, todos | **Gitea ONLY** |

```bash
# Code changes
cd ~/PycharmProjects/Route-Playout-Econometrics_POC
git add . && git commit -m "feat: whatever"
git push origin main && git push zimacube main

# Doc changes
cd ~/PycharmProjects/Route-Playout-Econometrics_POC-claude-docs
git add . && git commit -m "docs: session handover"
git push origin main      # Gitea ONLY
```

**New machine setup:** See `SETUP.md`

---

## Commit Rules

**NEVER commit without explicit user approval.** Wait for "commit" or "commit and push".

---

## Project Scope

**This POC is a read-only query interface:**
- Streamlit UI for campaign analysis
- Queries PostgreSQL materialised views (no API calls)
- Data export (CSV, Excel)
- For econometricians to browse campaigns and export audience data

**Pipeline work is separate:** `route-playout-pipeline` repo populates the database.

---

## Documentation

| Location | Content |
|----------|---------|
| `docs/01-architecture.md` | System architecture |
| `docs/02-ui-guide.md` | UI code patterns |
| `docs/03-demo-mode.md` | Brand anonymisation |
| `docs/04-cache-integration.md` | Cache query patterns |
| `reference/route-api-reference.md` | Route/SPACE API details (pipeline reference) |
| `reference/playout-file-formats/` | Playout schema docs |

---

## Quick Reference

### Run Application

```bash
startstream              # Primary database
startstream demo         # Primary + brand anonymisation
startstream local        # Secondary database
startstream local demo   # Secondary + brand anonymisation
stopstream               # Stop all instances
```

Or manually: `USE_PRIMARY_DATABASE=true DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504`

### Shell Function (in `~/.zshrc`)

```bash
alias stopstream='pkill -f "streamlit run"'

startstream() {
    pkill -f "streamlit run" 2>/dev/null
    sleep 1
    local use_primary="true" demo_mode="false" db_name="Primary"
    for arg in "$@"; do
        case "$arg" in
            demo)  demo_mode="true" ;;
            local) use_primary="false"; db_name="Local" ;;
        esac
    done
    USE_PRIMARY_DATABASE=$use_primary DEMO_MODE=$demo_mode streamlit run src/ui/app.py --server.port 8504 &
    local msg="Started on $db_name database"
    [[ "$demo_mode" == "true" ]] && msg="$msg (DEMO MODE)"
    echo "$msg"
}
```

**Why manual?** Running Streamlit via Claude Code background processes exhausts conversation token budget.

---

## Coding Guidelines

### UI Structure (`src/ui/`)
- **`components/`** — Reusable UI elements (charts, tables, maps)
- **`tabs/`** — Page-level tab implementations
- **`config/`** — Configuration and constants

### Rules
1. Check `src/ui/components/` for existing functions before creating new ones
2. Keep SQL in `src/db/`, not scattered in UI code
3. Extract reusable chart logic to `components/`

---

## Technology Stack

- **Python 3.11+** / **Streamlit** / **PostgreSQL**
- **Package Manager**: UV (recommended)
- **Demo mode**: `DEMO_MODE=true` anonymises brand names

---

*Last Updated: February 2026*
