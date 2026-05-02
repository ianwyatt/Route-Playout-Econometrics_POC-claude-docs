# Handover — Plan C complete, H1C ship signal

**Date:** 2026-05-02 (session ran across 2026-05-01 → 2026-05-02)
**Branch:** `feature/duckdb-migration` (pushed to `origin`, HEAD `e0198e1`)
**Status:** Plan C done. H1 (DuckDB → FastAPI → React) is feature-complete on a single branch. The React app is the demoable surface for stakeholder buy-in; Streamlit on `:8504` continues running for the tabs not yet ported.

---

## What shipped

H1 done-criteria from `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md`:

- ✅ `npm test -- --run`: 8/8 unit tests
- ✅ `npm run test:e2e` (Playwright): 1/1 happy-path PASS in ~22s cold
- ✅ Streamlit (`:8504`) + FastAPI (`:8000`) + React (`:5173`) run simultaneously
- ✅ `/advertisers/lidl` renders header + daily chart + weekly chart + campaign list + data limitations
- ✅ MI toggle changes both charts and persists across navigation (localStorage)
- ✅ Brand-transition colour coding on weekly chart (5-colour deterministic-hash palette)
- ✅ Campaign row → Streamlit `?campaign_id=` deep-link round-trips end-to-end
- 🔲 Visual fidelity vs Pepsi/Talon Netlify reference — needs a side-by-side review (subjective; no failure signal)

## Commits made this session (17 total, all on `origin/feature/duckdb-migration`)

| SHA | Message | Plan task |
|---|---|---|
| `927a4b1` | `feat: Tailwind theme tokens for dark advertiser-views design` | Task 1 |
| `d7c2c44` | `feat: api client and TanStack Query setup` | Task 2 |
| `f3b2cf8` | `feat: AppShell with header, sidebar, and routing skeleton` | Task 3 |
| `699752f` | `feat: persistent Mobile Index toggle` | Task 4 |
| `5f031e8` | `feat: migrate frontend to Tailwind v4 + shadcn (Radix/Nova)` | Task 5 prereq (see deviations) |
| `34c1b2d` | `feat: Card, MetricBlock, DataLimitationsPanel primitives` | Task 5 |
| `396399c` | `feat: Plotly wrapper with weekend bands and avg line helpers` | Task 6 |
| `7b40221` | `feat: advertiser data hooks via TanStack Query` | Task 7 |
| `3c5373b` | `feat: advertiser overview page (M5)` | Task 8 |
| `596d9f6` | `feat: AdvertiserHeader with metric blocks` | Task 9 |
| `d1e5ab3` | `feat: DailyTimeseriesChart with weekend bands, avg line, MI overlays` | Task 10 |
| `0475277` | `feat: WeeklyTimeseriesChart with brand transition colour coding` | Task 11 |
| `4ca9cda` | `feat: CampaignList with row-click → Streamlit deep link` | Task 12 |
| `b463b36` | `feat: wire single-advertiser detail page` | Task 13 |
| `55f74da` | `perf: lazy-load advertiser detail route to split Plotly out of main bundle` | Task 13 follow-up |
| `2d0449f` | `test: Playwright E2E happy path for advertiser flow` | Task 14 |
| `e0198e1` | `feat: Streamlit prefill via ?campaign_id= for cross-app deep-linking` | Task 15 |

Tasks 9–12 ran as **parallel subagents in a single Agent batch** (the orchestration plan — `Claude/Plans/2026-05-03-h1c-task-orchestration.md` — flagged them as disjoint and mechanical once Tasks 5/6/7 had landed). Each subagent's diff was reviewed before commit. Every other task was direct.

## Deviations from Plan C as written

### Tailwind v4 + shadcn integration (the big one)

Plan C assumed Tailwind v3 (Task-0 deviation pinned `tailwindcss@^3.4`). After Task 4 the user ran `npx shadcn@latest init` and picked Radix + Nova — but shadcn 4.6's Nova preset emits **Tailwind-v4-only syntax**: `@theme inline`, `@custom-variant`, `outline-ring/50`, `@apply bg-background`. None of that compiles against v3.

Resolution path A from the three options surfaced (migrate v4 / use old `shadcn-ui@latest` CLI / hand-write primitives) was chosen. Commit `5f031e8` migrates the whole frontend to Tailwind v4 in one pass:

- Replaced PostCSS with `@tailwindcss/vite` plugin; deleted `postcss.config.js` and `tailwind.config.ts` (v4 idiom: theme config in CSS)
- `globals.css` rewritten with `@theme inline` block bridging shadcn's runtime tokens (`--background`, `--card`, `--primary`, `--border`, `--muted-foreground`, etc.) to **our Pepsi/Talon hex palette** — every shadcn primitive inherits `bg-base/card/nav`, `accent-cyan/orange`, `border-#2d3348` with no per-component className overrides
- `<html class="dark">` so the `.dark` token block applies
- Existing component classNames (`bg-bg-base`, `text-text-primary`, `border-border`, `accent-cyan`, `text-h1`, `brand-{a..e}`) all survive via `--color-*` `@theme` declarations

Browser smoke confirmed every existing class still resolves to its Task-1 hex.

### Path alias landed in `tsconfig.app.json`, not the references-only root

Plan-C Task 3 says add `paths` to `tsconfig.json`, but the root is references-only (`files: []`). The alias has to live in `tsconfig.app.json` (the file with `include: ["src"]`) for `tsc -b` to apply it. We later added `compilerOptions.paths` to the root tsconfig too — purely so shadcn's init validator passes (it only reads root tsconfig).

### TS 6 deprecated `baseUrl`

`baseUrl` was a hard error at `tsc -b` under TypeScript 6. Modern TS roots `paths` at the tsconfig dir, so the workaround is to drop `baseUrl` entirely and use `"paths": { "@/*": ["./src/*"] }`.

### Plotly CJS/ESM interop

Surfaced when Task 13 first rendered a chart. `react-plotly.js/factory` is CJS. Two fixes were needed together:
- `vite.config.ts` adds `optimizeDeps.include: ['react-plotly.js/factory', 'plotly.js-dist-min']` so Vite pre-bundles them into ESM via esbuild (without this, dev mode serves the raw CJS file and the browser hits "exports is not defined")
- `PlotlyChart.tsx` defensively unwraps a nested `.default` because esbuild's interop returns the whole `module.exports` object as the default rather than auto-unwrapping `module.exports.default` for this particular package. Same code path works in dev and prod.

### `plotly.js-dist-min` types

There's no `@types/plotly.js-dist-min`. Added `src/types/plotly-dist-min.d.ts` re-exporting `plotly.js` types for the dist-min entry point.

### Bundle splitting (perf follow-up)

Task 13's wire-up brought Plotly into the initial bundle (4.93MB / 1.48MB gzip) — every visitor paid for it even on the overview page. Commit `55f74da` lazy-loads the detail-page route via `React.lazy` + `Suspense`. Result: initial bundle 320KB / 98KB gzip; lazy chunk 4.61MB / 1.39MB gzip loaded only on `/advertisers/:slug`.

### TanStack Query 5 idiom updates

The plan-as-written used `isLoading` and `(error as Error).message`. We use `isPending` (TanStack 5's preferred field for first-fetch loading) and drop the `as Error` cast (TanStack's `error` is already typed `Error` after the truthy check).

### TanStack Table sort wiring

The plan-as-written used `useState([])` + `setSorting as any`. We use typed `useState<SortingState>([])` and pass `setSorting` directly to `onSortingChange`. The cast was a workaround for the missing type annotation.

### `verbatimModuleSyntax` everywhere

`tsconfig.app.json` has `verbatimModuleSyntax: true`. Every type-only import had to be `import type { ... }` (or use the inline `type` modifier in mixed imports). The plan's `import { MIMode }`, `import { ReactNode }`, `import { ColumnDef }` etc. would have failed the build.

### Date column slicing

`AdvertiserDetail.period_start/end` and `AdvertiserCampaign.period_start/end` are full ISO datetime strings ("2025-01-15T00:00:00") from the API. We slice to YYYY-MM-DD for display in `AdvertiserHeader` and `CampaignList` so the time component doesn't render.

### Defensive null handling in CampaignList

The plan's `Math.round(c.getValue<number>() / 1000)` errored on undefined → NaN. `AdvertiserCampaign` has 4 optional fields per the Pydantic schema (`days_active`, `total_impacts`, `period_start`, `period_end`, `primary_media_owner`). We render '—' for any missing values.

### `peak_week_label` guard in AdvertiserCardGrid

The plan rendered "Peak {value}k {label}" unconditionally. When `peak_week_impacts === 0` and `peak_week_label === undefined` (advertisers with no data), the literal string "Peak 0k undefined" appeared. We guard the whole "Peak …" phrase on `peak_week_impacts > 0`.

### E2E test improvements

Plan-as-written had `await page.waitForTimeout(500)` — flaky pattern. Replaced with `toBeVisible({ timeout: 30_000 })` waits on visible elements (cold daily-timeseries fetch can take ~3s; 30s gives breathing room). Also clicks "Lidl" specifically rather than the table's first row (first row is "Brand not provided at point of trade" with 1820 campaigns — its daily aggregate is too slow for a happy-path test). `addInitScript(() => localStorage.clear())` keeps MI state unambiguous across runs.

