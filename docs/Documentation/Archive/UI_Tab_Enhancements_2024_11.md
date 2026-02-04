# UI Tab Enhancements - November 2024

**Date:** November 24-25, 2024
**Branch:** `feature/ui-tab-enhancements`
**Status:** ✅ Complete - Ready for Review

---

## Overview

Major UI/UX enhancements to the campaign analysis interface, including metrics reorganization, new analytical tables, and performance-optimized materialized views for frame-level daily and hourly analysis.

---

## 1. Metrics Cards Reorganization (4x4 Layout)

### Before:
- 5 columns + 3 columns layout (awkward spacing)
- Daily Average in main metrics (less useful)
- No Cover % metric

### After:
- **Balanced 4x4 grid layout** with icon-styled cards
- **Row 1 (Audience Metrics):**
  - Total Impacts
  - Total Reach (~approximate notation if applicable)
  - Total GRPs
  - Frequency

- **Row 2 (Playout Metrics):**
  - Total Playouts
  - Unique Frames
  - Avg Spot Length (rounded to whole seconds)
  - Cover % (of GB Adults 15+)

### Files Modified:
- `src/ui/components/key_metrics.py`

### Key Changes:
- Lucide icons for all metrics
- Gradient background cards
- Removed Daily Average (moved to Daily & Hourly Patterns tab)
- Added Cover % with percentage icon
- Rounded Avg Spot Length to whole numbers

---

## 2. Campaign Header Styling

### Enhancements:
- Campaign ID displayed in gradient card
- Export Data button repositioned below New Analysis button
- Better visual hierarchy

### Files Modified:
- `src/ui/app_api_real.py`

---

## 3. Daily & Hourly Patterns Tab

### New Features:
- **Daily Average Impacts (000s)** - with help text showing number of days
- **Weekly Average Impacts (000s)** - with help text showing number of weeks
- All impacts consistently displayed in thousands (000s)
- Peak Hour formatted with AM/PM and time range (e.g., "8:00-8:59 AM")
- Peak Day Impacts shown in 000s with 1 decimal place

### Files Modified:
- `src/ui/tabs/time_series.py`

### Key Changes:
- Added `daily_avg_impacts` and `weekly_avg_impacts` calculations
- Converted Decimal types to float to avoid type errors
- Consistent (000s) labeling across all daily/weekly metrics
- Hourly data kept as regular numbers (not 000s) since values are small

---

## 4. Overview Tab - Frame Audience Analysis

### Before:
- Top 5 Performing Frames only
- Environment Types pie chart (duplicated from Geographic tab)
- Day/Night Split (not useful)

### After:
- **Comprehensive Frame Audience Analysis Table**
- Shows ALL frames sorted by All Adults impacts
- Fully downloadable for econometric analysis

### Columns:
- Frame ID
- Impacts - All Adults (15+) (000s) - 3 decimal places
- Location (Town, TV Region)
- Active Dates (exact comma-separated list)
- Campaign ID
- Playouts
- Impacts by demographic (ABC1, C2DE, 15-34, 35+, 35-54, Main Shopper, Children HH)

### Files Modified:
- `src/ui/tabs/overview.py`
- `src/db/streamlit_queries.py` - added `get_frame_audience_table_sync()`

### Query Optimizations:
- Uses `mv_cache_campaign_impacts_frame` (pre-aggregated MV)
- GROUP BY with MAX() aggregations to prevent duplicates
- Composite indexes for fast lookups
- Active dates shown as comma-separated list for econometric matching

---

## 5. Geographic Tab Enhancements

### New Feature: Top Towns by Impact
- Shows top 10 towns ranked by total impacts
- Includes frame count, total impacts, avg impacts/frame, % of total
- Helps identify geographic concentration

### Files Modified:
- `src/ui/tabs/geographic.py`

---

## 6. Chart Color Consistency

