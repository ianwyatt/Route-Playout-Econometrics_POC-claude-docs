# Pipeline Changes Affecting POC

**Purpose**: Track pipeline changes that affect POC application
**Check Frequency**: Weekly
**Last Updated**: 2025-10-17

---

## How to Use This

- **[BREAKING]** = Requires POC code changes (act immediately)
- **[FEATURE]** = New capability available (optional integration)
- **[FYI]** = Informational only (no action needed)

---

## [Unreleased]

### Planned Features
- API caching system (see FUTURE_ROADMAP.md)
- SPACE entity lookup cache
- Route API audience cache

---

## [2025-10-17] - POC Handover Package Complete

### [FEATURE] Added

**Complete POC handover documentation package created:**
- `DATABASE_HANDOVER_FOR_POC.md` - Comprehensive database guide (1,150 lines)
- `QUICK_REFERENCE.md` - Quick lookup cheat sheet (360 lines)
- `PYTHON_EXAMPLES.py` - Ready-to-use integration code (680 lines)
- `FUTURE_ROADMAP.md` - Planned API caching features
- `SYNC_STRATEGY.md` - How to stay in sync with pipeline
- `CHANGELOG_FOR_POC.md` - This file

**What POC can do now:**
- Connect to MS-01 database (192.168.1.34:5432)
- Query `mv_playout_15min` for Route API data
- Get campaign summaries and statistics
- Determine Route releases for dates
- Split audience by brand (using `mv_playout_15min_brands`)

### POC Action Items
- ✅ Review `DATABASE_HANDOVER_FOR_POC.md`
- ✅ Test connection with `PYTHON_EXAMPLES.py`
- ✅ Integrate query functions into POC code
- ✅ Bookmark this CHANGELOG for weekly checks

### Breaking
- None (initial handover)

---

## [2025-10-15] - 15-Minute Aggregation Production Ready

### [FEATURE] Added

**New materialized views** (PRIMARY for Route API integration):
- `mv_playout_15min` - Pre-aggregated 15-minute windows (~700M rows)
- `mv_playout_15min_brands` - Brand-level tracking (~750M rows)

**Schema:**
```sql
-- Core view for Route API
CREATE MATERIALIZED VIEW mv_playout_15min (
    frameid VARCHAR(50),
    buyercampaignref VARCHAR(50),
    time_window_start TIMESTAMP,        -- 15-min boundaries (:00, :15, :30, :45)
    spacemediaownerid VARCHAR(50),
    spacebuyerid VARCHAR(50),
    spaceagencyid VARCHAR(50),
    spot_count INTEGER,                 -- Number of playouts in window
    playout_length_seconds INTEGER,     -- Avg spot duration (rounded)
    break_length_seconds INTEGER,       -- Avg break duration (rounded)
    -- ... additional fields
);

-- Brand tracking (for multi-brand campaigns)
CREATE MATERIALIZED VIEW mv_playout_15min_brands (
    frameid VARCHAR(50),
    buyercampaignref VARCHAR(50),
    time_window_start TIMESTAMP,
    spacebrandid VARCHAR(50),
    spots_for_brand INTEGER,
    -- ... additional fields
);
```

**Unique constraint:** ONE row per (frameid, campaign, 15-min window) in main view

**Indexes:**
- `idx_mv_playout_15min_pk` (UNIQUE): frameid, time_window_start, buyercampaignref
- `idx_mv_playout_15min_campaign_time`: buyercampaignref, time_window_start
- `idx_mv_playout_15min_frame_time`: frameid, time_window_start
- `idx_mv_playout_15min_time`: time_window_start

### POC Integration
- **Use `mv_playout_15min` for Route API calls** (not raw `playout_data`)
- **10,000x faster** than aggregating raw data
- **Route API ready format** (one row = one Route API request)
- Query pattern:
  ```sql
  SELECT frameid, time_window_start, spot_count,
         playout_length_seconds, break_length_seconds
  FROM mv_playout_15min
  WHERE buyercampaignref = :campaign_id
    AND time_window_start >= :start_date
    AND time_window_start < :end_date
  ORDER BY frameid, time_window_start
  ```

