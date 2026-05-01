# POC integration — operational reference for the Route-Playout-Econometrics POC team

**Last updated:** 2026-05-01
**Status:** Phase 4 complete (full-year 2025 demographic backfill in DuckDB). Phase 5 (campaign-reach for 2025) is the next planned addition.

This is the canonical reference for the POC team building against the post-Postgres operational stack. It supersedes the older `docs/07-poc-integration/` subdir, which predates the migration.

---

## TL;DR — what changed for you

| Aspect | Before (pre-2026-04-22) | After (today) |
|---|---|---|
| Where the data lives | Local Mac Postgres (~57 GB, ~9k pairs / 69 days) | **DuckDB** at `/var/lib/route/route_poc_cache.duckdb` on `playout-db` LXC (~140 GB post-rebuild) |
| Coverage | 2025-08-06 → 2025-10-13 (Test 10 baseline) | **2025-01-27 → 2025-12-31** (339 days, full year) |
| Demographic impacts row count | 415M | **~2.32B** (5.6× larger) |
| Pair count (campaign × date) | 9,575 | **51,178** |
| Canonical write target | Postgres `INSERT` | **Parquet** (`/var/lib/route/parquet/2025_{uat,live}/…`); DuckDB table is rebuilt from parquet periodically |
| Read pattern for POC | Postgres queries via psycopg | **DuckDB read-only attach**; same SQL surface for `SELECT`/`JOIN` queries |

**For POC purposes, treat `cache_route_impacts_15min_by_demo` as ready.** It's been rebuilt from the full-year parquet output, with a 4-column primary key matching the legacy schema (frameid, time_window_start, demographic_segment, campaign_id). One column dropped: `spot_break_id` (audited; zero readers in pipeline + POC).

---

## How to access the DuckDB

### Direct read-only on `playout-db`

The operational DuckDB lives on `playout-db` LXC. Read-only attach from a Python session:

```python
import duckdb
con = duckdb.connect("/var/lib/route/route_poc_cache.duckdb", read_only=True)
```

Multiple readers can attach concurrently. The cacher (single writer) holds an exclusive lock during rebuild operations — typical readers won't notice.

For SSH-tunneled access from your dev box:

```bash
ssh routeapp@playout-db   # tailnet MagicDNS
cd /home/routeapp/route-playout-pipeline-duckdb
.venv/bin/python -c "import duckdb; con = duckdb.connect('/var/lib/route/route_poc_cache.duckdb', read_only=True); print(con.execute('SELECT COUNT(*) FROM cache_route_impacts_15min_by_demo').fetchone())"
```

### Replica on `playout-frontend` (Phase 5a — pending)

The plan is to rsync the DuckDB file to the `playout-frontend` LXC where the Streamlit app reads it locally. The F4 post-write hook already exists for this (`scripts/tools/duckdb_post_write_hook.py`); fanout needs to be triggered after each cacher run + DB rebuild. **Not wired yet** — coming with Phase 5a.

For now, the POC reads directly off `playout-db`. Performance is fine for analytical queries; the LXC has 16 cores / 256 GB RAM and DuckDB caches column data internally.

### Single-writer constraint

DuckDB allows only one writer at a time. During cacher rebuilds (rare — every full-year backfill plus ad-hoc operator triggers), the file is locked exclusive for ~10-30 minutes. Reads during that window will fail with `IO Error: Could not set lock on file …`. Plan around this in the POC: graceful retry-with-backoff if you see that error.

---

## Schema — what's ready, what's stale, what's coming

### ✅ READY — use these now

#### `cache_route_impacts_15min_by_demo` (the headline table)

Per-(campaign × frame × 15-min window × demographic) audience impacts.

