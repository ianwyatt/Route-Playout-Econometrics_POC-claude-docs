# Next Session Prompt

**Last updated:** 2026-05-01 (Plan A Tasks 0–5 done; next session executes per-module conversions)
**Status:** Plan A infrastructure complete. The shape-validation test stands as the failing spec; per-module dialect conversions (Tasks 6–12) are the next executable unit of work.

This file holds the prompt to paste into a fresh Claude Code session to pick up where the previous session left off. Updated whenever the next-task target changes.

To use: copy the block below verbatim into a fresh Claude Code session as your first message.

**Convention (since 2026-05-01):** at the end of every session, also save a dated snapshot of this prompt as `NEXT_SESSION_PROMPT_YYYY-MM-DD.md` in this directory. The rolling file always reflects the latest state; the dated files are an archive of session boundaries, useful for retracing previous work when a session goes off track.

---

## Prompt

```
Pick up Plan A (DuckDB swap on the existing Streamlit app) for the
Route-Playout-Econometrics_POC project. Tasks 0–5 are done; the next
session executes the per-module dialect conversions (Tasks 6–12),
then full shape-test run (Task 13), Streamlit smoke (Task 14), and
.env.example cleanup (Task 15).

Read these in order before touching anything:

1. .claude/CLAUDE.md — project rules and key documents pointer
2. Claude/Handover/2026-05-01_plan-a-tasks-0-5-complete-ready-for-task-6.md
   — current state, commits made, deviations from plan, the
   conversion pattern Tasks 6–12 follow, UI callers already mapped
3. Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md — the plan being
   executed; jump to Task 6
4. Claude/docs/pipeline-coordination.md — cross-team state, schema
   gotchas (buyercampaignref sanitisation, route_release_id conventions,
   single-writer constraint, two demographic code spaces)

Execution environment: This Claude session runs on an LXC connected
to the Route Tailnet (tag:iw-dev). The DuckDB snapshot is already
pulled to /home/dev/data/route_poc_cache.duckdb (87 GB), the test
fixture is built at tests/fixtures/route_poc_test.duckdb (1.3 GB,
gitignored), .env has DUCKDB_PATH set, uv sync done, hooks installed.
Branch feature/duckdb-migration is checked out and up to date with
origin (ef0ab5c is HEAD).

Working constraints:

- Side-of-desk cadence per task. Walk through each task step-by-step,
  wait for "go" before moving to the next task. Tight-loop commands
  (sweeping %s → ?, running shape tests for one module) can chain
  within a task.
- TDD discipline. The shape test is the failing spec — each per-module
  conversion turns a slice green. Confirm the slice is green before
  committing.
- Do NOT push to public GitHub. Daily push goes to origin (private
  GitHub dev repo). Pre-push hook blocks branch pushes to public.
- NEVER commit without explicit "commit" or "commit and push".

Pre-flight check before starting Task 6:

1. cd /home/dev/projects/Route-Playout-Econometrics_POC
2. git fetch origin && git checkout feature/duckdb-migration && git pull --ff-only
3. git log --oneline -8 — confirm ef0ab5c is HEAD
4. uv run pytest tests/db/test_query_shape.py -v 2>&1 | tail -10
   — expect 33 failures, all "TypeError: get_db_connection() takes
   0 positional arguments but 1 was given"

If on a different machine, see the handover doc for full pre-flight
(rsync the snapshot, rebuild the fixture, etc).

Task 6 establishes the conversion pattern for Tasks 7–12. The
handover doc lists the 8 UI callers of campaigns.py functions that
need the use_primary= kwarg dropped in lockstep. The pattern is:

- Drop use_primary parameter from get_*_sync signature
- Drop psycopg2 imports
- Replace `with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)`
  block with execute_query(conn, query, params) (Task 6 Step 2 adds
  execute_query to _dict_cursor.py)
- For fetchone-style: result = execute_query(...); return result[0] if result else None
- For scalar lookups: cursor = conn.execute(query, params); row = cursor.fetchone(); return row[0] if row else 0
- Sweep %s → ? in SQL strings
- Update the UI call sites to drop the use_primary= kwarg

Walk through Task 6 step by step, confirm each module's slice of the
shape test goes green before committing, then ask for go before
moving to Task 7.
```

---

## When to update this file

- When Plan A Task 6 ships → update to point at Task 7 (or batch Tasks 7–12 if they go fast)
- When all of Plan A ships → update to point at Plan B (FastAPI layer)
- When Plan B ships → update to point at Plan C (React advertiser views)
- When Plan C ships → H1 is complete; rewrite to reflect H2 priorities
- When pipeline Phase 5 lands → update the "22 of 29 columns" notes (reach values fill in) wherever they appear
- If a session is interrupted mid-task → add a "current task in flight: Task N, step M" line so the next session resumes there
- If working constraints change (e.g. Tailnet access changes, branch convention changes) → update accordingly

Keep the prompt itself self-contained: a future session pasting it shouldn't need to chase additional context outside what the prompt already references.
