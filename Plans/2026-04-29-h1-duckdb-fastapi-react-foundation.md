# H1 — DuckDB Migration, FastAPI Layer, Single-Advertiser React View

**Status:** Design approved · ready for implementation planning
**Date:** 2026-04-29
**Horizon:** H1 (foundations + first new feature)
**Cadence:** Side of desk; ship-able milestones

## Context and Scope

The Route Playout Econometrics POC currently runs as a Streamlit app over PostgreSQL with a 69-day playout slice. Three forward directions have been agreed:

1. **Full 2025 dataset** — drives the DuckDB move (PostgreSQL becomes unwieldy at full scale)
2. **DuckDB backend (committed)** — replacing PostgreSQL for the read-only query layer
3. **React frontend** — to deliver UI polish needed for stakeholder buy-in and engagement

The work has been decomposed into four horizons. **This spec covers H1 only.**

| Horizon | Scope |
|---|---|
| **H1: Foundations + first new feature** | DuckDB app migration, full 2025 validation, FastAPI layer, single-advertiser React view |
| H2: Tab port + chart-overlay features | Remaining tabs ported to React, calendar/holiday markers, weather overlay, MI auto-annotation, frequency distribution, day×hour heatmap, demographic profile shift, plan vs delivered, geographic exploration mode |
| H3: Multi-user | Auth, user storage, saved campaigns, user-added annotations, saved views/URLs |
| H4: Custom audiences | Per-user audience definitions, batch/cached delivery vs plan, async job infrastructure |

H1 establishes the patterns (DuckDB connection model, FastAPI contract, React design system) that H2 will mechanically apply across remaining tabs.

## Repository Strategy

All H1 work happens on a feature branch (`feature/duckdb-migration`). The Streamlit app on `main` continues running against PostgreSQL throughout H1 and is unaffected. Adwanted's reference (the public repo) sees no H1 work.

## Architecture

End-state for the H1 feature branch:

```
┌─────────────────────────────────────────────────────────┐
│ feature branch — local dev                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Existing Streamlit app  ──reads──>  DuckDB file        │
│   (port 8504)                       (single .duckdb     │
│                                      file in H1;        │
│                                      partitioning       │
│                                      considered in H2)  │
│                                          ▲              │
│                                          │              │
│                                          │ reads        │
│                                          │              │
│  FastAPI service ────────────────────────┘              │
│   (port 8000)                                           │
│        ▲                                                │
│        │ HTTP/JSON                                      │
│        │                                                │
│  React + Vite app                                       │
│   (port 5173)                                           │
│   - shell with routing (React Router)                   │
│   - advertiser overview + single-advertiser detail      │
│   - placeholder shell for H2 tabs                       │
└─────────────────────────────────────────────────────────┘
```

**Key architectural properties:**

- Streamlit and FastAPI share the same DuckDB file (DuckDB allows multiple readers; the app is read-only so no locking issues).
- Query functions in `src/db/queries/*.py` are reused **directly** by FastAPI — no duplication. FastAPI endpoints are thin wrappers calling the existing `get_*_sync` functions.
- DuckDB file lives outside the repo (in `data/` or a configured path), referenced via `.env` (`DUCKDB_PATH`).
- Streamlit and FastAPI both run simultaneously on different ports, both pointed at the same DuckDB file.

**Repo layout additions:**

```
src/
├── db/
│   ├── queries/        # existing — minor dialect tweaks for DuckDB
│   └── connection.py   # gains DuckDB branch
├── api/                # NEW
│   ├── main.py         # FastAPI app
│   ├── deps.py         # connection dependency
│   ├── routes/         # one file per query domain
│   └── schemas/        # Pydantic response models
└── ui/                 # existing Streamlit, unchanged in H1

frontend/               # NEW — Vite project, separate package.json
├── src/
│   ├── routes/
│   ├── features/advertiser-view/
│   ├── components/
│   └── lib/api-client.ts
└── package.json
```