| Column | Type | Notes |
|---|---|---|
| `frameid` | BIGINT NOT NULL | Route frame ID |
| `time_window_start` | TIMESTAMP NOT NULL | 15-min window start |
| `time_window_end` | TIMESTAMP | 15-min window end (always start + 15min) |
| `campaign_id` | VARCHAR NOT NULL | `buyercampaignref`, sanitised (TAB/NL/CR stripped, trimmed) |
| `buyer_id` | VARCHAR | `spacebuyerid` |
| `demographic_segment` | VARCHAR NOT NULL | One of 7: `abc1`, `age_15_34`, `age_35_plus`, `all_adults`, `c2de`, `children_hh`, `main_shopper` |
| `impacts` | DOUBLE | Audience-exposure count |
| `route_release_id` | INTEGER | **Bare release number** (53 = R53, not the FK) |
| `cached_at` | TIMESTAMP | When the cacher wrote this row |
| **PK** | | (frameid, time_window_start, demographic_segment, campaign_id) |

**Coverage**: 51,178 (campaign × date) pairs, 339 dates (2025-01-27 → 2025-12-31), ~2.32B rows. R53 8,666 pairs / 97.6%, R54 12,993 / 98.4%, R55 13,580 / 99.0%, R56 15,939 / 98.3%.

**Aggregation rules (important)**:
- `SUM(impacts)` across releases is meaningful — impacts are count-like, summable.
- **Do NOT sum reach across releases or across days/weeks** — reach is a set cardinality, not additive. Use the dedicated reach tables (Phase 5, see below).
- Per-release filtering: `WHERE route_release_id = 55` (use bare number).

Full background in `docs/CACHER_GUIDE.md` and `Claude/Documentation/2026-04-30_cross_release_aggregation.md` (private docs repo).

#### `cache_demographic_universes` — denominators for Cover %

| Column | Type | Notes |
|---|---|---|
| `route_release_id` | INTEGER | **Bare release number** (53/54/55/56) |
| `demographic_code` | VARCHAR | One of the 7 demos above |
| `demographic_description` | VARCHAR | Human label |
| `universe` | DOUBLE | Population size in this demo for this release |
| `cached_at` | TIMESTAMP | |

16 rows (4 releases × 4 demographic categories). Used in the POC's existing migration-011 join: `cri.route_release_id = cdu.route_release_id`.

**`route_release_id` convention warning**: this column is the **bare number** (53). On `route_frames`, the same-named `release_id` is the **FK** to `route_releases.id` (10 for R53). Different conventions on similarly-named columns. Check which side you're on. Tracked as TODO #17 to unify.

#### `mv_playout_15min` — raw 15-min playout aggregate

Source-of-truth for "what did campaigns play, when, on which frames" before audience inference. ~379M rows for 2025. Every row: (frame × 15-min window × campaign × spot/break/cycle).

Useful for sanity checks (raw vs cached pair counts) and any per-spot analytics the cache table can't answer directly.

**Always sanitise `buyercampaignref` via** `sanitise_buyercampaignref_sql("p.buyercampaignref")` (defined in `scripts/lib/mv_definitions.py`). DuckDB's bare `TRIM()` only strips spaces, not tabs — there's a known TAB-suffix bug in some buyercampaignref values.

```sql
-- Typical pattern
SELECT TRIM(REGEXP_REPLACE(buyercampaignref, '[\t\n\r]', '', 'g')) AS campaign_id,
       time_window_start,
       SUM(spot_count) AS spots
FROM mv_playout_15min
WHERE time_window_start::DATE BETWEEN DATE '2025-01-27' AND DATE '2025-12-31'
GROUP BY 1, 2;
```

#### Frame metadata — `route_frames`, `route_frame_details`

Per-release frame inventory synced from BigQuery. `route_frames.release_id` is the **FK** (e.g. 10 for R53). Use a join to `route_releases` if you need the bare number.

#### Static reference tables (small, stable)

| Table | Rows | Use |
|---|---:|---|
| `cache_space_agencies` | 37 | OOH space owner agencies |
| `cache_space_brands` | 408 | brand inventory (refreshed 2026-05-01) |
| `cache_space_media_owners` | 7 | media owners (refreshed 2026-05-01) |
| `cache_space_buyers` | 3 | Talon Outdoor Limited, Talon Outdoor Limited (Atlas), Havas Media Limited (refreshed 2026-05-01 — non-Talon buyers exist) |
| `cache_statistics` | 4 | aggregate counts/timestamps |
| `route_releases` | (varies) | release metadata — `id` (FK), `release_number` (text), `trading_period_start`, `trading_period_end` |

