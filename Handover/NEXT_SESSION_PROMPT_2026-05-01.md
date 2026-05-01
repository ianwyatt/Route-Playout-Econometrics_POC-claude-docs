# Session prompt — 2026-05-01

Pick up Plan A (DuckDB swap on the existing Streamlit app) for the
Route-Playout-Econometrics_POC project. Tasks 0–5 are done; this session
executes the per-module dialect conversions (Tasks 6–12), then full
shape-test run (Task 13), Streamlit smoke (Task 14), and `.env.example`
cleanup (Task 15).

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules and key documents pointer
2. `Claude/Handover/2026-05-01_plan-a-tasks-0-5-complete-ready-for-task-6.md`
   — current state, commits made, deviations from plan, the conversion
   pattern Tasks 6–12 follow, UI callers already mapped
3. `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md` — the plan being
   executed; jump to Task 6
4. `Claude/docs/pipeline-coordination.md` — cross-team state, schema
   gotchas (`buyercampaignref` sanitisation, `route_release_id`
   conventions, single-writer constraint, two demographic code spaces)

## Execution environment

This Claude session runs on an LXC connected to the Route Tailnet
(`tag:iw-dev`). The DuckDB snapshot is already pulled to
`/home/dev/data/route_poc_cache.duckdb` (87 GB), the test fixture is
built at `tests/fixtures/route_poc_test.duckdb` (1.3 GB, gitignored),
`.env` has `DUCKDB_PATH` set, `uv sync` done, hooks installed. Branch
`feature/duckdb-migration` is checked out and up to date with origin
(`ef0ab5c` is HEAD).

## Working constraints

- **Side-of-desk cadence per task.** Walk through each task step-by-step,
  wait for "go" before moving to the next task. Tight-loop commands
  (sweeping `%s` → `?`, running shape tests for one module) can chain
  within a task.
- **TDD discipline.** The shape test is the failing spec — each
  per-module conversion turns a slice green. Confirm the slice is green
  before committing.
- **Do NOT push to public GitHub.** Daily push goes to `origin` (private
  GitHub dev repo). Pre-push hook blocks branch pushes to public.
- **NEVER commit without explicit "commit" or "commit and push".**

## Pre-flight check before starting Task 6

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git checkout feature/duckdb-migration
git pull --ff-only
git log --oneline -8                                          # confirm ef0ab5c is HEAD
uv run pytest tests/db/test_query_shape.py -v 2>&1 | tail -10 # expect 33 failures
```

All 33 should fail with `TypeError: get_db_connection() takes 0
positional arguments but 1 was given` — the per-module `use_primary`
plumbing being unwound.

If on a different machine, see the handover doc for full pre-flight
(rsync the snapshot, rebuild the fixture, etc).

## The conversion pattern (Tasks 6–12)

Task 6 establishes the pattern; Tasks 7–12 repeat it for each remaining
query module. The handover doc lists the 8 UI callers of `campaigns.py`
functions that need the `use_primary=` kwarg dropped in lockstep. The
pattern:

- Drop `use_primary` parameter from `get_*_sync` signature
- Drop `psycopg2` imports
- Replace `with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)`
  block with `execute_query(conn, query, params)` (Task 6 Step 2 adds
  `execute_query` to `_dict_cursor.py`)
- For fetchone-style:
  `result = execute_query(...); return result[0] if result else None`
- For scalar lookups:
  `cursor = conn.execute(query, params); row = cursor.fetchone(); return row[0] if row else 0`
- Sweep `%s` → `?` in SQL strings
- Update the UI call sites to drop the `use_primary=` kwarg

Walk through Task 6 step by step, confirm `campaigns.py`'s slice of the
shape test goes green before committing, then ask for go before moving
to Task 7.

## At the end of this session

Before stopping, write two files in the docs repo (`Claude/Handover/`):

1. A handover doc dated today: `Claude/Handover/YYYY-MM-DD_<short-status>.md`
   covering current state, commits made (with SHAs), deviations from
   the plan, the conversion pattern still ahead, gotchas discovered.
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
