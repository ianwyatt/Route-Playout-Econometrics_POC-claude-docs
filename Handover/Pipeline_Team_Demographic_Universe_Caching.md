# Pipeline Team Handover: Demographic Universe Caching

**Date**: 2025-11-20
**From**: POC Team (UI Development)
**To**: Pipeline Team (Data Ingestion & Caching)
**Priority**: Medium
**Status**: 🟡 Pending Pipeline Team Implementation

---

## Executive Summary

The POC UI needs to display **Cover (% of total population reached)** for campaigns. To calculate this, we need the universe/population size for each demographic target (e.g., GB All Adults 15+, 15-34, 35-54, etc.) for each Route release.

**Formula**: `Cover % = (Reach / Universe) × 100`

**Request**: Pipeline team to cache demographic universe sizes from Route API into a database table.

---

## Background

### Current State
- ✅ We cache reach, impacts, GRPs, and frequency from Route API
- ✅ Campaign browser displays reach and impacts
- ❌ We cannot display Cover % because we don't have universe sizes cached

### Desired State
- ✅ Universe sizes cached for all demographics we use
- ✅ Cover % calculated and displayed in campaign browser UI
- ✅ Universe data refreshed when new Route releases are published

---

## Technical Requirements

### 1. Route API Endpoint

**Endpoint**: `POST https://route.mediatelapi.co.uk/rest/validate/demographic`

**Purpose**: Returns the universe/population size for a given demographic target

**Request Format**:
```json
{
  "route_release_id": "55",
  "demographics": ["ageband>=1"]
}
```

**Response Format** (expected):
```json
{
  "demographics": [
    {
      "code": "ageband>=1",
      "description": "All Adults 15+",
      "universe": 53156000
    }
  ]
}
```

**Note**: Verify the actual response structure from Route API documentation or test call.

---

### 2. Database Schema

Create a new table to cache demographic universe sizes:

```sql
-- Table: cache_demographic_universes
CREATE TABLE cache_demographic_universes (
    id SERIAL PRIMARY KEY,
    route_release_id INTEGER NOT NULL,
    demographic_code VARCHAR(100) NOT NULL,
    demographic_description VARCHAR(255),
    universe BIGINT NOT NULL,
    cached_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint: one universe per demographic per release
    CONSTRAINT unique_release_demographic
        UNIQUE (route_release_id, demographic_code)
);

-- Indexes for fast lookups
CREATE INDEX idx_demographic_universe_release
    ON cache_demographic_universes(route_release_id);

CREATE INDEX idx_demographic_universe_code
    ON cache_demographic_universes(demographic_code);

-- Example data
-- INSERT INTO cache_demographic_universes
--     (route_release_id, demographic_code, demographic_description, universe)
-- VALUES
--     (55, 'ageband>=1', 'All Adults 15+', 53156000),
--     (55, 'ageband=1', 'Adults 15-34', 14237000),
--     (55, 'ageband=2', 'Adults 35-54', 17653000),
--     (55, 'ageband=3', 'Adults 55+', 21266000);
```

---

### 3. Demographics to Cache

**Priority 1** (Required for POC):
- `ageband>=1` - All Adults 15+ (GB)

**Priority 2** (Nice to have for future):
- `ageband=1` - Adults 15-34
- `ageband=2` - Adults 35-54
- `ageband=3` - Adults 55+
- Any other demographics we plan to support in the UI

---

### 4. Implementation Steps

1. **Add API Integration**
   - Add function to call Route API `POST validate/demographic` endpoint
   - Parse response to extract universe sizes
   - Handle errors (API down, invalid response, etc.)

2. **Create Caching Logic**
   - Create table `cache_demographic_universes` (if not exists)
   - For each Route release in `route_releases` table:
     - Call API for each demographic we support
     - Store universe size in database
     - Log success/failures

3. **Schedule Updates**
   - Run when new Route releases are published (quarterly)
   - Or run on-demand via management command
   - Add to existing pipeline data refresh workflow

4. **Add Validation**
   - Verify universe sizes are reasonable (e.g., 40-60M for GB All Adults)
   - Alert if universe changes dramatically between releases (>10% change)
   - Log all cached values for audit trail

---

### 5. Data Refresh Cadence

**Trigger**: When new Route release is published (quarterly)

**Process**:
1. Detect new Route release in system
2. Call `validate/demographic` for all supported demographics
3. Cache universe sizes in `cache_demographic_universes`
4. Verify data looks correct
5. Notify POC team when complete

