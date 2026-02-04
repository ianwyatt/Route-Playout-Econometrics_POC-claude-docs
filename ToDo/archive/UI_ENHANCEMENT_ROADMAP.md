# UI Enhancement Roadmap

**Created**: 2025-11-22
**Updated**: 2025-11-22
**Status**: In Progress (Phases 1-3 Complete, Instant Load Implemented)
**Priority**: High

---

## Overview

This document tracks UI enhancements needed to bring the real API app (`app_api_real.py`) to feature parity with the demo app, plus additional improvements.

---

## High Priority

### 1. Reach & GRP Analysis Tab
**Status**: Placeholder
**Location**: `render_reach_grp_tab()` in `app_api_real.py`

Port functionality from demo app including:
- [ ] Weekly reach & impacts table (individual week metrics)
- [ ] Cumulative reach & impacts build (running total)
- [ ] Weekly bar chart (reach/impacts per week)
- [ ] Cumulative reach curve (line chart)
- [ ] GRP trends
- [ ] Frequency distribution

**Data Sources**:
- `cache_campaign_reach_week` (reach_type = 'individual' for weekly, 'cumulative' for build)
- `cache_campaign_reach_full` for full campaign metrics

### 2. Look & Feel Improvements
**Status**: Not started

- [ ] Review overall styling consistency
- [ ] Improve color scheme and visual hierarchy
- [ ] Polish card layouts and spacing
- [ ] Enhance chart styling (consistent colors, legends, labels)
- [ ] Improve table formatting
- [ ] Add loading states and transitions
- [ ] Review mobile/responsive behavior

### 3. Landing Page Enhancement
**Status**: Not started

- [ ] Improve header/hero section
- [ ] Better navigation flow
- [ ] Clear call-to-action for campaign selection
- [ ] Summary statistics presentation
- [ ] Quick access to key features

---

## Medium Priority

### 4. Geographic Analysis Tab
**Status**: Placeholder
**Location**: `render_geographic_tab()` in `app_api_real.py`

Port functionality from demo app including:
- [ ] UK map with frame locations (Plotly scatter_mapbox)
- [ ] Regional performance bar chart
- [ ] TV region breakdown
- [ ] Environment distribution chart

**Data Sources**:
- Frame location data from playout tables
- Geographic aggregations

### 5. Time Series Tab
**Status**: Placeholder
**Location**: `render_time_series_tab()` in `app_api_real.py`

Port functionality from demo app including:
- [ ] Hourly impacts line chart
- [ ] Day-of-week performance bars
- [ ] Peak periods analysis
- [ ] Time period comparisons

**Data Sources**:
- `cache_route_impacts_15min_by_demo` for time-based metrics
- `mv_playout_15min` for playout timing

### 6. Executive Summary Tab
**Status**: Placeholder
**Location**: `render_executive_summary_tab()` in `app_api_real.py`

Port functionality from demo app including:
- [ ] Performance grade badge (A-F with color styling)
- [ ] Key metrics summary grid
- [ ] Campaign health indicators
- [ ] Insights and recommendations bullets
- [ ] Benchmark comparisons

---

## Future Enhancements

### 7. Geographic Reach Attribution
**Status**: Future
**Priority**: High value, significant work

**Goal**: Show where campaign audiences come from - reach/impact contribution by geographic area (town level).

**Requirements**:
- [ ] Additional geographic data from Route API
- [ ] Town-level aggregation in database
- [ ] UK choropleth map visualization
- [ ] Town contribution table
- [ ] Regional breakdown charts

**Value**: High for econometricians - understanding geographic distribution of campaign effectiveness.

**Complexity**: Significant - requires new data pipeline work and complex mapping visualizations.

---

## Reference: Demo App Features

Source: `src/ui/app_demo.py`

| Method | Lines | Description |
|--------|-------|-------------|
| `_render_overview_tab()` | 395-519 | Key metrics, playout stats |
| `_render_reach_analysis_tab()` | 521-620 | Reach curves, GRP, frequency |
| `_render_performance_charts_tab()` | 622-695 | Daily/hourly/frame charts |
| `_render_geographic_tab()` | 697-784 | UK map, regional analysis |
| `_render_time_series_tab()` | 786-841 | Temporal patterns |
| `_render_executive_summary_tab()` | 843-end | Performance grade, insights |

---

## Data Availability

| Feature | Data Source | Available |
|---------|-------------|-----------|
| Weekly reach/impacts | `cache_campaign_reach_week` | Yes |
| Cumulative build | `cache_campaign_reach_week` (cumulative) | Yes |
| Full campaign metrics | `cache_campaign_reach_full` | Yes |
| 15-min impacts | `cache_route_impacts_15min_by_demo` | Yes |
| Daily impacts (fast) | `mv_cache_campaign_impacts_day` | Yes |
| Hourly impacts (fast) | `mv_cache_campaign_impacts_1hr` | Yes |
| Campaign summary | `mv_campaign_browser` | Yes |
| Frame locations | `playout_data` + Route API | Partial |
| Town-level reach | Route API | Not yet cached |

---

## Performance Optimization

### Materialized View Strategy (Implemented 2025-11-22)

Queries now use pre-aggregated materialized views instead of the 41GB raw table:

| Query | Before | After | Improvement |
|-------|--------|-------|-------------|
| Daily impacts | `cache_route_impacts_15min_by_demo` (41GB) | `mv_cache_campaign_impacts_day` (5.6MB) | ~7000x smaller |
| Hourly impacts | `cache_route_impacts_15min_by_demo` (41GB) | `mv_cache_campaign_impacts_1hr` (99MB) | ~400x smaller |

**Implementation**: Functions in `streamlit_queries.py` now:
1. Try MV first for fast queries
2. Fall back to raw table if campaign not in MV (ensures completeness)

**Files Modified**: `src/db/streamlit_queries.py`
- `get_daily_impacts_sync()` - Uses `mv_cache_campaign_impacts_day`
- `get_hourly_impacts_sync()` - Uses `mv_cache_campaign_impacts_1hr`

---

## Progress Tracking

| Item | Status | Notes |
|------|--------|-------|
| Reach & GRP Analysis | **COMPLETE** | Weekly table, bar chart, cumulative build with curve selector |
| Weekly reach table | **COMPLETE** | Part of Reach tab |
| Cumulative build chart | **COMPLETE** | Part of Reach tab |
| Time Series | **COMPLETE** | Daily line, day of week bar, hourly heatmap |
| Executive Summary | **COMPLETE** | Performance grade, insights, CSV export |
| MV Query Optimization | **COMPLETE** | Use MVs with fallback to raw table |
| Streamlit Caching | **COMPLETE** | @st.cache_data decorators for campaign data |
| Instant Campaign Load | **COMPLETE** | MV-first pattern in analyze_campaign(), <10ms load time |
| Look & Feel | Not started | High priority |
| Landing Page | Not started | High priority |
| Geographic Analysis | Not started | Medium priority |
| Geographic Attribution | Future | Requires new data |

---

## Detailed Implementation Plan

For full technical specifications, code examples, and step-by-step implementation guidance, see:
**[UI_IMPLEMENTATION_PLAN.md](./UI_IMPLEMENTATION_PLAN.md)**

This includes:
- Complete code snippets for each tab
- Database query functions needed
- Reference to demo app code locations
- Implementation order and dependencies

---

*Last Updated: 2025-11-22*
