# Code review of `main` — 2026-05-08

Review of `Route-Playout-Econometrics_POC` at `89ed99e` (head of
`main`). Four parallel reviewers covered (1) backend FastAPI + DuckDB
query layer, (2) Streamlit UI, (3) React frontend, (4) tests +
dependencies + repo hygiene. The most consequential CRITICAL claims
were spot-verified against the source before being promoted into this
synthesis — items marked **VERIFIED** were checked directly; items
marked **UNVERIFIED** repeat the reviewer's claim and need a quick
check before fix work begins.

This document is the deliverable for floor item #1. **No code changes
have been made.** Section 6 proposes a prioritised fix sequence; wait
for user approval before executing.

---

## 1. CRITICAL — fix before next merge

### C1. `/api/campaigns/{id}/reach/weekly` returns mixed individual+cumulative rows (double-counting trap) — VERIFIED

`src/db/queries/reach.py:9-42` — `get_weekly_reach_data_sync` queries
`cache_campaign_reach_week` with **no `reach_type` filter**. The
sibling function `get_weekly_reach_for_campaigns_sync` at line 89-91
correctly filters `reach_type = 'individual'`, but `get_weekly_reach_data_sync`
returns both `individual` and `cumulative` rows in one list.

`src/api/routes/reach.py:31-40` (`/{campaign_id}/reach/weekly`) calls
this unfiltered function and passes the rows straight through. The
`WeeklyReach` schema has `reach_type: Optional[str]`, so a client that
ignores the field and sums `total_impacts` across the response will
roughly double-count — `cumulative` rows are a running total, not an
additional week.

**Fix options:**
- Split into `/reach/weekly/individual` and `/reach/weekly/cumulative`
  endpoints (cleanest contract).
- OR keep one endpoint but make `reach_type` the primary key in the
  response and document the contract explicitly.
- OR filter to `'individual'` server-side and add a separate cumulative
  endpoint for the React build.

Audit React consumers (`features/advertiser-view/`) for any sum/avg over
the weekly response before the fix lands.

### C2. `scripts/import_mobile_index.py` hard-fails on call: passes `use_primary=` to a no-arg function — VERIFIED

`scripts/import_mobile_index.py:413,463` calls
`get_db_connection(use_primary=use_primary)` but the current signature
at `src/db/queries/connection.py:13` is `def get_db_connection() -> Any:`
(no parameters). Both `import_to_database` and `build_cache` will raise
`TypeError` on first call. The script also imports `psycopg2` directly
(line 10) and uses `execute_values` — entirely Postgres-era code paths
left over from before the DuckDB swap.

`parse_mobile_index_csv` in the same file is the one piece still in use
(tested at `tests/unit/test_import_mobile_index.py`).

**Fix:** Either retire the broken halves of this script (it has no live
use today), or split it: keep `parse_mobile_index_csv` as a parser
module, archive the `import_to_database` / `build_cache` Postgres ops
code with a clear "Postgres-only — do not run against DuckDB" header.

### C3. `src/db/route_releases.py` is dead Postgres infrastructure that runs at import time — VERIFIED

`src/db/route_releases.py:11` imports `asyncpg`. Line 515 instantiates
the global `route_release_db = RouteReleaseDatabase()` at module
import. The class delegates to `DatabaseConfig` from `src/config.py`
whose `__post_init__` raises `ValueError` if `POSTGRES_HOST_PRIMARY` is
absent. No file in `src/api/`, `src/db/queries/`, or `src/ui/` imports
this module — it's strictly dead — but its existence keeps `asyncpg`
on the dependency tree (see C4) and means any wildcard import or lazy
test discovery would crash on a Postgres-less machine.

**Fix:** Move to `Claude/Archive/legacy-postgres/route_releases.py`
and remove from `src/db/`. Nothing in the live system imports it.

### C4. `pyproject.toml` declares `psycopg2-binary` and `asyncpg` as runtime deps despite Postgres being removed — VERIFIED

