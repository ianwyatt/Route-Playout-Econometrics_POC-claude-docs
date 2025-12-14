# Route Playout Econometrics POC - Complete Project Structure Analysis

**Date**: 2025-10-17
**Purpose**: Comprehensive analysis of current project structure before reorganization
**Status**: Analysis Complete, Awaiting Reorganization Decisions

---

## 🎯 Executive Summary

The Route Playout Econometrics POC has **7 application files** across two main versions, plus multiple supporting scripts and documentation. The project has grown organically, resulting in:

- **Fragile import system** (45+ files with sys.path hacks)
- **Brittle path references** (22 files with hardcoded config loading)
- **Unclear version separation** (files named similarly, hard to distinguish)
- **Multiple legacy/testing versions** that may no longer be needed

This document provides a complete analysis to guide reorganization decisions.

---

## 📊 Application Inventory

### Current Application Files (7 Total)

| # | File | Port | Type | Lines | Status | Last Modified |
|---|------|------|------|-------|--------|---------------|
| 1 | `src/ui/app_mock_full.py` | 8503 | **V1 Main** | 1,207 | ✅ Production | Recent |
| 2 | `src/ui/app_api_real.py` | 8504 | **V2 Main** | 585 | 🔄 In Dev | Recent |
| 3 | `src/ui/app_hybrid_demo.py` | 8505 | V2 Testing | 644 | 🧪 Testing | Recent |
| 4 | `src/ui/app_mock_simple.py` | 8502 | V1 Variant | 358 | ✅ Working | Recent |
| 5 | `src/ui/app_mock_modular.py` | 8507 | V1 Variant | 360 | ✅ Working | Recent |
| 6 | `src/ui/app.py` | 8501 | Legacy | 673 | 📦 Old | Older |
| 7 | `src/ui/app_enhanced.py` | 8506 | Legacy | 682 | 📦 Old | Older |

**Total Lines of UI Code**: 4,509 lines across 7 files

---

## 🏗️ Version 1: Mock Data (Demo/Board Presentation)

### Primary Application
**File**: `src/ui/app_mock_full.py` (1,207 lines)
- **Port**: 8503
- **Purpose**: Board demo, fast response time (<3 seconds)
- **Status**: ✅ **PRODUCTION READY**
- **Features**:
  - Complete mock data pipeline
  - All visualizations working
  - Cost upload functionality
  - 3D business charts
  - Executive summary
  - Multi-tab interface

### Dependencies (Version 1 Specific)
```
Mock Data Generation:
├── src/utils/mock_data_factory.py (221 lines)
├── src/utils/mock_data_generator.py (295 lines)
└── src/ui/data/mock_geo_data.py (467 lines)

Services (Mock Mode):
├── src/api/campaign_service.py (383 lines)
└── src/api/campaign_service_optimized.py (195 lines)

Mock Configuration:
└── USE_MOCK_DATA=True in config
```

### Variant Applications

#### 1. `app_mock_simple.py` (358 lines)
- **Port**: 8502
- **Purpose**: Simplified demo without advanced features
- **Status**: ✅ Working
- **Features**: Basic campaign display, minimal tabs
- **Value**: Unknown - possibly for simple demos?

#### 2. `app_mock_modular.py` (360 lines)
- **Port**: 8507
- **Purpose**: Modular architecture demonstration
- **Status**: ✅ Working
- **Features**: Similar to simple, different code structure
- **Value**: Unknown - architectural experiment?

### Assessment Questions for Version 1
- ✅ Keep `app_mock_full.py` (main demo app)
- ❓ Keep `app_mock_simple.py`? (When is this used?)
- ❓ Keep `app_mock_modular.py`? (Is this still needed?)

---

## 🚀 Version 2: Live API (Production Target)

### Primary Application
**File**: `src/ui/app_api_real.py` (585 lines)
- **Port**: 8504
- **Purpose**: Real Route API integration
- **Status**: 🔄 **IN DEVELOPMENT** (works but slow)
- **Features**:
  - Direct Route API calls
  - Real playout CSV loading
  - Live audience calculations
  - Performance: >10 seconds (needs optimization)

### Dependencies (Version 2 Specific)
```
API Clients:
├── src/api/route_client.py (295 lines)
├── src/services/route_service.py (428 lines)
└── src/services/space_service.py (198 lines)

Data Processing:
├── src/api/playout_processor.py (531 lines)
└── src/utils/time_converter.py (224 lines)

API Configuration:
├── ROUTE_API_KEY in .env
├── ROUTE_API_AUTH in .env
└── USE_MOCK_DATA=False
```

### Testing Application

