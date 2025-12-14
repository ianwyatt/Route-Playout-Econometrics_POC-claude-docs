# Plan: Daily Cumulative Build Enhancement

**Date**: 2025-11-29
**Status**: Planning

---

## Objective

Replace weekly cumulative build charts with daily data for smoother, more realistic reach/impact curves in:
1. Executive Summary tab - "Reach & Impact Build" chart
2. Reach & GRP tab - "Cumulative Build" chart

---

## Current State Analysis

### Data Sources

| Table | Granularity | Sample Data |
|-------|-------------|-------------|
| `cache_campaign_reach_week` | Weekly | W1, W2, W3... (~4-9 weeks per campaign) |
| `cache_campaign_reach_day_cumulative` | Daily | Day 1, 2, 3... (up to 64 days) |

**Daily table coverage**: 830 campaigns, 10,819 rows (avg ~13 days/campaign)

### Current Chart Behavior

- X-axis: Week labels (W1, W2, W3)
- Points: One per week → straight line segments between weeks
- Result: Angular/stepped appearance

### Target Chart Behavior

- X-axis: Date labels (Aug 24, Aug 25, Aug 26...)
- Points: One per day → smooth curves
- Result: Natural reach saturation curve

---

## Files to Modify

### 1. `src/db/streamlit_queries.py`

**Add new function**: `get_daily_cumulative_reach_sync()`

```python
def get_daily_cumulative_reach_sync(campaign_id: str, use_ms01: bool = None) -> List[Dict]:
    """
    Get daily cumulative reach data from cache_campaign_reach_day_cumulative.

    Returns daily reach build data for smoother cumulative charts.
    Values in database are stored in thousands.
    """
    query = """
        SELECT
            date,
            day_number,
            reach,
            grp,
            frequency,
            total_impacts,
            is_approximate,
            approximation_method,
            route_release_id
        FROM cache_campaign_reach_day_cumulative
        WHERE campaign_id = %s
        ORDER BY day_number
    """
    # ... standard connection handling
```

### 2. `src/ui/app_api_real.py`

**Add cached loader**:

```python
@st.cache_data(ttl=600, show_spinner=False)
def load_daily_cumulative_reach(campaign_id: str, use_ms01: bool = True) -> List[Dict]:
    """Load daily cumulative reach data with Streamlit caching."""
    return get_daily_cumulative_reach_sync(campaign_id, use_ms01=use_ms01)
```

### 3. `src/ui/tabs/executive_summary.py` (lines 193-256)

**Current**: Uses `load_weekly_reach_data()`, filters for `reach_type == 'cumulative'`

**Change to**:
- Import `load_daily_cumulative_reach`
- Use daily data for chart
- X-axis: dates formatted as `%d %b` (e.g., "24 Aug")
- Remove markers (too many points), use line only
- Fallback: If no daily data, use weekly data

### 4. `src/ui/tabs/reach_grp.py` (lines 176-267)

**Current**: Uses `load_weekly_reach_data()`, filters for `reach_type == 'cumulative'`

**Change to**:
- Import `load_daily_cumulative_reach`
- Use daily data for cumulative chart
- Keep same styling (Reach blue, Impacts pink, GRP orange)
- Keep dual y-axis (Reach/Impacts left, GRP right)
- Remove markers for cleaner appearance

---

## Chart Design Changes

| Aspect | Weekly (Current) | Daily (Target) |
|--------|------------------|----------------|
| X-axis labels | W1, W2, W3... | Aug 24, Aug 25... |
| Data points | 4-9 per campaign | 7-64 per campaign |
| Line markers | Yes (size=8) | No (too crowded) |
| Line width | 2px | 2px (keep same) |
| Curve appearance | Stepped/angular | Smooth |

### X-axis Format Decision

For long campaigns (60+ days):
- Use `%d %b` format: "24 Aug", "25 Aug"
- Plotly will auto-rotate/thin labels as needed
- Hover will show full date

---

## Implementation Steps

1. **Query Layer** (~10 min)
   - Add `get_daily_cumulative_reach_sync()` to `streamlit_queries.py`

2. **Cache Layer** (~5 min)
   - Add `load_daily_cumulative_reach()` to `app_api_real.py`

3. **Executive Summary Chart** (~15 min)
   - Update "Reach & Impact Build" section (lines 193-256)
   - Change data source to daily
   - Update x-axis to use dates
   - Remove markers, keep line

4. **Reach & GRP Chart** (~15 min)
   - Update "Cumulative Build" section (lines 176-267)
   - Change data source to daily
   - Update x-axis to use dates
   - Keep dual y-axis structure

5. **Testing** (~10 min)
   - Test with campaign 16699 (known to have daily data)
   - Verify chart renders correctly
   - Check fallback behavior

6. **Cleanup** (~5 min)
   - Remove unused weekly cumulative code if applicable
   - Update any related comments

---

## Fallback Strategy

If `cache_campaign_reach_day_cumulative` has no data for a campaign:
- Fall back to weekly data from `cache_campaign_reach_week`
- Show info message: "Daily data unavailable, showing weekly"

This ensures backward compatibility for campaigns that haven't been processed for daily cumulative data.

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Daily table missing data | Low | Fallback to weekly |
| Too many data points cluttering chart | Medium | Remove markers, use line only |
| Performance impact | Low | Already small dataset (~13 rows avg) |

---

## Verification Criteria

1. Charts show smooth curves instead of stepped lines
2. X-axis shows readable date labels
3. Hover shows correct values
4. Fallback to weekly works when daily unavailable
5. Both tabs (Exec Summary, Reach & GRP) updated consistently

---

*Plan created: 2025-11-29*