`pyproject.toml:8-9` keeps both Postgres clients as runtime
dependencies. The only consumers in `src/` are `src/db/route_releases.py`
(C3 — dead) and `src/config.py`'s `PostgreSQLConfig` (also dead post-DuckDB
swap). `scripts/import_mobile_index.py` is the one live(-ish) consumer
and is itself broken (C2). On ARM CI runners or minimal containers
these wheels can fail to install at all.

**Fix:** After C2/C3 land, drop both from `[project.dependencies]`.
If `scripts/import_mobile_index.py`'s ops half is retained for any
reason, move them to `[project.optional-dependencies] postgres`.

### C5. UI Mobile-Indexed Impacts metric: Overview multiplies ×1000, Geographic does not — at least one panel is wrong — VERIFIED

Both panels read from the same loader `load_mi_frame_totals`
(`src/ui/loaders.py:152`) which returns `indexed_impacts` and
`median_indexed_impacts` per frame.

- `src/ui/tabs/overview/precomputed.py:95-97` multiplies the sum by
  `1000.0` for the Overview metric card.
- `src/ui/tabs/geographic/_render.py:117-118` uses the raw value as a
  per-frame total and falls back to `total_impacts` (no scale change),
  so the Geographic "Mobile Mean / Median" totals stay on the raw
  scale.
- `src/ui/campaign_analyzer.py:77,81,88` also multiplies by 1000 in
  the legacy path.

Only one of the two scale conventions is correct. Decide which (likely
governed by what the cache table actually stores), then make all three
sites consistent.

**Fix:** Inspect the underlying `cache_mi_frame_totals` rows directly
to determine the unit, then standardise. This is a number shown to
econometricians — wrong scale is the worst failure mode.

### C6. `src/ui/app.py` ABOUTME and module docstring still claim PostgreSQL — VERIFIED

Line 2 says `# ABOUTME: Cache-first campaign analysis UI — all data
served from PostgreSQL`. The module docstring repeats it. Future
sessions and any newcomer reading this file will believe Postgres is
still the backend.

**Fix:** One-line update; trivial.

---

## 2. HIGH — silent failure modes, perf traps, schema gaps

### H1. `tests/conftest.py` and `tests/test_validators.py` are orphan Postgres-era files inflating green-test count — VERIFIED

`tests/conftest.py` defines four fixtures (`test_config`,
`sample_campaign_data`, `sample_playout_data`, `mock_api_response`) —
none are referenced by any test. Verified by grep across `tests/`.
`test_config` even sets `'mock_mode': True`, which the project rules
explicitly forbid. `tests/test_validators.py` exercises
`src/utils/validators.py`, which is not imported anywhere live (DuckDB
swap removed the consumer).

**Fix:** Delete `tests/test_validators.py`, `tests/conftest.py`, and
the dead `src/utils/validators.py`. Suite drops below 212; that's the
correct number.

### H2. No CI configured — VERIFIED

No `.github/workflows/` directory exists. Tests, mypy, frontend
vitest, and frontend build only run when a developer remembers. The
2026-05-03 floor-item #4 mobile-index test fixes were caught by a
manual audit, not by CI bisecting back to the breaking commit.