#### MI summary tables (frozen Mac-cache snapshots — useful for trend analytics)

| Table | Rows | Notes |
|---|---:|---|
| `cache_mi_frame_hourly` | 104.7M | per-frame hourly mediatel impacts |
| `cache_mi_frame_daily` | 7.4M | per-frame daily |
| `cache_mi_frame_totals` | 915k | per-frame summary |
| `cache_mi_hourly` | 504k | aggregate hourly |
| `cache_mi_daily` | 67k | aggregate daily |
| `cache_mi_weekly` | 14k | aggregate weekly |
| `cache_mi_coverage` | 831 | coverage stats |

**These are pre-migration snapshots** from MS-01, frozen at 2025-11-19 era. They cover only the 69-day Phase 2 seed window, not the full 339-day 2025 backfill. **If your queries need the full year for these granularities, raise it as a request** (see "How to request changes" below) — extending them requires either re-deriving from the new impacts table or a separate cacher pass.

---

### ⚠️ STALE / FROZEN — handle with care

#### `mv_*` tables (not real materialised views, despite the prefix)

These are **flat tables** populated by the legacy pipeline, not auto-refreshed views. Most are frozen at the 2026-04-22 Phase 2 seed state (Mac-cache snapshot) and don't reflect the full-year 2025 backfill. Check `mv_*` table mtimes before trusting them as current:

| Table | Rows | Status |
|---|---:|---|
| `mv_cache_campaign_impacts_1hr` | 1.1M | frozen 2026-04-22 era |
| `mv_cache_campaign_impacts_day` | 67k | frozen |
| `mv_cache_campaign_impacts_frame` | 915k | frozen |
| `mv_campaign_browser` | 836 | frozen — POC's primary view |
| `mv_frame_audience_daily/hourly` | 1.2M / 16.9M | frozen |
| `mv_frame_brand_daily/hourly` | 1.2M / 16.9M | frozen |
| `mv_frame_spot_distribution` | 647k | refreshed by current pipeline |
| `mv_frame_spot_summary` | 647k | refreshed by current pipeline |
| `mv_platform_stats` | 1 | frozen |

**`mv_campaign_browser` is the POC's main browse view** but currently reflects the old 9,575-pair scope. **Rebuild from the new 2.32B-row impacts table is needed before it's useful for the full year.** Coordinate with the pipeline team on the rebuild SQL (or define it as a POC-side derivation).

---

### ⏳ COMING (Phase 5)

#### Campaign-reach tables

The campaign-reach cacher (`backfill_route_cache.py`) hasn't been re-run for the 2025 window yet. The existing tables hold ~2025-08–10 era data only.

| Table | Current rows | Coverage when Phase 5 lands |
|---|---:|---|
| `cache_campaign_reach_full` | 835 | one row per campaign, full-window reach + GRP + frequency |
| `cache_campaign_reach_day` | 9,570 | per-day reach |
| `cache_campaign_reach_day_cumulative` | 10,819 | cumulative-by-day reach |
| `cache_campaign_reach_week` | 2,794 | per-week reach |
| `cache_campaign_brand_reach` | 17,406 | brand-level reach |

**Phase 5 is unblocked** as of 2026-05-01 (closing of Phase 4 unblocked it). Pre-launch readiness sketch is TODO #19. Once Phase 5 runs, these tables will be rebuilt to ~full-year scope, similar shape to the demographic impacts table.

**For now**: queries against these tables return only Aug-Oct 2025 data. Build with that limitation in mind; they'll grow when Phase 5 lands.

---

## How to request changes

The pipeline + POC repos are **separate**. Schema changes need coordination.

### If you need a schema change to an existing table

