# Cache Usage Guide for POC Developers

**Last Updated:** 2025-11-12
**Target Audience:** POC Application Developers, Data Analysts
**Purpose:** Practical guide to querying pre-cached Route audience data

---

## Table of Contents

1. [Overview](#overview)
2. [Cache Architecture](#cache-architecture)
3. [Demographic Cache - 15-Minute Impacts](#demographic-cache---15-minute-impacts)
4. [Campaign Reach Cache - Daily/Weekly/Full](#campaign-reach-cache---dailyweeklyfull)
5. [Brand Reach Cache - Brand Performance](#brand-reach-cache---brand-performance)
6. [Integration Patterns](#integration-patterns)
7. [Performance Best Practices](#performance-best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Cache Freshness](#cache-freshness)
10. [When to Call the Route API Directly](#when-to-call-the-route-api-directly)

---

## Overview

The Route Playout Pipeline maintains **three primary cache systems** to accelerate POC application queries. These caches pre-compute expensive Route API calls and store results in PostgreSQL for instant retrieval.

### Why Use Caches?

- **Speed**: Sub-second queries vs 5-30 second API calls
- **Cost**: No API rate limits or usage charges
- **Reliability**: No network timeouts or API downtime
- **Consistency**: Locked to specific Route release (R56)

### When to Query Raw Playout Data vs Caches

| Use Case | Data Source | Reason |
|----------|-------------|--------|
| Frame-level spot details | `playout_data` | Caches don't store individual spots |
| Creative analysis | `playout_data` | Need creative_id, spot metadata |
| Real-time today's data | `playout_data` | Caches updated nightly |
| Audience demographics | **Demographic Cache** | Pre-computed, instant results |
| Campaign reach metrics | **Campaign Reach Cache** | Pre-computed reach/GRP/frequency |
| Brand performance | **Brand Reach Cache** | Brand-level reach metrics |

---

## Cache Architecture

### Cache Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│ Level 1: Frame-Level Demographic Cache                     │
│ → cache_route_impacts_15min_by_demo                        │
│ → 252.7M records, 826 campaigns, 66GB (MS-01 production)   │
│ → 7 demographics, 15-min granularity, 69 days history      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Level 2: Campaign-Level Aggregations (Materialized Views)  │
│ → mv_cache_campaign_impacts_15min   (680 MB)               │
│ → mv_cache_campaign_impacts_1hr     (162 MB)               │
│ → mv_cache_campaign_impacts_day     (10 MB)                │
│ → mv_cache_campaign_impacts_daypart                        │
│ → mv_cache_campaign_impacts_week                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Level 3: Campaign Reach Cache (3 tables, 4.7 MB total)     │
│ → cache_campaign_reach_day       (9,570 records, 3.7 MB)   │
│ → cache_campaign_reach_week      (1,003 records, 696 KB)   │
│ → cache_campaign_reach_full      (790 records, 336 KB)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Level 4: Brand Reach Cache (1 table, 6.2 MB)               │
│ → cache_campaign_brand_reach     (17,406 records)          │
│   - day: 12,017 | week-ind: 2,200 | week-cum: 2,180       │
│   - full: 1,009 | 175 brands across 765 campaigns         │
└─────────────────────────────────────────────────────────────┘
```

### Database Locations

- **Local (Development)**: `localhost:5432/route_poc` - Last 7 days only
- **MS-01 (Production)**: `192.168.1.34:5432/route_poc` - Full 69-day archive (2025-08-06 to 2025-10-13)

---

## Demographic Cache - 15-Minute Impacts

### Table: `cache_route_impacts_15min_by_demo`

**Purpose**: Store Route API audience impacts at 15-minute granularity for 7 demographic segments.

**Use Cases**:
- Detailed time-of-day audience analysis
- Demographic breakdowns (age, socio-economic, household composition)
- Building custom aggregations not available in other caches
- Daypart analysis (morning, daytime, evening, night)

### Schema

```sql
cache_route_impacts_15min_by_demo (
    frameid              BIGINT,
    time_window_start    TIMESTAMP,
    time_window_end      TIMESTAMP,
    campaign_id          VARCHAR,
    buyer_id             VARCHAR,
    demographic_segment  VARCHAR,  -- See demographics table below
    impacts              NUMERIC,  -- In thousands (000s)
    route_release_id     INTEGER,  -- Currently: 56
    cached_at            TIMESTAMP,
    PRIMARY KEY (frameid, time_window_start, demographic_segment)
)
```

**Indexes**:
- `(frameid, demographic_segment)` - Fast frame lookups
- `(campaign_id, demographic_segment)` - Fast campaign lookups
- `(campaign_id, time_window_start, demographic_segment)` - Campaign time series
- `(buyer_id, demographic_segment)` - Buyer-level analysis

### Demographic Segments

| Segment Code | Description | Use Case |
|--------------|-------------|----------|
| `all_adults` | Total adult population (15+) | Overall reach baseline |
| `age_15_34` | Ages 15-34 | Youth demographic targeting |
| `age_35_plus` | Ages 35+ | Older demographic targeting |
| `abc1` | ABC1 socio-economic groups | Upmarket demographic |
| `c2de` | C2DE socio-economic groups | Mass market demographic |
| `main_shopper` | Primary household shopper | Retail/FMCG campaigns |
| `children_hh` | Households with children | Family-focused campaigns |

### Query Examples

#### Example 1: Get All Demographics for Single Frame + Date

```sql
-- Get demographic breakdown for frame 1234567890 on 2025-10-15 at 19:30
SELECT
    demographic_segment,
    impacts,
    impacts * 1000 as impacts_units  -- Convert from thousands to actual
FROM cache_route_impacts_15min_by_demo
WHERE frameid = 1234567890
  AND time_window_start = '2025-10-15 19:30:00'
ORDER BY demographic_segment;
```

**Expected Output**:
```
demographic_segment | impacts | impacts_units
--------------------|---------|---------------
abc1                | 12.456  | 12456
age_15_34           | 23.789  | 23789
age_35_plus         | 34.567  | 34567
all_adults          | 58.356  | 58356
c2de                | 45.900  | 45900
children_hh         | 15.234  | 15234
main_shopper        | 28.901  | 28901
```

#### Example 2: Campaign Total Impacts by Demographic

```sql
-- Get total impacts for campaign 18295 across all time, by demographic
SELECT
    demographic_segment,
    SUM(impacts) as total_impacts_thousands,
    SUM(impacts) * 1000 as total_impacts_units,
    COUNT(DISTINCT frameid) as frame_count,
    COUNT(*) as time_window_count
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
GROUP BY demographic_segment
ORDER BY total_impacts_thousands DESC;
```

**Expected Output**:
```
demographic_segment | total_impacts_thousands | total_impacts_units | frame_count | time_window_count
--------------------|-------------------------|---------------------|-------------|-------------------
all_adults          | 5234567.890            | 5234567890          | 450         | 12500
abc1                | 2345678.901            | 2345678901          | 450         | 12500
age_35_plus         | 3456789.012            | 3456789012          | 450         | 12500
...
```

#### Example 3: Time-of-Day Analysis (Hourly Aggregation)

```sql
-- Get hourly impacts for campaign 18295, all_adults demographic
SELECT
    DATE_TRUNC('hour', time_window_start) as hour,
    SUM(impacts) as total_impacts_thousands,
    COUNT(DISTINCT frameid) as active_frames
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
  AND demographic_segment = 'all_adults'
  AND time_window_start::date BETWEEN '2025-10-01' AND '2025-10-31'
GROUP BY hour
ORDER BY hour;
```

**Use Case**: Build hour-by-hour reach curves or identify peak performance times.

#### Example 4: Daypart Comparison

```sql
-- Compare performance across 4 dayparts for campaign 18295
-- Dayparts: Morning (06:00-09:59), Daytime (10:00-15:59), Evening (16:00-18:59), Night (19:00-05:59)
SELECT
    CASE
        WHEN EXTRACT(HOUR FROM time_window_start) BETWEEN 6 AND 9 THEN 'Morning'
        WHEN EXTRACT(HOUR FROM time_window_start) BETWEEN 10 AND 15 THEN 'Daytime'
        WHEN EXTRACT(HOUR FROM time_window_start) BETWEEN 16 AND 18 THEN 'Evening'
        ELSE 'Night'
    END as daypart,
    demographic_segment,
    SUM(impacts) as total_impacts_thousands,
    COUNT(DISTINCT frameid) as frame_count
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
  AND time_window_start::date BETWEEN '2025-10-01' AND '2025-10-31'
GROUP BY daypart, demographic_segment
ORDER BY daypart, total_impacts_thousands DESC;
```

#### Example 5: Multi-Campaign Comparison

```sql
-- Compare demographic performance across multiple campaigns
SELECT
    campaign_id,
    demographic_segment,
    SUM(impacts) as total_impacts_thousands,
    ROUND(SUM(impacts) * 1000) as total_impacts_units
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id IN ('18295', '18425', '18578')
  AND demographic_segment IN ('all_adults', 'age_15_34', 'abc1')
GROUP BY campaign_id, demographic_segment
ORDER BY campaign_id, demographic_segment;
```

**Use Case**: Portfolio analysis across multiple campaigns.

### Materialized Views (Pre-Aggregated)

The demographic cache includes 5 materialized views for faster queries. These are **read-only** and refreshed nightly.

#### mv_cache_campaign_impacts_15min

Campaign-level totals at 15-minute granularity (no frame-level detail).

```sql
-- Get campaign totals by 15-minute window
SELECT
    time_window_start,
    demographic_segment,
    total_impacts,
    frame_count
FROM mv_cache_campaign_impacts_15min
WHERE campaign_id = '18295'
  AND demographic_segment = 'all_adults'
  AND time_window_start::date = '2025-10-15'
ORDER BY time_window_start;
```

**Performance**: 5-10x faster than aggregating base table.

#### mv_cache_campaign_impacts_1hr

Campaign-level totals at 1-hour granularity.

```sql
-- Get hourly campaign totals
SELECT
    hour_start,
    demographic_segment,
    total_impacts
FROM mv_cache_campaign_impacts_1hr
WHERE campaign_id = '18295'
  AND demographic_segment = 'all_adults'
  AND hour_start::date BETWEEN '2025-10-01' AND '2025-10-31'
ORDER BY hour_start;
```

#### mv_cache_campaign_impacts_day

Campaign-level totals by calendar day.

```sql
-- Get daily campaign totals
SELECT
    date,
    demographic_segment,
    total_impacts,
    frame_count
FROM mv_cache_campaign_impacts_day
WHERE campaign_id = '18295'
  AND demographic_segment = 'all_adults'
ORDER BY date;
```

**Use Case**: Daily performance tracking, trend analysis.

#### mv_cache_campaign_impacts_daypart

Campaign-level totals by daypart (4 time periods per day).

```sql
-- Get daypart performance
-- Daypart values: 1=Morning (06:00-09:59), 2=Daytime (10:00-15:59),
--                 3=Evening (16:00-18:59), 4=Night (19:00-05:59)
SELECT
    date,
    daypart,
    demographic_segment,
    total_impacts
FROM mv_cache_campaign_impacts_daypart
WHERE campaign_id = '18295'
  AND demographic_segment = 'all_adults'
ORDER BY date, daypart;
```

#### mv_cache_campaign_impacts_week

Campaign-level totals by week (Monday-Sunday).

```sql
-- Get weekly campaign totals
SELECT
    week_start,  -- Monday of the week
    demographic_segment,
    total_impacts,
    frame_count
FROM mv_cache_campaign_impacts_week
WHERE campaign_id = '18295'
  AND demographic_segment = 'all_adults'
ORDER BY week_start;
```

**Performance Note**: Materialized views are typically **5-20x faster** than base table queries for aggregations. Use them when frame-level detail is not needed.

---

## Campaign Reach Cache - Daily/Weekly/Full

### Overview

The campaign reach cache stores **de-duplicated reach metrics** (unique people reached) at three time granularities. These caches answer "How many unique people saw this campaign?"

**Key Metrics**:
- **Reach**: Unique people reached (in thousands)
- **GRP**: Gross Rating Points (impressions as % of population)
- **Frequency**: Average exposures per person (impacts / reach)
- **Total Impacts**: Total audience impressions (in thousands)

### Table 1: `cache_campaign_reach_day`

**Purpose**: Daily reach metrics for each campaign.

**Use Cases**:
- Daily performance tracking
- Build daily reach curves
- Identify high/low performing days

#### Schema

```sql
cache_campaign_reach_day (
    buyer_id         VARCHAR,
    campaign_id      VARCHAR,
    date             DATE,
    reach            NUMERIC(15,3),  -- In thousands (000s)
    grp              NUMERIC(10,3),
    frequency        NUMERIC(10,3),  -- Average exposures per person
    total_impacts    NUMERIC(15,3),  -- In thousands (000s)
    frame_count      INTEGER,
    route_release_id INTEGER,
    cached_at        TIMESTAMP,
    UNIQUE (buyer_id, campaign_id, date)
)
```

#### Query Examples

##### Example 1: Get Daily Reach for Single Campaign

```sql
-- Get daily reach for campaign 18295
SELECT
    date,
    reach,
    grp,
    frequency,
    total_impacts,
    frame_count
FROM cache_campaign_reach_day
WHERE campaign_id = '18295'
ORDER BY date;
```

**Expected Output**:
```
date       | reach    | grp    | frequency | total_impacts | frame_count
-----------|----------|--------|-----------|---------------|-------------
2025-10-06 | 1234.567 | 12.34  | 3.45      | 4256.789      | 45
2025-10-07 | 1345.678 | 13.45  | 3.56      | 4789.012      | 48
2025-10-08 | 1456.789 | 14.56  | 3.67      | 5345.678      | 52
...
```

##### Example 2: Build Cumulative Reach Curve

```sql
-- Calculate running cumulative reach across campaign days
-- WARNING: This is NOT de-duplicated across days! See cache_campaign_reach_week for true cumulative reach.
WITH daily_reach AS (
    SELECT
        date,
        reach,
        total_impacts,
        ROW_NUMBER() OVER (ORDER BY date) as day_number
    FROM cache_campaign_reach_day
    WHERE campaign_id = '18295'
)
SELECT
    date,
    day_number,
    reach as daily_reach,
    SUM(reach) OVER (ORDER BY date) as cumulative_reach_estimate,  -- ESTIMATE ONLY!
    total_impacts as daily_impacts,
    SUM(total_impacts) OVER (ORDER BY date) as cumulative_impacts
FROM daily_reach
ORDER BY date;
```

**⚠️ IMPORTANT**: Daily reach values are **independent** (de-duplicated within each day only). You **cannot simply sum daily reach** to get true cumulative reach because people can see ads on multiple days. Use `cache_campaign_reach_week` (cumulative mode) for accurate cumulative reach.

##### Example 3: Find Best Performing Days

```sql
-- Find top 10 days by reach for campaign 18295
SELECT
    date,
    reach,
    grp,
    frequency,
    frame_count,
    RANK() OVER (ORDER BY reach DESC) as reach_rank
FROM cache_campaign_reach_day
WHERE campaign_id = '18295'
ORDER BY reach DESC
LIMIT 10;
```

##### Example 4: Multi-Campaign Daily Comparison

```sql
-- Compare daily reach across multiple campaigns
SELECT
    c.campaign_id,
    c.date,
    c.reach,
    c.grp,
    c.frequency
FROM cache_campaign_reach_day c
WHERE c.campaign_id IN ('18295', '18425', '18578')
  AND c.date BETWEEN '2025-10-01' AND '2025-10-31'
ORDER BY c.campaign_id, c.date;
```

##### Example 5: Average Daily Performance

```sql
-- Get average daily performance metrics for campaign 18295
SELECT
    campaign_id,
    COUNT(*) as days_active,
    ROUND(AVG(reach), 2) as avg_daily_reach,
    ROUND(AVG(grp), 2) as avg_daily_grp,
    ROUND(AVG(frequency), 2) as avg_frequency,
    ROUND(AVG(frame_count)) as avg_frames_per_day
FROM cache_campaign_reach_day
WHERE campaign_id = '18295'
GROUP BY campaign_id;
```

---

### Table 2: `cache_campaign_reach_week`

**Purpose**: Weekly reach metrics with two modes: **individual weeks** (non-overlapping 7-day periods) and **cumulative weeks** (running total from campaign start).

**Use Cases**:
- Weekly performance reports
- True cumulative reach curves (use `reach_type = 'cumulative'`)
- Week-over-week comparison (use `reach_type = 'individual'`)

#### Schema

```sql
cache_campaign_reach_week (
    id               SERIAL,
    buyer_id         VARCHAR,
    campaign_id      VARCHAR,
    week_number      INTEGER,  -- 1, 2, 3, etc. from campaign start
    start_date       DATE,     -- Campaign start date (same for all weeks)
    end_date         DATE,     -- End of this period
    days             INTEGER,  -- Number of days in period
    reach            NUMERIC(15,3),
    grp              NUMERIC(10,3),
    frequency        NUMERIC(10,3),
    total_impacts    NUMERIC(15,3),
    frame_count      INTEGER,
    route_release_id INTEGER,
    cached_at        TIMESTAMP,
    reach_type       VARCHAR(20),  -- 'individual' OR 'cumulative'
    UNIQUE (buyer_id, campaign_id, week_number, reach_type)
)
```

**Key Column**: `reach_type`
- `'individual'`: Week 1 = days 0-6, Week 2 = days 7-13 (non-overlapping, independent reach)
- `'cumulative'`: Week 1 = days 0-6, Week 2 = days 0-13 (running total, de-duplicated across weeks)

#### Query Examples

##### Example 1: Get Cumulative Reach Curve

```sql
-- Build true cumulative reach curve for campaign 18295
-- This is de-duplicated reach (people counted only once across all weeks)
SELECT
    week_number,
    end_date,
    days,
    reach as cumulative_reach,
    grp as cumulative_grp,
    frequency,
    total_impacts as cumulative_impacts
FROM cache_campaign_reach_week
WHERE campaign_id = '18295'
  AND reach_type = 'cumulative'
ORDER BY week_number;
```

**Expected Output**:
```
week_number | end_date   | days | cumulative_reach | cumulative_grp | frequency | cumulative_impacts
------------|------------|------|------------------|----------------|-----------|--------------------
1           | 2025-10-12 | 7    | 2345.678         | 23.45          | 4.56      | 10700.123
2           | 2025-10-19 | 14   | 3456.789         | 34.56          | 5.67      | 19600.456
3           | 2025-10-26 | 21   | 4123.890         | 41.23          | 6.12      | 25234.789
...
```

**Use Case**: Build reach curves showing how unique reach grows over campaign duration. This is the **correct way** to measure cumulative reach.

##### Example 2: Get Week-Over-Week Performance

```sql
-- Compare independent weekly reach (non-cumulative)
-- Each week is de-duplicated within itself only
SELECT
    week_number,
    start_date,
    end_date,
    days,
    reach as weekly_reach,
    grp as weekly_grp,
    frequency,
    total_impacts as weekly_impacts,
    frame_count
FROM cache_campaign_reach_week
WHERE campaign_id = '18295'
  AND reach_type = 'individual'
ORDER BY week_number;
```

**Use Case**: Weekly performance reports where each week is independent.

##### Example 3: Compare Individual vs Cumulative Reach

```sql
-- See the difference between individual and cumulative reach
SELECT
    week_number,
    MAX(CASE WHEN reach_type = 'individual' THEN reach END) as individual_reach,
    MAX(CASE WHEN reach_type = 'cumulative' THEN reach END) as cumulative_reach,
    MAX(CASE WHEN reach_type = 'cumulative' THEN reach END) -
        COALESCE(SUM(CASE WHEN reach_type = 'individual' THEN reach END), 0) as deduplication_savings
FROM cache_campaign_reach_week
WHERE campaign_id = '18295'
GROUP BY week_number
ORDER BY week_number;
```

**Use Case**: Understand how much reach overlap exists week-over-week.

##### Example 4: Calculate Reach Growth Rate

```sql
-- Calculate week-over-week reach growth percentage
WITH weekly_cumulative AS (
    SELECT
        week_number,
        reach,
        LAG(reach) OVER (ORDER BY week_number) as prev_week_reach
    FROM cache_campaign_reach_week
    WHERE campaign_id = '18295'
      AND reach_type = 'cumulative'
)
SELECT
    week_number,
    reach as cumulative_reach,
    prev_week_reach,
    CASE
        WHEN prev_week_reach IS NOT NULL AND prev_week_reach > 0
        THEN ROUND(((reach - prev_week_reach) / prev_week_reach * 100), 2)
        ELSE NULL
    END as growth_percentage
FROM weekly_cumulative
ORDER BY week_number;
```

**Expected Output**:
```
week_number | cumulative_reach | prev_week_reach | growth_percentage
------------|------------------|-----------------|-------------------
1           | 2345.678         | NULL            | NULL
2           | 3456.789         | 2345.678        | 47.35
3           | 4123.890         | 3456.789        | 19.30
4           | 4567.890         | 4123.890        | 10.77
...
```

**Use Case**: Measure diminishing returns as campaign reaches saturation.

##### Example 5: Multi-Campaign Weekly Comparison

```sql
-- Compare cumulative reach across multiple campaigns at week 4
SELECT
    campaign_id,
    week_number,
    reach as cumulative_reach,
    grp as cumulative_grp,
    frequency
FROM cache_campaign_reach_week
WHERE campaign_id IN ('18295', '18425', '18578')
  AND week_number = 4
  AND reach_type = 'cumulative'
ORDER BY reach DESC;
```

---

### Table 3: `cache_campaign_reach_full`

**Purpose**: Total campaign reach metrics across entire campaign duration.

**Use Cases**:
- Campaign summary reports
- Portfolio analysis
- Final performance measurement

#### Schema

```sql
cache_campaign_reach_full (
    id               SERIAL,
    buyer_id         VARCHAR,
    campaign_id      VARCHAR,
    start_date       DATE,
    end_date         DATE,
    days             INTEGER,
    reach            NUMERIC(15,3),
    grp              NUMERIC(10,3),
    frequency        NUMERIC(10,3),
    total_impacts    NUMERIC(15,3),
    frame_count      INTEGER,
    route_release_id INTEGER,
    cached_at        TIMESTAMP,
    UNIQUE (buyer_id, campaign_id, start_date, end_date)
)
```

#### Query Examples

##### Example 1: Get Total Campaign Reach

```sql
-- Get final reach metrics for campaign 18295
SELECT
    campaign_id,
    start_date,
    end_date,
    days,
    reach,
    grp,
    frequency,
    total_impacts,
    frame_count,
    -- Calculate reach efficiency (reach per frame)
    ROUND(reach / frame_count, 2) as reach_per_frame
FROM cache_campaign_reach_full
WHERE campaign_id = '18295';
```

**Expected Output**:
```
campaign_id | start_date | end_date   | days | reach    | grp    | frequency | total_impacts | frame_count | reach_per_frame
------------|------------|------------|------|----------|--------|-----------|---------------|-------------|----------------
18295       | 2025-10-06 | 2025-12-13 | 68   | 5234.567 | 52.34  | 7.89      | 41234.567     | 450         | 11.63
```

##### Example 2: Multi-Campaign Portfolio Analysis

```sql
-- Compare full campaign performance across portfolio
SELECT
    campaign_id,
    start_date,
    end_date,
    days,
    reach,
    grp,
    frequency,
    total_impacts,
    frame_count,
    ROUND(reach / NULLIF(days, 0), 2) as avg_daily_reach,
    ROUND(total_impacts / NULLIF(frame_count, 0), 2) as avg_impacts_per_frame
FROM cache_campaign_reach_full
WHERE campaign_id IN ('18295', '18425', '18578')
ORDER BY reach DESC;
```

##### Example 3: Find Top Performing Campaigns

```sql
-- Rank campaigns by reach efficiency
SELECT
    campaign_id,
    reach,
    grp,
    frequency,
    frame_count,
    days,
    ROUND(reach / NULLIF(frame_count, 0), 2) as reach_per_frame,
    RANK() OVER (ORDER BY reach / NULLIF(frame_count, 0) DESC) as efficiency_rank
FROM cache_campaign_reach_full
ORDER BY efficiency_rank
LIMIT 20;
```

##### Example 4: Campaign Duration Analysis

```sql
-- Analyze relationship between campaign duration and reach
SELECT
    CASE
        WHEN days <= 7 THEN '1 week'
        WHEN days <= 14 THEN '2 weeks'
        WHEN days <= 30 THEN '3-4 weeks'
        WHEN days <= 60 THEN '5-8 weeks'
        ELSE '9+ weeks'
    END as duration_bucket,
    COUNT(*) as campaign_count,
    ROUND(AVG(reach), 2) as avg_reach,
    ROUND(AVG(frequency), 2) as avg_frequency,
    ROUND(AVG(frame_count)) as avg_frame_count
FROM cache_campaign_reach_full
GROUP BY duration_bucket
ORDER BY MIN(days);
```

##### Example 5: Buyer-Level Aggregation

```sql
-- Sum reach across all campaigns for each buyer
-- WARNING: This sums independent reaches - actual cross-campaign reach would be lower due to overlap
SELECT
    buyer_id,
    COUNT(DISTINCT campaign_id) as campaign_count,
    SUM(reach) as total_reach_estimate,  -- NOT de-duplicated across campaigns!
    SUM(total_impacts) as total_impacts,
    AVG(frequency) as avg_frequency,
    SUM(frame_count) as total_frames
FROM cache_campaign_reach_full
GROUP BY buyer_id
ORDER BY total_reach_estimate DESC;
```

**⚠️ IMPORTANT**: Reach values from different campaigns **cannot be summed** to get de-duplicated cross-campaign reach. People may see multiple campaigns. This query provides an upper-bound estimate only.

---

## Brand Reach Cache - Brand Performance

### Table: `cache_campaign_brand_reach`

**Purpose**: Store reach metrics filtered by brand within campaigns. Enables brand-level performance analysis when campaigns contain multiple brands.

**Use Cases**:
- Brand performance within multi-brand campaigns
- Brand-level reach curves
- Brand comparison within same campaign
- Agency reporting by brand

### Schema

```sql
cache_campaign_brand_reach (
    campaign_id       VARCHAR,
    brand_id          VARCHAR,
    date_from         DATE,
    date_to           DATE,
    aggregation_level VARCHAR(20),  -- 'day', 'week-individual', 'week-cumulative', 'full'
    reach             NUMERIC(15,3),
    grp               NUMERIC(10,3),
    frequency         NUMERIC(10,3),
    total_impacts     NUMERIC(15,3),
    frame_count       INTEGER,
    route_release_id  INTEGER,
    cached_at         TIMESTAMP,
    PRIMARY KEY (campaign_id, brand_id, date_from, date_to, aggregation_level)
)
```

**Key Column**: `aggregation_level`
- `'day'`: Single day reach per brand
- `'week-individual'`: Independent 7-day periods per brand (weeks 1, 2, 3...)
- `'week-cumulative'`: Cumulative from campaign start per brand
- `'full'`: Entire campaign duration per brand

### Query Examples

#### Example 1: Get All Brands in Campaign

```sql
-- Find all brands in campaign 18295 with their full campaign reach
SELECT
    brand_id,
    date_from,
    date_to,
    reach,
    grp,
    frequency,
    total_impacts,
    frame_count,
    ROUND(reach / NULLIF(frame_count, 0), 2) as reach_per_frame
FROM cache_campaign_brand_reach
WHERE campaign_id = '18295'
  AND aggregation_level = 'full'
ORDER BY reach DESC;
```

**Expected Output**:
```
brand_id | date_from  | date_to    | reach    | grp   | frequency | total_impacts | frame_count | reach_per_frame
---------|------------|------------|----------|-------|-----------|---------------|-------------|----------------
21239    | 2025-10-06 | 2025-12-13 | 3456.789 | 34.56 | 6.78      | 23456.789     | 280         | 12.35
21240    | 2025-10-06 | 2025-12-13 | 1234.567 | 12.34 | 5.67      | 7000.123      | 120         | 10.29
21241    | 2025-10-06 | 2025-12-13 | 567.890  | 5.67  | 4.56      | 2589.456      | 50          | 11.36
```

#### Example 2: Build Brand-Level Reach Curve

```sql
-- Get cumulative reach curve for brand 21239 in campaign 18295
SELECT
    brand_id,
    date_from,
    date_to,
    EXTRACT(DAY FROM (date_to - date_from)) + 1 as days,
    reach as cumulative_reach,
    grp as cumulative_grp,
    frequency,
    total_impacts as cumulative_impacts
FROM cache_campaign_brand_reach
WHERE campaign_id = '18295'
  AND brand_id = '21239'
  AND aggregation_level = 'week-cumulative'
ORDER BY date_to;
```

**Use Case**: Show how brand reach builds over time within campaign.

#### Example 3: Compare Brand Performance by Week

```sql
-- Compare independent weekly performance across brands
SELECT
    brand_id,
    date_from,
    date_to,
    reach as weekly_reach,
    grp as weekly_grp,
    frequency,
    frame_count
FROM cache_campaign_brand_reach
WHERE campaign_id = '18295'
  AND aggregation_level = 'week-individual'
ORDER BY brand_id, date_from;
```

#### Example 4: Brand Daily Performance

```sql
-- Get daily reach for all brands in campaign 18295
SELECT
    date_from as date,
    brand_id,
    reach as daily_reach,
    grp as daily_grp,
    frequency,
    frame_count
FROM cache_campaign_brand_reach
WHERE campaign_id = '18295'
  AND aggregation_level = 'day'
  AND date_from BETWEEN '2025-10-01' AND '2025-10-31'
ORDER BY date_from, brand_id;
```

#### Example 5: Calculate Brand Share of Campaign Reach

```sql
-- Calculate each brand's share of total campaign reach
WITH brand_reach AS (
    SELECT
        brand_id,
        reach,
        total_impacts,
        frame_count
    FROM cache_campaign_brand_reach
    WHERE campaign_id = '18295'
      AND aggregation_level = 'full'
),
campaign_total AS (
    SELECT
        reach as campaign_reach,
        total_impacts as campaign_impacts,
        frame_count as campaign_frames
    FROM cache_campaign_reach_full
    WHERE campaign_id = '18295'
)
SELECT
    b.brand_id,
    b.reach as brand_reach,
    c.campaign_reach,
    ROUND((b.reach / NULLIF(c.campaign_reach, 0) * 100), 2) as reach_share_pct,
    b.frame_count as brand_frames,
    c.campaign_frames,
    ROUND((b.frame_count::NUMERIC / NULLIF(c.campaign_frames, 0) * 100), 2) as frame_share_pct
FROM brand_reach b
CROSS JOIN campaign_total c
ORDER BY reach_share_pct DESC;
```

**Expected Output**:
```
brand_id | brand_reach | campaign_reach | reach_share_pct | brand_frames | campaign_frames | frame_share_pct
---------|-------------|----------------|-----------------|--------------|-----------------|----------------
21239    | 3456.789    | 5234.567       | 66.04           | 280          | 450             | 62.22
21240    | 1234.567    | 5234.567       | 23.59           | 120          | 450             | 26.67
21241    | 567.890     | 5234.567       | 10.85           | 50           | 450             | 11.11
```

#### Example 6: Multi-Campaign Brand Comparison

```sql
-- Compare same brand across multiple campaigns
SELECT
    campaign_id,
    brand_id,
    date_from,
    date_to,
    EXTRACT(DAY FROM (date_to - date_from)) + 1 as days,
    reach,
    grp,
    frequency,
    frame_count,
    ROUND(reach / NULLIF(frame_count, 0), 2) as reach_per_frame
FROM cache_campaign_brand_reach
WHERE brand_id = '21239'
  AND aggregation_level = 'full'
ORDER BY reach DESC;
```

**Use Case**: Track brand performance across different campaigns and time periods.

#### Example 7: Find Best Performing Brand Days

```sql
-- Find top 10 daily brand performances across all campaigns
SELECT
    campaign_id,
    brand_id,
    date_from as date,
    reach as daily_reach,
    grp as daily_grp,
    frequency,
    frame_count,
    RANK() OVER (ORDER BY reach DESC) as reach_rank
FROM cache_campaign_brand_reach
WHERE aggregation_level = 'day'
ORDER BY reach DESC
LIMIT 10;
```

---

## Integration Patterns

### Pattern 1: API Endpoint Design

**Recommended approach**: Create dedicated cache endpoints that mirror POC needs.

#### Example: Campaign Summary Endpoint

```python
# Pseudocode: Flask/FastAPI endpoint
@app.get("/api/campaigns/{campaign_id}/summary")
def get_campaign_summary(campaign_id: str):
    """Get full campaign metrics from cache."""
    query = """
        SELECT
            campaign_id,
            start_date,
            end_date,
            days,
            reach,
            grp,
            frequency,
            total_impacts,
            frame_count,
            route_release_id,
            cached_at
        FROM cache_campaign_reach_full
        WHERE campaign_id = %s
    """
    result = db.execute(query, (campaign_id,))
    return result.to_dict()
```

#### Example: Daily Reach Curve Endpoint

```python
@app.get("/api/campaigns/{campaign_id}/reach-curve/daily")
def get_daily_reach_curve(campaign_id: str):
    """Get daily reach curve from cache."""
    query = """
        SELECT
            date,
            reach,
            grp,
            frequency,
            total_impacts,
            frame_count
        FROM cache_campaign_reach_day
        WHERE campaign_id = %s
        ORDER BY date
    """
    results = db.execute(query, (campaign_id,))
    return {
        "campaign_id": campaign_id,
        "data_points": results.to_dict(orient='records')
    }
```

#### Example: Brand Performance Endpoint

```python
@app.get("/api/campaigns/{campaign_id}/brands")
def get_campaign_brands(campaign_id: str):
    """Get brand-level performance from cache."""
    query = """
        SELECT
            brand_id,
            reach,
            grp,
            frequency,
            total_impacts,
            frame_count
        FROM cache_campaign_brand_reach
        WHERE campaign_id = %s
          AND aggregation_level = 'full'
        ORDER BY reach DESC
    """
    results = db.execute(query, (campaign_id,))
    return {
        "campaign_id": campaign_id,
        "brands": results.to_dict(orient='records')
    }
```

### Pattern 2: Cache-First with Fallback

Check cache first, fall back to Route API if missing.

```python
def get_campaign_reach(campaign_id: str, start_date: date, end_date: date) -> dict:
    """Get campaign reach with cache-first strategy."""

    # Try cache first
    cache_query = """
        SELECT reach, grp, frequency, total_impacts
        FROM cache_campaign_reach_full
        WHERE campaign_id = %s
          AND start_date = %s
          AND end_date = %s
    """
    result = db.execute(cache_query, (campaign_id, start_date, end_date))

    if result:
        return {
            "source": "cache",
            "reach": result["reach"],
            "grp": result["grp"],
            "frequency": result["frequency"],
            "total_impacts": result["total_impacts"]
        }

    # Cache miss - fall back to Route API
    route_response = call_route_api(campaign_id, start_date, end_date)

    # Optionally: Write to cache for next time
    write_to_cache(campaign_id, start_date, end_date, route_response)

    return {
        "source": "api",
        "reach": route_response["reach"],
        ...
    }
```

### Pattern 3: Demographic Breakdown with Impacts

Combine demographic cache with campaign metrics.

```python
@app.get("/api/campaigns/{campaign_id}/demographics")
def get_campaign_demographics(campaign_id: str):
    """Get demographic breakdown with impacts from cache."""
    query = """
        SELECT
            demographic_segment,
            SUM(impacts) * 1000 as total_impacts,
            COUNT(DISTINCT frameid) as frame_count,
            MIN(time_window_start::date) as start_date,
            MAX(time_window_end::date) as end_date
        FROM cache_route_impacts_15min_by_demo
        WHERE campaign_id = %s
        GROUP BY demographic_segment
        ORDER BY total_impacts DESC
    """
    results = db.execute(query, (campaign_id,))
    return {
        "campaign_id": campaign_id,
        "demographics": results.to_dict(orient='records')
    }
```

### Pattern 4: Time-Series Data for Charts

Optimize for charting libraries (e.g., Chart.js, Plotly).

```python
@app.get("/api/campaigns/{campaign_id}/daily-timeseries")
def get_daily_timeseries(campaign_id: str):
    """Get time-series data optimized for charts."""
    query = """
        SELECT
            date,
            reach,
            grp,
            frequency
        FROM cache_campaign_reach_day
        WHERE campaign_id = %s
        ORDER BY date
    """
    results = db.execute(query, (campaign_id,))

    # Format for Chart.js
    return {
        "labels": [row["date"].isoformat() for row in results],
        "datasets": [
            {
                "label": "Reach",
                "data": [row["reach"] for row in results]
            },
            {
                "label": "GRP",
                "data": [row["grp"] for row in results]
            }
        ]
    }
```

### Pattern 5: Pagination for Large Result Sets

Paginate when returning many campaigns.

```python
@app.get("/api/campaigns")
def list_campaigns(page: int = 1, page_size: int = 50):
    """List all campaigns with pagination."""
    offset = (page - 1) * page_size

    query = """
        SELECT
            campaign_id,
            start_date,
            end_date,
            days,
            reach,
            grp,
            frame_count
        FROM cache_campaign_reach_full
        ORDER BY reach DESC
        LIMIT %s OFFSET %s
    """
    results = db.execute(query, (page_size, offset))

    count_query = "SELECT COUNT(*) FROM cache_campaign_reach_full"
    total = db.execute(count_query)[0]["count"]

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
        "campaigns": results.to_dict(orient='records')
    }
```

---

## Performance Best Practices

### 1. Always Filter by Indexed Columns

**Good** (uses indexes):
```sql
-- Uses idx_reach_day_buyer_campaign index
SELECT * FROM cache_campaign_reach_day
WHERE buyer_id = '12345' AND campaign_id = '18295';

-- Uses idx_impacts_demo_campaign index
SELECT * FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295' AND demographic_segment = 'all_adults';
```

**Bad** (table scan):
```sql
-- No index on frame_count
SELECT * FROM cache_campaign_reach_day
WHERE frame_count > 100;
```

### 2. Use Materialized Views for Aggregations

**Good** (10x faster):
```sql
-- Use pre-aggregated materialized view
SELECT * FROM mv_cache_campaign_impacts_day
WHERE campaign_id = '18295';
```

**Bad** (slow):
```sql
-- Aggregating base table
SELECT
    time_window_start::date as date,
    SUM(impacts) as total_impacts
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
GROUP BY time_window_start::date;
```

### 3. Limit Result Sets

Always use `LIMIT` when exploring data:
```sql
-- Good: Limit results
SELECT * FROM cache_campaign_reach_day
ORDER BY date DESC
LIMIT 100;
```

### 4. Use EXPLAIN ANALYZE for Slow Queries

```sql
EXPLAIN ANALYZE
SELECT * FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
  AND demographic_segment = 'all_adults';
```

Look for:
- **Seq Scan** (bad) → Add index or use better filter
- **Index Scan** (good) → Query is optimized
- **Execution time** > 1 second → Consider caching or optimization

### 5. Avoid Joining Across Large Tables

**Bad** (slow):
```sql
-- Joining 192M playout_data with 252M demographic cache
SELECT p.*, d.impacts
FROM playout_data p
JOIN cache_route_impacts_15min_by_demo d
  ON p.frameid = d.frameid
  AND p.startdate = d.time_window_start;
```

**Good** (use cache only):
```sql
-- Query cache tables directly
SELECT campaign_id, SUM(impacts) as total_impacts
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
GROUP BY campaign_id;
```

### 6. Batch API Requests

When building POC endpoints, batch database queries:

```python
# Good: Single query for multiple campaigns
campaign_ids = ['18295', '18425', '18578']
query = """
    SELECT campaign_id, reach, grp, frequency
    FROM cache_campaign_reach_full
    WHERE campaign_id = ANY(%s)
"""
results = db.execute(query, (campaign_ids,))

# Bad: Multiple queries
for campaign_id in campaign_ids:
    query = "SELECT * FROM cache_campaign_reach_full WHERE campaign_id = %s"
    result = db.execute(query, (campaign_id,))  # N queries!
```

---

## Common Pitfalls

### Pitfall 1: Summing Daily Reach for Cumulative

**❌ WRONG**:
```sql
-- This is INCORRECT! Daily reach values are independent (not de-duplicated across days)
SELECT SUM(reach) as cumulative_reach  -- WRONG!
FROM cache_campaign_reach_day
WHERE campaign_id = '18295';
```

**✅ CORRECT**:
```sql
-- Use week cache with cumulative mode
SELECT reach as true_cumulative_reach
FROM cache_campaign_reach_week
WHERE campaign_id = '18295'
  AND reach_type = 'cumulative'
ORDER BY week_number DESC
LIMIT 1;

-- OR use full campaign cache
SELECT reach as true_cumulative_reach
FROM cache_campaign_reach_full
WHERE campaign_id = '18295';
```

**Why**: Reach measures **unique people**. Someone who sees an ad on Monday and Tuesday is counted as **1 person** in cumulative reach, but appears in **both** daily reach values. You must use de-duplicated cumulative caches.

### Pitfall 2: Summing Reach Across Campaigns

**❌ WRONG**:
```sql
-- This overestimates reach! People can see multiple campaigns.
SELECT SUM(reach) as total_reach  -- WRONG!
FROM cache_campaign_reach_full
WHERE campaign_id IN ('18295', '18425');
```

**✅ CORRECT**:
```sql
-- Either:
-- 1. Call Route API with combined frame list (expensive)
-- 2. Acknowledge this is an ESTIMATE (upper bound)
SELECT
    SUM(reach) as estimated_max_reach,
    'This is an UPPER BOUND estimate - actual reach is lower due to cross-campaign overlap' as warning
FROM cache_campaign_reach_full
WHERE campaign_id IN ('18295', '18425');
```

### Pitfall 3: Mixing Impacts Units

**❌ WRONG**:
```sql
-- Cache stores impacts in THOUSANDS, but user expects actual units
SELECT impacts as audience_size  -- WRONG! Off by 1000x
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295';
```

**✅ CORRECT**:
```sql
-- Always multiply by 1000 to get actual units
SELECT
    impacts * 1000 as impacts_units,
    'Impacts in actual audience impressions' as note
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295';
```

### Pitfall 4: Ignoring Route Release ID

**❌ WRONG**:
```sql
-- Missing route_release_id filter could mix different Route releases
SELECT * FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295';
```

**✅ CORRECT**:
```sql
-- Always check which Route release data came from
SELECT
    campaign_id,
    route_release_id,
    SUM(impacts) as total_impacts
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
  AND route_release_id = 56  -- Explicit Route R56
GROUP BY campaign_id, route_release_id;
```

**Note**: Currently all cached data uses Route R56. Future releases may require filtering.

### Pitfall 5: Querying Base Table Instead of Materialized View

**❌ SLOW**:
```sql
-- Aggregating 252M rows
SELECT
    campaign_id,
    time_window_start::date as date,
    demographic_segment,
    SUM(impacts) as total_impacts
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
GROUP BY campaign_id, time_window_start::date, demographic_segment;
-- Takes 5-10 seconds
```

**✅ FAST**:
```sql
-- Use pre-aggregated materialized view
SELECT
    campaign_id,
    date,
    demographic_segment,
    total_impacts
FROM mv_cache_campaign_impacts_day
WHERE campaign_id = '18295';
-- Takes 50-100ms (100x faster!)
```

### Pitfall 6: Not Checking Cache Coverage

**❌ WRONG**:
```sql
-- Assumes cache has data for this campaign
SELECT reach FROM cache_campaign_reach_full
WHERE campaign_id = '99999';
-- Returns empty set - cache may not have this campaign!
```

**✅ CORRECT**:
```python
# Check cache coverage first
cache_result = db.execute("""
    SELECT reach FROM cache_campaign_reach_full
    WHERE campaign_id = %s
""", (campaign_id,))

if not cache_result:
    # Cache miss - handle gracefully
    return {"error": "Campaign not found in cache", "campaign_id": campaign_id}

return cache_result
```

---

## Cache Freshness

### Update Schedule

| Cache Type | Update Frequency | Backfill Window | Lag Time |
|------------|-----------------|-----------------|----------|
| Demographic Cache | Nightly | Last 7 days (local), 80 days (MS-01) | +1 day |
| Campaign Reach Cache | Weekly | All active campaigns | +1 week |
| Brand Reach Cache | Weekly | All active campaigns | +1 week |

### Checking Cache Freshness

```sql
-- Check when demographic cache was last updated
SELECT
    campaign_id,
    MAX(cached_at) as last_cached,
    NOW() - MAX(cached_at) as cache_age
FROM cache_route_impacts_15min_by_demo
WHERE campaign_id = '18295'
GROUP BY campaign_id;
```

**Expected Output**:
```
campaign_id | last_cached          | cache_age
------------|----------------------|-----------
18295       | 2025-11-11 23:45:12  | 14:23:45
```

### Cache Coverage Query

```sql
-- Check which campaigns are in cache vs playout_data
WITH playout_campaigns AS (
    SELECT DISTINCT
        REGEXP_REPLACE(TRIM(buyercampaignref), '\.0$', '') as campaign_id
    FROM playout_data
),
cached_campaigns AS (
    SELECT DISTINCT campaign_id
    FROM cache_campaign_reach_full
)
SELECT
    (SELECT COUNT(*) FROM playout_campaigns) as total_campaigns,
    (SELECT COUNT(*) FROM cached_campaigns) as cached_campaigns,
    (SELECT COUNT(*) FROM playout_campaigns) -
        (SELECT COUNT(*) FROM cached_campaigns) as missing_campaigns;
```

**Expected Output**:
```
total_campaigns | cached_campaigns | missing_campaigns
----------------|------------------|-------------------
826             | 790              | 36
```

### Detecting Stale Data

```sql
-- Find campaigns with stale cache data (not updated in 7+ days)
SELECT
    campaign_id,
    MAX(cached_at) as last_cached,
    NOW() - MAX(cached_at) as cache_age
FROM cache_route_impacts_15min_by_demo
GROUP BY campaign_id
HAVING NOW() - MAX(cached_at) > INTERVAL '7 days'
ORDER BY cache_age DESC;
```

---

## When to Call the Route API Directly

### Cache vs API Decision Matrix

| Scenario | Use Cache | Call API | Reason |
|----------|-----------|----------|--------|
| Campaign already cached | ✅ | ❌ | Sub-second query vs 5-30s API call |
| New campaign (not in cache) | ❌ | ✅ | Cache doesn't have data yet |
| Custom demographic not in cache | ❌ | ✅ | Cache only has 7 standard demographics |
| Real-time "what-if" analysis | ❌ | ✅ | Testing frame combinations not yet played |
| Historical campaign analysis | ✅ | ❌ | Cache has 80 days on MS-01 |
| Large campaign (>10MB JSON) | ✅ | ⚠️ | Use week-cumulative cache, API will fail |

### Route API Endpoint Structure

The Route API uses a single endpoint for reach calculations:

```
POST https://route.mediatelapi.co.uk/rest/process/custom
```

**Authentication Required:**
- `Authorization: Basic <base64(username:password)>`
- `X-Api-Key: <your_api_key>`

### Understanding Frames vs Schedules

**Critical Concept**: Route API requires BOTH frame IDs and schedule times.

```python
# Example: Calculate reach for a campaign
request = {
    "route_release_id": 56,          # Route R56 release
    "algorithm_figures": ["reach", "grp", "frequency", "impacts"],
    "demographics": [{"demographic_id": 1}],  # All adults 15+
    "campaign": [{
        "frames": [12345, 12346, 12347],      # Frame IDs from playout_data
        "schedule": [                          # When playouts occurred
            {"datetime_from": "2025-10-01 09:00", "datetime_until": "2025-10-01 09:30"},
            {"datetime_from": "2025-10-01 12:00", "datetime_until": "2025-10-01 12:30"},
            {"datetime_from": "2025-10-01 18:00", "datetime_until": "2025-10-01 18:30"}
        ],
        "spot_length": 10,
        "spot_break_length": 50
    }],
    "target_month": 10  # October
}
```

**Key Points:**
- **Frames**: Which screens/locations the ads played on
- **Schedules**: When the ads played (15-minute windows)
- **Both are required** - you can't get reach without both frame AND time context
- **Deduplication**: Route API handles overlapping frames across time windows

### Query Pattern 1: Single Campaign Reach

Get reach metrics for one campaign:

```python
from route_api.client import RouteAPIClient

# Initialize client (uses .env credentials)
client = RouteAPIClient()

# Get playout data for campaign
query = """
    SELECT
        frameid,
        DATE_TRUNC('minute', startdate)::timestamp +
            ((EXTRACT(minute FROM startdate)::int / 15) * INTERVAL '15 minutes') as time_window_start,
        DATE_TRUNC('minute', startdate)::timestamp +
            ((EXTRACT(minute FROM startdate)::int / 15) * INTERVAL '15 minutes') + INTERVAL '15 minutes' as time_window_end
    FROM playout_data
    WHERE buyercampaignref = '18425'
      AND startdate >= '2025-10-01'
      AND startdate < '2025-11-01'
"""

# Convert to Route API format
frames = list(set(row['frameid'] for row in results))
schedules = [
    {
        "datetime_from": row['time_window_start'].strftime('%Y-%m-%d %H:%M'),
        "datetime_until": row['time_window_end'].strftime('%Y-%m-%d %H:%M')
    }
    for row in results
]

# Call Route API
response = client.call_process_custom(
    schedules=schedules,
    frames=frames,
    route_release_id=56,
    target_month=10,
    demographics=[{"demographic_id": 1}]  # All adults
)

print(f"Reach: {response['reach']}")
print(f"GRP: {response['grp']}")
print(f"Frequency: {response['frequency']}")
```

### Query Pattern 2: Multi-Demographic Breakdown

Get reach for multiple demographics in one API call:

```python
# Standard Route demographics
demographics = [
    {"demographic_id": 1},   # All adults 15+
    {"demographic_id": 2},   # Age 16-34
    {"demographic_id": 3},   # Age 35-54
    {"demographic_id": 4},   # Age 55+
    {"demographic_id": 5},   # ABC1 socio-economic
    {"demographic_id": 6},   # C2DE socio-economic
    {"demographic_id": 7}    # Households
]

response = client.call_process_custom(
    schedules=schedules,
    frames=frames,
    route_release_id=56,
    target_month=10,
    demographics=demographics  # Get all 7 demographics at once
)

# Response has separate metrics for each demographic
for demo in response['demographics']:
    print(f"{demo['name']}: Reach={demo['reach']}, GRP={demo['grp']}")
```

### Query Pattern 3: Brand-Specific Reach

Get reach for frames associated with specific brands:

```python
# Get frames for a specific brand within campaign
query = """
    SELECT DISTINCT
        frameid,
        spacebrandid
    FROM playout_data
    WHERE buyercampaignref = '18425'
      AND spacebrandid = '21239'
      AND startdate >= '2025-10-01'
      AND startdate < '2025-11-01'
"""

brand_frames = [row['frameid'] for row in results]

# Get schedules for these brand frames
schedule_query = """
    SELECT
        DATE_TRUNC('minute', startdate)::timestamp +
            ((EXTRACT(minute FROM startdate)::int / 15) * INTERVAL '15 minutes') as time_window_start,
        DATE_TRUNC('minute', startdate)::timestamp +
            ((EXTRACT(minute FROM startdate)::int / 15) * INTERVAL '15 minutes') + INTERVAL '15 minutes' as time_window_end
    FROM playout_data
    WHERE buyercampaignref = '18425'
      AND spacebrandid = '21239'
      AND frameid = ANY(%s)
      AND startdate >= '2025-10-01'
      AND startdate < '2025-11-01'
"""

brand_schedules = [
    {
        "datetime_from": row['time_window_start'].strftime('%Y-%m-%d %H:%M'),
        "datetime_until": row['time_window_end'].strftime('%Y-%m-%d %H:%M')
    }
    for row in results
]

# Call API with brand-specific frames
response = client.call_process_custom(
    schedules=brand_schedules,
    frames=brand_frames,
    route_release_id=56,
    target_month=10
)
```

### Handling API Limitations

#### 10MB JSON Payload Limit

Large campaigns can exceed Route API's 10MB JSON request limit:

```python
# Check if campaign is too large for full-campaign API call
check_query = """
    SELECT
        campaign_id,
        can_cache_full,
        full_cache_limitation_reason,
        json_size_mb
    FROM campaign_cache_limitations
    WHERE campaign_id = '18425'
"""

limitation = db.execute(check_query)

if limitation and not limitation['can_cache_full']:
    print(f"⚠️ Campaign exceeds 10MB limit ({limitation['json_size_mb']} MB)")
    print(f"Reason: {limitation['full_cache_limitation_reason']}")
    print("Solution: Use cache_campaign_reach_week (week-cumulative) instead of full")

    # Use cached week data instead
    week_query = """
        SELECT * FROM cache_campaign_reach_week
        WHERE campaign_id = '18425'
          AND reach_type = 'cumulative'
        ORDER BY date_from
    """
```

**Large Campaign Strategy:**
1. Check `campaign_cache_limitations` table first
2. If `can_cache_full = FALSE`, use week-level cache or API calls
3. Break large campaigns into weekly chunks for API calls
4. Aggregate weekly results for total campaign reach (use cumulative weeks)

#### Frame Count Limit (10,000 per request)

Route API accepts maximum 10,000 frames per call:

```python
MAX_FRAMES = 10000

if len(frames) > MAX_FRAMES:
    print(f"⚠️ Campaign has {len(frames)} frames, exceeding {MAX_FRAMES} limit")

    # Strategy 1: Use temporal batching (weeks)
    weekly_results = []
    for week_start in week_starts:
        week_frames = get_frames_for_week(campaign_id, week_start)
        if len(week_frames) <= MAX_FRAMES:
            response = client.call_process_custom(
                schedules=get_schedules_for_week(campaign_id, week_start),
                frames=week_frames,
                route_release_id=56,
                target_month=month
            )
            weekly_results.append(response)

    # Strategy 2: Use cached data instead
    # Large campaigns should already be in cache
    cache_query = """
        SELECT reach, grp, frequency
        FROM cache_campaign_reach_full
        WHERE campaign_id = '18425'
    """
```

### Rate Limiting and API Accounts

**CRITICAL**: The demographic cacher automatically alternates between API accounts (ianw + euanm).

**Rate Limits:**
- 6 calls per second per account
- 12 calls per second combined (with dual accounts)

**For POC Application:**
```python
# Initialize client with specific account
client_ianw = RouteAPIClient(
    api_key=os.getenv('ROUTE_API_KEY_IANW'),
    username=os.getenv('ROUTE_API_User_Name_IANW'),
    password=os.getenv('ROUTE_API_Password_IANW')
)

client_euanm = RouteAPIClient(
    api_key=os.getenv('ROUTE_API_KEY_EUANM'),
    username=os.getenv('ROUTE_API_User_Name_EUANM'),
    password=os.getenv('ROUTE_API_Password_EUANM')
)

# Round-robin between accounts
clients = [client_ianw, client_euanm]
current_client_index = 0

for campaign in campaigns:
    client = clients[current_client_index]
    response = client.call_process_custom(...)
    current_client_index = (current_client_index + 1) % len(clients)
```

**Built-in rate limiting**: `RouteAPIClient` automatically limits to 6 calls/second.

### Error Handling

```python
import requests

try:
    response = client.call_process_custom(
        schedules=schedules,
        frames=frames,
        route_release_id=56,
        target_month=10
    )

    if response['success']:
        print(f"✅ Reach: {response['reach']}")
    else:
        print(f"❌ API error: {response['error']}")

except ValueError as e:
    # Frame count validation or parameter errors
    print(f"❌ Validation error: {e}")
    # Solution: Check frame count, split into batches

except requests.Timeout:
    # API took too long (>30 seconds default)
    print("❌ API timeout - campaign may be too large")
    # Solution: Break into smaller time windows, use cache

except requests.HTTPError as e:
    if e.response.status_code == 413:
        # Payload too large (>10MB)
        print("❌ Request too large - exceeds 10MB limit")
        # Solution: Use week-level aggregation, add to campaign_cache_limitations
    elif e.response.status_code == 401:
        print("❌ Authentication failed - check API credentials")
    elif e.response.status_code == 429:
        print("❌ Rate limit exceeded - slow down API calls")
    else:
        print(f"❌ API error: {e}")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

### When to Cache API Results

**After calling the API, consider caching the results:**

```python
# After successful API call
if response['success']:
    # Store in cache_campaign_reach_full or appropriate cache table
    cache_insert = """
        INSERT INTO cache_campaign_reach_full (
            buyer_id, campaign_id, start_date, end_date, days,
            reach, grp, frequency, impacts, frame_count, cached_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
        )
        ON CONFLICT (buyer_id, campaign_id)
        DO UPDATE SET
            reach = EXCLUDED.reach,
            grp = EXCLUDED.grp,
            frequency = EXCLUDED.frequency,
            impacts = EXCLUDED.impacts,
            frame_count = EXCLUDED.frame_count,
            cached_at = NOW()
    """

    db.execute(cache_insert, (
        buyer_id,
        campaign_id,
        start_date,
        end_date,
        days,
        response['reach'],
        response['grp'],
        response['frequency'],
        response['impacts'],
        frame_count
    ))

    print("✅ Results cached for future queries")
```

### API Best Practices Summary

1. **Always check cache first** - avoid API call if data already cached
2. **Check `campaign_cache_limitations`** - know if campaign is too large before trying
3. **Use temporal batching** - break large campaigns into weeks or days
4. **Aggregate schedules** - use 15-minute windows, not individual spots
5. **Handle frame limit** - split if >10,000 frames
6. **Implement error handling** - gracefully handle timeouts, size limits, rate limits
7. **Cache successful results** - avoid repeated API calls
8. **Use dual accounts** - maximize throughput with round-robin
9. **Log API calls** - track usage, performance, errors
10. **Fallback to cache** - if API fails, use cached data even if slightly stale

---

## Next Steps

1. **Try Example Queries**: Copy queries from this guide into your SQL client
2. **Build POC Endpoints**: Use integration patterns to create API endpoints
3. **Monitor Performance**: Use `EXPLAIN ANALYZE` to optimize slow queries
4. **Check Coverage**: Verify cache has data for your target campaigns
5. **Test API Integration**: Start with small campaigns before calling API for large ones
6. **Read Backfill Docs**: See `docs/05-workflows/cache-backfill-reference.md` for cache maintenance

---

## See Also

- **Cache Backfill Reference**: `docs/05-workflows/cache-backfill-reference.md`
- **Database Schema**: `docs/03-database/schema.md`
- **System Architecture**: `docs/02-architecture/system-overview.md`
- **Script Reference**: `docs/04-scripts-reference/tools-overview.md`

---

**Questions or Issues?** Contact the Route Playout Pipeline team or see `docs/08-troubleshooting/`.
