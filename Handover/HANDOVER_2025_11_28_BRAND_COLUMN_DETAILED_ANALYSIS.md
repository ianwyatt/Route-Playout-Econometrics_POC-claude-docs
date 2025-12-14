# Handover: Brand Column in Detailed Analysis Tab

**Date:** November 28, 2025
**Branch:** `feature/demographic-filters-campaign-tabs`
**Commit:** `44eabf5`

---

## Summary

Added brand column to the Detailed Analysis tab's daily and hourly frame impacts tables. This allows econometricians to see which brand's ads were playing on each frame at each time period.

---

## What Was Done

### 1. Database Changes - New Materialized Views

Created two lookup MVs for fast brand queries:

| MV Name | Rows | Purpose |
|---------|------|---------|
| `mv_frame_brand_daily` | 1.2M | Daily brand lookup (campaign, frame, date → brand_names) |
| `mv_frame_brand_hourly` | 17M | Hourly brand lookup (campaign, frame, hour → brand_names) |

**SQL to recreate if needed:**
```sql
-- Daily brand lookup
CREATE MATERIALIZED VIEW mv_frame_brand_daily AS
SELECT
    pb.buyercampaignref as campaign_id,
    pb.frameid,
    DATE(pb.time_window_start) as date,
    STRING_AGG(DISTINCT sb.name, ', ' ORDER BY sb.name) as brand_names,
    COUNT(DISTINCT pb.spacebrandid) as brand_count,
    SUM(pb.spots_for_brand) as total_spots
FROM mv_playout_15min_brands pb
LEFT JOIN cache_space_brands sb ON pb.spacebrandid::text = sb.entity_id
GROUP BY pb.buyercampaignref, pb.frameid, DATE(pb.time_window_start);

CREATE INDEX idx_mv_frame_brand_daily_campaign ON mv_frame_brand_daily(campaign_id);

-- Hourly brand lookup
CREATE MATERIALIZED VIEW mv_frame_brand_hourly AS
SELECT
    pb.buyercampaignref as campaign_id,
    pb.frameid,
    DATE_TRUNC('hour', pb.time_window_start) as hour_start,
    STRING_AGG(DISTINCT sb.name, ', ' ORDER BY sb.name) as brand_names,
    COUNT(DISTINCT pb.spacebrandid) as brand_count,
    SUM(pb.spots_for_brand) as total_spots
FROM mv_playout_15min_brands pb
LEFT JOIN cache_space_brands sb ON pb.spacebrandid::text = sb.entity_id
GROUP BY pb.buyercampaignref, pb.frameid, DATE_TRUNC('hour', pb.time_window_start);

CREATE INDEX idx_mv_frame_brand_hourly_campaign ON mv_frame_brand_hourly(campaign_id);
```

### 2. Query Changes

Updated `src/db/streamlit_queries.py`:
- `get_frame_audience_by_day_sync()` - Added `include_brand` parameter
- `get_frame_audience_by_hour_sync()` - Added `include_brand` parameter

When `include_brand=True`, queries join to the lookup MVs to get brand information.

### 3. UI Changes

Updated `src/ui/tabs/detailed_analysis.py`:
- Brand column always displayed (no toggle needed - lookup MVs are fast)
- Brand column positioned after Frame ID and Date/Hour
- Column width set to "small" to show "Brand not provided" without excess space
- Demo mode anonymisation applied via `anonymise_brand_list()`

### 4. Anonymisation Updates

Updated `src/ui/config/anonymisation.py`:
- Placeholder brands pass through unchanged:
  - "Brand not provided at point of trade"
  - "Brand not provided"
  - "Unknown Brand"
  - "Unknown"
  - "N/A"

This ensures econometricians can distinguish real brands (anonymised as "Brand 1", "Brand 2") from data quality issues.

---

## Multi-Brand Handling

**Key finding:** 99% of frame-campaign combinations have a single brand. The 1% with multiple brands are typically data quality issues (real brand + placeholder).

**Approach taken:**
- Daily: Show all brands comma-separated (e.g., "Channel Four, Brand not provided at point of trade")
- Hourly: Same approach - comma-separated brands
- No proportional impact splitting - brands are listed, not apportioned

---

## Files Changed

| File | Changes |
|------|---------|
| `src/db/streamlit_queries.py` | Added `include_brand` parameter to daily/hourly queries |
| `src/ui/tabs/detailed_analysis.py` | Added brand column to both tables, demo mode anonymisation |
| `src/ui/config/anonymisation.py` | Added placeholder brand exceptions |
| `docs/DEMO_MODE_ANONYMISATION.md` | Documented new integration points and placeholder exceptions |
| `docs/UI_GUIDE.md` | Added Detailed Analysis tab documentation |

---

## Testing

1. **Normal mode**: Restart Streamlit, go to Detailed Analysis tab, verify Brand column shows real brand names
2. **Demo mode**: Run with `DEMO_MODE=true`, verify brands show as "Brand 1", "Brand 2" but placeholders show unchanged
3. **Multi-brand**: Find a campaign with multiple brands (e.g., campaign 16699 has "Channel Four" and "Brand not provided")

---

## MV Refresh Requirements

The new MVs should be refreshed when:
- New playout data is ingested
- Cache tables are updated

```sql
REFRESH MATERIALIZED VIEW mv_frame_brand_daily;
REFRESH MATERIALIZED VIEW mv_frame_brand_hourly;
```

Consider adding to the pipeline's MV refresh script.

---

## Known Limitations

1. **Multi-brand impacts not split**: When a frame has multiple brands, impacts are shown in full for each brand row (not proportionally split). This is intentional - the multi-brand cases are mostly data quality issues.

2. **MV size**: `mv_frame_brand_hourly` is 17M rows. This is acceptable but should be monitored as data grows.

---

## Next Steps (Optional)

- Add brand to the Overview tab's Frame Audience Analysis table
- Add brand filtering capability to the Detailed Analysis tab
- Consider adding brand aggregation charts

---

*Handover prepared by Claude Code*
