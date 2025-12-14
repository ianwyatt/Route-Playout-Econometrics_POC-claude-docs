# ABOUTME: Technical debt documentation for route_frames/route_frame_details consolidation
# ABOUTME: Tracks the issue, impact, and remediation plan

# Technical Debt: Consolidate route_frames and route_frame_details

**Priority**: HIGH
**Status**: OPEN
**Created**: 2025-12-05
**Owner**: Pipeline Team

---

## Summary

The database has two separate tables for frame data that should be consolidated into one:
- `route_frames` - Core frame data with coordinates
- `route_frame_details` - Extended frame metadata

These tables share the same composite key (`release_id`, `frameid`) and are **always joined together** in every query. This is unnecessary complexity.

---

## Current State

### route_frames
```sql
CREATE TABLE route_frames (
    id              BIGSERIAL PRIMARY KEY,
    release_id      INTEGER NOT NULL,
    frameid         BIGINT NOT NULL,
    frame_reference VARCHAR(50),
    environmentid   INTEGER,
    formatid        INTEGER,
    mediaownerid    INTEGER,
    illumination    VARCHAR(20),
    latitude        DECIMAL(10, 8),    -- ⬅️ ONLY UNIQUE DATA
    longitude       DECIMAL(11, 8)     -- ⬅️ ONLY UNIQUE DATA
);
```

### route_frame_details
```sql
CREATE TABLE route_frame_details (
    id                  BIGSERIAL PRIMARY KEY,
    release_id          INTEGER NOT NULL,
    frameid             BIGINT NOT NULL,
    environment_name    VARCHAR(100),
    environment_type    VARCHAR(50),
    format_name         VARCHAR(100),
    format_width        DECIMAL(10, 2),
    format_height       DECIMAL(10, 2),
    format_orientation  VARCHAR(20),
    mediaowner_name     VARCHAR(200),
    mediaowner_code     VARCHAR(50),
    postcode            VARCHAR(20),
    town                VARCHAR(100),
    barb_region_name    VARCHAR(100),
    additional_metadata JSONB
);
```

---

## Problem

### 1. Redundant Joins
Every POC query that needs frame data must join both tables:

```sql
-- From src/db/streamlit_queries.py (appears 5+ times)
JOIN route_frames rf ON mf.frameid = rf.frameid
JOIN route_frame_details rfd ON rf.release_id = rfd.release_id AND rf.frameid = rfd.frameid
```

### 2. Only 2 Columns Are Unique
The ONLY data in `route_frames` not duplicated in `route_frame_details`:
- `latitude`
- `longitude`

All other columns either:
- Are the same (`frameid`, `release_id`)
- Have human-readable equivalents in `route_frame_details` (e.g., `mediaownerid` → `mediaowner_name`)

### 3. Maintenance Burden
- Two tables to keep in sync
- Two tables to update when Route API changes
- Two tables to include in backups/restores
- Confusion for new developers

### 4. Performance Impact
- Extra join in every geographic query
- Additional index maintenance
- More complex query plans

---

## Impact Assessment

### POC Queries Affected
| Query Function | File | Line |
|----------------|------|------|
| `get_frame_geographic_data_sync` | streamlit_queries.py | 653-679 |
| `get_regional_impacts_sync` | streamlit_queries.py | 701-722 |
| `get_environment_impacts_sync` | streamlit_queries.py | 747-792 |
| `get_frame_audience_table_sync` | streamlit_queries.py | 1117-1119 |
| `mv_frame_audience_daily` | MV definition | - |
| `mv_frame_audience_hourly` | MV definition | - |

### Estimated Savings
- **Query simplification**: Remove 1 join from 6+ query patterns
- **MV simplification**: Simpler denormalised view definitions
- **Developer time**: Less confusion, faster onboarding

---

## Proposed Solution

### Target State: Single Consolidated Table

```sql
CREATE TABLE route_frame_details (
    -- Primary key
    release_id          INTEGER NOT NULL,
    frameid             BIGINT NOT NULL,

    -- Coordinates (from route_frames)
    latitude            DECIMAL(10, 8),
    longitude           DECIMAL(11, 8),

    -- Frame identity
    frame_reference     VARCHAR(50),
    illumination        VARCHAR(20),

    -- Environment
    environment_name    VARCHAR(100),
    environment_type    VARCHAR(50),

    -- Format
    format_name         VARCHAR(100),
    format_width        DECIMAL(10, 2),
    format_height       DECIMAL(10, 2),
    format_orientation  VARCHAR(20),

    -- Media owner
    mediaowner_name     VARCHAR(200),
    mediaowner_code     VARCHAR(50),

    -- Location
    postcode            VARCHAR(20),
    town                VARCHAR(100),
    barb_region_name    VARCHAR(100),

    -- Extensibility
    additional_metadata JSONB,

    PRIMARY KEY (release_id, frameid)
);

-- Indexes
CREATE INDEX idx_route_frame_details_frameid ON route_frame_details(frameid);
CREATE INDEX idx_route_frame_details_release ON route_frame_details(release_id);
CREATE INDEX idx_route_frame_details_town ON route_frame_details(town);
CREATE INDEX idx_route_frame_details_region ON route_frame_details(barb_region_name);
```

---

## Migration Plan

### Phase 1: Adwanted Delivery (Immediate)
- Request consolidated table from Adwanted in batch spec
- Adwanted provides single `route_frame_details` with lat/lon included
- No migration needed for new data

### Phase 2: POC Update (After Adwanted delivery)
1. Update all POC queries to use single table
2. Remove joins to `route_frames`
3. Update MVs (`mv_frame_audience_daily`, `mv_frame_audience_hourly`)
4. Test thoroughly

### Phase 3: Pipeline Update (Coordinate with pipeline team)
1. Update pipeline to populate consolidated table
2. Deprecate `route_frames` table
3. Drop `route_frames` after validation period

### Phase 4: Cleanup
1. Remove `route_frames` from all documentation
2. Update ARCHITECTURE.md
3. Archive migration scripts

---

## Queries to Update (POC)

After consolidation, queries simplify from:

```sql
-- BEFORE (2 joins)
FROM mv_cache_campaign_impacts_frame mf
JOIN route_frames rf ON mf.frameid = rf.frameid
JOIN route_frame_details rfd ON rf.release_id = rfd.release_id AND rf.frameid = rfd.frameid
WHERE ...
```

To:

```sql
-- AFTER (1 join)
FROM mv_cache_campaign_impacts_frame mf
JOIN route_frame_details rfd ON mf.frameid = rfd.frameid AND mf.route_release_id = rfd.release_id
WHERE ...
```

---

## Decision Log

| Date | Decision | By |
|------|----------|-----|
| 2025-12-05 | Identified as technical debt | POC Team |
| 2025-12-05 | Recommendation: consolidate for Adwanted spec | POC Team |
| | | |

---

## Related Documents

- `docs/pipeline-handover/ADWANTED_SPEC_POC_REQUIREMENTS.md` - Adwanted spec feedback
- `docs/pipeline-handover/MV_FRAME_AUDIENCE_FIX_2025-11-29.md` - Join logic documentation
- `src/db/streamlit_queries.py` - Affected queries

---

## Action Required

1. **Pipeline Team**: Include consolidated table in Adwanted spec
2. **POC Team**: Update queries after new data structure is available
3. **Both Teams**: Coordinate deprecation of `route_frames`

---

*Created: 2025-12-05*
*Status: OPEN - Awaiting Adwanted delivery*
