# Pipeline Request: Consolidate route_frames and route_frame_details

**Date:** 6 December 2025
**From:** POC Team
**Priority:** Medium (technical debt cleanup)
**Impact:** Simplifies queries, reduces joins, prepares for production

---

## Summary

The POC currently uses two tables for frame data that are **always joined together**:
- `route_frames` - Core identity + coordinates
- `route_frame_details` - Extended metadata

These should be consolidated into a single `route_frame_details` table that includes latitude/longitude.

---

## Current State (Technical Debt)

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
    latitude        DECIMAL(10, 8),   -- Only unique data
    longitude       DECIMAL(11, 8),   -- Only unique data
    UNIQUE(release_id, frameid)
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
    additional_metadata JSONB,
    UNIQUE(release_id, frameid)
);
```

### How POC Joins Them (Every Query)

```sql
-- This pattern appears everywhere in the POC
JOIN route_frames rf ON mf.frameid = rf.frameid
JOIN route_frame_details rfd ON rf.release_id = rfd.release_id AND rf.frameid = rfd.frameid
```

The **only unique data** in `route_frames` is `latitude` and `longitude`. Everything else is redundant or lookup IDs that aren't used.

---

## Requested Change

### Consolidated route_frame_details

```sql
CREATE TABLE route_frame_details (
    id                  BIGSERIAL PRIMARY KEY,
    release_id          INTEGER NOT NULL,
    frameid             BIGINT NOT NULL,
    -- Coordinates (moved from route_frames)
    latitude            DECIMAL(10, 8),
    longitude           DECIMAL(11, 8),
    -- Existing metadata
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
    additional_metadata JSONB,
    UNIQUE(release_id, frameid)
);

-- Indexes
CREATE INDEX idx_frame_details_frameid ON route_frame_details(frameid);
CREATE INDEX idx_frame_details_release ON route_frame_details(release_id);
CREATE INDEX idx_frame_details_lookup ON route_frame_details(release_id, frameid);
CREATE INDEX idx_frame_details_coords ON route_frame_details(latitude, longitude);
CREATE INDEX idx_frame_details_town ON route_frame_details(town);
CREATE INDEX idx_frame_details_region ON route_frame_details(barb_region_name);
```

---

## Migration Steps

### 1. Add columns to route_frame_details
```sql
ALTER TABLE route_frame_details
ADD COLUMN latitude DECIMAL(10, 8),
ADD COLUMN longitude DECIMAL(11, 8);
```

### 2. Populate from route_frames
```sql
UPDATE route_frame_details rfd
SET
    latitude = rf.latitude,
    longitude = rf.longitude
FROM route_frames rf
WHERE rfd.release_id = rf.release_id
  AND rfd.frameid = rf.frameid;
```

### 3. Add coordinate index
```sql
CREATE INDEX idx_frame_details_coords
ON route_frame_details(latitude, longitude);
```

### 4. Notify POC team
Once complete, notify POC team to update queries.

### 5. (Future) Drop route_frames
After POC confirms migration complete, drop redundant table:
```sql
DROP TABLE route_frames;
```

---

## POC Changes Required After Migration

The POC team will update all queries from:
```sql
-- OLD (two joins)
JOIN route_frames rf ON mf.frameid = rf.frameid
JOIN route_frame_details rfd ON rf.release_id = rfd.release_id AND rf.frameid = rfd.frameid
```

To:
```sql
-- NEW (single join)
JOIN route_frame_details rfd ON rr.id = rfd.release_id AND mf.frameid = rfd.frameid
```

**Files to update:**
- `src/db/queries/geographic.py`
- `src/db/queries/frame_audience.py`
- Any denormalised MVs that reference both tables

---

## Benefits

1. **Simpler queries** - One join instead of two
2. **Better performance** - Fewer joins = faster queries
3. **Cleaner schema** - No redundant tables
4. **Easier maintenance** - Single source of truth for frame data
5. **Production-ready** - Cleaner architecture for future deployment

---

## Timeline

No urgency - this is technical debt cleanup. Can be done when convenient.

**Notify POC team when complete** so we can update our queries.

---

## Contact

**POC Team:** Route Playout Econometrics POC
**Related Doc:** `Claude/Documentation/TECHNICAL_DEBT_FRAME_TABLES.md`

---

*Version 1.0 | 6 December 2025*
