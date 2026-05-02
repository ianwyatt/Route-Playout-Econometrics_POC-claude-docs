# Session prompt — 2026-05-04

H1 is shipped. Plan C (React advertiser views) closed out at HEAD
`e0198e1` on `feature/duckdb-migration` on 2026-05-02. The branch is
now ready for review-and-merge, OR the next session can start the
H2 work (cross-advertiser comparison, more Streamlit tabs ported,
demographic breakdowns).

This prompt assumes the natural next move: **finalise the H1 branch
for merge** (review pass, optional follow-ups, then merge to `main`
and tag for the public Adwanted repo). If you want to jump straight
into H2, skip the read-list below and read
`Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md` for
the H2 scope.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules and key documents pointer
2. `Claude/Handover/2026-05-02_plan-c-complete-h1c-shipped.md` —
   what shipped, the 17 commits, deviations from the plan,
   architectural notes that propagate to H2, and the floor items
3. `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md` §
   "Done Criteria" — confirms what was demonstrated; the only
   subjective check left is "visual fidelity vs Pepsi/Talon Netlify
   reference"
4. `Claude/docs/pipeline-coordination.md` — cross-team state, schema
   gotchas

## Floor items to consider before merge

From the Plan-C handover, in priority order:

1. **Sidebar refactor** (1-line) — `Sidebar.tsx` still has an inline
   `useQuery(['advertisers'])`; swap in `useAdvertisers()` from
   `@/features/advertiser-view/hooks/useAdvertiser.ts`. TanStack
   Query's cache already dedupes; this is purely DRY.
2. **Shape descriptor tuning** (Plan B carry-over) — every
   advertiser shows "Concentrated burst" in the live overview; the
   threshold heuristic in `src/api/services/advertisers.py`
   `_classify_shape` needs tuning. Subjective; involves looking at
   real data and choosing breakpoints.
3. **Visual fidelity review** vs Pepsi/Talon Netlify reference
   sites — only subjective check left in the Done Criteria. May
   surface chart-spacing or typography tweaks.
4. **Pre-existing test failures** in `tests/unit/test_import_mobile_index.py`
   and `tests/integration/test_mobile_index_integration.py` — would
   need a dedicated cleanup task to get a fully-green
   `pytest tests/`.
5. **`_aggregate_weekly_impacts` SQL rewrite** — N-queries-per-advertiser
   pattern; cold `/api/advertisers` is 3.2s. Single grouped query
   would amortise to milliseconds.
6. **`src/ui/app.py` decomposition** (635 lines) — modularity
   warning at every commit touching it.

## Merge / release flow when ready

```bash
# Local:
git checkout main
git merge --no-ff feature/duckdb-migration
git push origin main         # private dev repo

# Tag for the public Adwanted repo (PRIVATE remote → PUBLIC remote
# only via tags; the pre-push hook blocks branch pushes to public):
git tag -a v3.0-h1-react-foundation -m "H1: DuckDB + FastAPI + React advertiser views"
git push origin v3.0-h1-react-foundation         # tag to private dev
git push public v3.0-h1-react-foundation         # tag to public reference
```

Do NOT `git push public main` or any branch — the pre-push hook
will reject it.

**Wait for explicit user approval before merging.** Per CLAUDE.md
the user retains the merge decision.

## Execution environment

- DuckDB snapshot: `/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- Test fixture: `tests/fixtures/route_poc_test.duckdb` (~1.9 GB,
  gitignored). Rebuild via `uv run python scripts/build_test_duckdb.py`
  if missing
- `.env` (Plan C additions are in `.env.example`): `DUCKDB_PATH`,
  `DEMO_MODE`, `DEMO_PROTECT_MEDIA_OWNER`, `LOG_LEVEL`, `ENVIRONMENT`,
  `API_PORT=8000`, `ALLOWED_ORIGINS=http://localhost:5173`,
  `FRONTEND_PORT=5173`, `STREAMLIT_URL=http://localhost:8504`
- `frontend/.env.development`: `VITE_API_BASE_URL=http://localhost:8000`,
  `VITE_STREAMLIT_URL=http://localhost:8504`
- `uv sync --extra dev` done; Route hooks installed
- **Branch**: `feature/duckdb-migration` checked out at **`e0198e1`**
- Node v22.22.1, npm available
- `frontend/node_modules/` ~872 packages
- **Tailwind v4** + shadcn (Radix/Nova preset) + `@tailwindcss/vite`
  plugin (no PostCSS, no `tailwind.config.ts`); design tokens live
  in `frontend/src/styles/globals.css` `@theme inline` block
