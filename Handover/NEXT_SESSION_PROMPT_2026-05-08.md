# Session prompt — 2026-05-08

Floor items #4 (mobile_index test failures) and #8 (dead-code
cleanup) are both merged to `main` (`89ed99e`). Two `--no-ff` merges,
both pushed, both feature branches deleted locally + on `origin`. No
active feature branches.

Phase 5 pipeline ETA was ~2026-05-08; check
`Claude/docs/pipeline-coordination.md` first to see whether reach
columns in `mv_campaign_browser` have started populating — that
unblocks several outstanding items.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules. Public-repo policy section is
   load-bearing.
2. `Claude/Handover/2026-05-03_dead-code-and-mobile-index-test-fixes.md`
   — most recent session: floor items #4 and #8 closed, suite is
   212/212 green on `main`, no active branches.
3. `Claude/Handover/2026-05-03_h7-tab-decomposition-shipped.md` —
   floor #7 (tab decomposition) shipped just before that.
4. `Claude/Handover/2026-05-02_public-repo-policy-and-block-hook.md`
   — policy hardening + hook installation. Hook activates
   automatically in fresh sessions; live-fire confirmed.
5. `Claude/docs/pipeline-coordination.md` — Phase 5 ETA was
   ~2026-05-08. Confirm whether reach columns in `mv_campaign_browser`
   have populated. React Overview metrics and the Streamlit Weekly
   Reach tab start showing real values for many advertisers from that
   date.

## Branch state at session start

```
main                              ← 89ed99e (floor #4 + floor #8 merged)
```

The 4 commits since the prior merge:

```
89ed99e Merge branch 'fix/mobile-index-integration-tests'
0b1e4f7 Merge branch 'chore/remove-dead-code-from-tab-decomp'
c3dd0a5 fix(tests): update mobile_index CSV parser tests to current schema
db761be fix(tests): drop stale use_primary kwarg in mobile_index tests
cb717b0 chore(ui): remove dead code surfaced by tab decomposition
```

Net effect: dead `_estimate_load_time` and `_compute_mi_averages`
removed (60 lines); three test files migrated off stale `use_primary`
kwarg / `index_value` schema. Full suite **212 passed**.

## Outstanding work — start at the top

The 2026-05-03 session settled this priority order with the user.
Items 1–5 are eyes-free for the user (no visual review needed). Do
them in order; pause between each for "go". Items 6–7 need user
bandwidth and come last.

| # | Item | Notes |
|---|---|---|
| 1 | **Code review of `main`** | Broad review of the codebase as it stands at `89ed99e`. Surface bugs, smells, missing tests, dead code, schema drift, dependency hygiene. Group findings by severity and propose a prioritised fix list before writing any code. Do NOT start fixes without user approval — the review output is itself the deliverable. |
| 2 | Schema-drift / stale-reference sweep | Same shape as the 2026-05-03 audit that caught `use_primary` and `index_value` leftovers. Grep for any remaining `use_primary` references across `src/`, `scripts/`, and `tests/`; check for other params dropped during the DuckDB swap; check for stale column names. Likely a few small commits. |
| 3 | Backend test-coverage gap audit | `src/db/queries/` and `src/api/` — find untested paths against current behaviour and add unit tests. Pure backend, no UI. |
| 4 | mypy strict-mode pass | `pyproject.toml` already declares `disallow_untyped_defs = true`. Run `uv run mypy src/` and produce a mechanical fix list; commit annotation gaps in batches. |
| 5 | Docs drift check | `Claude/docs/pipeline-coordination.md`, `docs/README.md`, `Claude/Plans/*` vs current state of the code. Update or archive. |
| 6 | Shape-descriptor tuning | First-cut heuristic for the React Overview cards; **only useful once Phase 5 reach data has landed** — confirm via `Claude/docs/pipeline-coordination.md` before starting. Needs user eyes-on for label validation. |
| 7 | Visual fidelity review | React advertiser views vs Pepsi/Talon Netlify designs. Needs user eyes-on. |

Start with #1 (code review of `main`). It feeds the backlog — the
sweep / coverage / mypy / docs items (#2–#5) may be wholly or partly
absorbed into the review's findings, in which case execute against
the review output rather than the standalone item.

## Pre-flight check before starting

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git status                                # confirm clean working tree
git log --oneline -3 origin/main          # confirm 89ed99e is HEAD of main

# Start any new floor-item work on a fresh branch off main.

# Full backend + integration + unit suite (use this, not a sub-tree —
# 2026-05-03 caught a stale kwarg only because the full sweep ran)
uv run pytest tests/ 2>&1 | tail -3                    # 212 tests, all green

# Frontend unit tests
npm --prefix frontend test -- --run 2>&1 | tail -5     # 8 tests, all green

# Frontend builds
npm --prefix frontend run build 2>&1 | tail -5         # 320 KB main + 4.6 MB lazy
```

If anything fails, stop and surface — do not start changes on a stale
or broken base.

## Execution environment

- Branch: start any new work on a fresh feature branch off `main`.
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
- **Pre-flight uses `pytest tests/`, not a sub-tree.** The
  2026-05-03 session caught one stale call site only because the
  full sweep ran — `tests/api tests/db` alone misses `tests/unit/`
  and `tests/integration/`.

## Architectural notes that propagate forward

Same as the previous prompt:

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
- **DuckDB swap removed `use_primary` everywhere** — any remaining
  `use_primary=False` calls in tests, scripts, or docs are stale and
  should be dropped. The kwarg has been gone from `src/db/queries/`
  since the swap; keep an eye out during reviews.
- **`parse_mobile_index_csv` accepts both column shapes as input** —
  legacy `index_value` and new `average_index` (with optional
  `median_index`). The parser always emits rows keyed `average_index`;
  any test asserting `index_value` is stale.

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