**Fix:** Add a minimal GitHub Actions workflow: `uv sync --extra dev`,
`uv run pytest tests/`, and `npm --prefix frontend test -- --run`.
Mypy can be a separate job that initially runs informationally
(`continue-on-error: true`) until the strict-mode pass (floor item #4)
lands.

### H3. `src/ui/tabs/__init__.py` does not re-export `render_detailed_analysis_tab` — VERIFIED

`src/ui/tabs/__init__.py` exports five render functions; the sixth
tab is imported separately in `src/ui/app.py:27` via
`from src.ui.tabs.detailed_analysis import render_detailed_analysis_tab`.
The CLAUDE.md explicitly calls out preserving `__all__` after
package decomposition.

**Fix:** Add the import and `__all__` entry; collapse `app.py:27`
into the main tabs import block.

### H4. `frame_hourly` sub-tab calls `get_frame_hourly_with_mobile_index_sync` directly — un-cached, fires on every interaction — VERIFIED

`src/ui/tabs/detailed_analysis/frame_hourly.py:7,75` imports the raw
DB function and calls it inside the render path with no
`@st.cache_data` wrapper. Every other detailed-analysis sub-tab uses a
loader from `src/ui/tabs/detailed_analysis/loaders.py`. For large
campaigns this is a full DuckDB query per slider/checkbox change while
MI is enabled.

**Fix:** Add `_load_mi_frame_hourly` to `loaders.py` mirroring the
existing patterns; replace the direct call.

### H5. `frontend/AdvertiserSummaryTable.tsx` cells assume non-null `peak_week_impacts` / `mean_week_impacts` — wrong while pipeline Phase 5 pending — VERIFIED (per H1C plan + frontend reviewer)

`frontend/src/features/advertiser-view/AdvertiserSummaryTable.tsx:33,38`
calls `c.getValue<number>() / 1000` with no null guard. The `types.ts`
declaration types these as `number`, but `mv_campaign_browser` keeps
both columns NULL until pipeline Phase 5 (per CLAUDE.md). NULL coerces
to `0` here so users see `0k`, not an em-dash. The card grid
(`AdvertiserCardGrid.tsx:19`) already has the gate; the table doesn't.

**Fix:** Loosen `types.ts` to `number | null`, switch cell renderers
to `?? null`, render `'—'` matching `CampaignList.tsx:38-40`.

### H6. Advertiser detail page: silent empty sections when secondary queries error — UNVERIFIED (frontend reviewer)

`frontend/src/routes/advertisers/$slug.tsx:36-39` uses
`{query.data && <Component />}` for `campaigns`, `daily`, `weekly`,
`limitations`. If any of those endpoints 500s, the page section just
disappears with no error UI.

**Fix:** Add per-section `isPending` skeletons and `error` fallbacks.

### H7. N+1 DuckDB connections in advertiser timeseries when `include_mi=True` — VERIFIED (backend reviewer)

`src/api/services/advertisers/timeseries.py:43-48` (daily) and
`116-125` (weekly) loop over campaigns and call the per-campaign
`*_with_mobile_index_sync` function inside the loop. Each call
opens a new DuckDB connection (each connection memory-maps the 87 GB
file). For a portfolio advertiser with 20+ campaigns this is 20+
connect/execute/close cycles per request.

**Fix:** Add a `get_*_with_mobile_index_for_campaigns_sync` bulk
query mirroring `get_weekly_reach_for_campaigns_sync` (the reference
shape per CLAUDE.md). Group results by `campaign_id` in the service
layer.

### H8. `get_advertiser_detail` and `get_advertiser_data_limitations` issue duplicate full-table scans — VERIFIED (backend reviewer)

`src/api/routes/advertisers.py:42,55,66` calls
`get_campaigns_from_browser_sync()` indirectly twice per cold request
(once via `get_advertiser`, once via `get_advertiser_campaigns`).
`src/api/services/advertisers/limitations.py:20-25` does the same.
fastapi-cache2 hides this in production but the cold path and any
test path pays it twice.

**Fix:** Pass the campaigns list through the call chain or unify the
lookup.

### H9. `get_frame_audience_table_sync` and friends use f-string `LIMIT {int(limit)}` — style violation, not injection — VERIFIED

`src/db/queries/frame_audience.py:29-30,110-111,193,336` interpolate
`int(limit)` into the SQL string. The `int()` cast neutralises
injection risk, but CLAUDE.md says "never string interpolation for
SQL". DuckDB supports `LIMIT ?` with a bound parameter.

**Fix:** Switch to bound parameter for consistency.

### H10. `frontend/.vite/` not in `.gitignore` — VERIFIED

Confirmed: `.gitignore:231-251` covers `frontend/node_modules/`,
`frontend/dist/`, `frontend/coverage/`, etc., but not `frontend/.vite/`.
Already showing up as untracked in `git status`.

**Fix:** Add `frontend/.vite/` to `.gitignore`. One-line.

### H11. `docs/README.md` and `docs/09/10/11-*.md` describe a Postgres architecture that no longer exists — UNVERIFIED in detail (tests reviewer)

The file references PostgreSQL tables and credentials docs and is
dated "4 February 2026" — pre-DuckDB-migration (which shipped
2026-05-01). Anyone reading `docs/README.md` will be misled.

**Fix:** Update the README to reflect DuckDB-only architecture; mark
the Postgres-specific files as archived or rewrite them.

---

## 3. MEDIUM — duplication, dead config, type-safety, drift

### M1. `src/config.py` retains a 200-line `PostgreSQLConfig`/`DatabaseConfig` tree with no live consumers
Once C3/C4 land, this becomes pure dead code. Defer until those are
done, then strip with care — currently `__all__` exports both.

### M2. `tests/unit/test_mobile_index_queries.py` is a one-line trivial test
Asserts `isinstance(mobile_index_table_exists(), bool)`. The actual
weighted-mean computation in `get_campaign_mobile_index_sync` (the
`SUM(indexed)/SUM(raw)` formula — a number shown to users) has no
unit-level test. Add focused unit tests using `duckdb.connect(":memory:")`
to seed a minimal `cache_mi_daily` and assert the computation.

### M3. Demographic-selector pattern duplicated across `time_series` and `geographic` tabs
~35 identical lines in each (load demographics → sort by
`DEMOGRAPHIC_SORT_ORDER` → build `demo_options` → render `selectbox`).
Promote to `src/ui/components/` per the modularity rule.

### M4. MI weekly-aggregation loop duplicated across `reach_grp/weekly_table.py`, `weekly_charts.py`, and `cumulative_daily.py`
60+ lines of the same per-week-bucket aggregation. Extract a shared
helper.

### M5. `DataLimitation` type declared in two places in the React app
`frontend/src/features/advertiser-view/types.ts:57-61` and
`frontend/src/components/ui/DataLimitationsPanel.tsx:7-11`.
Structural compatibility hides the divergence today; remove the
panel-local copy.

### M6. Hard-coded hex bypassing the design-token bridge
`AdvertiserSummaryTable.tsx:74` and `CampaignList.tsx:83` use
`hover:bg-[rgba(79,195,247,0.04)]` instead of an `accent-cyan` token.
`Header.tsx:19,22` and `Sidebar.tsx:22` use `bg-[#2d3348]` instead of
a token. Both will silently miss the next palette change.

### M7. Mypy strict violations across the API layer (sample, not exhaustive)
- `src/db/queries/frame_audience.py:12,96,177,319` — `limit: int = None`
  should be `Optional[int]`.
- Several route handlers in `src/api/routes/` lack explicit return
  type annotations (FastAPI infers them from `response_model` but
  mypy won't).
- `src/api/routes/advertisers.py:164-171` — `_min_or_none`,
  `_max_or_none` have no annotations.
- `src/api/main.py:31` — deliberate `Any` in `cache_key_builder`
  should be documented with a precise `# type: ignore` rather than
  implicit-Any leakage.

A full `uv run mypy src/` pass is floor item #4; M7 is the
expectation-setter.

### M8. `format_brands` in `src/utils/formatters.py` imports from `src.ui.config.anonymisation` — layering violation
`src/utils/formatters.py:144` puts a UI dependency inside a generic
utility module. Move the anonymisation call to the UI layer.

### M9. `tests/api/test_caching.py` may be patching the wrong reference
The route holds a captured reference to `get_daily_impacts_sync` from
import-time `from src.db.queries.impacts import …`, but the test
patches `routes_mod.get_daily_impacts_sync`. Whether this works
depends on fastapi-cache2's wrapper. UNVERIFIED — worth a 5-minute
check before claiming caching is covered.

### M10. `tests/integration/test_mobile_index_integration.py` calls `mobile_index_table_exists()` at module load time
Will probe whatever `DUCKDB_PATH` is set when collected. Works inside
the API test session (autouse fixture) but breaks if the integration
folder is run in isolation. Add a local `conftest.py` or move the
check inside a fixture.

### M11. `.env.example` parity drift
`FRONTEND_PORT` and `STREAMLIT_URL` are documented but never read in
`src/`. Conversely `src/config.py` reads several env vars
(`ROUTE_API_URL`, `SPACE_API_BASE_URL`, `DEBUG_MODE`,
`ROUTE_RELEASE_ID`, etc.) that aren't in `.env.example`. Reconcile.

### M12. Test coverage gaps (consequential paths only)
- `src/api/services/advertisers/timeseries.py::get_advertiser_weekly_timeseries`
  `include_mi=True` path and active-brand selection.
- `src/api/services/advertisers/_helpers.py::_aggregate_weekly_impacts`
  fallback branch (line 53).
- `src/db/queries/campaigns.py::get_campaign_summary_sync` —
  `total_frames=0` existence proxy.
- `src/db/queries/frame_audience.py` — `include_brand=True` paths
  (joining `mv_frame_brand_*`) untested.
- `src/db/queries/impacts.py` — fallback to raw
  `cache_route_impacts_15min_by_demo` never triggered (fixture always
  has `mv_*` data).
- `src/api/services/shape_descriptor.py` — `Mid-dip then surge` and
  `Volatile, large spike` branches untested (4/7 labels covered).
- `src/api/routes/advertisers.py` private helpers (`_min_or_none` etc.)
  — no edge-case tests.

### M13. PlotlyChart memory hygiene
`frontend/src/components/charts/PlotlyChart.tsx` — `react-plotly.js`
factory pattern; no explicit `Plotly.purge` cleanup `useEffect`. The
factory-resolved component should call purge on unmount, but the dual
CJS-interop shape at lines 13-18 makes this worth a belt-and-braces
explicit cleanup.

---

## 4. LOW — style, freshness, ergonomics

- `frontend/index.html:7` — `<title>` is the default Vite placeholder
  `frontend`; should be product copy.
- `frontend/index.html:2` — `lang="en"` could be `lang="en-GB"` to
  match British English copy.
- `frontend/package.json:28` — `shadcn` CLI tool is in
  `dependencies`; should be `devDependencies`.
- `src/db/route_releases.py:88-143` — log messages use emoji (`✅`
  etc.); project guidelines say no.
- `tabs/reach_grp/cumulative_weekly.py:37-38` and
  `cumulative_daily.py:80-81` — pointless multiply-by-1000
  immediately followed by divide-by-1000 (no-op in local scope).
- `tabs/executive_summary/data.py:15` — `use_primary: bool = None`
  type annotation should be `Optional[bool]` (also at multiple sites
  in `tabs/detailed_analysis/loaders.py`).
- `pyproject.toml` does not wire up `pytest-cov` despite it being a
  dev dep; no coverage threshold set.
- `docs/README.md:1` — title says "Pharos"; the rest of the project
  is "Route Playout Econometrics POC". Inconsistency for newcomers.

---

## 5. Cross-cutting observations

- **Postgres residue is the dominant theme of this review.** C2, C3,
  C4, C6, M1, M11, H11 are all "Postgres swap was operationally
  complete but didn't sweep the long tail". Floor item #2 in the
  next-session prompt is a "schema-drift sweep" — these findings
  largely belong to that work and should be folded into it rather
  than treated as separate.
- **`use_primary` and `index_value` schema-drift sweep** found one
  more live site beyond what 2026-05-03 caught: `scripts/import_mobile_index.py`
  (C2). Worth a final grep across `scripts/` and `Claude/` once C2 is
  resolved.
- **The decomposed tab packages are clean.** Floor #7 paid off — no
  inline `from src.ui.app import ...` survives. The remaining
  inline imports (`from src.ui.loaders import ...` inside `_render.py`)
  are not the prohibited pattern but are inconsistent across files.
  Low priority.
- **Bulk-by-IDs is the right pattern** and is already applied for
  reach. Extending it to impacts (H7) and adding it to MI (H4
  loaders) closes most of the perf surface.
- **Frontend is in the best shape of the four areas.** No
  CRITICALs; HIGHs are nullable-handling and per-section error UI,
  both small. The `verbatimModuleSyntax` discipline is intact, query
  keys are consistent, Plotly lazy-load boundary holds.

---

## 6. Proposed prioritised fix sequence

The next-session prompt lists items #1-#5 as eyes-free; #1 (this
review) is the input to #2-#5. Below is what to do with the findings.

**Fold into floor item #2 (schema-drift sweep):**
- C2 (import_mobile_index.py crash + Postgres halves)
- C3 (route_releases.py archival)
- C4 (drop psycopg2/asyncpg from pyproject.toml)
- C6 (app.py ABOUTME/docstring update)
- M1 (strip dead config classes — only after C3/C4)
- M11 (.env.example reconciliation)
- H11 (docs/README.md PostgreSQL→DuckDB rewrite)

**Standalone CRITICAL — needs its own focused branch:**
- C1 (reach_type filter / endpoint shape) — ~1 day; affects the API
  contract and may need React-side updates depending on how the
  weekly chart consumes it.
- C5 (Overview vs Geographic ×1000 scale) — first task is
  forensics: query the cache table to determine the canonical unit;
  fix is then trivial.

**Fold into floor item #3 (backend test-coverage gap audit):**
- H1 (orphan tests + validators.py removal)
- M2 (mobile_index unit tests)
- M9 (caching test patch correctness)
- M10 (integration test conftest)
- M12 (named coverage gaps)

**Fold into floor item #4 (mypy strict-mode pass):**
- M7 (annotation gaps)
- L (type-annotation lows)

**Standalone HIGH — small focused commits:**
- H2 (CI workflow) — half-day, unblocks future safety net.
- H3 (tabs/__init__.py re-export) — 5-line fix.
- H4 (frame_hourly cached loader) — small, perf-visible.
- H7 (advertiser timeseries N+1 + bulk MI query) — half-day.
- H8 (advertiser detail/limitations duplicate scans) — small.
- H9 (LIMIT parameter binding) — small.
- H10 (frontend/.vite/ to .gitignore) — one line.
- H5 (AdvertiserSummaryTable null handling) — small frontend fix.
- H6 (per-section error/loading UI on detail page) — small frontend
  fix.

**Defer to floor item #5 (docs drift) and lower:**
- All MEDIUM duplication (M3, M4, M5, M6) and ergonomic items.
- All LOW items.

**Suggested first sequence after sign-off:**

1. C5 forensics — determine the canonical unit. Cheap, blocks fix.
2. H10 + H3 + C6 + L (frontend `<title>`, `lang`, `shadcn`
   devDependencies move) as one tiny housekeeping PR.
3. C1 — split or document the `/reach/weekly` endpoint; audit React
   consumer.
4. C2 + C3 + C4 + M1 + M11 + H11 as the schema-drift-sweep PR
   (floor #2).
5. H2 — CI workflow.
6. C5 fix once the unit is known.
7. H4 + H5 + H6 + H7 + H8 + H9 as a small "perf and contract
   fixes" sequence.
8. Backend coverage (H1 + M2 + M9 + M10 + M12) as floor #3.
9. mypy strict (M7 + L) as floor #4.
10. Docs drift (H11 was already absorbed into #4 above; floor #5
    becomes a Claude/ docs sweep).

---

## 7. Status

This review is the deliverable. **No code has been changed.** Items
should be tackled in user-approved batches; the floor items
#2-#5 in the next-session prompt absorb most of the findings.

Reviewers: four parallel `feature-dev:code-reviewer` agents
(backend + DB, Streamlit UI, React frontend, tests + deps + hygiene).
CRITICAL claims spot-verified before promotion; HIGH/MEDIUM/LOW
claims accepted as-reported with the UNVERIFIED tag where the
reviewer's evidence wasn't directly checked.
