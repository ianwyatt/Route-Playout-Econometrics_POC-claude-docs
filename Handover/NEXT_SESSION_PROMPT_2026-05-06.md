# Session prompt — 2026-05-06

H1 is merged to `main` (`5e7cf04`). Floor item #6 (advertisers.py +
app.py decomposition) is closed across 4 commits on
`refactor/decompose-advertisers-app`, **pushed to `origin` but not
merged**. The user retains the merge decision per CLAUDE.md — wait for
explicit "merge".

## Read these in order before touching anything

1. `.claude/CLAUDE.md` — project rules. Public-repo policy section is
   load-bearing.
2. `Claude/Handover/2026-05-02_h1-merged-and-floor-item-6-decomposition.md`
   — most recent session: H1 merge to main, floor item #6 decomposed
   in three staged commits, Playwright smoke clean, `startstream`
   helper added to zshrc.
3. `Claude/Handover/2026-05-02_public-repo-policy-and-block-hook.md`
   — policy hardening + hook installation. The hook activates
   automatically in fresh sessions; live-fire confirmed in the most
   recent session.
4. `Claude/docs/pipeline-coordination.md` — Phase 5 ETA still
   ~2026-05-08. Reach columns in `mv_campaign_browser` populate then;
   React Overview metrics and the Streamlit Weekly Reach tab will
   start showing real values for many advertisers from that date.

## Branch state at session start

```
main                                  ← 5e7cf04 (H1 merged + pushed)
refactor/decompose-advertisers-app    ← 8c79621 (4 commits, pushed,
                                                 not merged)
```

The 4 commits on the refactor branch:

```
8c79621 refactor: extract analyze_campaign and brand-display helper into module
ff812c7 refactor: extract campaign header card to reusable component
38af9bf refactor: extract Streamlit cached loaders into src/ui/loaders.py
aebc357 refactor: decompose advertisers service into a package
```

Net effect: `src/api/services/advertisers.py` (379 lines) → 5-file
package (largest 184 lines). `src/ui/app.py` (635 lines) → 4 files
(largest 246 lines). All 133 backend tests green; 6-tab Streamlit
smoke clean (Playwright-driven).

## Outstanding work — pick one with the user

| # | Item | Notes |
|---|---|---|
| 2 | Shape-descriptor tuning | First-cut heuristic for the React Overview cards; revisit once Phase 5 reach data lands (~2026-05-08) and real shapes emerge — much higher signal then |
| 3 | Visual fidelity review | React advertiser views vs Pepsi/Talon Netlify designs |
| 4 | Pre-existing mobile_index test failures | Outside H1 scope; dormant since pre-merge — `uv run pytest tests/integration/test_mobile_index_integration.py` to reproduce |
| 7 | **Tab-file decomposition** | NEW. Pre-commit hook flagged tab files over 300 lines: `detailed_analysis.py` (1170), `executive_summary.py` (739), `overview.py` (647), `time_series.py` (591), `reach_grp.py` (576), `geographic.py` (491). Same shape as #6 — staged refactor branches, behaviour-preserving, tests green at each stage |

Other possibilities:

- **Merge `refactor/decompose-advertisers-app` to `main`** — wait for
  explicit user instruction. Standard merge flow per the previous
  prompt. `origin` only, no public push.
- **Wait for Phase 5** — if user wants to see what changes after the
  pipeline lands before doing more, several items are higher-signal
  post-Phase-5.

## Pre-flight check before starting

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git fetch origin
git status                                # confirm clean working tree
git log --oneline -3 origin/main          # confirm 5e7cf04 is HEAD of main

# If continuing on the refactor branch:
git checkout refactor/decompose-advertisers-app
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
  out `refactor/decompose-advertisers-app` if continuing pre-merge
  polish.
- `DUCKDB_PATH=/home/dev/data/route_poc_cache.duckdb` (87 GB,
  identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- `.env`: see `.env.example`. Same values as previous prompt.
- `frontend/.env.development`: same values as previous prompt.
- `uv sync --extra dev` done; Route hooks installed.
- Node v22.22.1; `frontend/node_modules/` ~872 packages.
- System Chrome at `/opt/google/chrome/chrome` (Playwright uses
  `channel: 'chrome'`).
- **`startstream`/`stopstream` shell helpers** now in `~/.zshrc` —
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
  decomposition, prefer a package directory + re-export `__init__.py`
  to keep the public import surface stable. Tabs in `src/ui/tabs/`
  use inline `from src.ui.app import ...` inside render functions; if
  doing tab decomposition, the same pattern applies (move helpers to
  a sibling module + update inline imports).

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
