# Performance Investigation Results

**Date**: 2025-11-29
**Branch**: `feature/performance-investigation`

## Issue
After loading a campaign, navigating to Executive Summary tab shows Streamlit still loading/spinning even though that tab should be fast.

## Root Cause Analysis

### Finding 1: Streamlit Tabs Execute ALL Content

When using `st.tabs()`, **ALL tab content executes on every page load**, not just the visible tab. This is Streamlit's design - it renders everything server-side.

```python
# In app_api_real.py, lines 536-561
tabs = st.tabs([...])  # Creates 6 tabs

with tabs[0]:  # Overview - EXECUTES
    render_overview_tab()
with tabs[1]:  # Weekly Reach - EXECUTES
    render_reach_grp_tab()
# ... ALL tabs execute, even invisible ones
with tabs[4]:  # Frame Audiences - EXECUTES (SLOW!)
    render_detailed_analysis_tab()
with tabs[5]:  # Exec Summary - EXECUTES
    render_executive_summary_tab()
```

### Finding 2: Frame Audiences Tab is Heavy

The Frame Audiences tab (`src/ui/tabs/detailed_analysis.py`) runs **3 complex database queries**:

1. `get_frame_audience_by_day_sync()` - Multi-CTE query joining materialized views
2. `get_frame_audience_by_hour_sync()` - Similar hourly query
3. `get_frame_audience_table_sync()` - Campaign-level aggregation

These queries:
- Join multiple tables and MVs (mv_cache_campaign_impacts_frame_day, mv_playout_15min, route_frames, etc.)
- Return potentially thousands of rows (frame × day/hour combinations)
- Are NOT cached with `@st.cache_data`

### Finding 3: Nested Tabs Compound the Problem

Frame Audiences has 3 sub-tabs, and Streamlit executes all of them too:
```python
daily_tab, hourly_tab, campaign_tab = st.tabs([...])
with daily_tab:
    _render_frame_daily_impacts(campaign_id)  # EXECUTES
with hourly_tab:
    _render_frame_hourly_impacts(campaign_id)  # EXECUTES
with campaign_tab:
    _render_frame_campaign_audiences(campaign_id)  # EXECUTES
```

### Finding 4: Other Tabs Have Caching

Looking at `app_api_real.py`, other data loaders use `@st.cache_data`:
```python
@st.cache_data(ttl=600, show_spinner=False)
def load_weekly_reach_data(campaign_id: str, use_ms01: bool = True):
    ...
```

But Frame Audiences queries are called directly without Streamlit caching.

## Recommended Solutions

### Option A: Lazy Loading (Recommended)

Only execute Frame Audiences queries when the tab is actually clicked. Use session state to track active tab:

```python
# Add tab click tracking
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0  # Default to Overview

def render_detailed_analysis_tab():
    # Only load data if this tab was explicitly selected
    if st.session_state.get('frame_tab_loaded') != campaign_id:
        if st.button("Load Frame Audiences Data"):
            st.session_state.frame_tab_loaded = campaign_id
            st.rerun()
        return
    # ... rest of tab content
```

**Pros**: Fastest initial load, user explicitly controls heavy operations
**Cons**: Requires user interaction to see Frame Audiences data

### Option B: Add Streamlit Caching

Add `@st.cache_data` to frame audience queries:

```python
@st.cache_data(ttl=600, show_spinner=False)
def load_frame_daily_data(campaign_id: str):
    return get_frame_audience_by_day_sync(campaign_id, include_brand=True)
```

**Pros**: Simple to implement, data loads once per session
**Cons**: Still slow on first campaign load

### Option C: Move Heavy Tab to End + Add Loading Indicator

Move Frame Audiences to last tab position and add clear loading indicator:

```python
tabs = st.tabs([
    "📊 Overview",
    "📈 Weekly Reach",
    "⏰ Daily & Hourly",
    "🗺️ Geographic",
    "📑 Executive Summary",  # Moved up
    "🔬 Frame Audiences"     # Now last
])
```

**Pros**: Exec Summary renders before Frame Audiences starts
**Cons**: Doesn't actually prevent the queries from running

### Option D: Use st.fragment (Streamlit 1.33+)

Wrap Frame Audiences in `@st.fragment` decorator for independent reruns:

```python
@st.fragment
def render_detailed_analysis_tab():
    # Content only reruns when internal widgets change
    ...
```

**Pros**: Modern Streamlit pattern, better performance
**Cons**: May need Streamlit version upgrade

## Implementation Recommendation

**Implement Options A + B together:**

1. Add "Load Data" button to Frame Audiences tab (lazy loading)
2. Add `@st.cache_data` to the frame query functions
3. Optionally reorder tabs to put Exec Summary before Frame Audiences

This gives:
- Instant initial campaign load
- Cached data after first load
- User control over expensive operations

## Files to Modify

1. `src/ui/tabs/detailed_analysis.py` - Add lazy loading pattern
2. `src/db/streamlit_queries.py` - Add caching wrappers (or create new cached loaders)
3. `src/ui/app_api_real.py` - Optionally reorder tabs

---

## Implemented Solution (2025-11-29)

### 1. Database Materialized Views

Created pre-aggregated MVs to reduce query time from 2+ seconds to 8ms:

| MV | Source | Reduction |
|----|--------|-----------|
| `mv_playout_frame_day` | 67M rows → 1.2M | 57x smaller |
| `mv_playout_frame_hour` | 67M rows → 17M | 4x smaller |

See handover: `Claude/Handover/Pipeline/mv_playout_frame_day_handover.md`

### 2. Streamlit Caching

Added `@st.cache_data(ttl=3600)` to all frame audience loaders:
- `_load_frame_daily_data()`
- `_load_frame_hourly_data()`
- `_load_frame_campaign_data()`

### 3. Pagination for Large Datasets

Default limit of 5000 rows with "Load All" button for larger datasets:
- Displays record count and estimated load time
- Custom CSV/Excel download buttons for full dataset (bypassing Streamlit's built-in download which only gets displayed rows)

### 4. Query Updates

Updated `streamlit_queries.py` to use the new MVs instead of scanning `mv_playout_15min`.

---

*Investigation completed: 2025-11-29*
*Implementation completed: 2025-11-29*
