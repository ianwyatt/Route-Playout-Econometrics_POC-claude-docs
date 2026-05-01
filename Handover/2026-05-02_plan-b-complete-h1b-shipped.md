# Handover — Plan B complete, H1B ship signal

**Date:** 2026-05-02
**Branch:** `feature/duckdb-migration` (pushed to `origin`, HEAD `3a0ffb1`)
**Status:** Plan B done. FastAPI layer over DuckDB is feature-complete. Plan C (React advertiser views) can begin.

---

## What shipped

All Plan B done-criteria from `Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md`:

- All campaign routes (summary, browser, header, demographics, platform stats) PASS
- All impacts routes (daily/hourly/regional/environment) PASS
- All reach routes (weekly/cumulative-daily/full) PASS
- Geographic frames endpoint PASS
- All MI routes PASS
- Frame-audience routes PASS
- All advertiser routes (list, detail, campaigns, daily/weekly timeseries, data-limitations) PASS
- Integration smoke test PASS
- FastAPI runnable via `startapi` alongside Streamlit (helper documented in `Claude/docs/dev-shell-functions.md`)
- CORS allows `localhost:5173`
- Cache hit on second request to a heavy endpoint is faster (60× on `/api/advertisers`: 3.2s cold → 55ms warm)

127/127 db+api tests green.

## Commits made this session (all on `origin/feature/duckdb-migration`)

| SHA | Message | Plan task |
|---|---|---|
| `fbda2a4` | `chore: add fastapi and related deps` | Task 0 |
| `68d2cd4` | `feat: FastAPI skeleton with health endpoint` | Task 1 |
| `c61979b` | `feat: DB and current-user dependencies` | Task 2 |
| `d6a5d7b` | `feat: CORS middleware and structured 500 handler` | Task 3 |
| `a814800` | `feat: campaign summary endpoint with 404 handling` | Task 4 |
| `635b0af` | `feat: campaign browser, header, demographics, platform stats endpoints` | Task 5 |
| `6aee05a` | `feat: impacts endpoints (daily/hourly/regional/environment)` | Task 6 |
| `2983e1b` | `feat: reach endpoints (weekly/cumulative-daily/full)` | Task 7 |
| `0175de5` | `feat: geographic frames and demographics count endpoints` | Tasks 8, 9 |
| `f7fbca7` | `feat: frame-audience endpoints (daily/hourly/weekly/table/counts)` | Task 10 |
| `6da1509` | `feat: mobile-index endpoints (coverage/campaign + daily/hourly/weekly + frame variants + exists)` | Task 11 |
| `b7dfe83` | `feat: in-memory caching with fastapi-cache2` | Task 12 |
| `ac71da0` | `feat: campaign shape descriptor heuristic` | Task 13 |
| `d71c6f8` | `feat: advertiser grouping service (slugify + list/detail)` | Task 14 |
| `6266bd2` | `feat: advertisers list/detail/campaigns endpoints` | Task 15 |
| `9e6a284` | `feat: advertiser timeseries (daily/weekly) + data-limitations panel` | Tasks 16, 17, 18 |
| `a7aff8f` | `test: end-to-end API surface smoke` | Task 19 |
| `3a0ffb1` | `docs: API_PORT and ALLOWED_ORIGINS env vars` | Task 20 |

18 commits. Tasks 5–11 (mechanical endpoint wiring) were delegated to subagents, sequentially because every domain-router task touches a shared `src/api/main.py` for router registration. Each subagent's diff was reviewed before commit. Tasks 4, 12–18 were direct (pattern-setting / domain judgement) per the orchestration plan agreed mid-session.

## Endpoint surface (33 routes)

