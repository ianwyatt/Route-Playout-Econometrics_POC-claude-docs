# Session prompt — 2026-05-07

H1 floor item #6 is merged to `main` (`f165362`). Floor item #7
(tab-file decomposition) is closed across 6 commits on
`refactor/decompose-tab-files`, **pushed to `origin` but not
merged**. The user retains the merge decision per CLAUDE.md — wait
for explicit "merge".

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules. Public-repo policy section is
   load-bearing.
2. `Claude/Handover/2026-05-03_h7-tab-decomposition-shipped.md` —
   most recent session: floor #6 merged to main, floor #7 decomposed
   in six staged commits, full Playwright smoke clean, two pre-
   existing dead-code findings flagged for follow-up.
3. `Claude/Handover/2026-05-02_h1-merged-and-floor-item-6-decomposition.md`
   — context for floor item #6 (the previous decomposition that just
   merged).
4. `Claude/Handover/2026-05-02_public-repo-policy-and-block-hook.md`
   — policy hardening + hook installation. Hook activates
   automatically in fresh sessions; live-fire confirmed.
5. `Claude/docs/pipeline-coordination.md` — Phase 5 ETA still
   ~2026-05-08. Reach columns in `mv_campaign_browser` populate then;
   React Overview metrics and the Streamlit Weekly Reach tab will
   start showing real values for many advertisers from that date.

## Branch state at session start

```
main                              ← f165362 (floor #6 merged, pushed)
refactor/decompose-tab-files      ← ed6e31e (6 commits, pushed,
                                              not merged)
```

The 6 commits on the refactor branch:

```
ed6e31e refactor(ui): decompose detailed_analysis tab into a package
a5830b4 refactor(ui): decompose executive_summary tab into a package
4bb6d87 refactor(ui): decompose overview tab into a package
a51d0b9 refactor(ui): decompose time_series tab into a package
4b51702 refactor(ui): decompose reach_grp tab into a package
9a64032 refactor(ui): decompose geographic tab into a package
```

Net effect: the six oversize tab modules (1170, 739, 647, 589, 576,
491 lines) are now single-responsibility packages under
`src/ui/tabs/<name>/`. Largest individual file post-decomposition:
**289 lines** (`detailed_analysis/frame_weekly.py`), which is under
the 300-line pre-commit threshold; almost everything else is under
250. Public import surface (`render_*_tab`) preserved via re-exports
in each package's `__init__.py`. 133 backend + 8 frontend tests
green throughout; Playwright smoke clean on campaign 18925 covering
all six tabs (0 console errors, 0 warnings).

## Outstanding work — pick one with the user

| # | Item | Notes |
|---|---|---|
| 2 | Shape-descriptor tuning | First-cut heuristic for the React Overview cards; revisit once Phase 5 reach data lands (~2026-05-08) and real shapes emerge — much higher signal then |
| 3 | Visual fidelity review | React advertiser views vs Pepsi/Talon Netlify designs |
| 4 | Pre-existing mobile_index test failures | Outside H1 scope; dormant since pre-merge — `uv run pytest tests/integration/test_mobile_index_integration.py` to reproduce |
| 8 | **Dead-code cleanup** | NEW. Two pre-existing findings preserved verbatim through the floor-#7 refactor: `detailed_analysis/loaders.py:_estimate_load_time` (defined, never called) and `time_series/_render.py:mi_avg_daily_avg` etc. (computed via `data_prep._compute_mi_averages`, never read). Small grep-driven removal commit. |

Other possibilities:

- **Merge `refactor/decompose-tab-files` to `main`** — wait for
  explicit user instruction. Standard merge flow per the previous
  prompts. `origin` only, no public push.
- **Wait for Phase 5** — if user wants to see what changes after the
  pipeline lands before doing more, several items are higher-signal
  post-Phase-5.

## Pre-flight check before starting

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git status                                # confirm clean working tree
git log --oneline -3 origin/main          # confirm f165362 is HEAD of main

# If continuing on the refactor branch:
git checkout refactor/decompose-tab-files
git pull --ff-only

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

- Branch: depends on task. `main` for new floor-item branches; check
  out `refactor/decompose-tab-files` if continuing pre-merge polish.
