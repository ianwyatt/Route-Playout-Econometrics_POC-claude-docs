# Route Playout Econometrics POC - Project Specification

## Repository Setup

Three-remote pattern. Adwanted use the public repo as their production reference, so `main` on the public repo only advances via tagged releases.

**Code repo (`Route-Playout-Econometrics_POC`)**

| Remote | URL | Role |
|--------|-----|------|
| `origin` | GitHub private — `RouteResearch/Route-Playout-Econometrics_POC-dev` | Daily driver. `git push` defaults here. |
| `public` | GitHub public — `RouteResearch/Route-Playout-Econometrics_POC` | **Tags only.** Adwanted's reference. Pre-push hook blocks branch pushes; annotated tags required. |
| `zimacube` | Gitea (Tailscale) | Backup mirror. |

**Docs repo (`Route-Playout-Econometrics_POC-claude-docs`)** — handovers, todos, CLAUDE.md, plans

| Remote | URL | Role |
|--------|-----|------|
| `origin` | GitHub private — `ianwyatt/Route-Playout-Econometrics_POC-claude-docs` | Daily driver. Permitted by `.claude/route-mode` marker in the docs repo. |
| `zimacube` | Gitea (Tailscale) | Backup mirror. |

Docs repo NEVER goes to public GitHub — pre-push hook blocks it unless the `.claude/route-mode` marker is present (Route business projects only).

The code repo has symlinks (`.claude/` and `Claude/`) pointing to the docs repo. New machine setup: see `Claude/SETUP.md`.

### Release workflow (publishing to Adwanted)

```bash
git tag -a vX.Y-<theme> -m "release notes"
git push origin vX.Y-<theme>      # tag to private dev
git push public vX.Y-<theme>      # tag to public reference
```

Never `git push public main` or any branch — the pre-push hook will reject it.

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
startstream demo         # Primary + brand anonymisation (all brands)
startstream global       # Primary + selective anonymisation (Global campaigns show real brands)
startstream local        # Secondary database (localhost)
startstream local demo   # Secondary + brand anonymisation (all brands)
startstream local global # Secondary + selective anonymisation
stopstream               # Stop all instances
```

These are shell functions defined in `~/.zshrc`. Running Streamlit via Claude Code background processes exhausts the conversation token budget — always use these instead.

Or manually: `USE_PRIMARY_DATABASE=true DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504`

### Environment Variables (`.env`)

| Variable | Values | Default | Purpose |
|----------|--------|---------|---------|
| `USE_PRIMARY_DATABASE` | `true`/`false` | `false` | `true` = MS-01 remote database, `false` = localhost |
| `DEMO_MODE` | `true`/`false` | `false` | Anonymises brand names for presentations |
| `DEMO_PROTECT_MEDIA_OWNER` | media owner name | `""` | When set with DEMO_MODE, campaigns with this media owner show real brands |
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

- **18 tables + 1 view + 7 mobile index cache tables**, ~62 GB total
- Key tables: `cache_route_impacts_15min_by_demo` (44 GB), `mv_playout_15min` (8.6 GB), `mv_campaign_browser` (836 campaigns)
- Mobile index cache tables (`cache_mi_*`): pre-aggregated impacts at various grains, built by `scripts/import_mobile_index.py --cache-only`
- All data is pre-built by `route-playout-pipeline` — this app only reads
- Export: `exports/route_poc_adwanted_20260205.dump` (5.7 GB compressed)
- Schema reference: `docs/10-database-schema.md`

### PostgreSQL WAL Warning

**NEVER run bulk inserts (millions of rows) without CHECKPOINT calls between operations.** PostgreSQL WAL (Write-Ahead Log) files accumulate during large writes and can consume hundreds of GB of hidden disk space before a checkpoint reclaims them. The `cache_mi_frame_hourly` table (52M rows) once generated ~1.6 TB of temporary WAL, nearly filling the disk.

Rules for bulk database operations:
- Always `COMMIT` then `CHECKPOINT` between large table inserts
- Monitor disk space with `df -h /` during long-running builds
- Break inserts of 10M+ rows into batches if possible
- Check WAL accumulation: `SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')) as wal_size;`

### NEVER Run Long Database Operations as Background Tasks

**NEVER use Claude Code background tasks (`run_in_background`) for database scripts that run longer than ~2 minutes.** If the conversation compacts or the context resets, background DB connections become orphaned — they keep running with no way to monitor or stop them. An orphaned cache build query once consumed 803 GB of temp files before being discovered.

Instead:
- Run long DB scripts in a **separate terminal** (e.g. `uv run python scripts/import_mobile_index.py --cache-only`)
- Monitor from Claude Code using `psql` queries to check progress (row counts, `pg_stat_activity`)
- If a script must be killed, always `SELECT pg_terminate_backend(pid)` then `CHECKPOINT` to reclaim space

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

*Last Updated: 9 February 2026*
