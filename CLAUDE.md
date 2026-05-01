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

The code repo has symlinks (`.claude/` and `Claude/`) pointing to the docs repo. New machine setup: see `Claude/docs/multi-machine-setup-and-repo-workflow.md`.

### Release workflow (publishing to Adwanted)

```bash
git tag -a vX.Y-<theme> -m "release notes"
git push origin vX.Y-<theme>      # tag to private dev
git push public vX.Y-<theme>      # tag to public reference
```

Never `git push public main` or any branch — the pre-push hook will reject it.

**NEVER commit without explicit user approval.** Wait for "commit" or "commit and push".

## Project Scope

Read-only Streamlit query interface for econometricians, against pre-built DuckDB tables (no API calls). Data populated by `route-playout-pipeline` (separate repo). Exports to CSV/Excel.

## Running the App

```bash
startstream              # Streamlit on DuckDB
startstream demo         # + brand anonymisation (all brands)
startstream global       # + selective anonymisation (Global campaigns show real brands)
stopstream               # Stop all instances
```

Shell functions in `~/.zshrc`. Running Streamlit via Claude Code background processes exhausts the conversation token budget — always use these instead.

Manual fallback: `DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504`

Env vars (`.env`): `DUCKDB_PATH` (required), `DEMO_MODE`, `DEMO_PROTECT_MEDIA_OWNER`, `LOG_LEVEL`, `ENVIRONMENT`. See `.env.example` for values and defaults.

## Coding Rules

1. Check `src/ui/components/` for existing functions before creating new ones
2. Keep SQL in `src/db/queries/` (one file per domain), not scattered in UI code
3. Extract reusable chart logic to `components/`

## Database

DuckDB is the sole read-only query backend. Postgres has been removed from the query path; the legacy `feature/mobile-volume-index` branch retains the old Postgres connection logic for reference but is not maintained.

- Full-year 2025 coverage: ~2.32B rows in `cache_route_impacts_15min_by_demo`, 339 days
- `mv_campaign_browser`: 3,064 campaigns × 29 columns (7 reach-derived columns NULL until pipeline Phase 5 lands ~2026-05-08)
- Snapshot lives at `/var/lib/route/snapshots/route_poc_cache.latest.duckdb` on `playout-db` LXC (~87 GB); pulled via rsync to local `DUCKDB_PATH`. **Never rsync the live `route_poc_cache.duckdb`** — it can be mid-write during cacher rebuilds.
- Pull procedure: `Claude/Handover/POC_RSYNC_OPS.md`
- Connection: always `read_only=True` so multiple POC processes (Streamlit, FastAPI, parity test) can attach concurrently
- Memory: DuckDB memory-maps the file; budget 8–16 GB RAM headroom for analytical queries on the impacts table

Mobile index cache tables (`cache_mi_*`): currently 69-day Mac-cache snapshots; full-year extension deferred to pipeline's Phase 5 or 5a.

Fallback pattern in `impacts.py`: try precomputed `mv_*` first, fall back to raw `cache_route_impacts_15min_by_demo`.

### NEVER Run Long Database Operations as Background Tasks

**NEVER use Claude Code background tasks (`run_in_background`) for database scripts running longer than ~2 minutes.** If the conversation compacts, background DB connections become orphaned — they keep running with no way to monitor or stop them.

- Run long DB scripts in a **separate terminal**
- Monitor from Claude with quick query checks
- If a script must be killed, terminate the process explicitly

## Active Work — Horizon 1 (committed)

H1 is decomposed into three executable plans, each producing ship-able software:

- **Plan A — DuckDB swap** (`Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md`) — replace Postgres with DuckDB on the existing Streamlit app. Substrate ready (snapshot live, ops note delivered). Branch: `feature/duckdb-migration`.
- **Plan B — FastAPI layer** (`Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md`) — thin JSON layer over the existing query functions, plus new advertiser-trends endpoints.
- **Plan C — React advertiser views** (`Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md`) — Vite + React + TypeScript app on `localhost:5173` consuming Plan B's API; ports the Pepsi/Talon Netlify visual language; ships single-advertiser detail + overview.

Architectural spec covering all three: `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`.

H2–H4 (further tabs ported, multi-user, custom audiences) are captured as forward intent only; not in scope until H1 ships.

No live deployment target at present. Parallels VM retired; DigitalOcean plan paused. Public GitHub repo serves as Adwanted's production reference.

## Key Documents

| Document | Purpose |
|---|---|
| `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md` | H1 architectural spec |
| `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md` | Plan A — DuckDB migration tasks |
| `Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md` | Plan B — FastAPI layer tasks |
| `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md` | Plan C — React advertiser views tasks |
| `Claude/docs/pipeline-coordination.md` | Living record of cross-team coordination (schema contracts, gotchas, open items) |
| `Claude/docs/multi-machine-setup-and-repo-workflow.md` | Three-remote pattern, new-machine setup procedure |
| `Claude/Handover/POC_INTEGRATION.md` | Pipeline team's canonical operational reference (DuckDB schema, gotchas) |
| `Claude/Handover/POC_RSYNC_OPS.md` | How to pull the DuckDB snapshot via rsync |
| `docs/README.md` | Full doc index for source-code-side documentation |

When picking up an active session, read `Claude/docs/pipeline-coordination.md` first for the latest cross-team state, then the relevant Plan.