**Alternative**: Manual trigger via management command for testing/backfill

---

## POC Team Integration Plan

Once pipeline team completes this work, POC team will:

1. **Update materialized view** `mv_campaign_browser` to include:
   ```sql
   -- Join to get universe size
   LEFT JOIN cache_demographic_universes cdu
       ON cri.route_release_id = cdu.route_release_id
       AND cdu.demographic_code = 'ageband>=1'

   -- Calculate cover
   (cri.total_reach_all_adults * 1000) / cdu.universe * 100 AS cover_pct_all_adults
   ```

2. **Add Cover column to UI** campaign browser table
3. **Display as percentage** with 1 decimal place (e.g., "12.4%")

---

## Testing Criteria

### Unit Tests
- ✅ API call returns expected universe size
- ✅ Database insert works correctly
- ✅ Unique constraint prevents duplicates
- ✅ Universe sizes are within reasonable bounds

### Integration Tests
- ✅ Can retrieve universe for given release + demographic
- ✅ Cover calculation produces reasonable percentages (0-100%)
- ✅ Handles missing universe data gracefully

### Manual Testing
```sql
-- Verify data cached correctly
SELECT
    route_release_id,
    demographic_code,
    demographic_description,
    universe,
    cached_at
FROM cache_demographic_universes
ORDER BY route_release_id DESC, demographic_code;

-- Test cover calculation for campaign 18694
SELECT
    c.campaign_id,
    c.reach * 1000 as reach_absolute,
    u.universe,
    (c.reach * 1000.0 / u.universe * 100) as cover_pct
FROM cache_campaign_reach_full c
JOIN cache_demographic_universes u
    ON c.route_release_id = u.route_release_id
    AND u.demographic_code = 'ageband>=1'
WHERE c.campaign_id = '18694';
```

Expected: Cover % should be between 0-100%, typically 5-40% for most campaigns.

---

## Acceptance Criteria

- [ ] `cache_demographic_universes` table created with indexes
- [ ] Universe sizes cached for Route releases R54, R55, R56 (last 3 releases)
- [ ] At minimum, "All Adults 15+" (ageband>=1) universe cached
- [ ] Data verified to be reasonable (40-60M for GB All Adults)
- [ ] Documentation updated with table schema and usage
- [ ] Handover document created for POC team with:
  - Table name and schema
  - Sample query to retrieve universe sizes
  - Any caveats or limitations
  - Refresh schedule/process

---

## API Reference

### Route API Endpoint

**URL**: `POST https://route.mediatelapi.co.uk/rest/validate/demographic`

**Authentication**: Same as other Route API calls (API key + authorization header)

**Request Example**:
```bash
curl -X POST https://route.mediatelapi.co.uk/rest/validate/demographic \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "route_release_id": "55",
    "demographics": ["ageband>=1", "ageband=1", "ageband=2", "ageband=3"]
  }'
```

**Response Example** (verify actual structure):
```json
{
  "demographics": [
    {
      "code": "ageband>=1",
      "description": "All Adults 15+",
      "universe": 53156000,
      "valid": true
    },
    {
      "code": "ageband=1",
      "description": "Adults 15-34",
      "universe": 14237000,
      "valid": true
    }
  ]
}
```

---

## Contact & Questions

**POC Team Lead**: Doctor Biz
**Pipeline Team Lead**: [TBD]

**Questions or Issues?**
- Check Route API documentation for `validate/demographic` endpoint
- Verify response format with test API call
- Coordinate with POC team if universe calculation seems incorrect

---

## Timeline

**Estimated Effort**: 2-4 hours
- 1 hour: API integration
- 1 hour: Database schema + caching logic
- 1 hour: Testing + verification
- 1 hour: Documentation + handover

**Target Completion**: [To be scheduled with pipeline team]

---

## Handover Back to POC Team

When pipeline team completes this work, please provide:

1. ✅ Confirmation that `cache_demographic_universes` table is created and populated
2. ✅ List of Route releases cached (e.g., R54, R55, R56)
3. ✅ List of demographics cached (e.g., ageband>=1, ageband=1, etc.)
4. ✅ Sample query demonstrating how to retrieve universe for a given release + demographic
5. ✅ Any caveats or limitations we should be aware of
6. ✅ Refresh schedule/process documentation

**Handover Format**: Markdown document in `/Claude/Handover/` directory

---

*Document created: 2025-11-20*
*Last updated: 2025-11-20*
*Status: 🟡 Awaiting Pipeline Team Implementation*
