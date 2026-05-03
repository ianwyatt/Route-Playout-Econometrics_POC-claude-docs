# Route Playout Econometrics POC - Project Specification

## Repository Setup

Three-remote pattern. Adwanted use the public repo as their production reference, so `main` on the public repo only advances via tagged releases.

**Code repo (`Route-Playout-Econometrics_POC`)**

| Remote | URL | Role |
|--------|-----|------|
| `origin` | GitHub private — `RouteResearch/Route-Playout-Econometrics_POC-dev` | Daily driver. `git push` defaults here. |
| `public` | GitHub public — `RouteResearch/Route-Playout-Econometrics_POC` | Adwanted's public reference. **Default stance: do NOT push (tags or branches) without an explicit user instruction naming the `public` remote.** Pre-push hook blocks branch pushes regardless. |
| `zimacube` | Gitea (Tailscale) | Backup mirror. |

**Docs repo (`Route-Playout-Econometrics_POC-claude-docs`)** — handovers, todos, CLAUDE.md, plans

| Remote | URL | Role |
|--------|-----|------|
| `origin` | GitHub private — `ianwyatt/Route-Playout-Econometrics_POC-claude-docs` | Daily driver. Permitted by `.claude/route-mode` marker in the docs repo. |
| `zimacube` | Gitea (Tailscale) | Backup mirror. |

Docs repo NEVER goes to public GitHub — pre-push hook blocks it unless the `.claude/route-mode` marker is present (Route business projects only).

The code repo has symlinks (`.claude/` and `Claude/`) pointing to the docs repo. New machine setup: see `Claude/docs/multi-machine-setup-and-repo-workflow.md`.

### Public-repo policy

**Default: stay on `origin` (private dev). Do NOT push anything — tag or branch — to the `public` remote unless the user explicitly says so naming `public`.**

The current intent is to keep iterating on `origin` and only consider a public push later, possibly never (the public repo may simply remain frozen at the current Adwanted reference). The pre-push hook blocks branch pushes to `public` as a backstop, but the policy applies to tags too — the hook does not block those.

If asked to publish, the release flow is:

```bash
git tag -a vX.Y-<theme> -m "release notes"
git push origin vX.Y-<theme>      # tag to private dev
git push public vX.Y-<theme>      # ONLY when user explicitly asks
```

Never `git push public main` or any branch — the pre-push hook will reject it. And never offer "merge + tag + push public" as a single step in a session prompt or handover; the public push is always its own opt-in.

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
4. **`use_primary` is vestigial** — ~100 sites in `src/ui/` thread it as a cache-key differentiator from the Postgres era. The campaign-browser radio button toggles `os.environ["USE_PRIMARY_DATABASE"]` but no longer switches anything in DuckDB-only mode. Don't introduce new code that relies on it; a dedicated cleanup branch removes the chain.
5. **Route source audiences are in thousands.** `cache_route_impacts_15min_by_demo.impacts`, `mv_campaign_browser.total_impacts_all_adults` (and the other `*_impacts_*` / `*_reach_*` columns), `cache_mi_*` raw/indexed/median values — all stored in thousands per OOH industry convention. Display layer either multiplies by 1000 (Overview, campaign analyzer, `from_thousands()` helper) OR labels the metric/column "(000s)" (Executive Summary, Frame Audiences, Geographic). Both conventions are intentional and live side-by-side. Empirical equality between an MV and canonical (e.g. `total_impacts_all_adults` matches `SUM(impacts)`) does NOT establish that the unit is real impacts — it just means both sides use the same unit (thousands). Never remove a `×1000` site or a `(000s)` label thinking it's a bug. New code: pick whichever convention the surrounding view uses.

## Database

DuckDB is the sole read-only query backend. Postgres has been removed from the query path; the legacy `feature/mobile-volume-index` branch retains the old Postgres connection logic for reference but is not maintained.

- Full-year 2025 coverage: ~2.32B rows in `cache_route_impacts_15min_by_demo`, 339 days
- `mv_campaign_browser`: 3,064 campaigns × 29 columns (7 reach-derived columns NULL until pipeline Phase 5 — ETA was ~2026-05-08, slipping; check `Claude/docs/pipeline-coordination.md` for current status)
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

## Horizon 1 — shipped

All three Plan branches are merged. No active feature branches.

- **Plan A — DuckDB swap** — shipped 2026-05-01, `e358699`. Plan: `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md`. Completion: `Claude/Handover/2026-05-01_plan-a-complete-h1a-shipped.md`.
- **Plan B — FastAPI layer** — shipped, see `Claude/Handover/2026-05-02_plan-b-complete-h1b-shipped.md`.
- **Plan C — React advertiser views** — shipped, see `Claude/Handover/2026-05-02_plan-c-complete-h1c-shipped.md`.

Architectural spec: `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`.

## Current backlog

Active work is driven by the 2026-05-08 main code review and the floor-item list:

- **Review document:** `Claude/Plans/2026-05-08_main-code-review.md` — 6 CRITICAL, 11 HIGH, 13 MEDIUM, prioritised fix sequence in §6. **The canonical source of truth for the open backlog.**
- **Latest session prompt:** `Claude/Handover/NEXT_SESSION_PROMPT_*.md` (latest by date) — the re-ordered priority list folding the review's findings into the floor items.

H2–H4 (further tabs ported, multi-user, custom audiences) remain forward intent; not in scope until the post-H1 backlog clears.

No live deployment target at present. Parallels VM retired; DigitalOcean plan paused. Public GitHub repo serves as Adwanted's production reference.

## Key Documents

| Document | Purpose |
|---|---|
| `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md` | H1 architectural spec |
| `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md` | Plan A — DuckDB migration tasks |
| `Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md` | Plan B — FastAPI layer tasks |
| `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md` | Plan C — React advertiser views tasks |
| `Claude/Plans/2026-05-08_main-code-review.md` | Main code review — current backlog source of truth |
| `Claude/docs/pipeline-coordination.md` | Living record of cross-team coordination (schema contracts, gotchas, open items) |
| `Claude/docs/multi-machine-setup-and-repo-workflow.md` | Three-remote pattern, new-machine setup procedure |
| `Claude/docs/postgres-demo-worktree.md` | Frozen Postgres-demo worktree at `v2.1-postgres-final` — how to use, troubleshoot, replace |
| `Claude/Handover/POC_INTEGRATION.md` | Pipeline team's canonical operational reference (DuckDB schema, gotchas) |
| `Claude/Handover/POC_RSYNC_OPS.md` | How to pull the DuckDB snapshot via rsync |
| `docs/README.md` | Full doc index for source-code-side documentation |

When picking up an active session, read `Claude/docs/pipeline-coordination.md` first for the latest cross-team state, then the relevant Plan.
