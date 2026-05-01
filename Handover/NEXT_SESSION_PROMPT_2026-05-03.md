# Session prompt — 2026-05-03

Plan B (FastAPI layer) shipped on 2026-05-02. **Plan C Task 0 (Vite
scaffold) also shipped that evening** — the frontend tree exists,
deps are installed, the dev server boots clean. This session begins
**Plan C Task 1 — Tailwind theme + design tokens**.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules and key documents pointer
2. `Claude/Handover/2026-05-02_plan-b-complete-h1b-shipped.md` — the
   API surface that Plan C consumes (33 endpoints, schema gotchas)
3. `Claude/Handover/2026-05-02_plan-c-task-0-vite-scaffold.md` — what
   landed in the Vite scaffold, plus the Tailwind v3 pin and the
   skipped-shadcn-init deviation
4. `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md` — the
   plan being executed; jump to **Task 1: Tailwind theme + design
   tokens** (Task 0 is already done)
5. `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md` —
   architectural spec; the "Design Baseline" table (palette, typography,
   MI-toggle, partial-data styling) is the source of truth for the
   tokens about to be wired in Task 1
6. `Claude/docs/pipeline-coordination.md` — cross-team state, schema
   gotchas (especially the `route_release_id has two conventions`
   note since the React side may surface release info)

## Manual prereq before Task 5 — run shadcn init in a real terminal

shadcn 4.6's CLI prompts interactively for "component library" (Radix
vs Base) at the very start of `init`, and that prompt blocks in this
non-interactive Claude Code environment. **Run it yourself in a
terminal** before any UI primitive task lands:

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC/frontend
npx shadcn@latest init
```

Recommended answers:
- Component library: **Radix**
- Style: **New York** (or whichever the latest default is)
- Base colour: **Zinc** (neutral; the brand-cyan accent comes from our
  own Tailwind theme, not shadcn defaults)
- TypeScript: yes
- Tailwind config path: `tailwind.config.js`
- Components alias: `@/components`
- Utils alias: `@/lib/utils`
- React server components: no (we're a SPA, not Next)
- CSS variables: yes (matches the Plan C dark-theme approach)

This creates `frontend/components.json` and `frontend/src/lib/utils.ts`
(with the `cn()` helper). Commit both before starting Task 5. If the
init keeps fighting, falling back to hand-writing those two files is
a documented option — see the Task-0 handover for details.

Task 1 itself does not depend on shadcn init — only Task 5+ does — so
this can be deferred until just before Task 5.

## Execution environment

This Claude session runs on an LXC connected to the Route Tailnet
(`tag:iw-dev`).

- DuckDB snapshot: `/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- Test fixture: `tests/fixtures/route_poc_test.duckdb` (~1.9 GB,
  gitignored). Rebuild via `uv run python scripts/build_test_duckdb.py`
  if missing
- `.env` (Plan B vars now in `.env.example`): `DUCKDB_PATH`,
  `DEMO_MODE`, `DEMO_PROTECT_MEDIA_OWNER`, `LOG_LEVEL`, `ENVIRONMENT`,
  `API_PORT=8000`, `ALLOWED_ORIGINS=http://localhost:5173`
- `uv sync --extra dev` done; Route hooks installed
- **Branch**: `feature/duckdb-migration` checked out, up to date with
  `origin/feature/duckdb-migration` at **`a23ca97`** (was `3a0ffb1`
  at start of Plan C)
- Node v22.22.1 installed, npm available, pnpm not (Plan C uses npm
  in commands; pnpm-equivalent is fine if available)
- `frontend/node_modules/` already populated (~620 packages); npm
  install isn't needed unless package.json changes
- `Tailwind v3.4.19` pinned (Plan C plan assumes v3 config shape;
  see Task-0 handover for the v3-vs-v4 reasoning)
- Chrome installed at `/opt/google/chrome/chrome` for Playwright
  (used by Task 14 E2E)

## Working constraints

- **Side-of-desk cadence per task.** Walk each task step-by-step,
  wait for "go" before moving to the next. Tight-loop commands
  (running Vitest for one slice, sweeping a single rename) can chain
  within a task.