#### `app_hybrid_demo.py` (644 lines)
- **Port**: 8505
- **Purpose**: Real API with mock fallback
- **Status**: 🧪 Testing
- **Features**: Tries real API, falls back to mock if fails
- **Value**: Good for development/testing

### Assessment Questions for Version 2
- ✅ Keep `app_api_real.py` (production target)
- ✅ Keep `app_hybrid_demo.py` (useful for testing)

---

## 📦 Legacy Applications

### 1. `app.py` (673 lines)
- **Port**: 8501
- **Purpose**: Original main application
- **Status**: 📦 Legacy
- **Last Significant Update**: Unknown (appears older)
- **Deployment Reference**: `deployment/deploy-app.sh` points to this
- **Features**: Mix of mock and semi-real data

**Concerns**:
- Deployment scripts reference this file
- May still be "official" entry point
- Could be genuinely old and unused

**Assessment Questions**:
- ❓ Is this still used in production deployment?
- ❓ Can we safely archive this?
- ❓ Is deployment folder up to date?

### 2. `app_enhanced.py` (682 lines)
- **Port**: 8506
- **Purpose**: Enhanced UI features
- **Status**: 📦 Legacy
- **Features**: Additional UI enhancements, unclear if needed
- **Value**: Unclear - may be experimental

**Assessment Questions**:
- ❓ What enhancements does this have?
- ❓ Were these enhancements merged into other apps?
- ❓ Can we safely archive this?

---

## 🔗 Shared Components (Used by Multiple Versions)

### Core Infrastructure (CRITICAL - Don't Move)
```
src/
├── config.py (444 lines) - Configuration system
├── config_consolidated.py - Consolidated config access
├── __init__.py - Package marker
└── .env - Credentials (NEVER move)
```

### UI Components (Used by All Apps)
```
src/ui/components/ (18 components, 3,500+ lines)
├── business_3d.py (562 lines) - 3D visualizations
├── cost_upload.py (281 lines) - Cost data manager
├── visualizations.py (1,063 lines) - Charts and maps
├── metrics_cards.py (187 lines) - Metric displays
├── executive_summary.py (428 lines) - Summary reports
├── improved_maps.py (367 lines) - Enhanced maps
├── regional_viz.py (289 lines) - Regional charts
└── [11 more components...]
```

### UI Layouts (Used by Most Apps)
```
src/ui/layouts/ (7 modules, 1,200+ lines)
├── campaign_selector.py - Campaign picker
├── metrics_display.py - Metrics rendering
├── tab_manager.py - Tab interface
└── [4 more layouts...]
```

### Services (Shared Infrastructure)
```
src/services/ (8 services, 2,800+ lines)
├── base_service.py - Base service class
├── route_service.py (428 lines) - Route API service
├── space_service.py (198 lines) - SPACE API service
├── monitoring_service.py - Monitoring
└── [4 more services...]
```

### Database Layer
```
src/db/ (5 modules, 2,500+ lines)
├── ms01_helpers.py (758 lines) - MS-01 database helpers
├── route_releases.py (484 lines) - Route release management
├── optimized.py (503 lines) - Connection pooling
└── [2 more modules...]
```

### Utilities
```
src/utils/ (19 utilities, 4,000+ lines)
├── credentials.py (271 lines) - Credential management
├── mock_data_factory.py (221 lines) - Mock data
├── data_processor.py (397 lines) - Data processing
├── time_converter.py (224 lines) - Time conversions
├── performance.py (189 lines) - Performance monitoring
└── [14 more utilities...]
```

---

## 🚨 Critical Infrastructure Issues

### Issue 1: Config Loading (22 Files Affected)
**Pattern Found**:
```python
config_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')
spec = importlib.util.spec_from_file_location("config", config_file_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
```

**Files Affected** (22 total):
- `src/api/campaign_service_optimized.py:22`
- `src/api/frame_service.py:14`
- `src/api/base_client.py:16`
- `src/api/space_client.py:21`
- `src/api/route_release_service.py:15`
- `src/api/campaign_service.py:17`
- `src/api/route_client.py:29`
- `src/ui/app.py:26`
- `src/ui/app_enhanced.py:23`
- `src/ui/components/campaign_search.py:13`
- [12 more files...]

**Risk**: HIGH - Moving any file breaks config access
**Impact**: 22 files will fail to import config if structure changes
**Fix Required**: Replace with proper package imports

---

### Issue 2: sys.path Manipulation (45+ Files Affected)
**Pattern Found**:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Files Affected** (45+ total):
- All apps in `src/ui/` (7 files)
- All scripts in `scripts/` (30+ files)
- All tests in `tests/` (8+ files)
- Various utilities and services

**Risk**: HIGH - Fragile import system
**Impact**: Files won't import if moved or run from different directories
**Fix Required**: Install package properly with `pip install -e .`

