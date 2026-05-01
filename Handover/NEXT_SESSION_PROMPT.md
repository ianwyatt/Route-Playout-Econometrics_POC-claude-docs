# Next Session Prompt

**Last updated:** 2026-05-02
**Status:** Plan A (DuckDB swap) is the next executable unit of work.

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

Working constraints:

- Side-of-desk cadence; no autonomous execution. Walk through tasks
  step-by-step with me.
- TDD discipline per the plan. Don't skip the parity test (Task 5);
  it's the spine of the migration.
- The pipeline team's DuckDB substrate is ready at
  /var/lib/route/snapshots/route_poc_cache.latest.duckdb on the
  playout-db LXC. Pull it via rsync per POC_RSYNC_OPS.md before any
  code changes.
- Branch off main as feature/duckdb-migration; the existing
  feature/mobile-volume-index branch is unrelated work and should
  stay untouched.
- 22 of 29 columns in mv_campaign_browser are populated; 7 reach-
  derived columns are NULL until pipeline Phase 5 lands (~2026-05-08).
  Plan A doesn't depend on those, but the parity test must handle
  NULLs gracefully.
- Do NOT push to public GitHub. Daily push goes to origin (private
  GitHub dev repo). Pre-push hook blocks branch pushes to public.

When you're ready, walk me through pre-flight Task 0 of Plan A and
wait for my "go" before each task.
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
