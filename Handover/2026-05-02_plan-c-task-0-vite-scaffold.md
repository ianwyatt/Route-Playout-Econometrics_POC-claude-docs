# Handover — Plan C Task 0, Vite scaffold landed

**Date:** 2026-05-02 (continuation of the same calendar day as the Plan B handover)
**Branch:** `feature/duckdb-migration` (pushed to `origin`, HEAD `a23ca97`)
**Status:** Plan B shipped (`3a0ffb1`); Plan C Task 0 also shipped (`a23ca97`). Plan C Tasks 1+ deferred to the next session.

---

## What shipped after the Plan B closeout

A single follow-on commit on the same branch:

| SHA | Message | Plan task |
|---|---|---|
| `a23ca97` | `chore: scaffold Vite + React + TS frontend` | Plan C Task 0 |

Bringing the session total to **19 commits** on `feature/duckdb-migration`.

## What's in the scaffold

`frontend/` directory under the repo root with:

- Vite + React 18 + TypeScript 5 starter (`npm create vite@latest frontend -- --template react-ts`)
- Runtime deps: `react-router-dom`, `@tanstack/react-query`, `@tanstack/react-table`, `plotly.js-dist-min`, `react-plotly.js`, `zod`
- Dev deps: `tailwindcss@^3.4`, `postcss`, `autoprefixer`, `@types/plotly.js`, `@types/react-plotly.js`, `vitest`, `@testing-library/{react,jest-dom}`, `jsdom`, `msw`, `@playwright/test`
- `tailwind.config.js` and `postcss.config.js` from `npx tailwindcss init -p` (empty `content` array — Task 1 fills this in)

Smoke at end of Task 0: `npm run dev` boots the Vite server on `:5173` (HTTP 200, page title "frontend"). The Tailwind "content option missing" warn at boot is expected and is what Task 1 resolves.

## Deviations from Plan C Task 0 as written

### Tailwind pinned to v3

The latest Tailwind on npm is v4, which:
- Removed the `tailwindcss init` CLI
- Moved theme config from `tailwind.config.ts` into CSS via `@theme` directives
- Renamed the PostCSS plugin to `@tailwindcss/postcss`

The plan was written assuming v3. Pinned `tailwindcss@^3.4.0` (resolved 3.4.19) so `tailwind.config.js` and the design-token approach in Task 1 work as written. Worth revisiting v4 once the design system stabilises — it's the long-term direction.

### `npx shadcn@latest init` skipped

shadcn 4.6's CLI prompts interactively for "component library" (Radix vs Base) at the very start of `init`, even with `--yes`. Interactive input doesn't flow cleanly through this Claude Code environment, so the init step was skipped. **This is a manual prereq for the next session before any shadcn `add` works** — see the next-session prompt for the procedure.

Alternative if init keeps fighting the CLI: hand-write `frontend/components.json` plus `src/lib/utils.ts` with the `cn()` helper. Most shadcn primitives can be copy-pasted from the docs and don't strictly require the init scaffolding.

### Root `.gitignore` `*.html` rule was catching `frontend/index.html`

The Python-era `.gitignore` had a global `*.html` rule (with a `!docs/*.html` exception) intended to ignore pytest HTML test artefacts. This silently ignored Vite's entry `index.html`. Added an explicit `!frontend/index.html` and `!frontend/**/*.html` allowance below the Frontend section in the root `.gitignore`. Worth keeping an eye on if other `*.html` files end up in places we don't expect.

### `cd` doesn't persist across Bash tool calls

A minor process note: the Bash tool's working directory does not survive between calls in some scenarios — the first `cd frontend && npm run dev` smoke from this repo's root failed with `ENOENT: no such file or directory, open '.../package.json'` because the cwd reset. Workaround used: chain `cd /abs/path && cmd` in a single Bash call, or use `npm --prefix frontend run dev` style. Worth keeping in mind for any frontend command that follows.

## Things still on the floor

### shadcn init is the most pressing prereq

Before Task 5 (UI primitives — `Card`, `MetricBlock`, `DataLimitationsPanel`) lands, the next session needs a working shadcn config. The simplest path is the user runs `npx shadcn@latest init` in a real terminal, picks Radix as the component library, accepts defaults for everything else (TypeScript, src/, alias `@/*`, base colour zinc, CSS variables yes). This creates `frontend/components.json` plus `frontend/src/lib/utils.ts` (the `cn()` helper), which then unblocks `npx shadcn@latest add button card …`.

### Tailwind config is empty

Task 1 fills it. Until then, any utility classes added to the scaffolded JSX will silently produce no styles.

### Pre-existing test failures unchanged

The two pre-Plan-B failures in `tests/unit/test_import_mobile_index.py` / `tests/unit/test_mobile_index_queries.py` and the collection error in `tests/integration/test_mobile_index_integration.py` are still there. Same scope note as in the Plan B handover.

### Modularity warning still standing

`src/api/services/advertisers.py` at 336 lines. Decomposition into `services/advertisers/{__init__,grouping,timeseries,limitations}.py` is a candidate small follow-up if a Plan C task ever needs to touch one of those slices.

## Environment / fixture state at end of session

- Same as Plan B handover: `DUCKDB_PATH` unchanged, `tests/fixtures/route_poc_test.duckdb` unchanged
- 127/127 db+api tests still green
- `frontend/node_modules/` ~620 packages, gitignored
- Vite dev server confirmed working on `:5173`
- FastAPI service confirmed working on `:8000` (Plan B integration smoke)
- Both can run side-by-side with no port conflict

## Next session

Plan C Task 1 — Tailwind theme + design tokens. Sister prompt at
`Claude/Handover/NEXT_SESSION_PROMPT_2026-05-03.md`. Has been updated
to reflect Task 0's completion plus the manual `shadcn init` prereq.
