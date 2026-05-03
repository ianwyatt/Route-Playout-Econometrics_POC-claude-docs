# Session prompt — 2026-05-10

`main` is at `dd02243` (unchanged from 2026-05-09 prompt). Branch
`fix/geographic-data-scope-mismatch` exists locally with one commit
(`b89137b`) — review and decide whether to merge into main before
starting new work.

The previous session attempted review item C5, discovered the review's
framing was wrong, and pivoted to fix a different (real) bug class in
the Geographic tab. Bug 3 in that triad is pipeline-team work and a
handover doc has been prepared.

A pre-existing regression in **Daily Patterns** was spotted during
visual QA — demographic switch broken. NOT caused by this session's
work. Top priority for this session.

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules. Public-repo policy is
   load-bearing.
2. `Claude/Handover/2026-05-03_geographic-data-scope-fixes.md` —
   what shipped on the branch, the C5 misframing story, and the
   Daily Patterns finding.
3. `Claude/Plans/2026-05-03_geographic-overview-data-scope-forensics.md`
   — the three Geographic bugs, fix shapes, evidence. Mostly historical
   now (Bugs 1+2 fixed), but useful when looking at the merged shape.
4. `Claude/Handover/2026-05-03_pipeline-mv-cache-campaign-impacts-frame-stale.md`
   — Bug 3 handover for the pipeline team, not yet sent to them.
   Decide whether to forward this session.
5. `Claude/Plans/2026-05-08_main-code-review.md` — backlog source of
   truth. §C5 has a `2026-05-03 update` block noting the misframing.
6. `Claude/docs/pipeline-coordination.md` — confirms Phase 5 status
   (~ETA 2026-05-08 was the last word; check whether reach columns in
   `mv_campaign_browser` have started populating).

## Branch state at session start

```
main                                    ← dd02243
fix/geographic-data-scope-mismatch      ← b89137b (1 ahead, not pushed)
```

Recent commits on the branch:

```
b89137b  fix(geographic): dedupe route_frames join and label values as (000s)
dd02243  Merge branch 'chore/schema-drift-sweep'
```

## Re-ordered priority list

