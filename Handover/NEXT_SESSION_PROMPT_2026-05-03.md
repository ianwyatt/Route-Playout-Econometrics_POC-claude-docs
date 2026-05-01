# Session prompt — 2026-05-03

Plan B (FastAPI layer over DuckDB) shipped on 2026-05-02. This session
begins **Plan C — the React advertiser views**. Tasks 0–1 are the
natural opening: Vite scaffold, then Tailwind theme + design tokens.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules and key documents pointer
2. `Claude/Handover/2026-05-02_plan-b-complete-h1b-shipped.md` — the
   handover for Plan B: 18 commits on `feature/duckdb-migration`, the
   full endpoint surface (33 routes), schema gotchas (Pydantic v2
   `date` field-name shadow, frameid-as-int, route_release vs
   route_release_id), and known data quirks (Lidl/Lindt sub-brand,
   advertiser weekly `iso_week` falling back to campaign-week)
3. `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md` — the
   plan being executed; jump to Task 0 (Vite scaffold) then Task 1
   (Tailwind tokens)
4. `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md` —
   architectural spec covering Plans A/B/C if the H1C plan needs
   broader context (design baseline section is most relevant for
   Plan C: dark theme, cyan accent, MI toggle, partial-data styling)
5. `Claude/docs/pipeline-coordination.md` — cross-team state, schema
   gotchas (especially the `route_release_id has two conventions`
   note since the React side may surface release info)

## Execution environment

This Claude session runs on an LXC connected to the Route Tailnet
(`tag:iw-dev`).

- DuckDB snapshot: `/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- Test fixture: `tests/fixtures/route_poc_test.duckdb` (~1.9 GB,
  gitignored). Rebuild via `uv run python scripts/build_test_duckdb.py`
  if missing
- `.env` (Plan B vars now in `.env.example`): `DUCKDB_PATH`,
  `DEMO_MODE`, `DEMO_PROTECT_MEDIA_OWNER`, `LOG_LEVEL`, `ENVIRONMENT`,
  `API_PORT=8000`, `ALLOWED_ORIGINS=http://localhost:5173`
- `uv sync --extra dev` done; Route hooks installed
- Branch: `feature/duckdb-migration` checked out, up to date with
  `origin/feature/duckdb-migration` at `3a0ffb1`
- **Node not yet installed for Plan C** — Task 0 will need either
  `nvm install` or apt-installed Node ≥ 18. Verify before running
  `pnpm create vite`.
- Chrome installed at `/opt/google/chrome/chrome` for Playwright (Task 14)

## Working constraints

- **Side-of-desk cadence per task.** Walk each task step-by-step, wait
  for "go" before moving to the next. Tight-loop commands (running
  Vitest for one slice, sweeping a single rename) can chain within a
  task.
- **Commit autonomously when work is clean.** The 2026-05-02 session
  switched mid-stream from "commit only on explicit ask" to "commit
  and push without approval unless you find an error or are unsure".
  Continue that mode unless told otherwise.
- **Do NOT push to public GitHub.** `origin` (private dev repo) only.
  Pre-push hook blocks branch pushes to `public`; tag-push is the only
  way work reaches the public repo.
- **Subagents are fair game for mechanical work** (e.g. wiring
  similarly-shaped React components or hooks) once the pattern is
  established. Run sequentially when they touch shared files; parallel
  only when the files are disjoint. Always review the diff before
  committing.
- **`frontend/` is a separate Node project.** Its `package.json` /
  `pnpm-lock.yaml` (or `package-lock.json`) live alongside the Python
  `pyproject.toml`. The pre-commit modularity checker only scans
  Python paths so React components don't trip the 300-line warning.

## Pre-flight check before starting Task 0

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git checkout feature/duckdb-migration
git pull --ff-only
git log --oneline -5                 # confirm 3a0ffb1 is HEAD
uv run pytest tests/api tests/db 2>&1 | tail -3   # 127 tests, all green
uv run uvicorn src.api.main:app --port 8000 &
sleep 2
curl -sf http://localhost:8000/api/health           # {"status":"ok"}
curl -sf http://localhost:8000/api/advertisers?    # list
kill %1
node --version                       # ≥18 expected; install if missing
```

If any check fails, stop and surface — do not start Plan C on a stale
or broken base.

## Where Plan C picks up

**Task 0**: scaffold a Vite + React + TypeScript project under
`frontend/`. Plan section "### Task 0: Vite scaffold" (line ~59) lays
out `package.json`, `vite.config.ts`, `tsconfig.json`. Use `pnpm` if
available; otherwise `npm`.

**Task 1**: add Tailwind, configure design tokens (dark theme palette
from the architectural spec — `#1a1e2e` background, `#22273a` cards,
`#4fc3f7` cyan accent, etc.), wire shadcn/ui CSS variables.

After Tasks 0–1 land cleanly, Tasks 2–7 build the data layer
(api-client, TanStack Query, AppShell/Header/Sidebar, MI toggle,
primitives, Plotly wrapper, advertiser hooks). Tasks 8–13 build the
overview and detail pages. Task 14 is a Playwright E2E happy path.
Task 15 is M7 polish (Streamlit prefill via query param,
side-by-side integration).

## Plan B follow-ups to fold in if a natural moment appears

Per the 2026-05-02 handover's "Things still on the floor", none are
blocking but worth bundling into a future small PR:

- `src/api/services/advertisers.py` is at 336 lines (modularity warn);
  split into `services/advertisers/{__init__,grouping,timeseries,
  limitations}.py` if any module grows
- `Depends(get_db)` is dead-injection on every route (every request
  pays one connection open/close); could be removed for a small perf
  win
- `_aggregate_weekly_impacts` is N-queries-per-advertiser
  (3.2s cold on `/api/advertisers` over the live 3064-campaign DB);
  rewrite as a single grouped query
- Pre-existing test failures in `tests/unit/` and `tests/integration/`
  for mobile_index — not Plan B's fault but blocks a fully-green
  `pytest tests/`
- Plan-C Tailwind tokens may surface that `frameid` is `int` not `str`
  (assumption baked into the React code expecting URL-friendly IDs);
  worth confirming when wiring api-client

## At the end of this session

Before stopping, write two files in the docs repo (`Claude/Handover/`):

1. A handover doc dated today: `Claude/Handover/YYYY-MM-DD_<short-status>.md`
   covering current state, commits made (with SHAs), deviations from
   the plan, and gotchas discovered.
2. A dated session prompt for the next session:
   `Claude/Handover/NEXT_SESSION_PROMPT_YYYY-MM-DD.md`. This is a
   read-and-act doc — the user points the next session at it and asks
   them to read it. Include only what the next session needs:
   actionable read-list, env state, working constraints, pre-flight
   commands, and the next task to start. Keep this same "At the end
   of this session" section at the bottom so the convention persists.

The dated session prompts capture session boundaries and help retrace
work when later sessions go off track. The latest dated file is always
the next session prompt — sort by date to find it
(`ls Claude/Handover/NEXT_SESSION_PROMPT_*.md | sort | tail -1`).
