# H1C Task Orchestration — direct vs subagent vs parallel

**Date:** 2026-05-03
**Scope:** Plan C (`Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md`), Tasks 4–15. Tasks 0–3 already shipped on `feature/duckdb-migration`.

This is a working note about *how* to execute the remaining Plan C tasks, not *what* they do. The plan itself remains the source of truth for the work. Pick this up at the start of any new session that's continuing Plan C.

## Categorisation

### Direct (pattern-setting / cross-cutting — full attention required)

| Task | Why direct |
|---|---|
| **4** — MI toggle + persistent state | Sets the global-state pattern (localStorage-backed) reused everywhere. Small but design-y. |
| **5** — UI primitives (Card, MetricBlock, DataLimitationsPanel) | Visual atoms used by every later component. **Manual prereq:** run `npx shadcn@latest init` in a real terminal before this lands (interactive prompt blocks Claude Code). See `Claude/Handover/NEXT_SESSION_PROMPT_2026-05-03.md` for recommended answers. |
| **6** — Plotly chart wrapper + helpers | Codifies axis formatting, layout defaults, weekend bands, MI overlay mechanism. Every chart inherits this. |
| **7** — Advertiser data hooks | Write 1–2 hooks directly to set the typed-hook pattern; subagent can mechanically clone the rest of the family once shape is locked. |
| **8** — Advertiser overview page | Composition piece. Optional cut point per the plan, but if shipped, it's the exec-facing landing page — judgement matters. |
| **13** — Wire detail page | Composes Tasks 9–12 into the final advertiser detail page. Layout judgement; finds gaps in the primitives and chart wrapper that need direct iteration. |

### Subagent (mechanical, pattern already in place)

These four touch **disjoint files** and can be dispatched as **parallel subagents in a single Agent batch**, after Tasks 5 + 6 + 7 land:

| Task | File | Pattern source |
|---|---|---|
| **9** — AdvertiserHeader | `frontend/src/features/advertiser-view/AdvertiserHeader.tsx` | Task 5 primitives |
| **10** — Daily timeseries chart | `frontend/src/features/advertiser-view/DailyTimeseriesChart.tsx` | Task 6 wrapper |
| **11** — Weekly timeseries (brand transitions) | `frontend/src/features/advertiser-view/WeeklyTimeseriesChart.tsx` | Task 6 wrapper + hash-based colour mapping |
| **12** — Campaign list table | `frontend/src/features/advertiser-view/CampaignList.tsx` | TanStack Table (set columns, then mechanical) |

None imports from another at write-time; assembly happens in Task 13. **Always review each subagent's diff before committing** — orchestration confirmed in `NEXT_SESSION_PROMPT_2026-05-03.md`.

### Either (judgement call at execution time)

| Task | Notes |
|---|---|
| **14** — Playwright E2E happy path | Subagent fine if scenarios are crisp; charts/network timing can need iteration. Default direct unless the spec is unambiguous. |
| **15** — Streamlit prefill query param | Touches `src/ui/app.py` (Python, separate codebase from React). Mechanical and small (~10 lines). Subagent fine, but small enough to just do directly. |

## Execution cadence

```
Task 4  →  Task 5  (after manual `npx shadcn@latest init`)  →  Task 6
       →  Task 7  (direct first, subagent for tail of hook family)
       →  Task 8  (or skip — optional cut point)
       →  Tasks 9 / 10 / 11 / 12  in parallel subagents (one Agent batch)
       →  Task 13
       →  Task 14
       →  Task 15
```

Side-of-desk per task: the user gives "go" between tasks. Tight-loop commands (Vitest within one slice, sweeping a single rename) chain within a task without check-ins. Subagent dispatches happen in a single Agent batch when files are disjoint; sequential when files overlap.

## Why this lives here

Captured so a fresh session — even one that doesn't have the conversation context where this was decided — can read this file and continue with the same orchestration. The next-session prompt at the end of today's work will link back to this doc rather than re-stating the categorisation.
