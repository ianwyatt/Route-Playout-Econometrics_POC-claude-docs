# Session prompt — 2026-05-09

`main` is at `dd02243` (merged + pushed to `origin`). Floor items #1
(code review) and #2 (schema-drift sweep) from the 2026-05-08 prompt
are both done. The review document is the canonical reference for the
remaining backlog — read it before deciding the next move.

Phase 5 pipeline ETA was ~2026-05-08; check
`Claude/docs/pipeline-coordination.md` first to see whether reach
columns in `mv_campaign_browser` have started populating — that
unblocks shape-descriptor work and reach-driven React Overview
metrics.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules. Public-repo policy section is
   load-bearing.
2. `Claude/Plans/2026-05-08_main-code-review.md` — 6 CRITICAL, 11 HIGH,
   13 MEDIUM, plus a prioritised fix sequence in §6. This is the
   source of truth for what's left.
3. `Claude/Handover/2026-05-03_main-code-review-and-schema-drift-sweep.md`
   — what shipped in floor #2, what was deliberately deferred, and the
   gotchas discovered along the way.
4. `Claude/Handover/2026-05-03_dead-code-and-mobile-index-test-fixes.md`
   and `Claude/Handover/2026-05-03_h7-tab-decomposition-shipped.md` —
   the prior two sessions' work, still relevant context.
5. `Claude/docs/pipeline-coordination.md` — Phase 5 status. Confirm
   whether reach columns in `mv_campaign_browser` have populated.

## Branch state at session start

```
main                              ← dd02243 (schema-drift sweep merged)
```

Recent commits:

```
dd02243  Merge branch 'chore/schema-drift-sweep'
864352a  docs: fix Postgres residue in surviving in-repo docs
db9400a  docs: delete Postgres-era reference docs
fdfefea  chore(deps): drop psycopg2-binary and asyncpg
b04ae4c  chore(scripts): delete Postgres-era ingest/export tooling
89ed99e  Merge branch 'fix/mobile-index-integration-tests'
```

No active feature branches.

## Re-ordered priority list

The original floor #1-#7 ordering is partly absorbed by the review;
this list reflects the post-sweep state.

