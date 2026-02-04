# UI Implementation Plan - Full Technical Specification

**Created**: 2025-11-22
**Status**: Ready for Implementation
**Priority**: High

---

## Overview

This document provides detailed implementation specifications for bringing `app_api_real.py` to feature parity with `app_demo.py`, plus additional enhancements.

---

## Table of Contents

1. [Reach & GRP Analysis Tab](#1-reach--grp-analysis-tab)
2. [Geographic Analysis Tab](#2-geographic-analysis-tab)
3. [Time Series Tab](#3-time-series-tab)
4. [Executive Summary Tab](#4-executive-summary-tab)
5. [Look & Feel Improvements](#5-look--feel-improvements)
6. [Landing Page Enhancement](#6-landing-page-enhancement)
7. [Future: Geographic Reach Attribution](#7-future-geographic-reach-attribution)

---

## 1. Reach & GRP Analysis Tab

### Current State (`app_api_real.py:2003-2008`)

```python
def render_reach_grp_tab():
    """Render Reach & GRP Analysis tab (placeholder - keep existing functionality)"""
    st.markdown("#### Reach & GRP Analysis")
    st.info("📊 This tab will display reach, GRP, and frequency metrics from the PostgreSQL cache.")
    st.caption("Phase 10: Enhanced reach/GRP/frequency calculations will be added here.")
```

### Reference Implementation (`app_demo.py:521-620`)

```python
def _render_reach_analysis_tab(self):
    """Render reach & GRP analysis tab with DEMO DATA"""
    st.markdown("### 📈 Reach & GRP Analysis")

    # Campaign selector row
    col1, col2, col3 = st.columns([2, 1, 1])

    # Aggregation selector
    aggregation_level = st.selectbox(
        "Aggregation Level:",
        options=["Day", "Week", "Full Campaign"]
    )

    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Reach", "1,234,567")
    with col2:
        st.metric("GRP", "45.67")
    with col3:
        st.metric("Frequency", "2.34")
    with col4:
        st.metric("Total Impacts", "5,678,901")

    # Daily breakdown table (when aggregation = Day)
    demo_data = pd.DataFrame({
        'Date': pd.date_range('2025-08-20', periods=7),
        'Reach': [185234, 198456, 176890, 203567, 195432, 188901, 182345],
        'GRP': [6.52, 6.98, 6.23, 7.16, 6.88, 6.65, 6.42],
        'Frequency': [2.12, 2.28, 2.15, 2.31, 2.25, 2.19, 2.18],
        'Total Impacts': [812456, 905234, 782901, 934567, 867432, 824567, 795678]
    })
```

### Data Sources Available

| Table | Purpose | Fields |
|-------|---------|--------|
| `cache_campaign_reach_week` | Weekly reach metrics | `campaign_id`, `week_number`, `start_date`, `end_date`, `days`, `reach`, `grp`, `frequency`, `total_impacts`, `reach_type` |
| `cache_campaign_reach_full` | Full campaign reach | `campaign_id`, `reach`, `grp`, `frequency`, `total_impacts` |
| `mv_campaign_browser` | Pre-computed summary | `avg_weekly_reach_all_adults`, `full_week_count` |

### Implementation Plan

#### Step 1: Add Database Query Function (`streamlit_queries.py`)

```python
def get_weekly_reach_data_sync(campaign_id: str, use_ms01: bool = None) -> List[Dict]:
    """
    Get weekly reach data for a campaign.
    Returns both individual and cumulative reach types.
    """
    query = """
        SELECT
            week_number,
            start_date,
            end_date,
            days,
            reach,
            grp,
            frequency,
            total_impacts,
            frame_count,
            reach_type,
            route_release_id
        FROM cache_campaign_reach_week
        WHERE campaign_id = %s
        ORDER BY week_number, reach_type
    """
    # ... execute query
```

#### Step 2: Implement `render_reach_grp_tab()` Function

```python
def render_reach_grp_tab():
    """Render Reach & GRP Analysis tab with real cached data"""
    st.markdown("#### Reach & GRP Analysis")

    # Check for campaign data
    if 'campaign_result' not in st.session_state:
        st.warning("No campaign data loaded.")
        return

    campaign_id = st.session_state.selected_campaign_id

    # Load weekly reach data
    weekly_data = get_weekly_reach_data_sync(campaign_id)

    if not weekly_data:
        st.info("No weekly reach data available for this campaign.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(weekly_data)

    # Separate individual vs cumulative
    individual_df = df[df['reach_type'] == 'individual']
    cumulative_df = df[df['reach_type'] == 'cumulative']

    # === SECTION 1: Full Campaign Metrics ===
    st.markdown("### Full Campaign Metrics")

    # Get from cache_campaign_reach_full or sum individual weeks
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_reach = cumulative_df['reach'].max() if len(cumulative_df) > 0 else individual_df['reach'].sum()
        st.metric("Total Reach", f"{total_reach * 1000:,.0f}")

    # ... other metrics ...

    # === SECTION 2: Weekly Reach Table (Individual) ===
    st.markdown("### Weekly Reach & Impacts")
    st.caption("Reach & impacts for each individual week")

    if len(individual_df) > 0:
        display_df = individual_df[['week_number', 'start_date', 'end_date', 'days',
                                     'reach', 'total_impacts', 'grp', 'frequency']].copy()
        # Format columns
        display_df['reach'] = (display_df['reach'] * 1000).astype(int)
        display_df['total_impacts'] = (display_df['total_impacts'] * 1000).astype(int)
        display_df.columns = ['Week', 'Start', 'End', 'Days', 'Reach', 'Impacts', 'GRP', 'Freq']

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Bar chart
        fig = px.bar(
            individual_df,
            x='week_number',
            y=['reach', 'total_impacts'],
            title='Weekly Reach & Impacts',
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

    # === SECTION 3: Cumulative Build Table ===
    st.markdown("### Cumulative Reach Build")
    st.caption("Running total of reach across weeks")

    if len(cumulative_df) > 0:
        # Format cumulative display
        cumulative_display = cumulative_df[['week_number', 'reach', 'total_impacts', 'grp']].copy()
        cumulative_display['reach'] = (cumulative_display['reach'] * 1000).astype(int)
        cumulative_display['total_impacts'] = (cumulative_display['total_impacts'] * 1000).astype(int)
        cumulative_display.columns = ['Week', 'Cumulative Reach', 'Cumulative Impacts', 'Cumulative GRP']

        st.dataframe(cumulative_display, use_container_width=True, hide_index=True)

        # Line chart for reach curve
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cumulative_df['week_number'],
            y=cumulative_df['reach'] * 1000,
            mode='lines+markers',
            name='Cumulative Reach',
            line=dict(color='#2E86AB', width=3)
        ))
        fig.update_layout(
            title='Reach Curve - Cumulative Build',
            xaxis_title='Week',
            yaxis_title='Reach',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
```

### Deliverables

- [ ] `get_weekly_reach_data_sync()` function in `streamlit_queries.py`
- [ ] `render_reach_grp_tab()` implementation with:
  - [ ] Full campaign metrics row
  - [ ] Weekly reach table (individual weeks)
  - [ ] Weekly bar chart
  - [ ] Cumulative build table
  - [ ] Reach curve line chart

---

## 2. Geographic Analysis Tab

### Current State (`app_api_real.py:2012-2016`)

```python
def render_geographic_tab():
    """Render Geographic Analysis tab (placeholder for Phase 11)"""
    st.markdown("#### Geographic Analysis")
    st.info("🗺️ Geographic visualization will be implemented in Phase 11")
```

### Reference Implementation (`app_demo.py:697-784`)

```python
def _render_geographic_tab(self):
    """Render geographic analysis tab with maps"""
    st.markdown("#### Geographic Distribution")

    # Sample geographic data with UK coordinates
    geo_data = pd.DataFrame({
        'Region': ['London', 'Manchester', 'Birmingham', ...],
        'Impacts': [2500000, 1800000, 1200000, ...],
        'Frames': [12, 9, 7, ...],
        'lat': [51.5074, 53.4808, 52.4862, ...],
        'lon': [-0.1278, -2.2426, -1.8904, ...]
    })

    # Interactive UK map using Plotly scatter_mapbox
    fig_map = px.scatter_mapbox(
        geo_data,
        lat='lat', lon='lon',
        size='Impacts',
        color='Impacts',
        hover_name='Region',
        color_continuous_scale=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'],
        size_max=50,
        zoom=5,
        center={'lat': 54.0, 'lon': -2.0},
        mapbox_style='carto-positron'
    )

    # Regional bar chart
    fig = px.bar(
        geo_data,
        x='Region',
        y='Impacts',
        title='Regional Impact Comparison',
        color='Impacts'
    )

    # Regional performance table
    detailed_geo['Avg Impacts/Frame'] = detailed_geo['Impacts'] / detailed_geo['Frames']
    detailed_geo['Market Share'] = (detailed_geo['Impacts'] / total * 100).astype(str) + '%'
```

### Data Sources

| Table | Fields |
|-------|--------|
| `route_frames` | `frameid`, `latitude`, `longitude`, `town`, `tv_region`, `conurbation` |
| `cache_route_impacts_15min_by_demo` | Impacts by frame (join with route_frames for geo) |

### Implementation Plan

#### Step 1: Add Database Query Function

```python
def get_geographic_data_sync(campaign_id: str, use_ms01: bool = None) -> List[Dict]:
    """Get geographic distribution of impacts for a campaign"""
    query = """
        SELECT
            rf.tv_region,
            rf.town,
            rf.latitude,
            rf.longitude,
            COUNT(DISTINCT c.frameid) as frame_count,
            SUM(c.impacts) as total_impacts
        FROM cache_route_impacts_15min_by_demo c
        JOIN route_frames rf ON c.frameid = rf.frameid
        WHERE c.campaign_id = %s
          AND c.demographic_segment = 'all_adults'
          AND rf.latitude IS NOT NULL
        GROUP BY rf.tv_region, rf.town, rf.latitude, rf.longitude
    """
```

#### Step 2: Implement Tab

```python
def render_geographic_tab():
    """Render Geographic Analysis tab with maps"""
    campaign_id = st.session_state.selected_campaign_id

    # Load geographic data
    geo_data = get_geographic_data_sync(campaign_id)

    if not geo_data:
        st.info("No geographic data available")
        return

    df = pd.DataFrame(geo_data)

    # UK Map
    st.markdown("##### Interactive UK Coverage Map")
    fig_map = px.scatter_mapbox(
        df,
        lat='latitude', lon='longitude',
        size='total_impacts',
        color='total_impacts',
        hover_name='town',
        hover_data={'total_impacts': ':,.0f', 'frame_count': True},
        color_continuous_scale=['#2E86AB', '#A23B72', '#F18F01'],
        size_max=50,
        zoom=5,
        center={'lat': 54.0, 'lon': -2.0},
        mapbox_style='carto-positron'
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # Regional breakdown by TV region
    col1, col2 = st.columns(2)

    with col1:
        regional = df.groupby('tv_region').agg({
            'total_impacts': 'sum',
            'frame_count': 'sum'
        }).reset_index().sort_values('total_impacts', ascending=False)

        fig = px.bar(regional, x='tv_region', y='total_impacts',
                     title='Impacts by TV Region')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Sunburst or treemap
        fig = px.sunburst(df, path=['tv_region', 'town'], values='total_impacts')
        st.plotly_chart(fig, use_container_width=True)

    # Detailed table
    st.markdown("#### Regional Performance Metrics")
    st.dataframe(regional, use_container_width=True, hide_index=True)
```

### Deliverables

- [ ] `get_geographic_data_sync()` function
- [ ] `render_geographic_tab()` with:
  - [ ] Interactive UK map (Plotly scatter_mapbox)
  - [ ] Regional bar chart (by TV region)
  - [ ] Frame distribution sunburst
  - [ ] Performance metrics table

---

## 3. Time Series Tab

### Current State (`app_api_real.py:2019-2023`)

```python
def render_time_series_tab():
    """Render Time Series tab (placeholder for Phase 11)"""
    st.markdown("#### Time Series Analysis")
    st.info("⏰ Time series analysis will be implemented in Phase 11")
```

### Reference Implementation (`app_demo.py:786-841`)

```python
def _render_time_series_tab(self):
    """Render time series analysis tab"""
    st.markdown("#### Time Series Analysis")

    # Line chart of impacts over time
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Impacts'],
        mode='lines+markers',
        name='Impacts',
        line=dict(color='#2E86AB', width=3)
    ))

    # Forecast section (expandable)
    with st.expander("📈 Performance Forecast"):
        # Simple forecast chart with dashed line
        fig = px.line(forecast_df, x='Date', y='Forecast',
                      line_dash_sequence=['dash'])
```

### Data Sources

| Table | Fields |
|-------|--------|
| `cache_route_impacts_15min_by_demo` | `time_window_start`, `impacts`, `demographic_segment` |
| `mv_playout_15min` | `time_window_start`, `spot_count`, `frameid` |

### Implementation Plan

```python
def render_time_series_tab():
    """Render Time Series Analysis tab"""
    campaign_id = st.session_state.selected_campaign_id
    result = st.session_state.campaign_result

    if not result:
        st.warning("No campaign data loaded")
        return

    demographic_df = pd.DataFrame(result.get('demographic_data', []))
    all_adults_df = demographic_df[demographic_df['demographic_segment'] == 'all_adults']

    if 'time_window_start' not in all_adults_df.columns:
        st.info("Time data not available")
        return

    st.markdown("#### Time Series Analysis")

    # Daily impacts over time
    daily = all_adults_df.copy()
    daily['date'] = pd.to_datetime(daily['time_window_start']).dt.date
    daily_summary = daily.groupby('date')['impacts'].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_summary['date'],
        y=daily_summary['impacts'],
        mode='lines+markers',
        name='Impacts',
        line=dict(color='#2E86AB', width=3)
    ))
    fig.update_layout(
        title='Campaign Impacts Over Time',
        xaxis_title='Date',
        yaxis_title='Impacts',
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Hourly heatmap
    st.markdown("#### Hourly Impact Pattern")
    hourly = all_adults_df.copy()
    hourly['hour'] = pd.to_datetime(hourly['time_window_start']).dt.hour
    hourly['day'] = pd.to_datetime(hourly['time_window_start']).dt.day_name()

    pivot = hourly.pivot_table(values='impacts', index='day', columns='hour', aggfunc='sum')

    fig = px.imshow(
        pivot,
        labels=dict(x="Hour", y="Day", color="Impacts"),
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Day of week comparison
    st.markdown("#### Day of Week Performance")
    dow = daily.copy()
    dow['weekday'] = pd.to_datetime(dow['date']).dt.day_name()
    dow_summary = dow.groupby('weekday')['impacts'].mean().reset_index()

    # Order days correctly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_summary['weekday'] = pd.Categorical(dow_summary['weekday'], categories=day_order, ordered=True)
    dow_summary = dow_summary.sort_values('weekday')

    fig = px.bar(dow_summary, x='weekday', y='impacts',
                 title='Average Daily Impacts by Day of Week',
                 color_discrete_sequence=['#A23B72'])
    st.plotly_chart(fig, use_container_width=True)
```

### Deliverables

- [ ] `render_time_series_tab()` with:
  - [ ] Campaign impacts over time (line chart)
  - [ ] Hourly heatmap (day x hour)
  - [ ] Day of week comparison (bar chart)
  - [ ] Peak periods identification

---

## 4. Executive Summary Tab

### Current State (`app_api_real.py:2026-2030`)

```python
def render_executive_summary_tab():
    """Render Executive Summary tab (placeholder for Phase 11)"""
    st.markdown("#### Executive Summary")
    st.info("📑 Executive summary will be implemented in Phase 11")
```

### Reference Implementation (`app_demo.py:843-932`)

```python
def _render_executive_summary_tab(self):
    """Render executive summary tab"""
    st.markdown("#### Executive Summary")

    # Two-column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        ### {campaign_name} Performance Report

        **Campaign ID:** {campaign_id}

        #### Key Insights
        - ✅ Generated **{total_impacts:,.0f}** total impressions
        - ✅ Delivered across **{unique_frames}** unique locations
        - ✅ Total of **{total_playouts:,}** playouts
        - ✅ Campaign duration: **{date_range}**

        #### Performance Highlights
        - 📈 **Daily Average:** {daily_avg:,.0f} impacts per day
        - 💰 **Estimated CPM:** £12.50 (industry competitive)
        - 📊 **Peak Performance:** Friday shows highest engagement
        """)

    with col2:
        # Summary metrics table
        metrics_df = pd.DataFrame(...)
        st.dataframe(metrics_df)

        # Daily trend mini-chart
        fig = go.Figure(data=[go.Bar(...)])

    # Export buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("📄 Export PDF Report")
    with col2:
        st.button("📊 Export Excel Data")
    with col3:
        st.button("📧 Email Summary")
```

### Implementation Plan

```python
def render_executive_summary_tab():
    """Render Executive Summary tab"""
    campaign_id = st.session_state.selected_campaign_id
    result = st.session_state.campaign_result

    if not result:
        st.warning("No campaign data loaded")
        return

    st.markdown("#### Executive Summary")

    # Extract metrics
    demographic_df = pd.DataFrame(result.get('demographic_data', []))
    all_adults_df = demographic_df[demographic_df['demographic_segment'] == 'all_adults']

    total_impacts = all_adults_df['impacts'].sum()
    unique_frames = demographic_df['frameid'].nunique() if 'frameid' in demographic_df.columns else 0
    total_playouts = len(demographic_df) // 7 if len(demographic_df) > 0 else 0

    # Date range
    if 'time_window_start' in demographic_df.columns:
        dates = pd.to_datetime(demographic_df['time_window_start'])
        date_range = f"{dates.min().date()} to {dates.max().date()}"
        unique_days = dates.dt.date.nunique()
    else:
        date_range = "N/A"
        unique_days = 7

    daily_avg = total_impacts / unique_days if unique_days > 0 else 0

    # Performance grade calculation
    # Based on impacts per frame vs benchmark
    impacts_per_frame = total_impacts / unique_frames if unique_frames > 0 else 0

    if impacts_per_frame >= 10000:
        grade = "A"
        grade_class = "grade-excellent"
        grade_label = "Excellent"
    elif impacts_per_frame >= 5000:
        grade = "B"
        grade_class = "grade-good"
        grade_label = "Good"
    else:
        grade = "C"
        grade_class = "grade-needs-improvement"
        grade_label = "Needs Improvement"

    # Two-column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        ### Campaign {campaign_id} Performance Report

        **Campaign ID:** {campaign_id}

        #### Key Insights
        - ✅ Generated **{total_impacts:,.0f}** total impressions
        - ✅ Delivered across **{unique_frames:,}** unique locations
        - ✅ Total of **{total_playouts:,}** playouts
        - ✅ Campaign duration: **{date_range}**

        #### Performance Highlights
        - 📈 **Daily Average:** {daily_avg:,.0f} impacts per day
        - 📊 **Avg Impacts/Frame:** {impacts_per_frame:,.0f}
        """)

    with col2:
        # Performance grade badge
        st.markdown(f"""
        <div class="performance-grade {grade_class}">
            <h1>{grade}</h1>
            <p>{grade_label}</p>
        </div>
        """, unsafe_allow_html=True)

        # Summary table
        metrics_data = {
            'Total Impacts': f"{total_impacts:,.0f}",
            'Total Playouts': f"{total_playouts:,}",
            'Unique Frames': f"{unique_frames:,}",
            'Date Range': date_range,
            'Daily Average': f"{daily_avg:,.0f}"
        }
        metrics_df = pd.DataFrame(list(metrics_data.items()), columns=['Metric', 'Value'])
        st.dataframe(metrics_df, hide_index=True, use_container_width=True)

        # Mini daily chart
        if 'time_window_start' in all_adults_df.columns:
            daily = all_adults_df.copy()
            daily['day'] = pd.to_datetime(daily['time_window_start']).dt.day_name()
            daily_summary = daily.groupby('day')['impacts'].sum().reset_index()

            fig = go.Figure(data=[
                go.Bar(x=daily_summary['day'], y=daily_summary['impacts'],
                       marker_color='#73AB84')
            ])
            fig.update_layout(showlegend=False, height=200,
                              margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        csv = all_adults_df.to_csv(index=False)
        st.download_button("📄 Download CSV", data=csv,
                          file_name=f"campaign_{campaign_id}_summary.csv",
                          mime="text/csv")

    with col2:
        st.button("📊 Export Excel Data", disabled=True,
                  help="Excel export coming soon")

    with col3:
        st.button("📧 Email Summary", disabled=True,
                  help="Email functionality coming soon")
```

### Deliverables

- [ ] `render_executive_summary_tab()` with:
  - [ ] Performance grade badge (A-F)
  - [ ] Key insights markdown
  - [ ] Metrics summary table
  - [ ] Mini daily chart
  - [ ] Export buttons (CSV working, others placeholder)

---

## 5. Look & Feel Improvements

### Current CSS (`app_api_real.py:53-288`)

The current CSS is already extensive. Key improvements needed:

### Styling Enhancements

#### A. Consistent Card Styling
```css
/* Add to existing CSS */
.metric-card {
    background: linear-gradient(135deg, rgba(46,134,171,0.1) 0%, rgba(162,59,114,0.1) 100%);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border: 1px solid rgba(46,134,171,0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
```

#### B. Improved Table Styling
```css
/* Enhanced dataframe styling */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

[data-testid="stDataFrame"] thead tr th {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white !important;
    font-weight: 600;
    padding: 12px 16px;
}

[data-testid="stDataFrame"] tbody tr:nth-child(even) {
    background-color: rgba(46,134,171,0.03);
}
```

#### C. Chart Color Palette Consistency
```python
# Define consistent color palette
CHART_COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#73AB84',
    'warning': '#C73E1D',
    'gradient': ['#2E86AB', '#A23B72', '#F18F01', '#73AB84', '#C73E1D']
}
```

### Deliverables

- [ ] Add metric card styling
- [ ] Enhance table styling
- [ ] Define color palette constants
- [ ] Add loading state animations
- [ ] Improve spacing and visual hierarchy

---

## 6. Landing Page Enhancement

### Current Landing Page (`app_api_real.py:648-1151`)

The landing page with campaign browser is comprehensive. Enhancements needed:

### A. Hero Section Improvement

```python
def render_campaign_selector():
    # Enhanced header with stats
    st.markdown("""
        <div class="hero-section">
            <h1>Route Playout Analytics</h1>
            <p>Analyze campaign performance with real-time audience insights</p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="stat-value">836</span>
                    <span class="stat-label">Campaigns</span>
                </div>
                <div class="hero-stat">
                    <span class="stat-value">1.27B</span>
                    <span class="stat-label">Playouts</span>
                </div>
                <div class="hero-stat">
                    <span class="stat-value">252.7M</span>
                    <span class="stat-label">Cached Records</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
```

### B. Quick Stats Cards (Above Browser)

```python
# Show key stats prominently before table
col1, col2, col3, col4 = st.columns(4)

summary = load_campaign_browser_summary()

with col1:
    st.metric("Total Campaigns", f"{summary['total_campaigns']:,}")

with col2:
    playouts_b = summary['total_playouts'] / 1e9
    st.metric("Total Playouts", f"{playouts_b:.2f}B")

with col3:
    st.metric("With Route Data", f"{summary['campaigns_with_route_data']:,}")

with col4:
    st.metric("Unique Brands", summary['unique_brands_count'])
```

### C. Search Enhancement

```python
# Enhanced search with filters
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    search_query = st.text_input(
        "🔍 Search campaigns",
        placeholder="Search by campaign ID, brand, media owner..."
    )

with col2:
    brand_filter = st.selectbox(
        "Filter by Brand",
        options=["All Brands"] + sorted(df['primary_brand'].unique().tolist())
    )

with col3:
    media_owner_filter = st.selectbox(
        "Filter by Media Owner",
        options=["All Media Owners"] + sorted(df['primary_media_owner'].unique().tolist())
    )
```

### Deliverables

- [ ] Hero section with live stats
- [ ] Quick stats row above browser
- [ ] Enhanced search with filters
- [ ] Improved navigation flow

---

## 7. Future: Geographic Reach Attribution

### Overview

Show where campaign audiences come from - reach/impact contribution by geographic area (town level).

### Requirements

1. **Additional Data Needed**:
   - Route API provides town-level audience data
   - Need to cache town-level reach breakdowns

2. **Database Changes**:
   ```sql
   CREATE TABLE cache_campaign_reach_by_town (
       campaign_id VARCHAR(50),
       town VARCHAR(255),
       tv_region VARCHAR(100),
       latitude NUMERIC(10, 6),
       longitude NUMERIC(10, 6),
       reach NUMERIC,
       impacts NUMERIC,
       population NUMERIC,
       cover_pct NUMERIC,
       route_release_id INTEGER,
       cached_at TIMESTAMP DEFAULT NOW()
   );
   ```

3. **Visualization**:
   - UK choropleth map (towns colored by reach contribution)
   - Town contribution table (ranked by reach)
   - Regional breakdown pie chart

### Value

High for econometricians - understanding geographic distribution of campaign effectiveness enables better planning and attribution.

### Complexity

Significant - requires:
- New Route API data extraction
- Database schema changes
- Complex choropleth mapping (UK boundaries)
- Town-level aggregation logic

---

## Implementation Order

| Priority | Feature | Effort | Dependencies |
|----------|---------|--------|--------------|
| 1 | Reach & GRP Analysis Tab | Medium | `cache_campaign_reach_week` (data exists) |
| 2 | Executive Summary Tab | Low | Uses existing data |
| 3 | Time Series Tab | Low | Uses existing data |
| 4 | Geographic Analysis Tab | Medium | `route_frames` geo data |
| 5 | Look & Feel | Medium | None |
| 6 | Landing Page Enhancement | Low | None |
| 7 | Geographic Attribution | High | New data pipeline |

---

## Code File References

| File | Key Lines | Purpose |
|------|-----------|---------|
| `src/ui/app_demo.py` | 521-620 | Demo Reach tab |
| `src/ui/app_demo.py` | 697-784 | Demo Geographic tab |
| `src/ui/app_demo.py` | 786-841 | Demo Time Series tab |
| `src/ui/app_demo.py` | 843-932 | Demo Executive Summary tab |
| `src/ui/app_api_real.py` | 2003-2030 | Current placeholder tabs |
| `src/db/streamlit_queries.py` | 112-172 | Campaign browser queries |

---

*Created: 2025-11-22*
*Last Updated: 2025-11-22*