---

### Issue 3: Hardcoded Data Paths (10+ Files Affected)
**Pattern Found**:
```python
csv_path = Path(__file__).parent.parent.parent / "data" / "sample_playout.csv"
```

**Files Affected**:
- `src/api/campaign_service.py:49` (3 levels up)
- `src/api/campaign_service_optimized.py:65` (3 levels up)
- `src/api/playout_processor.py:29-30` (3 levels up)
- `src/ui/app_api_real.py:128` (no anchor!)
- `src/ui/data/mock_geo_data.py:230-231` (4 levels up!)
- [5+ more files...]

**Risk**: HIGH - Moving files breaks data access
**Impact**: CSV files won't load if directory depth changes
**Fix Required**: Centralize paths in configuration

---

### Issue 4: Absolute User Paths (5 Files Affected)
**Pattern Found**:
```python
'/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/Claude/Documentation/diagram.png'
```

**Files Affected**:
- `Claude/Documentation/generate_updated_diagrams.py` (3 paths)
- `Claude/Documentation/generate_architecture_diagrams.py` (3 paths)
- `scripts/demo_route_release_helpers.py` (1 path in docs)

**Risk**: MEDIUM - Only affects diagram generation
**Impact**: Won't work on other machines or users
**Fix Required**: Use relative paths

---

### Issue 5: Deployment Scripts (3 Files Affected)
**Pattern Found**:
```bash
exec streamlit run src/ui/app.py
```

**Files Affected**:
- `deployment/deploy-app.sh:150`
- `deployment/supervisor.conf:5`
- `deployment/health-check.py:31,310`

**Risk**: HIGH - Production deployment
**Impact**: Service won't start if app.py moves
**Fix Required**: Update deployment configs if restructuring

---

## 📈 Project Size Metrics

### Code Volume
```
Total Files: 150+ Python files
Total Lines: ~35,000 lines of code

Breakdown:
├── Applications (7 files): 4,509 lines
├── Services (8 files): 2,800 lines
├── UI Components (18 files): 3,500 lines
├── Database Layer (5 files): 2,500 lines
├── Utilities (19 files): 4,000 lines
├── API Clients (10 files): 2,500 lines
├── Scripts (30+ files): 5,000+ lines
├── Tests (8+ files): 1,500+ lines
└── Configuration (10 files): 1,000 lines
```

### Documentation Volume
```
Total Docs: 50+ markdown files
Total Size: ~500 KB

Breakdown:
├── Claude/ (main docs): 300 KB, 30+ files
├── MS01_Migration_Plan/: 162 KB, 9 files
├── Route_API/: 50 KB, 5 files
├── SPACE_API_Docs/: 30 KB, 3 files
└── Scattered .md files: 50+ KB, 10+ files
```

### Scripts Volume
```
Total Scripts: 35+ files
Categories:
├── Database import scripts: 8 files
├── Testing scripts: 10 files
├── Demo/example scripts: 7 files
├── Analysis scripts: 5 files
└── Utility scripts: 5+ files
```

---

## 🗂️ Current Folder Structure

```
/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/
│
├── src/
│   ├── api/ (10 files, 2,500 lines)
│   ├── config/ (10 files, 1,000 lines)
│   ├── db/ (5 files, 2,500 lines)
│   ├── services/ (8 files, 2,800 lines)
│   ├── ui/
│   │   ├── components/ (18 files, 3,500 lines)
│   │   ├── layouts/ (7 files, 1,200 lines)
│   │   ├── data/ (3 files, 800 lines)
│   │   ├── styles/ (4 files, 600 lines)
│   │   ├── utils/ (3 files, 400 lines)
│   │   └── [7 app files] (4,509 lines) ← NEED TO ORGANIZE
│   ├── utils/ (19 files, 4,000 lines)
│   ├── config.py (444 lines)
│   └── __init__.py
│
├── Claude/
│   ├── Documentation/ (20+ files) ← SCATTERED
│   ├── Handover/ (10+ files) ← SOME CURRENT, SOME OLD
│   ├── ToDo/ (5+ files) ← MIXED RELEVANCE
│   ├── MS01_Migration_Plan/ (9 files) ← NEW, ORGANIZED
│   └── [10+ loose .md files] ← NEED TO ORGANIZE
│
├── scripts/ (35+ files) ← MANY RANDOM SCRIPTS
├── tests/ (8+ files)
├── examples/ (5+ files)
├── data/ (CSV files)
├── Playout/ (Playout data)
├── deployment/ (Docker, configs)
├── sample_data/ (Sample datasets)
└── [Various root-level files]
```

---

## 🎯 Files Needing Assessment

