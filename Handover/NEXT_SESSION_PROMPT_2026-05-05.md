# Session prompt — 2026-05-05

H1 is shipped and pre-merge cleanup is done. The branch
`feature/duckdb-migration` is at HEAD `ccf78b8` and is ready to merge
to `main` and tag for the public Adwanted repo. **The user retains the
merge decision per CLAUDE.md** — wait for explicit "merge" instruction.

If the user defers merge and wants to land more pre-merge polish,
floor items `#2` (shape-descriptor tuning), `#3` (visual fidelity
review), `#4` (pre-existing mobile_index test failures), and `#6`
(advertisers.py + app.py decomposition) are all still on the table.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules and key documents pointer.
2. `Claude/Handover/2026-05-02_pre-merge-cleanup-floor-items-1-and-5.md`
   — what the previous session did (sidebar refactor + advertiser-overview
   perf rewrite + cumulative-row bug fix), perf timings, modularity
   warning on `src/api/services/advertisers.py`, floor-items state.
3. `Claude/Handover/2026-05-02_plan-c-complete-h1c-shipped.md` — original
   Plan-C close-out for full H1 commit list (now 71 commits ahead of
   `main`) and architectural notes.
4. `Claude/docs/pipeline-coordination.md` — cross-team state. Phase 5
   ETA was tightened to "next Friday-ish" (~2026-05-08); reach columns
   in `mv_campaign_browser` will start populating from then. No new
   coordination items in flight.

## Important — bug fix changes user-visible numbers

`ccf78b8` filtered `cache_campaign_reach_week` to `reach_type='individual'`
in the advertiser aggregation paths. Pre-fix, every per-week bucket was
silently summing `individual + cumulative` (the cumulative row is the
running total — see the handover for the worked example). React Overview
`peak_week_impacts` / `mean_week_impacts` / `weeks_active` /
`shape_descriptor` and the advertiser detail Weekly chart will all
display lower-but-correct values relative to any pre-merge demo.

If the user runs the app and is surprised by smaller numbers, this is
expected and intended — direct them to the handover doc for the
explanation.

## Merge / release flow

When the user explicitly says "merge":

```bash
git checkout main
git pull --ff-only origin main
git merge --no-ff feature/duckdb-migration
git push origin main          # private dev repo

git tag -a v3.0-h1-react-foundation -m "H1: DuckDB + FastAPI + React advertiser views"
git push origin v3.0-h1-react-foundation        # tag to private dev
git push public v3.0-h1-react-foundation        # tag to public reference
```

Do **NOT** `git push public main` or any branch — the pre-push hook
will reject it. Tag-push is the only path to the public repo.

After merge, the user may want a follow-up cleanup commit on `main`
for floor item `#6` (decomposition of `src/api/services/advertisers.py`
at 379 lines and `src/ui/app.py` at 635 lines).

## Pre-flight check before starting

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git checkout feature/duckdb-migration
git pull --ff-only
git log --oneline -5                 # confirm ccf78b8 is HEAD

# Backend tests
uv run pytest tests/api tests/db 2>&1 | tail -3        # 133 tests, all green

# Frontend unit tests
npm --prefix frontend test -- --run 2>&1 | tail -5     # 8 tests, all green

# Frontend builds
npm --prefix frontend run build 2>&1 | tail -5         # 320 KB main + 4.6 MB lazy
```

If anything fails, stop and surface — do not start changes on a stale
or broken base.

## Execution environment

- `DUCKDB_PATH=/home/dev/data/route_poc_cache.duckdb` (87 GB, identity
  `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- Test fixture: `tests/fixtures/route_poc_test.duckdb` (~1.9 GB,
  gitignored). Rebuild via `uv run python scripts/build_test_duckdb.py`
  if missing.
- `.env`: see `.env.example` for the full list. Key values:
  `DUCKDB_PATH`, `DEMO_MODE`, `DEMO_PROTECT_MEDIA_OWNER`, `LOG_LEVEL`,
  `ENVIRONMENT`, `API_PORT=8000`, `ALLOWED_ORIGINS=http://localhost:5173`,
  `FRONTEND_PORT=5173`, `STREAMLIT_URL=http://localhost:8504`.
