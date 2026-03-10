# Mobile Volume Index

## Overview

The mobile volume index adjusts raw OOH impact figures using mobile footfall data. Mobile network operators record device volumes passing each digital frame at hourly granularity. These volumes are normalised into an index (where 1.0 represents the baseline average) and applied as a multiplier to Route-modelled impacts.

This allows econometricians to compare standard Route impacts against mobile-adjusted impacts, highlighting frames and time slots where real-world footfall diverges from Route's modelled audience estimates.

**Scope:** The mobile volume index applies to **impacts only**. It does not affect reach, cover, GRP, or frequency metrics.

---

## Quick Start: Loading Data

### 1. Import CSV + build cache tables (standard workflow)

```bash
uv run python scripts/import_mobile_index.py /path/to/analyst_data.csv
```

This does three things:
1. Creates the `mobile_volume_index` table (if not exists)
2. Truncates and re-imports from CSV (with 2024-to-2025 date shifting)
3. Builds 7 pre-aggregated cache tables (the expensive step)

### 2. Rebuild cache only (after schema changes or fixes)

```bash
uv run python scripts/import_mobile_index.py --cache-only
```

### 3. Import CSV without rebuilding cache

```bash
uv run python scripts/import_mobile_index.py /path/to/data.csv --no-cache
```

### 4. Use primary (remote) database

```bash
uv run python scripts/import_mobile_index.py /path/to/data.csv --primary
```

---

## IMPORTANT: Disk Space Warning

The cache build performs massive INSERT...SELECT operations against the 44 GB `cache_route_impacts_15min_by_demo` table. PostgreSQL generates WAL (Write-Ahead Log) files during these inserts.

**The `cache_mi_frame_hourly` table alone is 52M rows and generated ~1.6 TB of temporary WAL files during testing.** The build script now runs `CHECKPOINT` between each table to force WAL cleanup, but you should still:

- **Monitor disk space** with `df -h /` during the build
- **Expect the build to take 45-60 minutes** on a local Mac
- **Ensure at least 100 GB free disk space** before starting
- Kill stale queries if the build fails: `SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query LIKE '%cache_mi%';`
- Then run `CHECKPOINT;` to reclaim WAL space

---

## CSV Format Specification

The import script expects a CSV file with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `frameid` | integer | Frame identifier matching `cache_route_impacts_15min_by_demo.frameid` |
| `date` | `YYYY-MM-DD` | Date of observation (2024 calendar) |
| `hour` | integer (0-23) | Hour of day |
| `index_value` | decimal | Mobile volume index value (1.0 = baseline average) |

### Example Rows

```csv
frameid,date,hour,index_value
1234567,2024-08-28,8,1.23
1234567,2024-08-28,9,1.45
1234567,2024-08-28,10,1.12
9876543,2024-08-28,8,0.87
```

---

## Date-Shifting: 2024 to 2025

Mobile footfall data is sourced from the 2024 calendar year, but the playout data covers 2025. Each 2024 date is shifted to the corresponding date in 2025 using **ISO 8601 week numbering**:

1. Extract the ISO week number and day-of-week from the 2024 date
2. Find the date in ISO year 2025 with the same week number and day-of-week

This preserves the day-of-week pattern (e.g., a Wednesday in week 35 of 2024 maps to the Wednesday of week 35 in 2025).

The database stores both the original `date_2024` and the shifted `date_2025` columns. The JOIN to impact data uses `date_2025`.

The date-shifting logic lives in `src/utils/date_shift.py`.

---

## Cache Table Architecture

Direct JOINs against the 44 GB impacts table are too slow for interactive use. The import script pre-aggregates results into 7 cache tables:

| Cache Table | Grain | Rows (test data) | Size | Purpose |
|-------------|-------|-------------------|------|---------|
| `cache_mi_daily` | campaign x date x demographic | 15K | 1.4 MB | Daily chart overlays |
| `cache_mi_weekly` | campaign x iso_week x demographic | 3.3K | 432 KB | Weekly table/chart overlays |
| `cache_mi_hourly` | campaign x day_of_week x hour x demographic | 120K | 14 MB | Hourly analysis |
| `cache_mi_frame_daily` | frame x date x demographic | 3.4M | 290 MB | Frame daily table indexed column |
| `cache_mi_frame_hourly` | frame x date x hour x demographic | 52M | 4.4 GB | Frame hourly table indexed column |
| `cache_mi_frame_totals` | frame x demographic | 370K | 31 MB | Frame campaign totals indexed column |
| `cache_mi_coverage` | campaign | 186 | 16 KB | Coverage metrics |

**With real analyst data covering more frames, expect these numbers to grow significantly.** The frame_hourly table scales with (frames x days x hours x demographics).

Each cache table has an index on `(campaign_id, demographic_segment)` for fast lookups.

### Build Timing (local Mac, test data)

| Table | Build Time |
|-------|-----------|
| `cache_mi_daily` | ~7 min |
| `cache_mi_weekly` | ~10 min |
| `cache_mi_hourly` | ~7 min |
| `cache_mi_frame_daily` | ~5 min |
| `cache_mi_frame_hourly` | ~7 min |
| `cache_mi_frame_totals` | ~5 min |
| `cache_mi_coverage` | instant (reads from cache_mi_frame_totals) |
| **Total** | **~41 min** |

