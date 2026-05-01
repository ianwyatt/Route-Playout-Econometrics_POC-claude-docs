# Next Session Prompt

**Last updated:** 2026-05-02 (Postgres removal scope decision baked in; autonomous LXC setup framing)
**Status:** Plan A (DuckDB swap, Postgres removed) is the next executable unit of work.

This file holds the prompt to paste into a fresh Claude Code session to pick up where the previous session left off. Updated whenever the next-task target changes (e.g. when Plan A ships, this points to Plan B; when Plan B ships, points to Plan C; etc).

To use: copy the block below verbatim into a fresh Claude Code session as your first message.

---

## Prompt

```
Pick up Plan A (DuckDB swap on the existing Streamlit app) for the
Route-Playout-Econometrics_POC project.

Read these in order before touching anything:

1. .claude/CLAUDE.md — project rules and key documents pointer
2. Claude/Handover/2026-05-02_h1-foundation-complete-ready-for-plan-a.md
   — current state, what's done, what's next, pre-flight steps
3. Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md — the plan to execute
4. Claude/docs/pipeline-coordination.md — cross-team state, gotchas,
   schema contracts
5. Claude/Handover/POC_RSYNC_OPS.md — how to pull the DuckDB snapshot

Scope decision: Postgres is removed entirely from the POC, not
maintained alongside DuckDB. Plan A is DuckDB-only — no BACKEND env
var, no dual-backend support, no Postgres regression test. The
legacy feature/mobile-volume-index branch retains the old Postgres
code for reference but is not migrated.

Execution environment: This Claude session runs on an LXC connected
to the Route Tailnet (tag:iw-dev), so access to playout-db is
automatic. Run setup steps yourself: rsync the DuckDB snapshot,
uv sync, set DUCKDB_PATH in .env, install hooks, run smoke test.
Walk me through each step but don't wait for manual setup.

Working constraints:

- Side-of-desk cadence per task. Walk through tasks step-by-step,
  wait for my "go" before moving to the next task. Tight-loop
  setup commands (rsync, uv sync, smoke checks) can chain.
- TDD discipline per the plan. Don't skip the shape test (Task 5);
  it's the spine of the migration.
- Branch off main as feature/duckdb-migration. Verify cf3c716
  (anonymisation-wiring fix) is in your base — Plan A Task 0 has
  the check command. If main is missing it, branch off
  feature/mobile-volume-index instead. The migration must not
  drop the anonymisation calls cf3c716 added.
- 22 of 29 columns in mv_campaign_browser are populated; 7 reach-
  derived columns are NULL until pipeline Phase 5 lands (~2026-05-08).
  Plan A doesn't depend on those, but the shape test and Streamlit
  smoke must handle NULLs gracefully.
- Always pass read_only=True to duckdb.connect(). Multiple POC
  processes (Streamlit, FastAPI, parity test) attach the same file
  concurrently this way.
- Do NOT push to public GitHub. Daily push goes to origin (private
  GitHub dev repo). Pre-push hook blocks branch pushes to public.

When you're ready, walk me through the pre-flight steps in the
2026-05-02 handover doc (pull both repos, verify Tailnet, rsync the
snapshot, branch off main, set DUCKDB_PATH, uv sync), then start
Plan A's Task 0.
```

---

## When to update this file

- When Plan A ships → update to point at Plan B
- When Plan B ships → update to point at Plan C
- When Plan C ships → H1 is complete; rewrite to reflect H2 priorities
- When pipeline Phase 5 lands → update the "22 of 29 columns" note since reach values fill in
- If a session is interrupted mid-plan → add a "current task in flight: Task N" line so the next session resumes there rather than starting over
- If working constraints change (e.g. Tailnet access changes, branch convention changes) → update accordingly

Keep the prompt itself self-contained: a future session pasting it shouldn't need to chase additional context outside what the prompt already references.