- `DUCKDB_PATH=/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- `.env`: see `.env.example`. Same values as previous prompt.
- `frontend/.env.development`: same values as previous prompt.
- `uv sync --extra dev` done; Route hooks installed.
- Node v22.22.1; `frontend/node_modules/` ~872 packages.
- System Chrome at `/opt/google/chrome/chrome` (Playwright uses
  `channel: 'chrome'`).
- **`startstream`/`stopstream` shell helpers** in `~/.zshrc` —
  start Streamlit on port 8504 in a separate terminal.
  - `startstream` — DuckDB only
  - `startstream demo` — `DEMO_MODE=true`
  - `startstream global` — `DEMO_MODE=true` + `DEMO_PROTECT_MEDIA_OWNER=Global`
  - `stopstream` — kill any process on port 8504

## Working constraints

- **Side-of-desk cadence per task.** Wait for "go" between tasks.
  Tight-loop commands chain within a task.
- **Commit autonomously when work is clean** on the active branch
  unless the user signals otherwise. NEVER use `--no-verify`.
- **NEVER merge without explicit user approval.**
- **Do NOT push anything to the `public` remote** — neither branches
  (blocked by pre-push hook) nor tags (policy). `origin` (private dev
  repo) only. Public repo stays as a frozen Adwanted reference unless
  the user explicitly says otherwise, naming the `public` remote.
- **Subagents for mechanical work**, parallel when files are disjoint.
  Always review the diff before committing.
- **NEVER run Streamlit or the FastAPI service as a Claude Code
  background process** — exhausts the conversation token budget.
  Ask the user to run `startstream` / `startapi` in a terminal.
- **Bash cwd does not persist across tool calls.** Chain
  `cd /abs/path && cmd` in a single Bash call or use
  `npm --prefix frontend run X`.

## Architectural notes that propagate forward

Same as the previous prompt, plus:

- **Tab decomposition pattern** — for any future tab-file work, the
  package shape is: `__init__.py` (re-exports only),
  `_render.py` (orchestrator), section modules (one per markdown
  subheader / logical sub-view), shared helpers in named sibling
  modules (`data_prep.py`, `aggregations.py`, etc.). Where a section
  has two mutually-exclusive paths (e.g. daily-cumulative vs
  weekly-fallback), use a thin dispatch module that calls one of two
  sibling helpers — see
  `src/ui/tabs/reach_grp/cumulative.py` and
  `src/ui/tabs/executive_summary/reach_build.py` for the shape.
- **Inline `from src.ui.app import ...` is no longer used in tabs** —
  loaders moved to `src/ui/loaders.py` in floor item #6, so tab
  modules import directly from there.
- **Public surface preservation** — when decomposing modules into
  packages, always keep the package's `__all__`/re-exports identical
  to the previous module-level public surface so `app.py` and
  `tabs/__init__.py` need no edits.
- **`cache_campaign_reach_week` has two `reach_type` values** —
  `'individual'` (per-week) and `'cumulative'` (running total). Any
  new SQL must filter `reach_type = 'individual'` unless it explicitly
  wants the cumulative line.
- **Bulk-by-IDs query pattern**: `get_weekly_reach_for_campaigns_sync`
  is the reference shape for new bulk queries — empty-list short-
  circuit, generated `?,?,?` placeholders, return `campaign_id` so
  callers can group/attribute downstream.
- **Connection cost dominates for many small queries**: each
  `get_db_connection()` memory-maps the 87 GB file. Batch into one
  bulk query rather than caching connections.
- **Tailwind v4 design system** — token bridge in `globals.css` maps
  shadcn's runtime tokens to the Pepsi/Talon hex palette.
- **`verbatimModuleSyntax: true`**: every type-only import must use
  `import type { ... }`. Build fails otherwise.
- **TanStack Query 5 idioms**: `isPending` (not `isLoading`); `error`
  is already typed `Error`.
- **Lazy-loaded routes**: detail page uses `React.lazy()` to keep
  Plotly out of the initial bundle.
- **Floor item #6 split pattern** — for any future Python module
  decomposition outside `src/ui/tabs/`, prefer a package directory +
  re-export `__init__.py` to keep the public import surface stable
  (e.g. the advertisers/ package shape).

## At the end of this session

Per the dated-session-prompt convention (memory: feedback_dated_session_prompts.md):

Before stopping, write two files in the docs repo (`Claude/Handover/`):

1. A handover doc dated today: `Claude/Handover/YYYY-MM-DD_<short-status>.md`
   covering current state, commits made (with SHAs), deviations from
   the plan, and gotchas discovered.
2. A dated session prompt: `Claude/Handover/NEXT_SESSION_PROMPT_YYYY-MM-DD.md`.
   This is a read-and-act doc — the user points the next session at
   it and asks them to read it. Include only what the next session
   needs: actionable read-list, env state, working constraints,
   pre-flight commands, and the next task to start. Date the file so
   it sorts AFTER the existing latest prompt (use `ls
   Claude/Handover/NEXT_SESSION_PROMPT_*.md | sort | tail -1` to find
   the current latest, then pick a later date). Keep this same "At
   the end of this session" section at the bottom so the convention
   persists.

Both files live in the docs repo, not the code repo. After writing,
commit and push from inside the docs repo (`git -C Claude add ...`).