## DuckDB Migration

### Connection Model

- One read-only DuckDB connection **per process**, opened at startup, shared across all queries.
- Both Streamlit and FastAPI open their own connections (DuckDB allows multiple readers).
- No connection pooling needed — DuckDB connections are cheap and the workload is read-only.
- Path comes from `.env`: `DUCKDB_PATH=/path/to/route_poc.duckdb`.

### Backend Selection

`connection.py` becomes a backend selector:

- Existing `use_primary` parameter stays (env-driven).
- New `BACKEND=postgres|duckdb` env var picks the engine.
- During H1 dev: `BACKEND=duckdb`. `main` stays `BACKEND=postgres` until cut-over.
- Single function `get_db_connection()` returns the right connection type; downstream code is signature-compatible.

### Result Format

- Keep `List[Dict]` return shape — no signature changes in tabs/components.
- DuckDB's `cursor.fetchall()` returns tuples; wrap with column names from `cursor.description` (small helper, ~6 lines, in `connection.py`). Same shape as `RealDictCursor` produced.
- **Not** switching to DataFrames in H1 — too much surface area to change. Defer if useful later.

### Dialect Changes (Mechanical Sweep)

- `%s` → `?` parameter style across `src/db/queries/*.py`
- `::date` and other PostgreSQL casts → `CAST(... AS DATE)` (DuckDB also supports `::` but cleaner to use ANSI)
- `pg_*` functions — only used in admin scripts, not in app query path. Skip.
- Verify `EXTRACT()`, window functions, CTEs work as-is (DuckDB is very PG-compatible).

### Cache Build Scripts

- Out of scope for H1 app-side migration — covered by separate in-flight DuckDB data work.
- The app consumes whatever cache tables exist; we verify cache table names match.

### Fallback Pattern

The `mv_cache_campaign_impacts_day` → raw `cache_route_impacts_15min_by_demo` fallback in `impacts.py` survives unchanged — the SQL is dialect-agnostic.

### Risks

- Param-style sweep could miss an edge case (string literals containing `%s`, dynamic SQL building). **Mitigation:** parity test (see Testing) runs every `get_*_sync` against DuckDB and asserts shape.
- DuckDB type quirks (DECIMAL vs FLOAT, timestamp precision). **Mitigation:** existing `pd.to_numeric(..., errors='coerce')` calls in tabs already swallow these.

## FastAPI Layer

### Endpoint Shape

Pragmatic — mirror existing query functions, one route per `get_*_sync`:

```
GET /api/campaigns/{campaign_id}/summary
GET /api/campaigns/{campaign_id}/impacts/daily?demographic=all_adults
GET /api/campaigns/{campaign_id}/impacts/hourly?demographic=all_adults
GET /api/campaigns/{campaign_id}/reach/weekly
GET /api/campaigns/{campaign_id}/geographic/frames?demographic=all_adults
GET /api/campaigns/{campaign_id}/mobile-index/coverage
GET /api/campaigns/{campaign_id}/mobile-index/daily
... (one per query function, ~25–30 routes)

# H1 NEW routes (advertiser views):
GET /api/advertisers                          # list with counts
GET /api/advertisers/{slug}                   # advertiser metadata
GET /api/advertisers/{slug}/campaigns         # all campaigns for an advertiser
GET /api/advertisers/{slug}/timeseries/daily?demographic=&mi=
GET /api/advertisers/{slug}/timeseries/weekly?demographic=&mi=
GET /api/advertisers/{slug}/data-limitations  # structured caveats
```

This matches existing query functions 1:1, requires no semantic re-modelling, and keeps ceremony low. We can refactor toward a domain-driven contract later if there are external consumers.

### Module Layout

```
src/api/
├── main.py              # FastAPI app, middleware, CORS
├── deps.py              # connection dependency
├── routes/
│   ├── campaigns.py     # mirrors src/db/queries/campaigns.py
│   ├── impacts.py
│   ├── reach.py
│   ├── geographic.py
│   ├── mobile_index.py
│   ├── demographics.py
│   └── advertisers.py   # NEW for advertiser views
└── schemas/
    ├── campaign.py
    ├── impacts.py
    └── advertiser.py
```