| # | Item | Notes |
|---|---|---|
| 1 | **Daily Patterns demographic switch** | NEW finding from 2026-05-03. On Detailed Analysis → Daily Patterns, switching the demographic doesn't update avg/weekly-avg metrics or the trends chart, but the Mobile Mean overlay does update. Bug is in the non-MI loader. Investigate `src/ui/tabs/detailed_analysis/frame_daily.py::_render_frame_daily_impacts` and the `_load_frame_daily_data` cached loader. Suspect: cache key omits demographic, or hard-coded demographic, or demographic param dropped on the way to SQL. |
| 2 | **Decide on `fix/geographic-data-scope-mismatch`** | Branch ready. One commit, tests green, visual confirmed against campaign 17498 (5/6 checks; #6 surfaced the unrelated finding above). Merge into main + push, or hold? Recommend merge — branch's scope is clean. |
| 3 | **Forward Bug 3 handover to pipeline team** | `Claude/Handover/2026-05-03_pipeline-mv-cache-campaign-impacts-frame-stale.md` is ready to be sent. Coordinate with Adwanted via the usual channel. |
| 4 | **C1 — `/reach/weekly` endpoint contract** | Original review CRITICAL. `get_weekly_reach_data_sync` returns mixed `individual` + `cumulative` rows. Decide: split into two endpoints, or filter to `'individual'` server-side. Audit `frontend/src/features/advertiser-view/` for any sum/avg over the response before changing the contract. |
| 5 | **HIGH-batch perf + contract fixes** | One small focused branch each: H3 (tabs/__init__ re-export, 5 lines), H4 (frame_hourly cached loader), H5 (AdvertiserSummaryTable null-handling), H6 (per-section error/loading UI on advertiser detail), H7 (bulk MI query for advertiser timeseries — eliminates N+1), H8 (collapse duplicate full-table scans), H9 (LIMIT bound parameter). Eyes-free except H5/H6. |
| 6 | **H2 — CI workflow** | `.github/workflows/` does not exist. Add one job: `uv sync --extra dev` → `pytest tests/` → `npm --prefix frontend test -- --run`. Mypy can be a parallel job initially with `continue-on-error: true`. Half-day. |
| 7 | **Floor item #3 — backend test-coverage gap audit + orphan removal** | Now the natural home for review's H1 (delete `tests/conftest.py`, `tests/test_validators.py`, `src/utils/validators.py` — all orphan), M2 (extend `tests/unit/test_mobile_index_queries.py`), M9 (verify `tests/api/test_caching.py` patches the right reference), M10 (integration-test conftest), M12 (named coverage gaps in `src/api/services/` and `src/db/queries/`). |
| 8 | **Floor item #4 — mypy strict-mode pass** | `pyproject.toml` declares `disallow_untyped_defs = true`. Run `uv run mypy src/` and produce a mechanical fix list; commit annotation gaps in batches. Folds in M7. |
| 9 | **`use_primary` UI cleanup** | OWN BRANCH OWN SESSION per user. ~100 sites in `src/ui/` thread the parameter; the `os.environ["USE_PRIMARY_DATABASE"]` toggle in `campaign_browser/header.py:24-27` is a UI-visible radio button that doesn't switch anything in DuckDB-only mode. Behavioural — needs user awareness during the work. |
| 10 | **Shape-descriptor tuning** | First-cut heuristic for the React Overview cards; only useful once Phase 5 reach data has landed. Confirm via `Claude/docs/pipeline-coordination.md` before starting. |
| 11 | **Visual fidelity review** | React advertiser views vs Pepsi/Talon Netlify designs. Needs user eyes-on. |

**Suggested first move:** Item #1 (Daily Patterns demographic switch).
Cheap to investigate, user-visible, blocks anyone else hitting the same
bug. After that, item #2 (merge decision on the Geographic branch).

## Pre-flight check before starting

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git status                                # confirm clean working tree
git log --oneline -3 main                 # confirm dd02243 is HEAD of main
git log --oneline fix/geographic-data-scope-mismatch ^main  # b89137b should appear

# Full backend + integration + unit suite
uv run pytest tests/ 2>&1 | tail -3                    # 209/209 expected

# Frontend unit tests + build
npm --prefix frontend test -- --run 2>&1 | tail -5     # 8/8 expected
npm --prefix frontend run build 2>&1 | tail -5         # ~320 KB main + 4.6 MB lazy
```

If anything fails, stop and surface — do not start changes on a stale
or broken base.

## Execution environment

- Branch: start any new work on a fresh feature branch off `main`.
  The Geographic branch is in flight (item #2 above) and is its own
  decision.
- `DUCKDB_PATH=/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- `.env`: see `.env.example`.
- `frontend/.env.development`: same as previous prompt.
- `uv sync --extra dev` done; Route hooks installed.
- Node v22.22.1; `frontend/node_modules/` ~872 packages.
- System Chrome at `/opt/google/chrome/chrome` (Playwright uses
  `channel: 'chrome'`).
- **`startstream` / `stopstream` shell helpers** in `~/.zshrc`:
  - `startstream` — DuckDB only
  - `startstream demo` — `DEMO_MODE=true`
  - `startstream global` — `DEMO_MODE=true` + `DEMO_PROTECT_MEDIA_OWNER=Global`
  - `stopstream` — kill process on port 8504

## Working constraints

- **Side-of-desk cadence per task.** Wait for "go" between tasks.
  Tight-loop commands chain within a task.
- **Commit autonomously when work is clean** on the active branch
  unless the user signals otherwise. NEVER use `--no-verify`.
- **NEVER merge without explicit user approval.**
- **Do NOT push anything to the `public` remote** — neither branches
  (blocked by pre-push hook) nor tags (policy). `origin` (private dev
  repo) only.
- **NEVER run Streamlit or the FastAPI service as a Claude Code
  background process** — exhausts the conversation token budget.
- **Bash cwd does not persist across tool calls.** Chain
  `cd /abs/path && cmd` in a single Bash call or use
  `npm --prefix frontend run X`.
- **Pre-flight uses `pytest tests/`, not a sub-tree.** A full sweep
  catches stale call sites that subset runs miss.
- **Visual confirmation is mandatory before claiming a Streamlit fix
  is correct.** The 2026-05-03 session twice landed code that tests
  passed and visual rejected — once when removing ×1000 (data unit
  misread), once would have been worse if the user hadn't caught it.

## Architectural notes that propagate forward

- **Route source audiences are in thousands.** `cache_route_impacts_15min_by_demo.impacts`,
  `mv_campaign_browser.total_impacts_all_adults`, MI cache table values
  — all in thousands. Display layer either ×1000 (Overview pattern) or
  labels "(000s)" (Executive Summary / Frame Audiences / now Geographic
  pattern). Both intentional. Empirical equality between MV and
  canonical does NOT establish the unit. Memory rule:
  `feedback_route_audiences_in_thousands.md`.
- **`route_release_id` has three conventions.** `route_frames.release_id`
  is FK to `route_releases.id`; `cache_route_impacts_15min_by_demo.route_release_id`
  is bare number; `mv_campaign_browser.route_release_id` is bare number.
  When joining `route_frames`, prefer `MAX(release_id)` per frameid
  unless the campaign-of-record release matters specifically — that
  sidesteps the conversion gymnastics.
- **JOIN duplication on `route_frames` is silent.** Frames appear once
  per Route release the catalogue lists them in (up to 4 in the current
  snapshot). Any new query joining `route_frames` should aggregate-then-join,
  not join-then-aggregate, OR pre-deduplicate via a CTE. The
  `latest_release` CTE in `src/db/queries/geographic.py` is the
  reference shape.
- **`use_primary` is vestigial.** Until swept, every UI loader takes
  the kwarg as a cache-key differentiator. Don't introduce new code
  that relies on it.
- **Tab decomposition pattern** — `__init__.py` (re-exports only),
  `_render.py` (orchestrator), section modules (one per logical
  sub-view), shared helpers in named sibling modules. See
  `src/ui/tabs/reach_grp/cumulative.py` and
  `src/ui/tabs/executive_summary/reach_build.py` for examples.
- **`detailed_analysis` is NOT in `tabs/__init__.py`** (review item H3
  open). `app.py` imports it via the package path directly.
- **Bulk-by-IDs query pattern**: `get_weekly_reach_for_campaigns_sync`
  is the reference shape for new bulk queries — empty-list short-circuit,
  generated `?,?,?` placeholders, return `campaign_id` for downstream
  group/attribute.
- **Connection cost dominates for many small queries**: each
  `get_db_connection()` memory-maps the 87 GB file. Batch into one
  bulk query rather than caching connections.
- **`cache_campaign_reach_week` has two `reach_type` values** —
  `'individual'` and `'cumulative'`. Any new SQL must filter
  `reach_type = 'individual'` unless it explicitly wants cumulative.
  Note: the current `/api/campaigns/{id}/reach/weekly` endpoint returns
  BOTH unfiltered — review item C1 (priority #4 here).
- **`mv_campaign_browser` reach-derived columns are NULL until pipeline
  Phase 5.** Frontend treats them as nullable in `AdvertiserCardGrid.tsx`
  (gated) but NOT in `AdvertiserSummaryTable.tsx` (review H5 — open).
- **`mv_cache_campaign_impacts_frame` is stale (~2025-10-13 cap).**
  Pipeline-team work — handover doc ready at
  `Claude/Handover/2026-05-03_pipeline-mv-cache-campaign-impacts-frame-stale.md`.
  Until refreshed, Geographic's per-frame totals are ~30% under canonical.

## At the end of this session

Per the dated-session-prompt convention (memory: `feedback_dated_session_prompts.md`):

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
