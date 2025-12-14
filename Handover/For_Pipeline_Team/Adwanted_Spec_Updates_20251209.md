# Adwanted Spec Updates Required

**Date:** 2025-12-09
**From:** POC Team
**To:** Pipeline Team
**Re:** Updates needed to ADWANTED_REQUEST_FINAL.md

---

## Summary

After reviewing the Adwanted batch data spec against POC UI requirements, we've identified updates needed before finalising the request.

---

## 1. Add Playout Aggregation Tables

**Rationale:** Raw playout_data is 11B+ records. Aggregating to 15-min/day/hour windows on our side would be extremely resource-intensive. Request Adwanted create these during batch processing.

### Add Table 14: playout_15min

15-minute aggregations of raw playouts (used for impacts queries).

| Column | Type | Description |
|--------|------|-------------|
| frameid | BIGINT | Frame identifier |
| campaign_id | STRING | Campaign reference (buyercampaignref) |
| time_window_start | DATETIME | 15-min window start (00:00, 00:15, 00:30, 00:45...) |
| time_window_end | DATETIME | 15-min window end |
| spot_count | INTEGER | Number of playouts in window |
| avg_spot_length_seconds | INTEGER | CEIL(AVG(spotlength) / 1000) |
| spacemediaownerid | INTEGER | Media owner ID |
| spacebuyerid | INTEGER | Buyer ID |
| spacebrandid | INTEGER | Brand ID |

### Add Table 15: playout_frame_day

Daily playout counts per frame (used for Frame Audiences daily tab).

| Column | Type | Description |
|--------|------|-------------|
| campaign_id | STRING | Campaign reference |
| frameid | BIGINT | Frame identifier |
| date | DATE | Calendar date |
| playout_count | INTEGER | Total playouts that day |

### Add Table 16: playout_frame_hour

Hourly playout counts per frame (used for Frame Audiences hourly tab).

| Column | Type | Description |
|--------|------|-------------|
| campaign_id | STRING | Campaign reference |
| frameid | BIGINT | Frame identifier |
| hour_start | DATETIME | Hour start |
| playout_count | INTEGER | Total playouts that hour |

---

## 2. Update campaign_cache_limitations Schema

**Current spec has:**
```
is_on_off_campaign, gap_days, active_periods, limitation_reason
```

**Simplified schema needed:**

| Column | Type | Description |
|--------|------|-------------|
| campaign_id | STRING | Campaign reference |
| buyer_id | STRING | Buyer ID |
| limitation_type | STRING | 'flighted_campaign' or 'no_route_frames' |
| limitation_reason | STRING | Human-readable explanation |
| detected_at | DATETIME | When detected |

**Limitation Types:**
- `flighted_campaign` - On/off patterns where cumulative reach is unavailable
- `no_route_frames` - Campaign has no frames in the Route release

**Note:** Remove JSON size limitation - Adwanted maintains the API so payload size isn't a constraint for them.

---

## 3. Naming Convention

Adwanted will deliver tables **without** the `mv_` prefix:

```
playout_15min
playout_frame_day
playout_frame_hour
```

This keeps naming clear - Adwanted-delivered tables are tables, not materialised views.

---

## 4. Post-Import: Create Alias Views (Pipeline Team Action Required)

The POC UI expects `mv_*` prefixed names. After importing Adwanted data, the pipeline team **must** create alias views:

```sql
-- Create alias views for POC compatibility
CREATE VIEW mv_playout_15min AS SELECT * FROM playout_15min;
CREATE VIEW mv_playout_frame_day AS SELECT * FROM playout_frame_day;
CREATE VIEW mv_playout_frame_hour AS SELECT * FROM playout_frame_hour;
```

| POC Expects | Adwanted Delivers |
|-------------|-------------------|
| `mv_playout_15min` | `playout_15min` |
| `mv_playout_frame_day` | `playout_frame_day` |
| `mv_playout_frame_hour` | `playout_frame_hour` |

---

## 5. No Changes Needed

These tables are correctly specified:
- All `cache_route_impacts_*` tables
- All `cache_campaign_reach_*` tables
- All `cache_space_*` entity lookup tables
- `cache_demographic_universes`

---

## Files to Update

- `/Claude/Documentation/Adwanted_Batch_Request/ADWANTED_REQUEST_FINAL.md`

---

## Contact

POC Team - ian@route.org.uk

---

*Created: 2025-12-09*
