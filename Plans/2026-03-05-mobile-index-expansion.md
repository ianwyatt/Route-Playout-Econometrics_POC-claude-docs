# Mobile Index Expansion: Performance + Full UI Coverage

**Date:** 5 March 2026
**Status:** Draft
**Context:** Mobile index overlay currently only on Time Series tab. Needs expanding to all tabs + performance fix.

---

## Problem

The current mobile index queries LEFT JOIN `cache_route_impacts_15min_by_demo` (44 GB, 415M rows) to `mobile_volume_index` at query time. This is slow (~15-30s per query) and will get worse as we add more call sites across all tabs.

---

## Phase 1: Cache Table (Performance Fix)

### New Table: `cache_mobile_indexed_impacts`

Pre-aggregate indexed impacts at the grains the UI needs. Built by the import script after loading raw index data.

**Aggregation grains:**

| Grain | Columns | Purpose |
|-------|---------|---------|
| **Frame x Date** | frameid, campaign_id, date, demographic_segment, raw_impacts, indexed_impacts | Frame daily tables, overview chart |
| **Frame x Date x Hour** | frameid, campaign_id, date, hour, demographic_segment, raw_impacts, indexed_impacts | Frame hourly tables, hourly heatmap |
| **Campaign x Date** | campaign_id, date, demographic_segment, raw_impacts, indexed_impacts | Daily charts (all tabs) |
| **Campaign x Week** | campaign_id, iso_year, iso_week, week_start, demographic_segment, raw_impacts, indexed_impacts | Weekly charts + weekly performance table |
| **Campaign x Day-of-Week x Hour** | campaign_id, day_of_week, hour, demographic_segment, raw_avg_impacts, indexed_avg_impacts, raw_total_impacts, indexed_total_impacts, count | Hourly heatmap, avg by hour |
| **Frame x Campaign Total** | frameid, campaign_id, demographic_segment, raw_impacts, indexed_impacts | Frame campaign totals table |

**Implementation:**
- Import script (`scripts/import_mobile_index.py`) gains a `--build-cache` flag (default: on)
- After loading raw index data, runs the 6 aggregation queries as INSERT INTO ... SELECT
- Each aggregation query runs the expensive JOIN once and stores results
- Indexes on (campaign_id, demographic_segment) for each grain
- Truncate + rebuild pattern (same as raw index data)
- **Must be re-run after loading real analyst data**

**Query layer changes:**
- All `get_*_with_mobile_index_sync()` functions switch from real-time JOIN to cache table SELECT
- Coverage query can use the frame x date grain (much faster than joining 415M rows)
- Queries go from ~15-30s to sub-second

---

## Phase 2: UI Expansion

### Tab 1: Overview

**Campaign Shape chart** — add second orange dashed line (indexed impacts) using Campaign x Date cache grain.

- Toggle checkbox at top of tab (same pattern as Time Series)
- Coverage banner below toggle
- Dual-line chart: blue solid (raw) + orange dashed (indexed)

### Tab 2: Weekly Reach, Impacts & GRPs

**Weekly Performance table** — add "Indexed Impacts (000s)" column using Campaign x Week cache grain.

- Toggle checkbox at tab level
- Additional column in the weekly metrics table alongside existing Impacts column
- No change to reach/GRP/frequency columns (unaffected by mobile index)

### Tab 3: Daily & Hourly Patterns (Existing — Expand)

Currently has: daily trend dual-line chart, weekly trends dual-line chart.

**Add:**
- **Daily Impact Distribution bar chart** — add indexed impacts as grouped bars or overlay
- **Average Daily Impacts by Day of Week bars** — add indexed bars alongside raw
- **Campaign Averages stats** — show indexed daily/weekly averages alongside raw values
- **Peak Performance stats** — show indexed peak values alongside raw

All from existing cache grains (Campaign x Date, Campaign x Day-of-Week x Hour).

### Tab 4: Geographic

No change (geographic doesn't have frame-level index data at OA level — out of scope for this phase).

### Tab 5: Frame Audiences

**Three sub-tabs need indexed columns:**

| Sub-tab | Cache Grain | New Columns |
|---------|-------------|-------------|
| Frame Campaign Audiences | Frame x Campaign Total | Indexed Impacts (per demographic) |
| Frame Daily Audiences | Frame x Date | Indexed Impacts (per demographic) |
| Frame Hourly Audiences | Frame x Date x Hour | Indexed Impacts (per demographic) |

- Toggle checkbox at Frame Audiences tab level
- When active, tables gain additional "Indexed" column per demographic
- Large tables — cache grain is critical for performance

### Tab 6: Executive Summary

**Campaign Shape chart** — same dual-line as Overview (reuse same data/component).
**Key metrics** — show indexed total impacts alongside raw in the metrics cards.

- Toggle checkbox at tab level
- Coverage banner

---

## Phase 3: Export Updates

Expand the export to include indexed columns from all affected sheets:

| Sheet | Change |
|-------|--------|
| Daily Impacts | Already done (3 columns) |
| Frame Daily | Add indexed impacts columns per demographic |
| Frame Hourly | Add indexed impacts columns per demographic |
| Frame Totals | Add indexed impacts column per demographic |
| Weekly Metrics | Add indexed impacts column |
| Summary | Add mobile index coverage stat |

---

## Execution Order

| Step | What | Why First |
|------|------|-----------|
| 1 | Build cache table infrastructure | Everything depends on fast queries |
| 2 | Refactor existing Time Series queries to use cache | Validate cache correctness against known-working output |
| 3 | Overview tab overlay | Highest visibility |
| 4 | Executive Summary overlay | Reuses overview pattern |
| 5 | Daily & Hourly Patterns expansion | Extend existing tab |
| 6 | Weekly Reach tab column | New column in existing table |
| 7 | Frame Audiences tables | Most complex — 3 sub-tabs x multiple demographics |
| 8 | Export expansion | Last — feeds from all the above |

---

## Data Refresh Note

The cache table must be rebuilt whenever:
- New raw index data is imported (analyst provides updated CSV)
- Real data replaces test data

Command: `uv run python scripts/import_mobile_index.py /path/to/data.csv` (cache build is automatic).

---

## What's NOT Changing

- Reach, cover, GRP, frequency — completely unaffected
- Geographic tab — no frame-level index at OA grain
- Raw index data table (`mobile_volume_index`) — stays as-is, cache is derived from it
- Toggle defaults to off everywhere — no change to existing behaviour

---

*Draft: 5 March 2026*
