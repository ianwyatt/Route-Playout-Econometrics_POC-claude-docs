# Handover Document - November 23, 2025 (Geographic Tab Implementation)

## Session Summary

**Focus**: Geographic Analysis Tab implementation
**Branch**: `feature/ui-tab-enhancements`
**Status**: Complete - MV created and indexed, Geographic Tab ready for testing

---

## Completed This Session

### 1. Materialized View for Frame-Level Impacts
**File**: `migrations/007_create_mv_cache_campaign_impacts_frame.sql`

Created a reusable MV that pre-aggregates the 415M row `cache_route_impacts_15min_by_demo` table:

```sql
CREATE MATERIALIZED VIEW mv_cache_campaign_impacts_frame AS
SELECT
    campaign_id,
    frameid,
    demographic_segment,
    SUM(impacts) as total_impacts,
    COUNT(*) as time_window_count,
    MIN(time_window_start) as first_playout,
    MAX(time_window_start) as last_playout
FROM cache_route_impacts_15min_by_demo
GROUP BY campaign_id, frameid, demographic_segment;
```

**Indexes created**:
- `idx_mv_frame_campaign_demo` - for campaign+demographic queries
- `idx_mv_frame_frameid` - for joining to route_frames
- `idx_mv_frame_campaign_demo_frame` - compound index

**Status**: Migration running in background, processing 415M rows. Expected completion: ~10-20 minutes.

### 2. Geographic Database Queries
**File**: `src/db/streamlit_queries.py` (lines 465-631)

Added 4 new query functions:
- `get_frame_geographic_data_sync()` - Frame-level data with lat/lon for mapping
- `get_regional_impacts_sync()` - Aggregated by TV region
- `get_environment_impacts_sync()` - Aggregated by environment type
- `get_available_demographics_for_campaign_sync()` - List demographics for campaign

All queries use the new MV with demographic parameter filtering.

### 3. Geographic Analysis Tab
**File**: `src/ui/tabs/geographic.py` (complete rewrite)

Implemented full geographic visualization tab with:
- **Demographic selector** - Choose from all available demographics
- **Summary metrics** - Total frames, impacts, TV regions, towns
- **UK Coverage Map** - Interactive Plotly scatter_mapbox with carto-positron style
- **Regional Impact Distribution** - Bar chart of top 12 TV regions
- **Environment Distribution** - Pie/donut chart with automatic "Other" grouping
- **Regional Performance Table** - Detailed metrics with market share

---

## Files Modified/Created

| File | Action | Description |
|------|--------|-------------|
| `migrations/007_create_mv_cache_campaign_impacts_frame.sql` | Created | MV migration for frame impacts |
| `src/db/streamlit_queries.py` | Modified | Added 4 geographic query functions |
| `src/ui/tabs/geographic.py` | Rewritten | Full geographic tab implementation |

---

## Migration Status

**COMPLETE** - MV created and indexed successfully.

| Metric | Value |
|--------|-------|
| Rows | 915,383 |
| Table Size | 81 MB |
| Total with Indexes | 135 MB |
| Campaigns | 833 |
| Demographics | 7 |

**Indexes**:
- `idx_mv_frame_campaign_demo` - for campaign+demographic queries
- `idx_mv_frame_frameid` - for joining to route_frames
- `idx_mv_frame_campaign_demo_frame` - compound index

**To refresh MV** (if source data changes):
```sql
REFRESH MATERIALIZED VIEW mv_cache_campaign_impacts_frame;
ANALYZE mv_cache_campaign_impacts_frame;
```

---

## Testing the Geographic Tab

Once the MV is ready:

1. Start the app:
```bash
USE_MS01_DATABASE=true streamlit run src/ui/app_api_real.py --server.port 8504
```

2. Select a campaign from the browser
3. Navigate to the "Geographic" tab
4. Select different demographics from the dropdown
5. Verify:
   - UK map shows frame locations with impact markers
   - Regional bar chart shows TV region breakdown
   - Environment pie chart shows distribution
   - Table shows detailed regional metrics

---

## Remaining UI Work

### High Priority (From Roadmap)

#### 1. Look & Feel Improvements
- Review overall styling consistency
- Improve color scheme and visual hierarchy
- Polish card layouts and spacing
- Enhance chart styling
- Improve table formatting
- Add loading states and transitions

#### 2. Landing Page Enhancement
- Improve header/hero section
- Better navigation flow
- Clear call-to-action for campaign selection
- Summary statistics presentation

---

## Key Technical Decisions

1. **Reusable MV pattern**: Created `mv_cache_campaign_impacts_frame` following the same pattern as `mv_cache_campaign_impacts_day/1hr` - aggregates data by frame rather than including geographic columns. Geographic data is joined at query time from `route_frame_details`.

2. **Demographic filtering**: All geographic queries accept a `demographic_segment` parameter. The tab includes a dropdown selector populated from available demographics for the selected campaign.

3. **Map visualization**: Uses Plotly's `scatter_mapbox` with free `carto-positron` style (no API key required), centered on UK (lat=54.0, lon=-2.0, zoom=5).

---

## Bug Fixes Applied

### Narwhals Series / Plotly Compatibility (Nov 23, 2025)
**Issue**: `ValueError: Invalid value of type 'narwhals.stable.v1.Series' received for the 'size' property of scattermapbox.marker`

**Root Cause**: Plotly does not accept Narwhals Series objects directly; requires native Python floats/ints.

**Fix**: Added explicit type conversions in all chart rendering functions:

```python
# _render_uk_map()
df_map['latitude'] = df_map['latitude'].astype(float)
df_map['longitude'] = df_map['longitude'].astype(float)
df_map['total_impacts'] = df_map['total_impacts'].astype(float)

# _render_regional_chart()
df_chart['total_impacts'] = df_chart['total_impacts'].astype(float)

# _render_environment_chart()
df_chart['total_impacts'] = df_chart['total_impacts'].astype(float)
df_chart['frame_count'] = df_chart['frame_count'].astype(int)
```

---

## Code Quality Notes

- All Python files pass syntax check (`python3 -m py_compile`)
- Geographic tab follows same pattern as existing Reach & GRP and Time Series tabs
- Functions use `@st.cache_data(ttl=300)` for demographic list caching
- Error handling for MV not yet existing (returns `['all_adults']` as fallback)
- Explicit type conversions for Plotly compatibility with database result types

---

## Running the App

```bash
# Start app on port 8504
USE_MS01_DATABASE=true streamlit run src/ui/app_api_real.py --server.port 8504
```

**URLs**:
- Local: http://localhost:8504
- Network: http://192.168.1.13:8504

---

## Database Connection

```bash
PGPASSWORD='S1lgang-Amu\ck' psql -h 192.168.1.34 -U postgres -d route_poc
```

---

*Created: November 23, 2025*
*Author: Claude Code*