1. **Open an issue** (or message the pipeline team) describing the change + why.
2. The pipeline team validates it doesn't break the cacher's write path.
3. Pipeline team coordinates the schema migration (rebuild from parquet — costs ~10-30 min wall + a snapshot for rollback).
4. POC team's parity test verifies the new shape on first deploy.

### If you need a table or view that doesn't exist

Two flavours:

**(A) Derived from existing tables**: usually best done as a view in the POC's own DuckDB read layer, or as a CTE inside the POC's queries. No pipeline change needed — the POC team can define and own these.

**(B) Cached output that requires a cacher run**: needs pipeline support. Open an issue with:
- The desired shape (columns, grain, expected row count)
- The query you'd otherwise have to run (so we understand what's being cached)
- Why caching is needed (e.g. query takes >Xs in the POC, frontend latency budget)

### If you find a column drift / something looks wrong

The pipeline team's parity test (`tests/integration/cachers/test_demographic_cacher_parity.py`) covers the cacher's write path. The POC's own migration parity test (per the team's standing practice — every POC migration runs all query functions against the new DuckDB) catches the read side. **If both pass and you still see a discrepancy**, raise it — there's likely a third path neither test covers.

---

## Operational gotchas worth knowing

### `route_release_id` has two conventions

- `route_frames.release_id`: **FK** to `route_releases.id` (e.g. 10 for R53)
- `cache_route_impacts_15min_by_demo.route_release_id`: **bare number** (e.g. 53 for R53)
- `cache_demographic_universes.route_release_id`: **bare number** (post-fix `64b1a47`)

The cacher's join works correctly via text-match on `release_number`, but new join code must check which side it's on. Tracked as TODO #17.

### Releases per-date are deterministic

Each playout date maps to exactly one release via `route_releases.trading_period_start..end` (contiguous, non-overlapping). For 2025:

| Release | Trading period | API endpoint (for cacher info; POC reads from cache) |
|---|---|---|
| R52 | 2024-10-14 → 2025-01-26 | (local algo only — out of API scope) |
| R53 | 2025-01-27 → 2025-04-06 | UAT |
| R54 | 2025-04-07 → 2025-06-29 | UAT |
| R55 | 2025-06-30 → 2025-09-28 | Live |
| R56 | 2025-09-29 → 2026-01-04 | Live |

R52 era (2025-01-01 → 2025-01-26) is **not in the cache table** — neither API endpoint serves it. It'll be filled by a parallel local-algo session (Phase 4a, ongoing).

### Inherent gaps (data_quality_skip)

562 (campaign × date) pairs in the 2025 window have playouts whose frames aren't in `route_frames` for the per-date release. These are inherent: some OOH frames aren't measured by Route. The cacher classifies them `data_quality_skip` and writes nothing. Don't expect 100% pair coverage; ~98.5% is the real ceiling. Full background in `Claude/Documentation/2026-04-30_phase_4c_readiness_audit.md`.

### Snapshot rollback exists

If the POC sees catastrophic schema corruption or wrong data, the pipeline team can roll back DuckDB to a snapshot in ~5 min. Snapshots live at:
- Local: `/var/lib/route/snapshots/route_poc_cache.<reason>.<ts>.duckdb`
- B2: `s3://route-playout-duckdb-snapshots/` (zstd-compressed)

Latest known-good: `route_poc_cache.post-phase4c.20260501T062854Z.duckdb` (87 GB local; 39.7 GiB compressed in B2).

### Parquet is the source of truth, not the table

The cacher writes parquet under `/var/lib/route/parquet/2025_{uat,live}/cache_route_impacts_15min_by_demo/run_id=*/`. The DuckDB table is rebuilt from parquet on demand. If you ever spot a value in the table that you can't reconcile, the parquet is authoritative.

You can read parquet directly from the POC if it's useful for cross-check:

```python
import duckdb
con = duckdb.connect()  # in-memory, no attach
con.execute("""
    SELECT route_release_id, COUNT(*) AS rows
    FROM read_parquet('/var/lib/route/parquet/2025_*/cache_route_impacts_15min_by_demo/run_id=*/*.parquet')
    GROUP BY 1 ORDER BY 1
""").fetchall()
```