### Category A: UI Applications (Decision Required)

| File | Keep? | Archive? | Delete? | Reason |
|------|-------|----------|---------|--------|
| `app_mock_full.py` | ✅ YES | ❌ | ❌ | Main demo app |
| `app_api_real.py` | ✅ YES | ❌ | ❌ | Production target |
| `app_hybrid_demo.py` | ✅ YES | ❌ | ❌ | Useful for testing |
| `app_mock_simple.py` | ❓ | ❓ | ❓ | **ASSESS**: When used? |
| `app_mock_modular.py` | ❓ | ❓ | ❓ | **ASSESS**: Still needed? |
| `app.py` | ❓ | ❓ | ❌ | **ASSESS**: Used in deployment? |
| `app_enhanced.py` | ❓ | ❓ | ❓ | **ASSESS**: Enhancements merged? |

### Category B: Scripts (Decision Required)

**Testing/Demo Scripts** (10+ files):
- `scripts/test_*.py` (5+ files) - Are these still used?
- `scripts/demo_*.py` (5+ files) - Which demos are current?
- `scripts/analyze_*.py` (3+ files) - One-time analysis?

**Database Scripts** (8 files):
- `scripts/playout_postgres_importer.py` - Still used?
- `scripts/import_*.py` (3 files) - Active or archived?
- Various database maintenance scripts

**Utility Scripts** (10+ files):
- Random utility scripts scattered
- Some one-time use
- Some critical infrastructure

### Category C: Documentation (Decision Required)

**Claude/Documentation/** (20+ files):
- Which docs are current?
- Which are outdated?
- Some duplicates possible

**Claude/Handover/** (10+ files):
- Old session handovers
- Current session handovers
- Which are still relevant?

**Claude/ToDo/** (5+ files):
- Active todo lists
- Completed todo lists
- Which should be archived?

**Root-level .md files** (10+ files):
- README.md, CLAUDE.md (keep)
- Various random docs (assess)

---

## 📋 Recommended Assessment Process

### Step 1: Application Assessment (30 minutes)

For each questionable app, answer:
1. **When was this last used?** (check git logs)
2. **What unique features does it have?**
3. **Are those features in other apps now?**
4. **Would removing it break anything?**
5. **Keep, Archive, or Delete?**

### Step 2: Script Assessment (1 hour)

For each script, answer:
1. **Is this a one-time script or recurring use?**
2. **Does another script do the same thing?**
3. **Is it documented anywhere?**
4. **When was it last run?**
5. **Move to archive/ or keep active?**

### Step 3: Documentation Assessment (30 minutes)

For each doc, answer:
1. **Is this information current?**
2. **Is it superseded by newer docs?**
3. **Is it referenced by active docs?**
4. **Move to Archive/ or keep current?**

---

## 🗄️ Proposed Archive Structure

Create archive directories:
```
archive/
├── apps/
│   └── [old app versions]
├── scripts/
│   ├── one_time_analysis/
│   ├── old_tests/
│   └── superseded/
└── docs/
    ├── old_sessions/
    ├── old_todos/
    └── superseded/
```

---

## ⚡ Action Plan Phases

### Phase 0: Assessment (This Document)
- ✅ Analyze current structure
- ⏳ Decide what to keep/archive
- ⏳ Document decisions

### Phase 1: Archive Unnecessary Files
- Move old apps to archive/apps/
- Move one-time scripts to archive/scripts/
- Move outdated docs to archive/docs/
- **Goal**: Reduce clutter by 30-40%

### Phase 2: Fix Foundation Issues
- Create centralized paths.py
- Fix 22 config import statements
- Install package properly (eliminate sys.path hacks)
- Fix hardcoded data paths
- **Goal**: Make structure change-safe

### Phase 3: Reorganize Remaining Files
- Organize by version (v1/v2)
- Clear naming conventions
- Update imports
- **Goal**: Clean, maintainable structure

### Phase 4: Test Everything
- Test all active apps
- Verify all imports
- Check deployment
- **Goal**: Nothing breaks

---

## 🎯 Next Steps

**Immediate Actions Required**:

1. **Review this analysis** - Understand current state
2. **Complete APP_VERSION_ASSESSMENT.md** - Decide which apps to keep
3. **Create ARCHIVE_CANDIDATES.md** - List files for archival
4. **Get approval** - Don't move anything without decision
5. **Execute Phase 1** - Archive unnecessary files
6. **Execute Phase 2** - Fix foundation issues
7. **Execute Phase 3** - Reorganize structure

---

**Prepared By**: Claude Code Analysis Agents
**Date**: 2025-10-17
**Status**: Awaiting Assessment Decisions
**Next Document**: `APP_VERSION_ASSESSMENT.md`
