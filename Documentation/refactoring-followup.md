# Refactoring Follow-up: Deferred Items

**Created**: 6 December 2025
**Status**: TO BE SCHEDULED (after initial refactor complete)
**Prerequisite**: Complete `refactoring-plan.md` phases 1-4 first

---

## Overview

These items were identified during the modularity exploration but deferred to minimise risk during the initial cleanup. Each requires more planning and discussion before implementation.

---

## 1. Large File Splits

### 1.1 `src/db/streamlit_queries.py` (1,135 lines)

**Problem**: Single "god file" containing all database queries, mixing concerns.

**Proposed Split**:
```
src/db/
├── queries/
│   ├── __init__.py          # Re-exports for backwards compatibility
│   ├── campaign.py          # Campaign queries (get_all_campaigns_sync, get_campaign_summary_sync)
│   ├── impacts.py           # Impact queries (get_daily_impacts_sync, get_hourly_impacts_sync)
│   ├── demographics.py      # Demographic queries (get_demographic_count_sync)
│   ├── reach.py             # Reach/GRP queries (get_full_campaign_reach_sync, get_weekly_reach_data_sync)
│   ├── geographic.py        # Geographic queries (get_regional_impacts_sync)
│   └── browser.py           # Campaign browser queries (get_campaigns_from_browser_sync)
└── streamlit_queries.py     # Keep as facade, re-exporting from queries/
```

**Risk**: Medium - many files import from this module
**Effort**: Medium - need to trace all imports and update

---

### 1.2 `src/ui/components/campaign_browser.py` (1,011 lines)

**Problem**: Largest component, mixing table rendering, search, selection, and styling.

**Proposed Split**:
```
src/ui/components/
├── campaign_browser/
│   ├── __init__.py           # Main render_campaign_browser() function
│   ├── table.py              # Table rendering logic
│   ├── filters.py            # Filter controls
│   ├── selection.py          # Row selection handling
│   └── styles.py             # Component-specific CSS
└── campaign_browser.py       # Keep as facade for backwards compatibility
```

**Risk**: Medium - need to understand component boundaries
**Effort**: Medium-High - requires understanding UI flow

---

### 1.3 `src/ui/utils/export.py` (926 lines)

**Problem**: Complex export logic for multiple formats in one file.

**Proposed Split**:
```
src/ui/utils/
├── export/
│   ├── __init__.py           # Main create_excel_export() facade
│   ├── excel.py              # Excel-specific formatting
│   ├── csv.py                # CSV export
│   ├── parquet.py            # Parquet export
│   └── common.py             # Shared data preparation
└── export.py                 # Keep as facade
```

**Risk**: Low-Medium - exports are self-contained
**Effort**: Medium - need to identify shared vs format-specific logic

---

## 2. Service Layer Architecture Review

### 2.1 Current State

Two parallel hierarchies exist:

| API Layer (`src/api/`) | Services Layer (`src/services/`) |
|------------------------|----------------------------------|
| `RouteAPIClient` | `RouteServiceLayer` |
| `SpaceAPIClient` | `SpaceServiceLayer` |
| `CampaignService` | `CampaignServiceLayer` |
| `PlayoutProcessor` | `PlayoutService` |

### 2.2 Questions to Resolve

1. **What's the intended separation?**
   - Is `api/` for raw API calls and `services/` for business logic?
   - Or is there overlap/duplication?

2. **Which layer should UI components call?**
   - Currently `app.py` imports from both layers
   - Should there be a single entry point?

3. **What about `*ServiceLayer` vs `*Service` naming?**
   - Inconsistent naming between layers

### 2.3 Proposed Investigation

1. Trace all imports from `app.py` to understand actual usage
2. Document data flow: UI → Service → API → External
3. Identify truly duplicate code vs intentional layering
4. Propose consolidation or clarify boundaries

**Risk**: High - touching core architecture
**Effort**: High - requires deep understanding

---

## 3. Config Consolidation ✅ COMPLETED

**Completed**: 6 December 2025
**Branch**: `refactor/config-consolidation`
**Documentation**: See `config-consolidation-plan.md` for full details

### Summary

Consolidated three config systems into one:
- `src/config.py` is now the **single source of truth**
- Added `DatabaseConfig` and `PostgreSQLConfig` dataclasses
- Added `get_database_config()` lazy-loader function
- Archived `config_consolidated.py` and `config_package/` to `src/archive/`

### Key Design Decision

`DatabaseConfig` uses lazy initialisation via `get_database_config()` rather than being included in the global `RoutePlayoutConfig` because it requires environment variables at instantiation time.

---

## 4. Additional Cleanup Candidates

### 4.1 Unused/Minimal Files to Review

| File | Lines | Status |
|------|-------|--------|
| `src/ui/layouts/` | ~3 files | Unclear if used |
| `src/ui/data/mock_geo_data.py` | 369 | Mock data - is it needed? |
| `src/services/base.py` | 192 | Abstract base - check usage |

### 4.2 Potential Dead Code in Used Files

- `src/services/playout_service.py:308` - "For now, return mock data" (should this exist?)
- `src/api/frame_service.py:76` - "For now, we'll generate realistic mock data"
- `src/services/space_service.py:301` - "For now, return empty list"

These comments suggest incomplete implementations that may need attention.

---

## Execution Priority

Suggested order for remaining items:

1. ~~**Config Consolidation**~~ ✅ COMPLETED (6 Dec 2025)
2. **Service Layer Review** - Clarify architecture before splitting files
3. **Large File Splits** - Once architecture is clear, these become easier

---

## Notes

- Each item requires a separate planning session
- Don't attempt multiple items in parallel
- Each should have its own branch and PR
- User testing required after each change
