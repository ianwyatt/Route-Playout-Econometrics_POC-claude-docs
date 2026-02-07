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
- Queries pre-built PostgreSQL tables (no API calls)
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
| `docs/05-cache-troubleshooting.md` | Cache debugging guide |
| `docs/06-campaign-indicators.md` | Campaign indicator definitions |
| `docs/07-weekly-averages.md` | Weekly average calculations |
| `docs/08-geographic-visualization.md` | Map and geographic features |
| `docs/09-credentials.md` | Credential management |
| `docs/10-database-schema.md` | Table/index schema reference |
| `docs/11-database-export.md` | Database export procedures |

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
- **`config/`** — Anonymisation and demographic segment definitions

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

## Database

- **18 tables + 1 view**, 19 indexes, 57 GB total
- Key tables: `cache_route_impacts_15min_by_demo` (44 GB), `mv_playout_15min` (8.6 GB), `mv_campaign_browser` (836 campaigns)
- All data is pre-built by `route-playout-pipeline` — this app only reads
- Export: `exports/route_poc_adwanted_20260205.dump` (5.7 GB compressed)

---

## Deployment

- **GitHub**: Public repo at `https://github.com/RouteResearch/Route-Playout-Econometrics_POC`
- **VM**: Ubuntu 24.04.3 ARM64 on Parallels (IP: 10.211.55.5, user: `parallels`)
- **Adwanted**: Handover package shared via Dropbox (database + source + README)

---

*Last Updated: 6 February 2026*
