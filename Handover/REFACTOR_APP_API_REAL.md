# app_api_real.py Refactoring - Handover Document

## Overview

Major refactoring of `src/ui/app_api_real.py` to improve modularity, maintainability, and testability.

## Phase 1 - Completed (2025-11-23)

### Changes Made

**Original State:**
- `app_api_real.py`: 1,835 lines (monolithic)
- Two "god functions": `render_campaign_selector()` (507 lines), `analyze_campaign()` (482 lines)
- 235 lines of inline CSS
- Duplicate utility functions

**New Modules Created:**

| File | Purpose | Lines |
|------|---------|-------|
| `src/utils/formatters.py` | Number formatting utilities (safe_float, from_thousands) | ~120 |
| `src/ui/config/demographics.py` | DEMOGRAPHIC_NAMES constant | ~35 |
| `src/ui/styles/css.py` | All CSS constants and inject_css() | ~370 |
| `src/ui/components/campaign_browser.py` | Campaign browser with browse/manual tabs | ~443 |
| `src/ui/components/key_metrics.py` | 5-column metrics row component | ~150 |
| `src/ui/components/demographic_analysis.py` | Demographic selector and charts | ~200 |

**Result After Phase 1:**
- `app_api_real.py`: 1,031 lines (44% reduction)

### Key Technical Patterns

1. **MV-First Pattern**: Campaign browser uses materialized views for instant loading
2. **Values in Thousands**: Database stores reach/impacts in thousands, use `from_thousands()` to convert
3. **Decimal Conversion**: PostgreSQL Decimal values need `safe_float()` for JSON serialization
4. **CSS Injection**: Use `inject_css()` at start of `main()` to apply all styles

### Import Structure

```python
# In app_api_real.py
from src.ui.styles.css import inject_css
from src.ui.config.demographics import DEMOGRAPHIC_NAMES
from src.ui.components import (
    render_campaign_selector,
    render_key_metrics,
    render_demographic_analysis
)
```

## Phase 2 - Completed (2025-11-23)

### Changes Made

**Replaced inline code with component calls:**

1. **Key Metrics Section** (~135 lines removed)
   - Replaced with `render_key_metrics(result)` call
   - Component handles both MV-first and legacy data paths

2. **Demographic Analysis Section** (~170 lines removed)
   - Replaced with `render_demographic_analysis(result, campaign_id)` call
   - Component handles demographic selector, charts, and export

**Result After Phase 2:**
- `app_api_real.py`: 724 lines (60% total reduction from 1,835)

### Remaining Code (Not Extracted)

The following remain in `app_api_real.py` by design:

1. **`calculate_reach()` / `calculate_reach_async()`** (~190 lines)
   - UI wrapper around `src/services/reach_service.py` (logic already extracted)
   - Contains Streamlit-specific display code (st.metric, st.spinner)

2. **Data Loaders** (~37 lines)
   - Small functions with `@st.cache_data` decorators
   - Tightly coupled to Streamlit caching

3. **`analyze_campaign()`** (~110 lines after Phase 2)
   - Orchestrates MV-first vs legacy path
   - Calls extracted component functions

4. **`test_api_request()`** (~57 lines)
   - Dev/debug utility function

### Decision: No Further Extraction Needed

Further extraction would add complexity without significant benefit:
- Remaining functions are mostly Streamlit UI wrappers
- Core business logic already in services (reach_service, campaign_service)
- 60% reduction achieves original goal of improved maintainability

## Testing

App runs successfully on http://localhost:8504

```bash
USE_MS01_DATABASE=true streamlit run src/ui/app_api_real.py --server.port 8504
```

## Phase 3 - Code Quality (2025-11-23)

### Unit Tests Added

Created `tests/unit/test_formatters.py` with 40 unit tests covering:

| Test Class | Functions Tested | Tests |
|------------|-----------------|-------|
| `TestSafeFloat` | `safe_float()` | 6 |
| `TestSafeInt` | `safe_int()` | 5 |
| `TestFromThousands` | `from_thousands()` | 6 |
| `TestFormatLargeNumber` | `format_large_number()` | 4 |
| `TestFormatPercentage` | `format_percentage()` | 4 |
| `TestFormatFrequency` | `format_frequency()` | 4 |
| `TestFormatBrands` | `format_brands()` | 5 |
| `TestFormatListToString` | `format_list_to_string()` | 5 |

All 40 tests passing.

### Magic Number Extraction

Extracted `DEMOGRAPHICS_PER_PLAYOUT = 7` constant to `src/ui/config/demographics.py`:

```python
# Number of demographic segments cached per playout in the database.
# Update this if demographics are added/removed from the pipeline caching.
DEMOGRAPHICS_PER_PLAYOUT = 7
```

Updated `src/ui/components/key_metrics.py` to import and use this constant instead of hardcoded `7`.

**Rationale**: Makes the codebase future-proof for when additional demographics are added to the pipeline.

## Phase 4 - Dynamic Demographics Count (2025-11-23)

### Changes Made

Replaced hardcoded `DEMOGRAPHICS_PER_PLAYOUT` constant with database-driven approach:

