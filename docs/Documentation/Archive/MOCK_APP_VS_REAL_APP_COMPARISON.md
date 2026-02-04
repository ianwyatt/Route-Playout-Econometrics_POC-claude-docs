# Mock App vs Real App - Feature Comparison

**Created**: 2025-11-15
**Purpose**: Document differences between app_demo.py (mock/board presentation app) and app_api_real.py (real data app)

---

## 📊 High-Level Architecture

### Mock App (`app_demo.py`)
- **Lines**: 1004
- **Structure**: Class-based (`BalancedPOCApp`)
- **Service**: `OptimizedCampaignService`
- **State**: Session state management
- **Sidebar**: Collapsed by default (no visible sidebar)
- **Navigation**: Campaign selector → Analysis view

### Real App (`app_api_real.py`)
- **Lines**: ~1100
- **Structure**: Functional (no class)
- **Service**: `CampaignService` (cache-first)
- **State**: Minimal session state
- **Sidebar**: Visible with configuration options
- **Navigation**: Tabs visible from start

---

## ✨ Key Features Comparison

| Feature | Mock App | Real App | Status |
|---------|----------|----------|--------|
| **Campaign Selector** | ✅ Dedicated view with 4 demo buttons | ❌ Only text input + analyze button | 🔴 Missing |
| **Campaign Browser** | ⚠️ Hardcoded 4 campaigns | ❌ No browsing capability | 🔴 Missing |
| **Sidebar Configuration** | ❌ No sidebar (collapsed) | ✅ Visible sidebar | 🟡 Wrong approach |
| **Key Metrics Row** | ✅ 5 metrics (Impacts, Playouts, Frames, Daily Avg, Peak Hour) | ✅ 1 metric (All Adults impacts only) | 🔴 Incomplete |
| **Tabs** | ✅ 6 tabs | ✅ 4 tabs | 🟡 Missing 2 tabs |
| **Export Button** | ✅ In header | ✅ In tabs | 🟢 Present |
| **New Analysis Button** | ✅ In header | ❌ Must use sidebar | 🔴 Missing |
| **Reach/GRP/Frequency** | ✅ Displayed in metrics | ❌ Only impacts shown | 🔴 Missing |
| **Charts** | ✅ Multiple chart types | ⚠️ Basic charts only | 🟡 Incomplete |
| **Visual Polish** | ✅ Professional gradients | ⚠️ Basic styling | 🟡 Needs work |

---

## 📋 Detailed Feature Breakdown

### 1. Campaign Selector (Mock App Only)

**Location**: Lines 212-281

**Features**:
- Clean landing page before analysis
- 4 demo campaign buttons with emojis:
  - 🏖️ Summer Sale (16012)
  - 🎯 Brand Campaign (16013)
  - 📈 Q4 Campaign (16014)
  - 🔴 Live API Demo (16015)
- Custom campaign input field
- "Analyse" button (primary)
- Expandable "Platform Features" overview

**Real App**: No campaign selector - goes straight to analysis interface

---

### 2. Key Metrics Row

**Mock App** (Lines 341-393):
```
5 metrics displayed:
1. Total Impacts (with tooltip)
2. Total Playouts (with tooltip)
3. Unique Frames (with tooltip)
4. Daily Average (with delta "↑ 12%")
5. Peak Hour (with delta "8-9am")
```

**Real App**:
```
1 metric displayed:
1. All Adults (15+) impacts only
```

**Missing**: Playouts, Frames, Daily Average, Peak Hour, Reach, GRP, Frequency

---

### 3. Tab Structure

#### Mock App Tabs (6 total):
1. **📊 Overview** - Campaign details + Quick Stats (Daily/Hourly/Frames sub-tabs)
2. **📈 Reach & GRP Analysis** - Detailed reach metrics with visualizations
3. **📊 Performance Charts** - Multiple chart types
4. **🗺️ Geographic Analysis** - Maps and geographic distribution
5. **⏰ Time Series** - Time-based analysis
6. **📑 Executive Summary** - High-level summary for stakeholders

#### Real App Tabs (4 total):
1. **📍 Campaign Analysis** - Basic campaign query interface
2. **📊 Reach & GRP Analysis** - Minimal reach interface
3. **🧪 API Testing** - Manual API request builder (not needed)
4. **📄 Playout Data** - Playout loader (not needed)

**Missing Tabs**:
- Overview (with sub-visualizations)
- Performance Charts
- Geographic Analysis
- Time Series
- Executive Summary

**Unnecessary Tabs**:
- API Testing (developer tool, not user-facing)
- Playout Data (not needed for POC)

---

### 4. Overview Tab Features (Mock App)

**Left Column** (Lines 400-432):
- Campaign Details table with 9 metrics:
  - Total Frames
  - Date Range
  - Total Playouts
  - Campaign Duration
  - Avg Impacts/Frame
  - Avg Impacts/Playout
  - Peak Day
  - Peak Hour
  - Processing Time

**Right Column** (Lines 434-503):
- Quick Stats with 3 sub-tabs:
  - **Daily**: Bar chart of impacts by day (Mon-Sun)
  - **Hourly**: Line chart of hourly impact pattern
  - **Frames**: Horizontal bar chart of top 5 performing frames

**Additional Section** (Lines 507-520):
- Frame Performance Analysis
- 3 metrics showing frame efficiency

**Real App**: No overview tab exists

---

### 5. Reach & GRP Analysis Tab

#### Mock App (Lines 521-621):
- Audience reach visualization
- GRP calculations
- Frequency distribution
- Multiple chart types:
  - Reach curve
  - Frequency histogram
  - Cumulative reach

#### Real App:
- Campaign ID input
- Aggregation level selector (Day/Week/Full Campaign)
- Date range picker
- "Calculate Reach" button
- Minimal output display