### Schemas

One Pydantic model per response shape. Lean — fields match what existing queries return. Response validation only (not request-body validation, since everything is GET with path/query params).

### Caching

- Server-side: keep existing `@st.cache_data` for the Streamlit path. For FastAPI, add `fastapi-cache2` with in-memory backend, TTL matching the Streamlit cache (5–10 min for volatile, 60 min for MI overlays).
- Client-side: TanStack Query handles the React side.

### Auth

- **Out of H1 scope.** Localhost-only during H1.
- *Forward intent for H3:* the API is designed to accept JWT bearer tokens later. Routes use `current_user: User = Depends(get_current_user)` parameter that is a no-op stub in H1 returning a default user. H3 wires the real implementation; route signatures don't change.

### CORS

Permissive for `localhost:5173` only during H1. Configurable via env for any future deploy.

### Error Handling

- Single exception handler in `main.py` mapping `psycopg2.Error` / `duckdb.Error` → HTTP 500 with structured JSON `{error, detail}`.
- 404 when query returns empty for a `campaign_id` / advertiser slug that doesn't exist.
- No retry logic — DuckDB is local and deterministic.

### Deployment

- During H1: `uv run uvicorn src.api.main:app --reload --port 8000`. New shell function `startapi` alongside existing `startstream`.
- Both Streamlit and FastAPI runnable simultaneously, both reading the same DuckDB file.

## React App + Advertiser Views

### Stack

- Vite + React 18 + TypeScript
- React Router v6 (file-based routing convention, not a meta-framework)
- TanStack Query for server state
- shadcn/ui + Tailwind for components and styling
- Plotly.js for charts (preserves existing Plotly investment)
- MapLibre GL JS for maps (free, no Mapbox token; not used in H1 but stack pick)
- TanStack Table for data tables
- Zod for runtime validation of API responses

### Project Structure

```
frontend/
├── src/
│   ├── main.tsx                   # Vite entry, providers
│   ├── App.tsx                    # router shell
│   ├── routes/
│   │   ├── index.tsx              # advertiser overview
│   │   ├── advertisers/
│   │   │   ├── index.tsx          # advertiser list
│   │   │   └── $slug.tsx          # single-advertiser detail
│   │   └── campaigns/             # placeholder routes for H2
│   ├── features/
│   │   └── advertiser-view/       # the H1 feature
│   │       ├── AdvertiserHeader.tsx
│   │       ├── CampaignList.tsx
│   │       ├── DailyTimeseriesChart.tsx
│   │       ├── WeeklyTimeseriesChart.tsx
│   │       ├── DataLimitationsPanel.tsx
│   │       ├── MobileIndexToggle.tsx
│   │       └── hooks/
│   │           └── useAdvertiserData.ts
│   ├── components/
│   │   ├── ui/                    # shadcn primitives
│   │   ├── charts/                # Plotly wrappers reused across features
│   │   └── layout/                # AppShell, Sidebar, Header
│   └── lib/
│       ├── api-client.ts          # fetch wrapper, base URL from env
│       ├── query-client.ts        # TanStack Query config
│       └── format.ts              # number/date formatters
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### Design Baseline

Adopt the visual language proven in the existing Netlify advertiser-trends sites (`/Users/ianwyatt/PycharmProjects/route-playout-pipeline/scripts/temp_sensitive_files/pepsi_netlify`):

| Element | Specification |
|---|---|
| Background | `#1a1e2e` |
| Card background | `#22273a` |
| Nav background | `#171b28` |
| Borders | `#2d3348` |
| Cyan accent | `#4fc3f7` |
| Body text | `#c8cdd8` |
| Muted text | `#8891a5` |
| Heading text | `#e0e4ed` |
| Dim text (e.g. partial weeks) | `#5a6178` |
| MI toggle active border | `#ffb74d` (orange) |
| Brand colour palette (portfolio sub-brands) | cyan `#4fc3f7`, green `#81c784`, purple `#ba68c8` |
| Chart wrapper | 420px height, 24/28/16px padding |
| Typography | h1 22px/600, chart-title 15px/500, chart-subtitle 12px muted, body 12–13px |
| MI toggle | Right-aligned in nav, 📱 icon, orange border + tinted bg when active, localStorage-persisted |
| Partial-data styling | Greyed-out row (`#5a6178`) — surfaces data quality inline |
| Commentary block convention | Factual only, no opinion about strategy/scheduling |
| Week label format | `Wk 33 (Aug 11)` two-line in chart axes |
| Data source footer | Structured caveats (Route release IDs, demographic, units), `#171b28` block |