- `frontend/.env.development`: `VITE_API_BASE_URL=http://localhost:8000`,
  `VITE_STREAMLIT_URL=http://localhost:8504`.
- `uv sync --extra dev` done; Route hooks installed.
- **Branch**: `feature/duckdb-migration` checked out at **`ccf78b8`**.
- 71 commits ahead of `main`.
- Node v22.22.1, npm available, `frontend/node_modules/` ~872 packages.
- **Tailwind v4** + shadcn (Radix/Nova preset) + `@tailwindcss/vite`
  (no PostCSS, no `tailwind.config.ts`); design tokens in
  `frontend/src/styles/globals.css` `@theme inline` block.
- System Chrome at `/opt/google/chrome/chrome` (Playwright uses
  `channel: 'chrome'`).

## Working constraints

- **Side-of-desk cadence per task.** Wait for "go" between tasks.
  Tight-loop commands chain within a task.
- **Commit autonomously when work is clean.** `feature/duckdb-migration`
  is in "commit and push without approval unless you find an error or
  are unsure" mode. NEVER use `--no-verify`.
- **NEVER merge without explicit user approval** — the user retains
  the merge decision per CLAUDE.md.
- **Do NOT push to public GitHub branches.** `origin` (private dev
  repo) only. Pre-push hook blocks branch pushes to `public`; tag-push
  is the only way to reach the public repo.
- **Subagents for mechanical work**, parallel when files are disjoint,
  sequential when they share a file. Always review the diff before
  committing.
- **NEVER run Streamlit or the FastAPI service as a Claude Code
  background process** — exhausts the conversation token budget per
  CLAUDE.md. If a live cross-app smoke is needed, ask the user to run
  `startstream` / `startapi` in a terminal.
- **Bash cwd does not persist across tool calls.** Chain
  `cd /abs/path && cmd` in a single Bash call or use
  `npm --prefix frontend run X`.

## Architectural notes that propagate forward

- **`cache_campaign_reach_week` has two `reach_type` values** —
  `'individual'` (per-week) and `'cumulative'` (running total). Any
  new SQL must filter `reach_type = 'individual'` unless it explicitly
  wants the cumulative line. Worth flagging in next pipeline-team
  coordination round.
- **Bulk-by-IDs query pattern**: `get_weekly_reach_for_campaigns_sync`
  is the first POC query taking a list of IDs with `?,?,?` placeholders.
  Future bulk queries should follow the same shape — empty-list
  short-circuit, generated placeholders, return `campaign_id` so callers
  can group/attribute downstream.
- **Connection cost dominates for many small queries**: each
  `get_db_connection()` memory-maps the 87 GB file. When refactoring
  N-queries-per-X loops, batch into one bulk query rather than caching
  connections — cleaner and catches behaviour bugs at the boundary.
- **Tailwind v4 design system** (carry-forward from Plan C): token
  bridge in `globals.css` maps shadcn's runtime tokens to the
  Pepsi/Talon hex palette. New shadcn primitives via
  `npx shadcn@latest add` inherit the design without overrides.
- **`verbatimModuleSyntax: true`**: every type-only import must use
  `import type { ... }` (or inline `type` modifier). Build fails
  otherwise.
- **TanStack Query 5 idioms**: `isPending` (not `isLoading`); `error`
  is already typed `Error`.
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
   read-and-act doc — the user points the next session at it and asks
   them to read it. Include only what the next session needs:
   actionable read-list, env state, working constraints, pre-flight
   commands, and the next task to start. Keep this same "At the end
   of this session" section at the bottom so the convention persists.

The dated session prompts capture session boundaries and help retrace
work when later sessions go off track. Sort by date to find the latest
(`ls Claude/Handover/NEXT_SESSION_PROMPT_*.md | sort | tail -1`).