| Domain | Routes | Schema models |
|---|---|---|
| Health | `/api/health` | none |
| Platform | `/api/platform/stats` | `PlatformStats` |
| Demographics | `/api/demographics/count` | `DemographicCount` |
| Mobile-index meta | `/api/mobile-index/exists` | `MobileIndexTableExists` |
| Campaigns | `/api/campaigns`, `/browser-summary`, `/{id}/{summary,header,demographics}` | `CampaignBrowserRow` (29 cols), `CampaignBrowserSummary` (24 cols), `CampaignSummary`, `CampaignHeader` |
| Impacts | `/api/campaigns/{id}/impacts/{daily,hourly,regional,environment}` | `DailyImpact`, `HourlyImpact`, `RegionalImpact`, `EnvironmentImpact` |
| Reach | `/api/campaigns/{id}/reach/{weekly,cumulative-daily,full}` | `WeeklyReach`, `CumulativeDailyReach`, `FullCampaignReach` |
| Geographic | `/api/campaigns/{id}/geographic/frames` | `FrameLocation` |
| Frame-audience | `/api/campaigns/{id}/frame-audience/{daily,hourly,weekly,table,counts}` | `FrameAudience{Daily,Hourly,Weekly,TableRow,Counts}` |
| Mobile-index | `/api/campaigns/{id}/mobile-index/{coverage,campaign,daily,hourly,weekly,frame-totals,frame-daily,frame-hourly}` | nine `MobileIndex*` models |
| Advertisers | `/api/advertisers`, `/{slug}`, `/{slug}/campaigns`, `/{slug}/timeseries/{daily,weekly}`, `/{slug}/data-limitations` | `Advertiser{Summary,Detail,Campaign,DailyPoint,WeeklyPoint,DataLimitations}` |

29 of 30 read endpoints are decorated with `@cache(...)`; only `/api/health` is intentionally uncached. TTLs by domain: 300s (campaign list / summary / header / demographics, platform stats), 600s (impacts / reach / geographic / frame-audience / advertiser), 3600s (all mobile-index).

## Deviations from Plan B as written

### Schemas mirror actual SQL output, not plan sketches

The plan's `CampaignSummary` schema was wrong (the plan author conflated `get_campaign_summary_sync` with `get_campaign_from_browser_by_id_sync`), and many other endpoint sketches were approximate. Each task therefore read the underlying `src/db/queries/*.py` source to learn actual return shapes before writing the Pydantic model. Several specific corrections:

- `CampaignSummary`: dropped `primary_brand` / `primary_media_owner` / `total_impacts`; added `avg_spot_length` / `avg_spots_per_window`. `campaign_id` is injected by the route handler from the path param because the SQL doesn't return it.
- 404 detection on summary uses `total_frames == 0` because `COUNT()` aggregates over zero rows return 0, not NULL — a `result is None` check would never trigger.
- `route_release_id` is `Optional[int]` not `Optional[str]` — DuckDB returns it as a bare int. Caught by Pydantic v2 `ResponseValidationError` on Task 7's first run.
- `route_release` (the VARCHAR variant on frame-audience tables, e.g. "R55") is a different column from `route_release_id` (bare int 55). Both conventions coexist in the data — see `Claude/docs/pipeline-coordination.md` "route_release_id has two conventions".
- `frameid` is `int` not `str` — the React side (Plan C) may need to assume ints.
- `MobileIndexCoverage` and `MobileIndexCampaign` always return objects with zero defaults rather than `Optional[Dict]`; the underlying functions return tuples (e.g. `(0, 0)`), never `None`.
- Frame-audience `weekly` query has additional ISO-week columns (`iso_year`, `iso_week`, `week_start`, `week_end`, `days_in_week`) that none of the daily/hourly queries select.

### Pydantic v2 field-name shadowing

A field named `date` whose type is also `date` (imported from `datetime`) is silently resolved by Pydantic v2 as a `None`-only annotation — the field name shadows the type within the class body. Symptom: `ResponseValidationError: Input should be None`. Worked around in every schema with a `date` column by importing `from datetime import date as date_type` and annotating fields as `Optional[date_type]`. Documented in the relevant schema docstrings.

### `BACKEND` env var no longer exists

The plan's Task 2 conftest set `BACKEND=duckdb` for the test session. Per the 2026-05-02 scope decision (see pipeline-coordination doc), Postgres has been removed entirely — no `BACKEND` env var lives anywhere in the codebase. That conftest line was dropped.

### Plan B Task 2 `test_db_dependency_returns_connection` placeholder skipped

The plan included a `pass`-only placeholder test deferred to Task 5. Skipped — no functional value, just noise. Real DB dep coverage comes via the integration smoke at Task 19.

### `routes/platform.py` as a separate small router

Plan Task 5 said `GET /api/platform/stats` could go either as a top-level main.py route or in its own router. I created `src/api/routes/platform.py` with its own `prefix="/api/platform"` router so the campaigns router stays scoped to `/api/campaigns`. Future platform-tile endpoints can land in the same module.

### `mobile_index.py` has two routers in one file

The 8 campaign-scoped MI endpoints share `prefix="/api/campaigns"`; the meta `/api/mobile-index/exists` needs a different prefix. Both `router` and `meta_router` live in `src/api/routes/mobile_index.py`; both registered in `main.py`. Tag `mobile-index` is shared so OpenAPI groups them together.

