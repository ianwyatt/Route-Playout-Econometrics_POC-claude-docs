# Route Playout Econometrics POC - Project Specification

## Repository Setup

| Repo | What Goes Here | Where to Push |
|------|----------------|---------------|
| **Code repo** (`Route-Playout-Econometrics_POC`) | Python, Streamlit, src/, tests/ | GitHub (`origin`) + Gitea (`zimacube`) |
| **Docs repo** (`Route-Playout-Econometrics_POC-claude-docs`) | CLAUDE.md, handovers, todos | **Gitea ONLY** — NEVER push to GitHub |

The code repo has symlinks (`.claude/` and `Claude/`) pointing to the docs repo. Pre-push hooks enforce these rules automatically. New machine setup: see `Claude/SETUP.md`.

**NEVER commit without explicit user approval.** Wait for "commit" or "commit and push".

---

## Project Scope

**Read-only query interface for econometricians:**
- Streamlit UI for campaign analysis against pre-built PostgreSQL tables (no API calls)
- Data export (CSV, Excel)
- Data is populated by `route-playout-pipeline` (separate repo)

---

## Running the App

```bash
startstream              # Primary database (MS-01)
startstream demo         # Primary + brand anonymisation
startstream local        # Secondary database (localhost)
startstream local demo   # Secondary + brand anonymisation
stopstream               # Stop all instances
```

These are shell functions defined in `~/.zshrc`. Running Streamlit via Claude Code background processes exhausts the conversation token budget — always use these instead.

Or manually: `USE_PRIMARY_DATABASE=true DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504`

### Environment Variables (`.env`)

| Variable | Values | Default | Purpose |
|----------|--------|---------|---------|
| `USE_PRIMARY_DATABASE` | `true`/`false` | `false` | `true` = MS-01 remote database, `false` = localhost |
| `DEMO_MODE` | `true`/`false` | `false` | Anonymises brand names for presentations |
| `LOG_LEVEL` | `DEBUG`/`INFO`/`WARNING`/`ERROR` | `INFO` | Logging verbosity |
| `ENVIRONMENT` | `development`/`production` | `production` | Environment identifier |

---

## Source Code Structure

```
src/
├── db/
│   ├── queries/           # All SQL lives here — one file per domain
│   │   ├── connection.py  # Database connection management
│   │   ├── campaigns.py   # Campaign browser queries
│   │   ├── demographics.py
│   │   ├── frame_audience.py
│   │   ├── geographic.py
│   │   ├── impacts.py     # Reach/frequency/impacts queries (largest)
│   │   └── reach.py       # Weekly reach and GRP queries
│   ├── route_releases.py  # Route release metadata
│   └── streamlit_queries.py  # Cached wrappers for Streamlit (@st.cache_data)
├── ui/
│   ├── app.py             # Main Streamlit entry point
│   ├── components/        # Reusable UI elements (charts, tables, maps)
│   ├── tabs/              # Page-level tab implementations
│   │   ├── overview.py, detailed_analysis.py, time_series.py
│   │   ├── geographic.py, reach_grp.py, executive_summary.py
│   └── config/            # Anonymisation and demographic segment definitions
└── utils/
    ├── formatters.py      # Number/date formatting helpers
    ├── validators.py      # Input validation
    └── ttl_cache.py       # Time-based cache utility
```

### Coding Rules

1. Check `src/ui/components/` for existing functions before creating new ones
2. Keep SQL in `src/db/queries/`, not scattered in UI code
3. Extract reusable chart logic to `components/`

---

## Database

- **18 tables + 1 view**, 19 indexes, 57 GB total
- Key tables: `cache_route_impacts_15min_by_demo` (44 GB), `mv_playout_15min` (8.6 GB), `mv_campaign_browser` (836 campaigns)
- All data is pre-built by `route-playout-pipeline` — this app only reads
- Export: `exports/route_poc_adwanted_20260205.dump` (5.7 GB compressed)
- Schema reference: `docs/10-database-schema.md`

---

## Deployment

| Target | Details |
|--------|---------|
| **GitHub** | Public repo: `https://github.com/RouteResearch/Route-Playout-Econometrics_POC` |
| **VM** | Ubuntu 24.04.3 ARM64 on Parallels (IP: `10.211.55.5`, user: `parallels`) |
| **Adwanted** | Handover package shared via Dropbox (database + source + README) |
| **DigitalOcean** | Next priority — see `Claude/todo/upcoming_tasks.md` |

---

## Documentation

Full index at `docs/README.md`. Key documents:

- `docs/01-architecture.md` — system architecture and data flow
- `docs/10-database-schema.md` — table/index schema reference
- `docs/11-database-export.md` — database export and restore procedures
- `docs/02-ui-guide.md` — UI code patterns
- `docs/03-demo-mode.md` — brand anonymisation

---

## Technology Stack

- **Python 3.11+** / **Streamlit** / **PostgreSQL**
- **Package Manager**: UV (`pyproject.toml` + `uv.lock`)
- **No API credentials needed** — all data served from PostgreSQL

---

*Last Updated: 7 February 2026*