These are codified in M3 as Tailwind config + CSS variables + shadcn theme overrides + reusable chart components.

### H1 Pages

**`/` — Advertiser Overview**

- Top: summary table (advertiser, campaign count, weeks active, peak, mean, peak week, shape descriptor)
- Below: card grid, one per advertiser, with stats + shape blurb. Click → advertiser detail.
- This is the exec-facing landing page. Sets the tone.

**`/advertisers/:slug` — Single-Advertiser Detail**

- Header: brand name, period covered, campaign count, MI toggle, totals
- **Daily chart** (hero) — Plotly area+line with weekend shading, avg line, MI overlay
- **Weekly chart** — bar chart with shape colour-coding by active campaign (when multiple sub-brands present)
- **Campaign list table** (TanStack Table) — sortable, click row → deep-link back to existing Streamlit campaign detail page
- **Data Limitations panel** at bottom — automatically surfaced (brand attribution gaps, MI coverage, period boundaries)

**Sidebar nav** matching the Netlify nav style — top brands as quick links, "All advertisers" link to `/`.

### Brand Transition Colour Coding

When a portfolio has multiple sub-brands active across weeks, each week's bar is coloured by the active brand that week, with a small legend above. For advertisers with overlapping campaigns this becomes a campaign-overlap visualisation.

### Internal vs External Modes

The Pepsi pattern generates two versions (with/without MI). Maps to existing `DEMO_MODE` env var. Not H1 scope, but the API is designed to accept a `hide_mi` flag from the start so this is a future config flip, not a refactor.

### Data and Logic Reuse

Port the data-shape builders, brand-attribution logic, and shape-descriptor heuristics directly from `pepsi_netlify/_build_pages.py` rather than re-deriving. SQL patterns are proven.

### What's Out of H1 Scope

- Cross-advertiser comparison (overlay 2+ on the same chart) → H2
- Per-campaign demographic breakdown on advertiser pages → H2
- Saved views / URL state for filters → H3
- User-added annotations → H3

## Milestones

Side-of-desk friendly. Each milestone is ship-able, can sit for a week without rotting, and is demonstrable.

### M1: DuckDB swap in Streamlit *(2–3 sessions)*

- Add `BACKEND` env var to `connection.py`, wire DuckDB branch
- Param-style sweep across `src/db/queries/*.py` (`%s` → `?`)
- Helper to wrap `cursor.fetchall()` + `cursor.description` into `RealDictCursor`-style dicts
- Smoke test: every `get_*_sync` returns shape against the DuckDB file
- **Ship signal:** Streamlit app runs unchanged with `BACKEND=duckdb`, all tabs work

### M2: FastAPI scaffold + first batch of endpoints *(2 sessions)*

- `src/api/{main,deps,schemas,routes}` skeleton
- Connection dep injecting shared DuckDB read-only connection
- Implement campaign endpoints first (mirrors `src/db/queries/campaigns.py`)
- CORS for `localhost:5173`, exception handler, stub auth dep
- **Ship signal:** `curl localhost:8000/api/campaigns/18023/summary` returns valid JSON