### fastapi-cache2 key_builder gotcha

First cut of the cache key builder used `*args, **kwargs` to capture the route function's parameters. Worked for path params but query params didn't differentiate keys — the same daily endpoint with different `demographic` query strings hit the same cache. Cause: fastapi-cache2 passes the route's args/kwargs as nested keyword arguments named `args=...` and `kwargs=...` on the builder, NOT as `*args/**kwargs`. The fix reads from those nested keys explicitly. Caught by a dedicated `tests/api/test_caching.py::test_different_query_params_bypass_cache` test.

### Advertiser brand-transition iso_week is approximate

Plan Task 17 calls for ISO-calendar-week labels per row. The underlying `get_weekly_reach_data_sync` returns `week_number` (campaign-relative 1/2/3...) and a `start_date`. The route falls back to `week_number` when `iso_week` isn't on the row, so React gets the campaign-week number rather than the calendar ISO week. Mitigation: React should prefer `week_label` (the start-date string) for calendar-week display until a proper ISO-week column lands upstream.

### `_aggregate_weekly_impacts` is N-queries-per-advertiser

For each advertiser, `_aggregate_weekly_impacts` iterates campaigns and calls `get_weekly_reach_data_sync` once per campaign (Lidl: 42 calls). The route-level cache (300s) amortises this; cold first hit on `/api/advertisers` is 3.2s on the live DB, warm hits are 55ms. Future optimisation: a single SQL query over all campaign IDs grouped by week.

### Reference source not on this LXC

Plan Task 13 references `pepsi_netlify/_build_pages.py` for the canonical shape descriptor heuristic. That file only exists on the Mac, not the LXC. The plan provides a usable starter heuristic in code; I used it but reordered "Steady ramp-up" before "Late surge" so monotonic ramps aren't misclassified (caught by `test_steady_ramp_up`). Thresholds will need a tuning pass once stakeholders see the React overview.

## Things still on the floor

### Modularity warning

Pre-commit modularity checker flagged `src/api/services/advertisers.py` at 336 lines. Within tolerance, commit allowed. Natural decomposition would split it into `services/advertisers/{__init__,grouping,timeseries,limitations}.py` once one of the modules grows further.

### Pre-existing test failures outside Plan B scope

`tests/unit/test_import_mobile_index.py` and `tests/unit/test_mobile_index_queries.py` have 2 failing tests; `tests/integration/test_mobile_index_integration.py` has a collection error. These were pre-existing at the start of Plan B (not caused by this session's work). Out of Plan B scope; would be worth a dedicated cleanup task before Plan C if anyone cares about a fully-green `pytest tests/`.

### `Depends(get_db)` dead-injection on every route

Every route declares `conn=Depends(get_db)` for forward consistency, but no route actually uses the injected connection — every underlying `get_*_sync` function manages its own connection. Cost is one extra DuckDB connection open/close per request (~1ms on memory-mapped reads). Could be removed for a small perf win OR refactored to push `conn` down into `get_*_sync` for true single-connection-per-request. Not blocking.

### `CurrentUser` stub is forward-architecture

`get_current_user` returns a hard-coded anonymous user. H3 will swap in real JWT validation; route signatures don't change. Not relevant for H1.

### Lidl detail shows "Lindt" as a sub-brand on live DB

Worth flagging as a data quirk: a campaign primary-tagged "Lidl" with a "Lindt" secondary brand. The advertiser detail endpoint surfaces this in `sub_brands`. Either the data is correct (genuine Lidl/Lindt collab) or there's an upstream tagging error. Investigate during Plan C QA.

## Environment / fixture state at end of session

- `DUCKDB_PATH=/home/dev/data/route_poc_cache.duckdb` (87 GB, MD5 unchanged from session start, identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`)
- `tests/fixtures/route_poc_test.duckdb` unchanged (1.9 GB, gitignored)
- 127/127 db+api tests, all green
- New runtime deps: `fastapi`, `uvicorn[standard]`, `fastapi-cache2`, `httpx` (Task 0)
- `Chrome installed for Playwright` from prior session — still around, harmless
- `startapi` / `stopapi` zsh helpers documented in `Claude/docs/dev-shell-functions.md`; user adds them to their own `~/.zshrc` (not committed)

## Next session

Plan C — React advertiser views. Spec at `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md`. The sister prompt is `Claude/Handover/NEXT_SESSION_PROMPT_2026-05-03.md`.
