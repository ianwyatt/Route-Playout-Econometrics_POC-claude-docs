# Plan: Add Demographic Filters to Campaign Tabs

## Objective
Add demographic filtering to the "Weekly Reach, Impacts & GRPs" and "Daily & Hourly Patterns" tabs, following the same pattern used in the Geographic tab.

---

## Current State Analysis

### Geographic Tab (reference implementation)
- Uses `st.selectbox` for demographic selection
- Calls `get_available_demographics_for_campaign_sync()` to get available options
- Passes `selected_demographic` parameter to all data-fetching functions
- Defaults to "All Adults (15+)"

### Weekly Reach Tab (`reach_grp.py`)
- Currently NO demographic filtering
- Uses `get_weekly_reach_data_sync()` → queries `cache_campaign_reach_week` table
- **Issue**: Need to verify if `cache_campaign_reach_week` has demographic data

### Daily & Hourly Patterns Tab (`time_series.py`)
- Currently NO demographic filtering
- Uses:
  - `get_daily_impacts_sync()` → `mv_cache_campaign_impacts_day`
  - `get_hourly_impacts_sync()` → `mv_cache_campaign_impacts_1hr`
- **Good news**: Both MVs have `demographic_segment` column - currently hardcoded to `'all_adults'`

---

## Implementation Plan

### Step 1: Update Database Queries (src/db/streamlit_queries.py)

#### 1a. Modify `get_daily_impacts_sync()`
- Add `demographic: str = 'all_adults'` parameter
- Replace hardcoded `'all_adults'` with parameterised value
- Both MV and fallback queries need updating

#### 1b. Modify `get_hourly_impacts_sync()`
- Add `demographic: str = 'all_adults'` parameter
- Replace hardcoded `'all_adults'` with parameterised value
- Both MV and fallback queries need updating

#### 1c. Check `get_weekly_reach_data_sync()`
- Investigate `cache_campaign_reach_week` table schema
- If demographic column exists: add parameter
- If not: may need different approach or skip this tab

### Step 2: Update Cached Loaders (src/ui/app_api_real.py)

#### 2a. Update `load_daily_impacts()`
- Add `demographic` parameter
- Pass through to `get_daily_impacts_sync()`
- Update cache key to include demographic

#### 2b. Update `load_weekly_reach_data()` (if applicable)
- Add `demographic` parameter if backend supports it

### Step 3: Update Daily & Hourly Patterns Tab (src/ui/tabs/time_series.py)

- Import demographic config and query functions
- Add demographic selector (copy pattern from geographic.py):
  ```python
  from src.ui.config.demographics import DEMOGRAPHIC_SORT_ORDER, get_demographic_display_name
  from src.db.streamlit_queries import get_available_demographics_for_campaign_sync
  ```
- Get available demographics for campaign
- Create selectbox with sorted options
- Pass `selected_demographic` to `get_daily_impacts_sync()` and `get_hourly_impacts_sync()`
- Update UI labels to show selected demographic

### Step 4: Update Weekly Reach Tab (src/ui/tabs/reach_grp.py)

- Same pattern as Step 3
- Add demographic selector
- Pass demographic to data loading functions
- Update chart/table titles to reflect selected demographic

### Step 5: Testing
- Test both tabs with different demographic selections
- Verify data changes when demographic is switched
- Ensure "All Adults (15+)" remains default
- Check performance (queries should remain fast with MV)

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/db/streamlit_queries.py` | Add demographic param to `get_daily_impacts_sync`, `get_hourly_impacts_sync`, possibly `get_weekly_reach_data_sync` |
| `src/ui/app_api_real.py` | Update cached loader functions with demographic param |
| `src/ui/tabs/time_series.py` | Add demographic selector UI, pass to queries |
| `src/ui/tabs/reach_grp.py` | Add demographic selector UI, pass to queries |

---

## Findings

### Weekly Reach Tab - NO demographic support
Checked `cache_campaign_reach_week` table - **no demographic column exists**.

Reach/GRP calculations require complex Route API calls and are only computed for All Adults (15+). This is standard industry practice.

**Decision**: Skip demographic filter for Weekly Reach tab, OR add note explaining "Reach & GRP metrics are calculated for All Adults (15+) only"

### Daily & Hourly Patterns Tab - FULL demographic support
Both MVs (`mv_cache_campaign_impacts_day` and `mv_cache_campaign_impacts_1hr`) have `demographic_segment` column. Ready to implement.

---

## Estimated Effort
- Database queries: 15 mins
- Time series tab: 20 mins
- Weekly reach tab: 20 mins (or skip if no demographic data)
- Testing: 15 mins

**Total: ~1 hour**