1. **Database View Created**: `v_demographic_segment_count`
   - Queries `cache_route_impacts_15min_by_demo` for distinct segment count
   - Returns `segment_count` (integer) and `segment_names` (array)
   - Automatically updates when demographics are added/removed from pipeline

2. **Migration Added**: `005_create_v_demographic_segment_count.sql`
   - Creates the view for version control

3. **Function with Cache**: `get_demographics_per_playout()`
   - Uses `@st.cache_data(ttl=3600)` for 1-hour cache
   - Falls back to `DEMOGRAPHICS_PER_PLAYOUT_FALLBACK = 7` if query fails
   - Backwards compatible: `DEMOGRAPHICS_PER_PLAYOUT` constant still exported

### Benefits

- No code changes required when demographics are added/removed
- 1-hour cache minimizes database queries
- Graceful fallback if database unavailable

## Files Modified

- `src/ui/app_api_real.py` - Main app (reduced)
- `src/utils/__init__.py` - Added formatter exports
- `src/ui/styles/__init__.py` - Added CSS exports
- `src/ui/components/__init__.py` - Added component exports
- `src/ui/config/demographics.py` - Added `get_demographics_per_playout()` function
- `src/ui/components/key_metrics.py` - Uses `get_demographics_per_playout()` function
- `tests/unit/test_formatters.py` - New file with 40 unit tests
- `migrations/005_create_v_demographic_segment_count.sql` - Database view migration

## Phase 5 - Performance Charts Bugfix (2025-11-23)

### Issue

Performance Charts tab was showing empty charts (daily impacts and hourly heatmap).

### Root Cause

Demographic segment filter in SQL queries used `'All Adults'` (title case) but MVs store segments in snake_case format `'all_adults'`.

### Fix

Changed demographic_segment filter from `'All Adults'` to `'all_adults'` in 4 queries in `src/db/streamlit_queries.py`:

1. `get_daily_impacts_sync()` - MV query
2. `get_daily_impacts_sync()` - fallback query
3. `get_hourly_impacts_sync()` - MV query
4. `get_hourly_impacts_sync()` - fallback query

### Commit

`02ceaa3` - fix: correct demographic segment filter in performance charts queries

## Phase 6 - Tab Consolidation (2025-11-23)

### Changes Made

Merged "Performance Charts" and "Time Series" tabs into unified "Time Analysis" tab.

**Before:**
- 6 tabs total
- Performance Charts: Daily Impacts line, Daily Distribution bar, Hourly bar
- Time Series: Daily line, Day of Week comparison, Hourly heatmap, Peak metrics
- Overlapping content: Two nearly identical daily line charts

**After:**
- 5 tabs total
- Time Analysis tab contains all time-based visualizations:
  1. **Daily Trends** (side by side):
     - Daily Impacts: smooth spline line chart (`line_shape='spline'`)
     - Daily Impact Distribution: bar chart
  2. **Day of Week Comparison**: average impacts by day
  3. **Hourly Analysis** (side by side):
     - Average Impacts by Hour: vertical bar chart
     - Hourly Activity Heatmap: day × hour matrix
  4. **Peak Performance**: metrics for peak hour/day

### Files Changed

| File | Change |
|------|--------|
| `src/ui/tabs/time_series.py` | Rewritten with merged content (217 lines) |
| `src/ui/tabs/performance.py` | Deleted |
| `src/ui/tabs/__init__.py` | Removed performance export |
| `src/ui/app_api_real.py` | Updated imports, tabs reduced 6→5, renamed tab |

### Commit

`e57aadd` - refactor: merge Performance Charts and Time Series into Time Analysis tab

## Phase 7 - Hourly Bar Chart Fix (2025-11-23)

### Issue

Hourly bar chart in Time Analysis tab was showing thin horizontal lines instead of proper vertical bars.

### Root Cause

Data had gaps (missing hours) which caused bars to render at non-contiguous x positions, appearing as thin horizontal lines.

### Fix

In `src/ui/tabs/time_series.py`:

1. Fill all 24 hours (0-23) before rendering:
```python
all_hours = pd.DataFrame({'hour': range(24)})
hourly_complete = all_hours.merge(hourly_summary, on='hour', how='left').fillna(0)
```

2. Use explicit `go.Bar` with controlled x-axis range:
```python
xaxis=dict(tickmode='linear', dtick=2, range=[-0.5, 23.5]),
bargap=0.1
```

### Commit

`a493acd` - fix: render hourly impacts as proper vertical bars

## Phase 8 - Auto-Hide Status Box (2025-11-23)

### Issue

"Analyzing Campaign" status box persisted after analysis completed, cluttering the UI.

### Changes Made

1. **British Spelling**: Changed "Analyzing" to "Analysing"

2. **Auto-Hide Pattern**: Used `st.empty()` placeholder:
```python
status_placeholder = st.empty()

# Show status
with status_placeholder.container():
    st.markdown(f"### Analysing Campaign: {campaign_id}")
    st.success(f"✅ Campaign {campaign_id} loaded instantly")

# Auto-hide after 1.5 seconds
time.sleep(1.5)
status_placeholder.empty()
```

3. **Applied to Both Paths**:
   - FAST PATH (MV cache hit)
   - SLOW PATH (API query)

### Commit

`3b46ed3` - feat: auto-hide analysing status box and use British spelling
