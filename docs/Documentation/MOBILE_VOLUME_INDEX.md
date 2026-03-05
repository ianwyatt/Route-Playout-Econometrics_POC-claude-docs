# Mobile Volume Index

## Overview

The mobile volume index provides a mechanism to adjust raw OOH (out-of-home) impact figures using mobile footfall data. Mobile network operators record device volumes passing each digital frame at hourly granularity. These volumes are normalised into an index (where 1.0 represents the baseline average) and applied as a multiplier to Route-modelled impacts.

This allows econometricians to compare standard Route impacts against mobile-adjusted impacts, highlighting frames and time slots where real-world footfall diverges from Route's modelled audience estimates.

**Scope:** The mobile volume index applies to **impacts only**. It does not affect reach, cover, GRP, or frequency metrics.

---

## CSV Format Specification

The import script expects a CSV file with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `frameid` | integer | Frame identifier matching `cache_route_impacts_15min_by_demo.frameid` |
| `date` | `YYYY-MM-DD` | Date of observation (2024 calendar) |
| `hour` | integer (0–23) | Hour of day |
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

## Import Command

Import CSV data into the local database:

```bash
uv run python scripts/import_mobile_index.py <csv_path>
```

Import into the primary (remote) database:

```bash
uv run python scripts/import_mobile_index.py <csv_path> --primary
```

The import is **idempotent**: the `mobile_volume_index` table is created if it does not exist, truncated, then repopulated from the CSV. Each import replaces all previous data.

Rows are inserted in batches of 10,000 for efficiency.

---

## Date-Shifting: 2024 to 2025

Mobile footfall data is sourced from the 2024 calendar year, but the playout data in this POC covers 2025. To align the two datasets, each 2024 date is shifted to the corresponding date in 2025 using **ISO 8601 week numbering**:

1. Extract the ISO week number and day-of-week from the 2024 date
2. Find the date in ISO year 2025 with the same week number and day-of-week

This preserves the day-of-week pattern (e.g., a Wednesday in week 35 of 2024 maps to the Wednesday of week 35 in 2025), which is important because mobile footfall varies significantly by day-of-week.

### Example

| 2024 Date | Day | ISO Week | 2025 Date | Day |
|-----------|-----|----------|-----------|-----|
| 2024-08-28 | Wednesday | 35 | 2025-08-27 | Wednesday |
| 2024-01-01 | Monday | 1 | 2024-12-30 | Monday |

The database stores both the original `date_2024` and the shifted `date_2025` columns. The JOIN to impact data uses `date_2025`.

The date-shifting logic lives in `src/utils/date_shift.py`.

---

## Database Table Schema

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

The index supports the primary lookup pattern: joining to impact data at `(frameid, date, hour)` granularity.

---

## UI: Time Series Tab

When the `mobile_volume_index` table exists and contains data, a **"Show mobile-indexed impacts"** checkbox appears on the Time Series (Daily & Hourly Patterns) tab.

### When the toggle is off

Charts display standard Route impacts only. No change from baseline behaviour.

### When the toggle is on

- **Coverage statistic** is displayed: e.g., "Coverage: 85% of frames (1,234 / 1,452)"
- **Daily Impacts chart** shows two lines:
  - **Raw Impacts** — solid blue line (`#2E86AB`)
  - **Mobile-Indexed** — dashed orange line (`#F18F01`)
- **Weekly Trends chart** appears as an additional section ("Weekly Trends — Raw vs Mobile-Indexed"), showing the same dual-line pattern aggregated by ISO week
- Chart legends are shown when the toggle is active

### Missing index data

Frames or time slots without a matching row in `mobile_volume_index` default to an index value of **1.0** (i.e., raw impacts are unchanged). The coverage statistic shows what proportion of the campaign's frame-hours have index data.

---

## UI: Detailed Analysis Tab

The Detailed Analysis (Frame Audiences) tab also shows the **"Show mobile-indexed impacts"** checkbox when index data is available.

When active, it displays the same coverage statistic as the Time Series tab.

---

## Exports

When the mobile index toggle is active, CSV and Excel exports include three additional columns for daily impacts:

| Column | Description |
|--------|-------------|
| `impacts` | Raw Route-modelled impacts |
| `mobile_index` | Effective mobile index ratio (indexed / raw, defaults to 1.0 where raw is zero) |
| `impacts_mobile_indexed` | Impacts multiplied by the mobile volume index |

For hourly impacts, the export includes `mobile_index_avg` (ratio of indexed to raw average impacts) alongside the standard hourly columns.

When the toggle is off, exports contain only the standard `impacts` column with no mobile index columns.

---

## Query Architecture

All mobile index queries live in `src/db/queries/mobile_index.py` and are re-exported via `src/db/streamlit_queries.py` with Streamlit caching.

The core pattern is a **LEFT JOIN** from the impacts table to the mobile index table at `(frameid, date, hour)` granularity:

```sql
SELECT
    DATE(c.time_window_start) AS date,
    SUM(c.impacts) AS raw_impacts,
    SUM(c.impacts * COALESCE(m.index_value, 1.0)) AS indexed_impacts
FROM cache_route_impacts_15min_by_demo c
LEFT JOIN mobile_volume_index m
    ON c.frameid = m.frameid
    AND DATE(c.time_window_start) = m.date_2025
    AND EXTRACT(HOUR FROM c.time_window_start)::int = m.hour
WHERE c.campaign_id = %s
    AND c.demographic_segment = %s
GROUP BY DATE(c.time_window_start)
ORDER BY date
```

The `COALESCE(m.index_value, 1.0)` ensures that frames without index data pass through unchanged.

### Available query functions

| Function | Returns |
|----------|---------|
| `mobile_index_table_exists()` | Whether the table exists and has data |
| `get_mobile_index_coverage_sync()` | (frames_with_index, total_frames) tuple |
| `get_daily_impacts_with_mobile_index_sync()` | Daily raw + indexed impacts |
| `get_hourly_impacts_with_mobile_index_sync()` | Hourly raw + indexed impacts by day-of-week |
| `get_weekly_impacts_with_mobile_index_sync()` | Weekly raw + indexed impacts by ISO week |

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/import_mobile_index.py` | CSV import CLI script |
| `src/utils/date_shift.py` | ISO week date-shifting (2024 to 2025) |
| `src/db/queries/mobile_index.py` | All mobile index SQL queries |
| `src/db/streamlit_queries.py` | Cached Streamlit wrappers |
| `src/ui/tabs/time_series.py` | Time Series tab with dual-line charts |
| `src/ui/tabs/detailed_analysis.py` | Detailed Analysis tab with coverage indicator |
| `src/ui/utils/export/data.py` | Export logic with three-column mobile index support |

---

*Last Updated: 5 March 2026*