### M3: React scaffold + design system *(2 sessions)*

- Vite + React + TS + Tailwind + shadcn init
- Tailwind config with dark-theme palette as CSS variables
- Layout primitives: `AppShell`, `Sidebar`, `Header`, `Card`, `MetricBlock`, `DataLimitationsPanel`
- Plotly wrapper component with weekend-shading + avg-line helpers
- Routing skeleton with placeholder pages
- **Ship signal:** dev server runs, navigation works, design language locked in

### M4: Advertiser endpoints *(1–2 sessions)*

- Implement `/api/advertisers`, `/api/advertisers/{slug}`, `/api/advertisers/{slug}/campaigns`, `/api/advertisers/{slug}/timeseries/{daily,weekly}`, `/api/advertisers/{slug}/data-limitations`
- Port shape-descriptor heuristics + data-limitations logic from `pepsi_netlify/_build_pages.py`
- Pydantic schemas for each
- **Ship signal:** all advertiser routes return valid JSON via curl

### M5: Advertiser overview page (`/`) *(2 sessions, optional cut point)*

- Summary table component (TanStack Table)
- Advertiser card grid
- Wire to `/api/advertisers`
- **Ship signal:** overview live, looks good

### M6: Single-advertiser detail page *(3 sessions)*

- Header with metrics + MI toggle (localStorage persistence)
- Daily chart with weekend shading, avg line, MI overlay
- Weekly chart with brand transition colour coding
- Campaign list table with deep-link back to Streamlit
- Data Limitations panel
- **Ship signal:** end-to-end advertiser detail view works, polished, demoable

### M7: Final QA + integration polish *(1 session)*

- Run Streamlit and React side-by-side, verify no port conflicts
- Verify DuckDB shared-reader works with both processes
- Add `startapi` shell function (alongside `startstream`)
- Update `.env.example`, README pointers
- **Ship signal:** clean handover to H2

**Total: ~13–15 sessions** at side-of-desk cadence.

**Critical path:** M1 unblocks everything. M2 and M3 can run in parallel after M1 lands. M4 needs M2; M5/M6 need M3 and M4.

**Cut point if H1 needs to slim:** drop M5 (overview page), go straight from M4 to M6. Single-advertiser detail alone is still a complete H1.

## Testing

### M1 — DuckDB swap

The highest-stakes test work. Write a parity test before changing any query module:

```python
@pytest.mark.parametrize("backend", ["postgres", "duckdb"])
@pytest.mark.parametrize("query_fn,fixture_args", QUERY_FIXTURES)
def test_query_returns_consistent_shape(backend, query_fn, fixture_args, monkeypatch):
    monkeypatch.setenv("BACKEND", backend)
    result = query_fn(**fixture_args)
    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)
        assert set(result[0].keys()) == EXPECTED_KEYS[query_fn]
```

`QUERY_FIXTURES` is one row per `get_*_sync` function. ~25 rows. Failing tests pinpoint exactly which dialect issue needs fixing.

**Value-equivalence check** (separate, slower test) — for representative queries, assert numeric values match between backends within tolerance. Run on demand, not in CI.

### M2 + M4 — FastAPI

`fastapi.testclient.TestClient` per route. For each endpoint:

- Happy path: known ID → 200 + valid Pydantic shape
- 404 path: unknown ID → 404 with structured error
- Bad query param: invalid demographic → 422

Pydantic `response_model` gives free schema validation. TDD: write the test, watch it 404, implement the route, watch it pass.

### M3 + M5 + M6 — React

| Layer | Tool | What we test |
|---|---|---|
| Pure utilities | Vitest | format helpers, date math, MI-toggle reducer, shape-descriptor port |
| Hooks | Vitest + Testing Library | `useAdvertiserData` — mocks fetch, asserts loading/error/data states |
| API client | MSW | `api-client.ts` produces expected requests; mocked responses parse cleanly |
| Components | Vitest + Testing Library | Smoke render only — assert key text, MI toggle changes state |
| E2E | Playwright | One happy-path: visit `/`, click Lidl card, see chart, toggle MI |

