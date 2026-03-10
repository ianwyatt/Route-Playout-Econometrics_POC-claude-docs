# Design: Mobile Volume Index Overlay

**Date:** 5 March 2026
**Status:** Approved
**Authors:** Doctor Biz + Claude

---

## Purpose

Enable econometricians to evaluate whether mobile device volume data is a useful factor for adjusting OOH audience impacts. The analyst provides pre-calculated indexes (mobile volume vs yearly OA average) per frame per hour. The app overlays these as a second line on impact charts so users can visually compare raw vs mobile-indexed impacts.

This is exploratory/POC work — testing suitability of the methodology before any production commitment.

---

## Data Architecture

### New PostgreSQL Table: `mobile_volume_index`

| Column | Type | Description |
|--------|------|-------------|
| `frameid` | bigint | Frame ID (matches existing playout tables) |
| `date_2024` | date | Original 2024 date from analyst's CSV |
| `hour` | smallint | Hour of day (0-23) |
| `index_value` | numeric | Mobile volume index (1.0 = OA yearly average) |
| `date_2025` | date | Date-shifted to 2025 (same day-of-week mapping) |

**Index:** `(frameid, date_2025, hour)` for fast joins to impact data.

### CSV Import

- **Input:** Analyst provides CSV with columns: `frameid, date, hour, index_value`
  - Dates are 2024 dates
  - ~400k frames x 69 days x 24 hours = ~662 million rows (raw), but only frames matching our playout data are used at query time
- **Date-shifting:** Each 2024 date is mapped to the same day-of-week in the same ISO week in 2025
  - Wed 28 Aug 2024 (ISO week 35) -> Wed 27 Aug 2025 (ISO week 35)
  - Day-of-week alignment is critical — mobile footfall patterns differ fundamentally between weekdays and weekends
- **Import script:** Python script, re-runnable if analyst provides updated data
- **Storage:** The full dataset loads into PostgreSQL; queries only join the subset matching campaign frames

### Index Calculation Context (for reference)

The index itself is calculated by the analyst, not by this app:
1. For each Output Area (OA), calculate the yearly average mobile volume
2. Index = OA volume at specific hour/day / OA yearly average
3. All frames within an OA share the same index values

---

## Query Layer

### Core Principle

Index always applied at the finest grain: frame x 15-minute interval. The 15-min slot inherits the index for its containing hour. All higher aggregations are `SUM(impacts * COALESCE(index_value, 1.0))`.

### Join Pattern

```sql
SELECT
    DATE(c.time_window_start) as date,
    SUM(c.impacts) as raw_impacts,
    SUM(c.impacts * COALESCE(m.index_value, 1.0)) as indexed_impacts
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

### Aggregation Levels

- **Daily:** `GROUP BY date` -> daily chart with two lines
- **Hourly heatmap:** `GROUP BY day_of_week, hour` -> second heatmap or dual values
- **Weekly:** `GROUP BY ISO week` -> weekly chart with two lines

### Missing Index Handling

Frames with no matching index default to 1.0 (raw impact passes through unchanged). Coverage statistic displayed to user.

### New Query Functions

- `get_daily_impacts_with_mobile_index_sync(campaign_id, demographic)`
- `get_hourly_impacts_with_mobile_index_sync(campaign_id, demographic)`

These sit alongside existing functions, not replacing them.

---

## UI Changes

### Affected Tabs

| Tab | Change |
|-----|--------|
| **Time Series** | Dual-line charts (raw + indexed) for daily and weekly views |
| **Detailed Analysis** | Dual hourly heatmap or toggle; dual columns in regional/environment tables |
| Overview | No change |
| Executive Summary | No change |
| Reach/GRP | No change — reach, cover, GRP, frequency are completely unaffected |
| Geographic | No change |

### Toggle

Streamlit checkbox: "Show mobile-indexed impacts" in the sidebar or tab header.

- **Off (default):** Current behaviour, no change
- **On:** Charts show both raw and indexed lines; tables show both columns

### Visual Indicator

Banner when mobile index is active: "Mobile volume index applied - showing adjusted impacts alongside raw"

### Coverage Statistic

Displayed near the toggle: "Mobile index coverage: X% of frames (N / M)"

### Chart Behaviour

- Two distinct lines with clear legend: "Impacts (raw)" and "Impacts (mobile-indexed)"
- Distinct colours for easy differentiation
- Both lines always visible when toggle is on (no switching between them)

---

## Export

### When Mobile Index Toggle Is On

Three columns per impact field in CSV/Excel exports:

| Column | Description |
|--------|-------------|
| `impacts` | Raw impact value |
| `mobile_index` | The index value applied |
| `impacts_mobile_indexed` | `impacts * mobile_index` |

### When Mobile Index Toggle Is Off

Exports unchanged — identical to current behaviour.

---

## What's NOT In Scope

- Reach, cover, GRP, frequency — completely unaffected by mobile index
- Overview tab, Executive Summary tab — no changes
- Calculating the indexes — analyst provides them
- Holiday/anomaly handling — simple day-of-week mapping, no special cases
- Production-grade index management UI — this is a one-off CSV import

---

## Technical Notes

- Branch: feature work done in a dedicated branch, not main
- The raw 15-min impacts table (`cache_route_impacts_15min_by_demo`) is 44 GB with ~415M+ rows
- The mobile index table will be large (~662M rows for 400k frames) but most rows won't be joined — only frames in active campaigns
- Consider whether to load all 400k frames or pre-filter to only frames in our playout dataset during import

---

*Approved: 5 March 2026*