**Issue**: Real app requires manual calculation - not intuitive

---

### 6. Performance Charts Tab (Mock App Only)

**Location**: Lines 622-696

**Features**:
- Impact trends over time
- Frame performance comparison
- Day-of-week analysis
- Hour-of-day heatmap
- Interactive plotly charts

**Real App**: No dedicated performance charts tab

---

### 7. Geographic Analysis Tab (Mock App Only)

**Location**: Lines 697-785

**Features**:
- Geographic heat maps
- Frame location visualization
- Regional performance breakdown
- Interactive map controls

**Real App**: No geographic analysis

---

### 8. Time Series Tab (Mock App Only)

**Location**: Lines 786-842

**Features**:
- Hourly impact trends
- Daily patterns
- Time-of-day optimization
- Peak period identification

**Real App**: No time series analysis

---

### 9. Executive Summary Tab (Mock App Only)

**Location**: Lines 843-1001

**Features**:
- High-level KPIs
- Performance grade (Excellent/Good/Needs Improvement)
- Key insights summary
- Recommended actions
- Exportable summary report

**Real App**: No executive summary

---

## 🎨 Visual Design Differences

### Mock App Strengths:
1. **Professional gradient header** - Linear gradient (primary → secondary)
2. **Metric cards with left border** - 4px colored border
3. **Hover effects on buttons** - Transform & shadow
4. **Performance grades** - Color-coded badges
5. **Tab styling** - Selected tab has gradient background
6. **Consistent spacing** - Clean visual hierarchy

### Real App Issues:
1. **Visible sidebar** - Takes up screen space
2. **No campaign selector** - Jumps straight to analysis
3. **Minimal metrics** - Only shows impacts
4. **Basic charts** - Missing polish
5. **Configuration in sidebar** - Should be in settings cog

---

## 🔧 Configuration Differences

### Mock App:
- **No visible sidebar** (`initial_sidebar_state="collapsed"`)
- Configuration managed internally
- Clean, uncluttered interface

### Real App:
- **Visible sidebar with:**
  - Configuration section
  - REAL API MODE badge
  - Route API status
  - SPACE API status
  - Route Release selector
  - Date Adjustment checkbox
  - API Settings (max frames, max schedules)

**Issue**: Configuration should be in a cog/settings icon, not always-visible sidebar

---

## 📊 Data Flow Comparison

### Mock App Flow:
```
1. Landing page (campaign selector)
   ↓
2. Click campaign button OR enter custom ID
   ↓
3. Load campaign data (OptimizedCampaignService)
   ↓
4. Display analysis with all 6 tabs
   ↓
5. "New Analysis" button → back to step 1
```

### Real App Flow:
```
1. Configure settings in sidebar
   ↓
2. Enter campaign ID in tab 1
   ↓
3. Click "Analyze" button
   ↓
4. Display results in same tab
   ↓
5. Demographic selector appears
   ↓
6. Charts render below
```

**Issue**: Real app has no clear campaign browsing or selection workflow

---

## 🚨 Critical Issues to Fix

### Priority 1 (High Impact):
1. **Add campaign selector landing page** - Like mock app
2. **Remove visible sidebar** - Collapse by default
3. **Add all 5 key metrics** - Impacts, Playouts, Frames, Daily Avg, Peak Hour
4. **Add Reach/GRP/Frequency** - To metrics and analysis
5. **Restructure tabs** - Match mock app's 6-tab structure

### Priority 2 (Medium Impact):
6. **Port Overview tab** - With sub-tabs (Daily/Hourly/Frames)
7. **Port Performance Charts tab** - Multiple visualizations
8. **Port Geographic Analysis tab** - Maps and regional breakdown
9. **Port Time Series tab** - Hourly/daily patterns
10. **Port Executive Summary tab** - Stakeholder-friendly summary

### Priority 3 (Polish):
11. **Move configuration to cog icon** - Remove sidebar
12. **Improve visual design** - Match mock app gradients and styling
13. **Add "New Analysis" button** - In header, not sidebar
14. **Add export functionality** - In header

### Priority 4 (Cleanup):
15. **Remove API Testing tab** - Not needed for users
16. **Remove Playout Data tab** - Not needed for POC
17. **Remove API documentation** - Replace with user guide

---

## 📝 Recommended Implementation Strategy

### Phase 1: Foundation (Quick Wins)
1. Collapse sidebar by default
2. Add campaign selector landing page
3. Add 5 key metrics row
4. Add "New Analysis" button in header

### Phase 2: Core Features
5. Restructure to 6-tab layout
6. Port Overview tab with sub-tabs
7. Add Reach/GRP/Frequency calculations
8. Port Performance Charts tab

### Phase 3: Advanced Features
9. Port Geographic Analysis tab
10. Port Time Series tab
11. Port Executive Summary tab

### Phase 4: Polish & Cleanup
12. Move configuration to cog icon
13. Match visual design from mock app
14. Remove unnecessary tabs
15. Add comprehensive export

---

## 🎯 Success Criteria

**When real app matches mock app, we should have:**

✅ Campaign selector landing page
✅ 4+ demo campaign buttons
✅ No visible sidebar (collapsed)
✅ 5 key metrics in header row
✅ 6 comprehensive tabs
✅ Reach/GRP/Frequency displayed
✅ Multiple chart types and visualizations
✅ Geographic analysis with maps
✅ Time series analysis
✅ Executive summary for stakeholders
✅ Professional visual design
✅ Configuration in cog icon
✅ Export functionality in header
✅ "New Analysis" workflow

---

**Last Updated**: 2025-11-15
**For**: Route Playout Econometrics POC Development Team
**Next Steps**: Review with Doctor Biz and prioritize implementation phases