---

## Database Tables

### Raw index data

```sql
CREATE TABLE mobile_volume_index (
    frameid     BIGINT   NOT NULL,
    date_2024   DATE     NOT NULL,
    hour        SMALLINT NOT NULL,
    index_value NUMERIC  NOT NULL,
    date_2025   DATE     NOT NULL
);

CREATE INDEX idx_mobile_volume_index_lookup
    ON mobile_volume_index (frameid, date_2025, hour);
```

### Cache tables

Each cache table stores both raw and indexed (mobile-adjusted) impact values. The core aggregation pattern:

```sql
SUM(c.impacts) AS raw_impacts,
SUM(c.impacts * COALESCE(m.index_value, 1.0)) AS indexed_impacts
```

The `COALESCE(m.index_value, 1.0)` ensures frames without index data pass through unchanged.

---

## UI Integration: All 6 Tabs

Each tab has an independent toggle checkbox. When the toggle is on:

| Tab | What's shown |
|-----|-------------|
| **Overview** | Dual-line campaign shape chart (blue raw, orange dashed indexed) |
| **Executive Summary** | "Indexed Impacts" and "Indexed/Day" rows in delivery table + daily chart overlay |
| **Weekly Reach** | "Indexed (000s)" column in weekly table + orange bar in grouped chart |
| **Daily & Hourly** | Indexed daily/weekly avg metrics + indexed bars in distribution + day-of-week charts |
| **Frame Audiences** | "Indexed: All Adults (000s)" column in campaign/daily/hourly tables |
| **Excel Export** | Includes indexed columns when any toggle is active |

### Visual conventions

- **Raw impacts**: solid blue line/bar (`#2E86AB`)
- **Mobile-indexed**: dashed orange line/bar (`#F18F01`)
- **Coverage banner**: shows frames_with_index / total_frames when toggle is on
- **Missing index data**: defaults to index 1.0 (raw = indexed)

---

## Query Architecture

All queries read from pre-built cache tables (never from the 44 GB impacts table at runtime).

Queries live in `src/db/queries/mobile_index.py` and are re-exported via `src/db/streamlit_queries.py`.

| Function | Source Table | Returns |
|----------|-------------|---------|
| `mobile_index_table_exists()` | `cache_mi_daily` | Whether cache tables exist and have data |
| `get_mobile_index_coverage_sync()` | `cache_mi_coverage` | (frames_with_index, total_frames) tuple |
| `get_daily_impacts_with_mobile_index_sync()` | `cache_mi_daily` | Daily raw + indexed impacts |
| `get_hourly_impacts_with_mobile_index_sync()` | `cache_mi_hourly` | Hourly raw + indexed impacts by day-of-week |
| `get_weekly_impacts_with_mobile_index_sync()` | `cache_mi_weekly` | Weekly raw + indexed impacts by ISO week |
| `get_frame_daily_with_mobile_index_sync()` | `cache_mi_frame_daily` | Frame x date raw + indexed impacts |
| `get_frame_hourly_with_mobile_index_sync()` | `cache_mi_frame_hourly` | Frame x date x hour raw + indexed impacts |
| `get_frame_totals_with_mobile_index_sync()` | `cache_mi_frame_totals` | Frame campaign total raw + indexed impacts |

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/import_mobile_index.py` | CSV import + cache table build (7 tables with CHECKPOINT) |
| `src/utils/date_shift.py` | ISO week date-shifting (2024 to 2025) |
| `src/db/queries/mobile_index.py` | 8 query functions reading from cache tables |
| `src/db/queries/__init__.py` | Re-exports all mobile index functions |
| `src/db/streamlit_queries.py` | Re-exports for Streamlit import compatibility |
| `src/ui/tabs/overview.py` | Toggle + dual-line campaign shape chart |
| `src/ui/tabs/executive_summary.py` | Toggle + delivery metrics + daily chart |
| `src/ui/tabs/reach_grp.py` | Toggle + weekly table column + bar chart |
| `src/ui/tabs/time_series.py` | Toggle + stats + distribution + day-of-week charts |
| `src/ui/tabs/detailed_analysis.py` | Toggle + indexed columns in 3 frame tables |
| `src/ui/utils/export/data.py` | Multi-toggle export check |

---

## Troubleshooting

### Cache build fails or stalls

1. Check for stale queries: `SELECT pid, left(query, 80), now() - query_start FROM pg_stat_activity WHERE state = 'active';`
2. Cancel stale ones: `SELECT pg_cancel_backend(<pid>);`
3. Reclaim WAL: `CHECKPOINT;`
4. Re-run: `uv run python scripts/import_mobile_index.py --cache-only`

### Disk space fills during build

The build generates large WAL files. The script runs CHECKPOINT between tables to mitigate this, but if disk fills:
1. Cancel the running query (see above)
2. Run `CHECKPOINT;` to reclaim WAL
3. Consider dropping `cache_mi_frame_hourly` if space is tight — it's 4.4 GB and the least critical table
4. Re-run with more free space

### Toggle doesn't appear

The toggle only appears when `mobile_index_table_exists()` returns True. This checks for `cache_mi_daily` having data. Run `--cache-only` to rebuild if the table exists but is empty.

---

*Last Updated: 5 March 2026*