- System Chrome at `/opt/google/chrome/chrome` (Playwright uses
  `channel: 'chrome'`, no bundled chromium download)

## Working constraints

- **Side-of-desk cadence per task.** Wait for "go" between tasks.
  Tight-loop commands chain within a task.
- **Commit autonomously when work is clean.** `feature/duckdb-migration`
  is in "commit and push without approval unless you find an error
  or are unsure" mode. NEVER use `--no-verify`.
- **Do NOT push to public GitHub branches.** `origin` (private dev
  repo) only. Pre-push hook blocks branch pushes to `public`;
  tag-push is the only way work reaches the public repo.
- **NEVER merge without explicit user approval** — the user retains
  the merge decision per CLAUDE.md.
- **Subagents for mechanical work**, parallel when files are
  disjoint, sequential when they share a file. Always review the
  diff before committing.
- **NEVER run Streamlit as a Claude Code background process** —
  exhausts the conversation token budget per CLAUDE.md. If a live
  cross-app smoke is needed, ask the user to run `startstream` in
  a terminal.
- **Bash cwd does not persist across tool calls.** Chain
  `cd /abs/path && cmd` in a single Bash call or use
  `npm --prefix frontend run X`.

## Pre-flight check before starting

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git checkout feature/duckdb-migration
git pull --ff-only
git log --oneline -5                 # confirm e0198e1 is HEAD

# Backend still works
uv run pytest tests/api tests/db 2>&1 | tail -3   # 127 tests, all green

# Frontend unit tests
cd frontend && npm test -- --run 2>&1 | tail -5    # 8 tests, all green
cd ..

# Frontend builds
npm --prefix frontend run build 2>&1 | tail -5     # split bundle: 320KB main + 4.6MB lazy chunk

# E2E (slower, requires API + Vite)
# Skip in pre-flight; run on-demand via npm --prefix frontend run test:e2e
```

If anything fails, stop and surface — do not start changes on a
stale or broken base.

## Architectural notes that propagate forward

These are documented at length in
`Claude/Handover/2026-05-02_plan-c-complete-h1c-shipped.md` but worth
keeping in mind for any new frontend work:

- **Tailwind v4 design system**: token bridge in `globals.css` maps
  shadcn's runtime tokens (`--background`, `--card`, `--primary`,
  `--border`, …) to our Pepsi/Talon hex palette via the `.dark`
  block. New shadcn primitives via `npx shadcn@latest add` will
  inherit the design without overrides.
- **`verbatimModuleSyntax: true`**: every type-only import must use
  `import type { ... }` (or inline `type` modifier). The TS build
  fails otherwise.
- **`@/` path alias**: defined in `tsconfig.app.json` AND `tsconfig.json`
  (the latter is shadcn-validator-only).
- **TanStack Query 5 idioms**: `isPending` (not `isLoading`),
  `error` is already typed `Error` (no cast).
- **Plotly via factory + dist-min**: `react-plotly.js/factory` +
  `plotly.js-dist-min` need to be in `optimizeDeps.include` for
  Vite dev. Defensive `.default` unwrap in `PlotlyChart.tsx`
  handles esbuild's interop quirk.
- **Lazy-loaded routes**: detail page uses `React.lazy()` to keep
  Plotly out of the initial bundle. Pattern to follow for any heavy
  route in H2.

## At the end of this session

Before stopping, write two files in the docs repo (`Claude/Handover/`):

1. A handover doc dated today: `Claude/Handover/YYYY-MM-DD_<short-status>.md`
   covering current state, commits made (with SHAs), deviations from
   the plan, and gotchas discovered.
2. A dated session prompt for the next session:
   `Claude/Handover/NEXT_SESSION_PROMPT_YYYY-MM-DD.md`. This is a
   read-and-act doc — the user points the next session at it and
   asks them to read it. Include only what the next session needs:
   actionable read-list, env state, working constraints, pre-flight
   commands, and the next task to start. Keep this same "At the end
   of this session" section at the bottom so the convention persists.

The dated session prompts capture session boundaries and help retrace
work when later sessions go off track. The latest dated file is always
the next session prompt — sort by date to find it
(`ls Claude/Handover/NEXT_SESSION_PROMPT_*.md | sort | tail -1`).