We don't visual-regression-test the chart pixels — too brittle. We assert chart data binding (data array passed to Plotly is correct shape), not visual output.

### Cross-Cutting Integration Smoke

One pytest test that:

1. Spins up FastAPI on a test DuckDB file
2. Hits `/api/advertisers/lidl/timeseries/daily`
3. Validates response against the Pydantic schema the React app uses

Catches DuckDB → FastAPI → contract drift in one go. Lives in `tests/integration/`.

### Test Data

- One small fixture DuckDB file in `tests/fixtures/route_poc_test.duckdb` — subset of full data, ~50MB, 5 advertisers, 20 campaigns. Generated by a committed script; the binary is gitignored.
- Tests set `DUCKDB_PATH` to point at the fixture. Production data never touched by CI.

### Out of Scope for H1 Testing

- Streamlit tabs E2E on DuckDB — covered indirectly by M1's parity test
- Visual regression on charts — defer to H2 once design is stable
- Formal performance benchmarks — defer to M1 validation step
- React components beyond smoke render — testing shadcn or Plotly internals is wasted

### CI Shape

GitHub Actions on the feature branch: `uv run pytest` + `cd frontend && npm test` on every push. No deployment. No Playwright in CI yet.

## Open Risks and Forward Intent

| Risk | Mitigation |
|---|---|
| Param-style sweep misses an edge case | Parity test on every `get_*_sync` |
| DuckDB type quirks surface in UI | Existing `pd.to_numeric` coercions catch most |
| Cache table schema diverges between in-flight DuckDB data work and app expectations | Add explicit cache-table schema check in M1 smoke test; verify column names match `cache_mi_*` queries |
| FastAPI + Streamlit DuckDB read contention | DuckDB supports concurrent readers; verified in M7 integration smoke |
| Frontend dir vs Python repo conventions clash | `frontend/` is gitignored in Python tooling configs; separate `package.json` keeps Node out of the Python build |
| Side-of-desk cadence stretches H1 indefinitely | Each milestone ships independently; M5 is documented cut point |

**Forward intent (not H1 work, but H1 must not paint into corners):**

- API auth via JWT bearer (H3) — `current_user` dependency stub in place from M2
- Cross-advertiser comparison (H2) — `/api/advertisers/{slug}/timeseries` endpoint shape is composable for multi-slug requests later
- React shell taking over from Streamlit (H2+) — design system in M3 is the same one H2 tabs will use
- `DEMO_MODE`-style "hide MI" flag (future) — API accepts `hide_mi` query param from M4

## Out of Scope (Captured for H2–H4)

**H2:**
- Cross-campaign comparison
- Calendar / holiday markers
- Weather overlay
- MI auto-annotation
- User-added annotations (read-only display only in H1; user-added in H3)
- Day × hour heatmap
- Frequency distribution histogram
- Demographic profile shift over time
- Plan vs delivered (predefined audiences)
- Geographic exploration mode
- Remaining tabs ported to React

**H3:**
- User accounts + auth
- Per-user saved campaigns/specs
- Saved views / shareable URLs

**H4:**
- Custom audiences (planning vs delivered)
- Background job infrastructure for audience computation
- Per-user audience definitions

## References

- Existing Streamlit app: `src/ui/app.py`, `src/ui/tabs/*.py`, `src/db/queries/*.py`
- Visual reference (heavy advertisers): `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/scripts/temp_sensitive_files/netlify_deploy/`
- Visual reference (Pepsi portfolio with MI toggle): `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/scripts/temp_sensitive_files/pepsi_netlify/`
- Pepsi build script (logic to port): `pepsi_netlify/_build_pages.py`
- Pepsi handover: `/Users/ianwyatt/PycharmProjects/route-playout-pipeline-claude-docs/Handover/2026-03-25_pepsi_talon_campaign_shape.md`
