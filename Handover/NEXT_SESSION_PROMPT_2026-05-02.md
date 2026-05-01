# Session prompt — 2026-05-02

Plan A (DuckDB swap on the existing Streamlit app) shipped on
2026-05-01. This session begins **Plan B — the FastAPI layer over the
DuckDB query functions**. Tasks 0–1 are the natural opening: add the
deps, then build the package skeleton with a health endpoint.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules and key documents pointer
2. `Claude/Handover/2026-05-01_plan-a-complete-h1a-shipped.md` — the
   handover for what landed yesterday: 9 commits on
   `feature/duckdb-migration`, deviations from Plan A, and the small
   pile of cleanup-deferred items (`use_primary` parameters still
   sitting on Streamlit cache wrappers; `mv_playout_15min`
   sanitisation gotcha)
3. `Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md` — the plan
   being executed; jump to Task 0 then Task 1
4. `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md` —
   architectural spec covering Plans A/B/C if the H1B plan needs
   broader context
5. `Claude/docs/pipeline-coordination.md` — cross-team state, schema
   gotchas

## Execution environment

This Claude session runs on an LXC connected to the Route Tailnet
(`tag:iw-dev`).

- DuckDB snapshot: `/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- Test fixture: `tests/fixtures/route_poc_test.duckdb` (~1.9 GB,
  gitignored). Rebuild via `uv run python scripts/build_test_duckdb.py`
  if missing
- `.env`: `DUCKDB_PATH` set, `DEMO_MODE=false`, `LOG_LEVEL=INFO`,
  `ENVIRONMENT=development`
- `uv sync --extra dev` done; Route hooks installed
- Branch: `feature/duckdb-migration` checked out, up to date with
  `origin/feature/duckdb-migration` at `e358699`
- Chrome installed at `/opt/google/chrome/chrome` for Playwright (used
  for the Plan A Task 14 smoke; available if Plan B needs UI smoke)

## Working constraints

- **Side-of-desk cadence per task.** Walk each task step-by-step, wait
  for "go" before moving to the next. Tight-loop commands (running
  endpoint tests for one slice, sweeping a single rename) can chain
  within a task.
- **NEVER commit without explicit "commit" or "commit and push".**
- **Do NOT push to public GitHub.** `origin` (private dev repo) only.
  Pre-push hook blocks branch pushes to `public`; tag-push is the only
  way work reaches the public repo.
- **Subagents are fair game for mechanical work** (e.g. wiring
  similarly-shaped endpoints) once the pattern is established. Run
  sequentially when they touch shared files; parallel only when the
  files are disjoint. Always review the diff before committing.

## Pre-flight check before starting Task 0

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git checkout feature/duckdb-migration
git pull --ff-only
git log --oneline -10                # confirm e358699 is HEAD
uv run pytest tests/db/ -v 2>&1 | tail -3   # 37 tests, all green
```

If any of those check fails, stop and surface — do not start Plan B
on a stale or broken base.

## Where Plan B picks up

**Task 0**: add `fastapi`, `uvicorn[standard]`, `fastapi-cache2`,
`httpx` runtime deps and `pytest-asyncio` dev dep, commit.

**Task 1**: create `src/api/` package skeleton with a `/api/health`
endpoint. Verify by running `uv run uvicorn src.api.main:app --reload
--port 8000` and curling `http://localhost:8000/api/health`. The plan
covers this at line ~81 onwards.

After Tasks 0–1 land cleanly, Tasks 2–11 progressively port query
functions to JSON endpoints (one task per query module, mirroring
Plan A's structure). Tasks 13–18 are the new advertiser-service
endpoints. Task 19 is an integration smoke; Task 20 wires up
`startapi` and `.env.example`.

## Cleanup-deferred from Plan A (worth knowing about, not urgent)

Per the Plan A handover: `use_primary: bool = True` parameters still
sit on Streamlit cache-data wrappers (`load_campaign_header`,
`load_mi_daily`, `load_regional_impacts`, etc.) as dead variables.
They no longer plumb anywhere. Either fold the cleanup into the first
Plan B commit that touches `src/ui/app.py`, or open a small follow-up
PR mid-Plan-B once a natural pause appears. Not blocking.

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
   commands, and the next task to start. Keep this same "At the end of
   this session" section at the bottom so the convention persists.

The dated session prompts capture session boundaries and help retrace
work when later sessions go off track. The latest dated file is always
the next session prompt — sort by date to find it
(`ls Claude/Handover/NEXT_SESSION_PROMPT_*.md | sort | tail -1`).