### Streamlit prefill clears the query param

Plan-as-written set `selected_campaign_id` and `show_analysis=True`. We also call `st.query_params.clear()` after consumption so a "Reset" inside Streamlit doesn't immediately re-prefill from the same URL.

### `.gitignore` re-allows for React conventions

The Python-era `.gitignore` had `lib/` and `hooks/` rules (Python distutils + dev tooling) that caught the React `frontend/src/lib/` and `frontend/src/features/**/hooks/` folders. Added explicit `!frontend/src/lib/`, `!frontend/src/features/**/hooks/` re-allows. Also re-allowed `frontend/.env.development` (Vite convention to commit; only `.env.local` is per-machine).

## Things still on the floor

### Sidebar still has its own inline `useQuery(['advertisers'])`

`Sidebar.tsx` predates the Task-7 hook family. TanStack Query's cache dedupes the two — same `queryKey: ['advertisers']` — so there's no perf cost, but it's a DRY-refactor candidate. Could swap in `useAdvertisers()` from `@/features/advertiser-view/hooks/useAdvertiser.ts` in a one-line change.

### Shape descriptor heuristic needs tuning

Plan-B Task 13 noted the shape-descriptor thresholds need tuning. Confirmed visible in browser smoke: nearly every advertiser shows "Concentrated burst" with little differentiation. Out of Plan C scope; tweak in `src/api/services/advertisers.py`.

### `_aggregate_weekly_impacts` is N-queries-per-advertiser

Carried over from Plan B — for each advertiser, `_aggregate_weekly_impacts` iterates campaigns and calls `get_weekly_reach_data_sync` once per campaign. Lidl: 42 calls. Cold first hit on `/api/advertisers` ≈ 3.2s; warm hits ≈ 55ms. Future optimisation: a single SQL query over all campaign IDs grouped by week.

### `src/ui/app.py` modularity warning

635 lines after the 10-line prefill addition. Pre-commit modularity checker flagged it. Pre-existing; would need a dedicated decomposition pass.

### Pre-existing test failures (still present)

`tests/unit/test_import_mobile_index.py` and `tests/unit/test_mobile_index_queries.py` have 2 failing tests; `tests/integration/test_mobile_index_integration.py` has a collection error. Pre-existed at the start of Plan B; out of Plan C scope.

### `Depends(get_db)` dead-injection on every API route

Carried over from Plan B handover — every route declares `conn=Depends(get_db)` for forward consistency, but no route uses the injected connection. ~1ms cost per request.

### Lidl detail shows "Lindt" as a sub-brand

Per Plan B handover. Investigated in Plan C smoke — the detail page now shows `Sub-brands: 1`, suggesting the data may have been corrected upstream OR the rendering filters Lindt out. Not deeply verified; flag if it returns.

## Environment / fixture state at end of session

- `DUCKDB_PATH=/home/dev/data/route_poc_cache.duckdb` (87 GB, identity unchanged from session start)
- `tests/fixtures/route_poc_test.duckdb` unchanged (1.9 GB, gitignored)
- 127/127 db+api tests, all green
- 8/8 frontend Vitest unit tests
- 1/1 Playwright E2E
- `frontend/node_modules/` ~872 packages (up from 620 pre-shadcn)
- `frontend/.env.development` has both `VITE_API_BASE_URL` and `VITE_STREAMLIT_URL`

## Architectural notes worth carrying forward

### Tailwind v4 design system

The token bridge in `globals.css` is the single source of truth. Two layers of CSS variables:
- Our Task-1 tokens (`--color-bg-base`, `--color-text-primary`, `--color-accent-cyan`, …) — produce utilities like `bg-bg-base`, `text-text-primary`
- shadcn's runtime tokens (`--background`, `--foreground`, `--card`, `--primary`, …) — consumed by every shadcn primitive

Both resolve to the same hex palette via the `.dark` block. Shadcn primitives can be added with `npx shadcn@latest add <component>` and will inherit the design language without overrides.

### Cross-app deep-linking convention

`VITE_STREAMLIT_URL` (frontend) + `STREAMLIT_URL` (.env.example) document the React → Streamlit handoff. Streamlit's `initialize_session_state()` reads `?campaign_id=<id>` from `st.query_params` and clears the param after consumption.

### Lazy-loaded routes

The detail-page route is `React.lazy()`-loaded. Pattern to follow when porting more Streamlit tabs to React in H2.

## Next session

The session prompt is `Claude/Handover/NEXT_SESSION_PROMPT_2026-05-04.md`.