- **Commit autonomously when work is clean.** The 2026-05-02 session
  was running in "commit and push without approval unless you find
  an error or are unsure" mode. Continue that mode unless told
  otherwise. NEVER use `--no-verify`.
- **Do NOT push to public GitHub.** `origin` (private dev repo) only.
  Pre-push hook blocks branch pushes to `public`; tag-push is the
  only way work reaches the public repo.
- **Subagents are fair game for mechanical work** (e.g. wiring
  similarly-shaped React components or hooks) once the pattern is
  established. Run sequentially when they touch shared files;
  parallel only when the files are disjoint. Always review the diff
  before committing.
- **Foundation tasks are NOT mechanical.** Task 1 (design tokens),
  Task 2 (api-client + Query setup), Task 3 (AppShell layout) all
  encode design decisions that propagate. Do these directly with
  full attention.
- **`frontend/` is a separate npm package.** Its lockfile lives
  alongside the Python `pyproject.toml`. The pre-commit modularity
  checker only scans Python paths, so React components don't trip
  the 300-line warning.
- **Bash cwd does not persist across tool calls.** When running
  frontend commands, either chain `cd frontend && cmd` in a single
  Bash call or use `npm --prefix frontend run X`. Discovered during
  Task 0; flagged in the Task-0 handover.

## Pre-flight check before starting Task 1

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git checkout feature/duckdb-migration
git pull --ff-only
git log --oneline -5                 # confirm a23ca97 is HEAD

# Backend still works
uv run pytest tests/api tests/db 2>&1 | tail -3   # 127 tests, all green

# Frontend dev server still boots
cd frontend && npm run dev > /tmp/vite-preflight.log 2>&1 &
sleep 3
curl -sf http://localhost:5173 -o /dev/null && echo "vite OK on :5173"
pkill -f "vite" 2>/dev/null
cd ..
```

If anything fails, stop and surface — do not start Task 1 on a stale
or broken base.

## Where Plan C picks up

**Task 1**: replace the empty `tailwind.config.js` with a typed config
that codifies the design baseline from
`Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`:

- Background `#1a1e2e`, card `#22273a`, nav `#171b28`
- Borders `#2d3348`
- Text: primary `#e0e4ed`, body `#c8cdd8`, muted `#8891a5`,
  dim `#5a6178`
- Accents: cyan `#4fc3f7`, orange `#ffb74d`
- Brand palette (sub-brand colour-coding): `#4fc3f7`, `#81c784`,
  `#ba68c8`, `#ffb74d`, `#f06292`
- Typography: h1 22px/600, chart-title 15px/500,
  chart-subtitle 12px muted, body 12-13px

Then create `frontend/src/styles/globals.css` with the Tailwind
imports and CSS variables that mirror the theme, and update
`frontend/src/main.tsx` to import the new globals.

The plan section "### Task 1: Tailwind theme + design tokens" (line
~127 of the H1C plan) has the full step-by-step. After Task 1 lands
cleanly, Task 2 builds the API client + TanStack Query setup; Task 3
wires the AppShell/Header/Sidebar layout.

## Plan B follow-ups to fold in if a natural moment appears

Per the Plan B handover's "Things still on the floor", none are
blocking but worth bundling into a future small PR:

- `src/api/services/advertisers.py` is at 336 lines (modularity warn);
  split into `services/advertisers/{__init__,grouping,timeseries,
  limitations}.py` if any module grows
- `Depends(get_db)` is dead-injection on every route (every request
  pays one connection open/close); could be removed for a small perf
  win
- `_aggregate_weekly_impacts` is N-queries-per-advertiser
  (3.2s cold on `/api/advertisers` over the live 3064-campaign DB);
  rewrite as a single grouped query
- Pre-existing test failures in `tests/unit/` and `tests/integration/`
  for mobile_index — not Plan B's fault but blocks a fully-green
  `pytest tests/`
- Plan-C api-client may surface that `frameid` is `int` not `str`
  (assumption baked into any URL-friendly ID expectation); worth
  confirming when wiring api-client (Task 2)

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