### Updates:
- Regional Impact Distribution: Neutral slate gray (#546E7A) for all bars
- Environment Distribution: Categorical colors for pie chart segments
- Distinct color schemes prevent visual confusion between chart types

### Files Modified:
- `src/ui/tabs/geographic.py`

---

## 7. Reach & GRP Tab Cleanup

### Removed:
- Redundant "Campaign Totals" summary that duplicated top metrics cards

### Files Modified:
- `src/ui/tabs/reach_grp.py`

---

## 8. NEW: Detailed Analysis Tab

### Purpose:
Frame-level daily and hourly impacts for econometric analysis - allows matching OOH exposure data with sales/outcome data at granular time intervals.

### Performance Optimization:

#### New Materialized Views Created:
```sql
-- Frame impacts by day (7.4M rows)
CREATE MATERIALIZED VIEW mv_cache_campaign_impacts_frame_day AS
SELECT campaign_id, frameid, DATE(time_window_start) as date,
       demographic_segment, SUM(impacts) as total_impacts,
       COUNT(*) as interval_count
FROM cache_route_impacts_15min_by_demo
GROUP BY campaign_id, frameid, DATE(time_window_start), demographic_segment;

-- Frame impacts by hour (104.7M rows)
CREATE MATERIALIZED VIEW mv_cache_campaign_impacts_frame_1hr AS
SELECT campaign_id, frameid, DATE_TRUNC('hour', time_window_start) as hour_start,
       demographic_segment, SUM(impacts) as total_impacts,
       COUNT(*) as interval_count
FROM cache_route_impacts_15min_by_demo
GROUP BY campaign_id, frameid, DATE_TRUNC('hour', time_window_start), demographic_segment;
```

#### Performance Test Results:
- **Daily MV Query:** 9.1ms execution time (~39K rows)
- **Hourly MV Query:** 78.9ms execution time (~744K rows)
- **Conclusion:** No partitioning needed - performance is excellent!

### Tab Structure:
Two sub-tabs:
1. **📅 Frame Level Daily Impacts**
   - Frame ID, Date, Location, Campaign ID
   - Intervals count
   - All demographic impacts (000s, 3 decimal places)

2. **🕐 Frame Level Hourly Impacts**
   - Frame ID, Hour (YYYY-MM-DD HH:MM), Location, Campaign ID
   - Intervals count
   - All demographic impacts (000s, 3 decimal places)

### Files Created:
- `src/ui/tabs/detailed_analysis.py`
- `sql/create_mv_frame_day_hour.sql`

### Files Modified:
- `src/db/streamlit_queries.py` - added `get_frame_audience_by_day_sync()` and `get_frame_audience_by_hour_sync()`
- `src/ui/app_api_real.py` - added Detailed Analysis tab

---

## Technical Improvements

### Data Type Fixes:
- Fixed Decimal/float division errors by converting to float before operations
- Fixed object dtype errors by using `pd.to_numeric()` with error handling
- Used `sort_values()` instead of `nlargest()` to avoid dtype issues

### Duplicate Prevention:
- Used `DISTINCT ON` for unique frame locations
- Used `GROUP BY` with `MAX()` aggregations in final queries
- Ensured one row per frame (or frame+date, frame+hour)

### Column Configuration:
- Active Dates column set to "medium" width to save space
- All impact columns show 3 decimal places for precision
- (000s) labels in column headers for clarity

---

## Database Changes

### New Materialized Views:
1. `mv_cache_campaign_impacts_frame_day` - 7.4M rows
2. `mv_cache_campaign_impacts_frame_1hr` - 104.7M rows

### Indexes Created:
```sql
-- Daily MV Indexes
idx_mv_frame_day_campaign (campaign_id)
idx_mv_frame_day_frame (frameid)
idx_mv_frame_day_date (date)
idx_mv_frame_day_demo (demographic_segment)
idx_mv_frame_day_composite (campaign_id, frameid, date)

-- Hourly MV Indexes
idx_mv_frame_1hr_campaign (campaign_id)
idx_mv_frame_1hr_frame (frameid)
idx_mv_frame_1hr_hour (hour_start)
idx_mv_frame_1hr_demo (demographic_segment)
idx_mv_frame_1hr_composite (campaign_id, frameid, hour_start)
```

### Refresh Strategy:
- MVs should be refreshed periodically as new data arrives
- Commands:
  ```sql
  REFRESH MATERIALIZED VIEW mv_cache_campaign_impacts_frame_day;
  REFRESH MATERIALIZED VIEW mv_cache_campaign_impacts_frame_1hr;
  ```

---

## Files Summary

### Created:
- `src/ui/tabs/detailed_analysis.py`
- `sql/create_mv_frame_day_hour.sql`

### Modified:
- `src/ui/app_api_real.py`
- `src/ui/components/key_metrics.py`
- `src/ui/tabs/overview.py`
- `src/ui/tabs/time_series.py`
- `src/ui/tabs/geographic.py`
- `src/ui/tabs/reach_grp.py`
- `src/db/streamlit_queries.py`

### SQL Migrations:
- MVs created on MS-01 database (192.168.1.34)
- No schema changes to existing tables

---

## Testing Notes

### Performance:
- All queries under 100ms for campaign 16699
- No performance degradation noticed
- Streamlit app responsive

### Data Validation:
- Verified no duplicate rows in tables
- Confirmed active dates match playout data
- Checked demographic totals match overall totals

### Browser Testing:
- Chrome: ✅ Works
- Need to test: Safari, Firefox (assumed working)

---

## User Impact

### Benefits:
1. **Cleaner UI** - Better organized metrics and tabs
2. **Better Context** - Active dates show exactly when frames were used
3. **Econometric Analysis** - Daily and hourly frame-level data for matching
4. **Faster Downloads** - Pre-aggregated MVs make exports instant
5. **More Precision** - 3 decimal places for detailed analysis

### Breaking Changes:
- None - all changes are additive or UI improvements

---

## Next Steps / Future Enhancements

### Potential Improvements:
1. **Filtering** - Add frame ID or date range filters to Detailed Analysis tables
2. **Export Buttons** - Direct CSV/Excel export from each table
3. **Pagination** - For very large hourly tables (>500K rows)
4. **Aggregation Options** - Toggle between 15-min, hourly, daily views
5. **MV Refresh Automation** - Scheduled refresh of materialized views

### Known Limitations:
- Hourly table can be very large (744K rows for campaign 16699)
- Active Dates column can be long for frames used many days
- No filtering yet - shows all frames/dates/hours

---

## Commit History

1. **feat: enhance UI layout and add analytical sections to tabs**
   - Reorganize metrics from 5+3 to 4x4 grid layout
   - Add Cover % metric, remove Daily Average
   - Style campaign header as card
   - Add daily/weekly average impacts to Daily & Hourly Patterns
   - Format impacts consistently in 000s
   - Add AM/PM to peak hour
   - Add Environment Types and Top Performing Frames to Overview
   - Add Top Towns to Geographic
   - Remove redundant sections

2. **feat: add comprehensive frame audience analysis and detailed analysis tab** (pending)
   - Create mv_cache_campaign_impacts_frame_day materialized view
   - Create mv_cache_campaign_impacts_frame_1hr materialized view
   - Add get_frame_audience_table_sync() query function
   - Add get_frame_audience_by_day_sync() query function
   - Add get_frame_audience_by_hour_sync() query function
   - Replace Top Performing Frames with comprehensive Frame Audience Analysis
   - Create new Detailed Analysis tab with daily/hourly frame-level tables
   - Add active dates to frame audience table
   - Format all impacts with 3 decimal places and (000s) labels

---

**Documentation Date:** November 25, 2024
**Author:** Claude Code (with Doctor Biz)