| # | Item | Notes |
|---|---|---|
| 1 | **C5 forensics — Mobile-Indexed Impacts ×1000 scale** | Cheap, blocks the C5 fix. Query `cache_mi_frame_totals` (or wherever `load_mi_frame_totals` reads from) to determine the canonical unit. Three sites (Overview ×1000, campaign_analyzer ×1000, Geographic ÷nothing) need to agree. The wrong sites must be corrected; the result is user-visible numbers. **Find the truth, surface it, then fix.** |
| 2 | **C1 — `/reach/weekly` endpoint contract** | `get_weekly_reach_data_sync` returns mixed `individual`+`cumulative` rows. Decide: split into two endpoints, or filter to `'individual'` server-side and add a separate cumulative endpoint. Audit `frontend/src/features/advertiser-view/` for any sum/avg over the response before changing the contract. |
| 3 | **HIGH-batch perf + contract fixes** | One small focused branch each: H3 (tabs/__init__ re-export — 5 lines), H4 (frame_hourly cached loader), H5 (AdvertiserSummaryTable null-handling), H6 (per-section error/loading UI on advertiser detail page), H7 (bulk MI query for advertiser timeseries — eliminates N+1 connections), H8 (collapse duplicate full-table scans in advertiser detail/limitations), H9 (LIMIT bound parameter). Eyes-free except H5/H6. |
| 4 | **H2 — CI workflow** | `.github/workflows/` does not exist. Add one job: `uv sync --extra dev` → `pytest tests/` → `npm --prefix frontend test -- --run`. Mypy can be a parallel job that initially runs informationally (`continue-on-error: true`). Half-day. |
| 5 | **Floor item #3 — backend test-coverage gap audit + orphan removal** | Now the natural home for the review's H1 (delete `tests/conftest.py`, `tests/test_validators.py`, `src/utils/validators.py` — all orphan), M2 (`tests/unit/test_mobile_index_queries.py` is a one-line trivial test — extend to cover `get_campaign_mobile_index_sync` weighted mean/median), M9 (verify `tests/api/test_caching.py` patches the right reference), M10 (integration test conftest), and M12 (named coverage gaps in `src/api/services/` and `src/db/queries/`). |
| 6 | **Floor item #4 — mypy strict-mode pass** | `pyproject.toml` declares `disallow_untyped_defs = true`. Run `uv run mypy src/` and produce a mechanical fix list; commit annotation gaps in batches. Folds in M7 (`limit: int = None` should be `Optional[int]`, untyped route handlers, `_min_or_none`/`_max_or_none` helpers). |
| 7 | **`use_primary` UI cleanup** | OWN BRANCH OWN SESSION per user. ~100 sites in `src/ui/` thread the parameter through every loader; the `os.environ["USE_PRIMARY_DATABASE"]` toggle in `src/ui/components/campaign_browser/header.py:24-27` is a UI-visible radio button that doesn't switch anything in DuckDB-only mode. Removing this is behavioural — needs user awareness during the work. |
| 8 | **Shape-descriptor tuning (review §6 → floor #6)** | First-cut heuristic for the React Overview cards; **only useful once Phase 5 reach data has landed**. Confirm via `Claude/docs/pipeline-coordination.md` before starting. Needs user eyes-on for label validation. |
| 9 | **Visual fidelity review (floor #7)** | React advertiser views vs Pepsi/Talon Netlify designs. Needs user eyes-on. |

**Suggested first move:** Item #1 (C5 forensics). The whole question
is "what unit does the cache table store?" — one query answers it.
Once the answer is known the fix is trivial. After that, item #2
(C1 reach contract). After that, the H-batch in small commits.

## Pre-flight check before starting

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git status                                # confirm clean working tree
git log --oneline -3 origin/main          # confirm dd02243 is HEAD of main

# Start any new floor-item work on a fresh branch off main.

# Full backend + integration + unit suite (use this, not a sub-tree)
uv run pytest tests/ 2>&1 | tail -3                    # 209 tests, all green

# Frontend unit tests + build
npm --prefix frontend test -- --run 2>&1 | tail -5     # 8 tests, all green
npm --prefix frontend run build 2>&1 | tail -5         # 320 KB main + 4.6 MB lazy
```

If anything fails, stop and surface — do not start changes on a
stale or broken base.

## Execution environment

- Branch: start any new work on a fresh feature branch off `main`.
- `DUCKDB_PATH=/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- `.env`: see `.env.example`.
- `frontend/.env.development`: same values as previous prompt.
- `uv sync --extra dev` done; Route hooks installed. Note: post-sweep
  the dep tree is two packages lighter (`psycopg2-binary` and
  `asyncpg` removed).
- Node v22.22.1; `frontend/node_modules/` ~872 packages.
- System Chrome at `/opt/google/chrome/chrome` (Playwright uses
  `channel: 'chrome'`).
- **`startstream`/`stopstream` shell helpers** in `~/.zshrc` —
  start Streamlit on port 8504 in a separate terminal.
  - `startstream` — DuckDB only
  - `startstream demo` — `DEMO_MODE=true`
  - `startstream global` — `DEMO_MODE=true` + `DEMO_PROTECT_MEDIA_OWNER=Global`
  - `stopstream` — kill any process on port 8504

  (The `startstream local` keyword from the Postgres era is gone;
  docs/03 was updated to remove the row.)

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
- **Pre-flight uses `pytest tests/`, not a sub-tree.** A full sweep
  catches stale call sites that subset runs miss.
- **Verify Edits with `git diff` before staging** when you've done
  parallel Edits across multiple files. The 2026-05-03 sweep
  discovered an `Edit` call that reported success but didn't land
  in the working tree at commit time — root cause unknown.

## Architectural notes that propagate forward

- **`use_primary` is vestigial.** Until it's swept, every UI loader
  takes the kwarg as a cache-key differentiator. The
  `os.environ["USE_PRIMARY_DATABASE"]` toggle in the campaign-browser
  header doesn't switch anything in DuckDB-only mode. Don't introduce
  new code that relies on it.
- **Tab decomposition pattern** (floor #7 outcome) — for any future
  tab-file work, the package shape is: `__init__.py` (re-exports
  only), `_render.py` (orchestrator), section modules (one per
  markdown subheader / logical sub-view), shared helpers in named
  sibling modules. Where a section has two mutually-exclusive paths,
  use a thin dispatch module that calls one of two sibling helpers.
  See `src/ui/tabs/reach_grp/cumulative.py` and
  `src/ui/tabs/executive_summary/reach_build.py`.
- **`detailed_analysis` is NOT in `tabs/__init__.py`.** Floor item
  H3 will fix this. Until then `app.py` imports it via the package
  path directly.
- **Public surface preservation** — when decomposing modules into
  packages, always keep the package's `__all__`/re-exports identical
  to the previous module-level public surface so `app.py` and
  `tabs/__init__.py` need no edits.
- **`cache_campaign_reach_week` has two `reach_type` values** —
  `'individual'` (per-week) and `'cumulative'` (running total). Any
  new SQL must filter `reach_type = 'individual'` unless it explicitly
  wants the cumulative line. **Note:** the current
  `/api/campaigns/{id}/reach/weekly` endpoint returns BOTH unfiltered
  — review item C1 covers this.
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
- **`mv_campaign_browser` reach-derived columns are NULL until
  pipeline Phase 5.** Frontend treats them as nullable in
  `AdvertiserCardGrid.tsx` (gated) but NOT in
  `AdvertiserSummaryTable.tsx` (review H5 — open).
- **Postgres is fully gone.** No more `psycopg2`, `asyncpg`,
  `route_releases.py`, or `PostgreSQLConfig`. The remaining
  `psycopg2`-shaped comment in `src/db/queries/_dict_cursor.py` is
  intentional — the helper produces the same row shape as
  `psycopg2.extras.RealDictCursor` for code originally written
  against psycopg2.

## At the end of this session

Per the dated-session-prompt convention (memory:
`feedback_dated_session_prompts.md`):

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