### Changed
- Database size: 480GB → 596GB (added aggregation views)
- Daily refresh: Both views refreshed at 2am UTC (~50 min duration)

### Breaking
- None (new views, existing tables unchanged)

### POC Action Items
- ✅ Update queries to use `mv_playout_15min` instead of raw data
- ✅ See `PYTHON_EXAMPLES.py` for integration code
- ✅ Always include `time_window_start` filter for performance

---

## [2025-10-14] - PostgreSQL COPY Optimization

### [FYI] Performance Improvement

**Import performance**: 10-50x faster bulk imports using PostgreSQL COPY

**Impact on POC:**
- None (internal import optimization)
- Data refresh still happens at 2am UTC

### Changed
- Internal: Import method changed from execute_batch to COPY
- Internal: Local import + dump/restore strategy for large datasets

---

## [2025-09-10] - Initial Database Setup

### [FEATURE] Added

**Core tables created:**
- `playout_data` (1.28B records) - Raw playout events
- `playout_imports` (915 records) - Import tracking
- `playout_dates` (35 records) - Daily summaries
- `route_releases` (8 records) - Route release metadata (R54-R61)

**Date coverage:** August 6 - October 13, 2025 (69 days)

### POC Action Items
- ✅ Can query `playout_data` for raw data
- ✅ Use `route_releases` to determine Route release for dates

---

## Migration Guides

### Upgrading to Use mv_playout_15min

**Old code** (slow):
```python
# BAD: Aggregating raw data on-the-fly
query = """
    SELECT frameid,
           DATE_TRUNC('hour', startdate) +
               INTERVAL '15 minutes' * FLOOR(EXTRACT(minute FROM startdate) / 15) as window,
           COUNT(*) as spots,
           ROUND(AVG(spotlength / 1000)) as avg_length
    FROM playout_data
    WHERE buyercampaignref = %s
    GROUP BY frameid, window
    ORDER BY window
"""
# Takes 30+ seconds for large campaigns
```

**New code** (fast):
```python
# GOOD: Query pre-aggregated view
query = """
    SELECT frameid,
           time_window_start as window,
           spot_count as spots,
           playout_length_seconds as avg_length
    FROM mv_playout_15min
    WHERE buyercampaignref = %s
      AND time_window_start >= %s
      AND time_window_start < %s
    ORDER BY time_window_start
"""
# Takes < 1 second
```

**Key changes:**
1. Table: `playout_data` → `mv_playout_15min`
2. Add time filter (required for performance)
3. Use pre-computed fields (no aggregation needed)

---

## Rollback Procedures

### If mv_playout_15min Queries Fail

**Fallback to raw data:**
```python
# Emergency fallback
query = """
    SELECT * FROM playout_data
    WHERE buyercampaignref = %s
    LIMIT 1000
"""
# Slower but always works
```

**Contact pipeline team:** ian@route.org.uk

---

## Performance Notes

### Query Performance with mv_playout_15min

**Expected performance:**
- Campaign query (1 month): < 1 second
- Campaign summary: < 0.5 seconds
- Specific window lookup: < 0.1 seconds

**If queries are slow:**
1. Check: Is `time_window_start` filter present?
2. Run: `EXPLAIN ANALYZE <your query>`
3. Look for: "Index Scan" (good) vs "Seq Scan" (bad)
4. Contact: Pipeline team if still slow

---

## Known Issues

### None Currently

---

## Future Breaking Changes

### None Planned

All planned features (API caching) are additive and optional.

---

## Support

**Pipeline Team:** ian@route.org.uk
**Slack:** #route-playout-pipeline
**Documentation:** `Claude/POC_Handover/`

**For urgent issues:** Same-day email response

---

## Change Request Process

### POC Team Requests

1. **Need new data/view?**
   - Post in Slack or email
   - Describe use case
   - Pipeline team estimates effort

2. **Found a bug?**
   - Document issue with example query
   - Share expected vs actual results
   - Pipeline team investigates

3. **Performance issue?**
   - Share slow query
   - Share `EXPLAIN ANALYZE` output
   - Pipeline team optimizes

---

**Check this file weekly for updates!**

**Last reviewed:** 2025-10-17
**Next review:** 2025-10-24