---

## Useful query patterns

### Per-release total impacts for a campaign

```sql
SELECT route_release_id, demographic_segment, SUM(impacts) AS total_impacts
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '12345'
GROUP BY 1, 2
ORDER BY 1, 2;
```

### Cover % (impacts / universe denominator)

```sql
SELECT
    cri.route_release_id,
    cri.demographic_segment,
    SUM(cri.impacts) AS total_impacts,
    cdu.universe,
    SUM(cri.impacts) / cdu.universe * 100 AS cover_pct
FROM cache_route_impacts_15min_by_demo cri
JOIN cache_demographic_universes cdu
  ON cri.route_release_id = cdu.route_release_id
 AND cri.demographic_segment = cdu.demographic_code
WHERE cri.campaign_id = '12345'
GROUP BY 1, 2, cdu.universe
ORDER BY 1, 2;
```

### Daily impacts for a campaign over the 2025 window

```sql
SELECT
    time_window_start::DATE AS d,
    demographic_segment,
    SUM(impacts) AS daily_impacts
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '12345'
  AND demographic_segment = 'all_adults'
GROUP BY 1, 2
ORDER BY 1;
```

339 rows per (campaign × demo) over the full year. Performance: <1 sec on the LXC.

### Per-frame impact intensity (frequency proxy — but **not** reach)

```sql
SELECT
    frameid,
    COUNT(DISTINCT time_window_start) AS active_windows,
    SUM(impacts) AS total_impacts,
    AVG(impacts) AS avg_impacts_per_window
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '12345'
  AND demographic_segment = 'all_adults'
GROUP BY 1
ORDER BY total_impacts DESC
LIMIT 50;
```

For actual reach, **wait for Phase 5** (`cache_campaign_reach_full` etc. will be rebuilt).

---

## Cross-references

| Topic | Where |
|---|---|
| Operational stack (hosts, storage, secrets) | [`docs/CURRENT_INFRASTRUCTURE.md`](CURRENT_INFRASTRUCTURE.md) |
| Cacher mechanics + flag reference | [`docs/CACHER_GUIDE.md`](CACHER_GUIDE.md) |
| Project root quick reference + critical warnings | [`CLAUDE.md`](../CLAUDE.md) |
| Phase tracker | `Claude/Documentation/2026-04-30_project_phases.md` (private docs repo) |
| Cross-release aggregation rules | `Claude/Documentation/2026-04-30_cross_release_aggregation.md` (private docs repo) |
| Route release schedule (canonical) | `Claude/Documentation/route_release_schedule_authoritative.md` |
| BWS shim setup (if you need it for cacher access) | `Claude/Documentation/2026-04-24_bws_setup_walkthrough.md` |

---

## Open questions for the POC team

These need POC-team input before the pipeline team can act on them:

1. **`mv_campaign_browser` rebuild**: the POC's primary browse view is frozen at the 9,575-pair scope. Do you want the pipeline team to rebuild it from the new 2.32B-row table, or is the POC team going to redefine it on its own DuckDB read layer? If the former, we need the SQL definition + any column-rename concerns.

2. **POC's parity test**: when's the right moment to run it against the new DuckDB? Right after Phase 4c rebuild lands? After a snapshot+rsync to `playout-frontend`? Sequence affects how we coordinate.

3. **Phase 5a cutover target**: do you want to read DuckDB on `playout-db` (network round-trip via Tailscale) or wait for the rsync replica on `playout-frontend`? Performance + operational trade-offs each way.

4. **MI summary tables coverage extension**: do you need the `cache_mi_*` tables extended to the full year (currently 69-day Mac-cache snapshot only)? If yes, that's a separate cacher pass we'd plan into Phase 5 or 5a.

5. **Anything we're missing**: tables / views / aggregations the POC needs that aren't in the schema today, list 'em here and we'll work out whether they're POC-side derivations or pipeline cacher additions.

---

**Maintained by the Route Pipeline Team.** Update this doc as the schema evolves.
