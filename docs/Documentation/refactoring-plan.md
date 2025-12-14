# Refactoring Plan: Modularity & Cleanup

**Branch**: `refactor/modularity-cleanup`
**Date**: 6 December 2025
**Status**: AWAITING APPROVAL

---

## Executive Summary

This plan addresses modularity issues, duplicate code, and redundant files identified during codebase exploration. The work is organised into **5 phases**, ordered by risk level (lowest risk first).

**Key Principles**:
- Make smallest possible changes
- Test after each phase
- No changes to working logic
- Preserve all functionality

---

## Phase 1: Safe Deletions & Rename (LOWEST RISK)

Files that are **confirmed unused** and can be safely removed, plus renaming the main entry point.

### 1.0 Rename Main Entry Point

**Current**: `src/ui/app_api_real.py` (terrible name - temporal, unclear)
**Proposed**: `src/ui/app.py` (Streamlit convention, path provides context)

**Files to update** (documentation only - no code imports this file):
- `CLAUDE.md` (5 references)
- `docs/ARCHITECTURE.md`
- `docs/UI_GUIDE.md`
- `docs/CACHE_TROUBLESHOOTING.md`
- `docs/GIT_QUICK_REFERENCE.md`
- `docs/CACHE_INTEGRATION.md`

**User action required**: Update `~/.zshrc` `startstream` function after this change.

### 1.1 Unused Files to Archive

| File | Lines | Reason | Action |
|------|-------|--------|--------|
| `src/api/campaign_service_optimized.py` | 545 | Only imported by archived `app_demo.py` | Move to `src/api/archive/` |
| `src/utils/mock_data_generator.py` | 317 | Only imported by above | Move to `src/utils/archive/` |
| `src/utils/mock_data_factory.py` | 308 | Only imported by above | Move to `src/utils/archive/` |
| `src/utils/data_processing.py` | 636 | `DataProcessor` class never imported anywhere | Move to `src/utils/archive/` |
| `src/services/service_integration_example.py` | 279 | Example file, not production code | Move to `examples/` or delete |
| `src/services/brand_split_integration_example.py` | 465 | Example file, not production code | Move to `examples/` or delete |
| `src/services/test_brand_split.py` | 413 | Test file in wrong location | Move to `tests/services/` |

**Total lines removable from src/**: ~2,963 lines

### 1.2 Verification Steps
1. Run `grep -r "campaign_service_optimized" src/` - confirm only archived imports
2. Run `grep -r "mock_data_generator\|mock_data_factory" src/` - confirm only above imports
3. Run `grep -r "DataProcessor" src/` - confirm only self-references
4. Run the app and all tests to confirm nothing breaks

---

## Phase 2: Extract Duplicate Code (LOW RISK)

### 2.1 Extract `_export_dialog()` to Shared Utility

**Current State**: Identical function in two files:
- `src/ui/tabs/overview.py` (lines 14-45)
- `src/ui/tabs/executive_summary.py` (lines 19-50)

**Action**: Create shared function in `src/ui/utils/export_dialog.py`

```python
# src/ui/utils/export_dialog.py
# ABOUTME: Shared export dialog component for campaign data export
# ABOUTME: Provides reusable modal with progress bar and session state management

import streamlit as st
import time
from src.ui.utils.export import create_excel_export


@st.dialog("Exporting Campaign Data", width="large")
def export_dialog(campaign_id: str, campaign_result: dict):
    """Modal dialog for Excel export progress.

    Auto-closes after export completes, download button appears on main page.
    """
    progress_bar = st.progress(0, "Initializing export...")

    def update_progress(message: str, progress_pct: int):
        progress_bar.progress(progress_pct, f"⏳ {message}")

    try:
        excel_data = create_excel_export(
            campaign_id,
            campaign_result,
            progress_callback=update_progress
        )
        st.session_state.export_ready = True
        st.session_state.export_data = excel_data
        st.session_state.export_filename = f"campaign_{campaign_id}_data.xlsx"
        st.session_state.export_campaign_id = campaign_id
        progress_bar.progress(100, "✅ Export complete!")
        time.sleep(0.8)
        st.rerun()

    except Exception as e:
        progress_bar.empty()
        st.error(f"Export failed: {e}")
        if st.button("Close"):
            st.rerun()
```

**Then update both tabs**:
```python
from src.ui.utils.export_dialog import export_dialog

# Replace _export_dialog() calls with export_dialog()
```

### 2.2 Verification Steps
1. Test export from Overview tab
2. Test export from Executive Summary tab
3. Confirm export file downloads correctly

---

## Phase 3: Complete Styles Migration (MEDIUM RISK)

### 3.1 Current State

Two styling systems exist in parallel:
- **Old**: `src/ui/styles.py` (729 lines) - used by 3 components
- **New**: `src/ui/styles/` directory - used by main app and campaign_browser

**Files using OLD styles.py**:
- `src/ui/components/campaign_search.py` → imports `RouteColors, create_status_message`
- `src/ui/components/data_filters.py` → imports `RouteColors`
- `src/ui/components/results_table.py` → imports `RouteColors, format_number`

### 3.2 Migration Plan

1. **Check what's in the new `styles/` directory** that can replace old imports
2. **Move `RouteColors`** to `src/ui/styles/themes.py` (if not already there)
3. **Move `create_status_message`** to `src/ui/styles/components.py`
4. **Move `format_number`** to `src/ui/utils/formatters.py` (it's not really styling)
5. **Update imports** in the 3 affected components
6. **Archive** `src/ui/styles.py` → `src/ui/archive/styles_legacy.py`

### 3.3 Verification Steps
1. Test campaign search functionality
2. Test data filtering
3. Test results table display
4. Visual inspection for styling consistency

---

## Phase 4: Clean Up Temporal Comments (LOW RISK)

### 4.1 Identified Temporal Comments

| File | Line | Current Comment | Proposed Change |
|------|------|-----------------|-----------------|
| `src/config.py` | 217 | `# Demo Campaign IDs - Added 16015 for real API demo` | `# Demo Campaign IDs` |
| `src/ui/components/campaign_browser.py` | 113 | `# Primary button styling is now global` | `# Primary button styling in global CSS` |

### 4.2 Action
Update comments to be evergreen (remove temporal references like "now", "added", etc.)

---

## Phase 5: Future Considerations (DEFERRED)

**See**: `Claude/Documentation/refactoring-followup.md` for detailed follow-up items.

Summary of deferred work:
- Large file splits (streamlit_queries.py, campaign_browser.py, export.py)
- Service layer architecture review (api/ vs services/ duplication)
- Config consolidation (3 systems exist)

---

## Execution Order

```
Phase 1: Safe Deletions & Rename
    ├── 1.0 Rename app_api_real.py → app.py
    ├── 1.0b Update all documentation references
    ├── 1.1 Archive unused files
    ├── 1.2 Run tests
    └── CHECKPOINT: Verify app works (user updates ~/.zshrc)

Phase 2: Extract Duplicate Code
    ├── 2.1 Create export_dialog.py
    ├── 2.2 Update tabs to use shared function
    └── CHECKPOINT: Test export functionality

Phase 3: Complete Styles Migration
    ├── 3.1 Analyse styles/ directory contents
    ├── 3.2 Migrate RouteColors, helpers
    ├── 3.3 Update component imports
    ├── 3.4 Archive old styles.py
    └── CHECKPOINT: Visual inspection + tests

Phase 4: Clean Up Comments
    ├── 4.1 Update temporal comments
    └── CHECKPOINT: Code review
```

---

## Risk Mitigation

1. **Git branch**: All work on `refactor/modularity-cleanup`
2. **Incremental commits**: One commit per sub-phase
3. **Testing after each phase**: Run app + automated tests
4. **No logic changes**: Only moving/renaming code
5. **Easy rollback**: Each phase is independently revertible

---

## Estimated Effort

| Phase | Complexity | Files Affected |
|-------|------------|----------------|
| Phase 1 | Low | 1 rename + 6 docs + 7 files archived |
| Phase 2 | Low | 3 files (1 new, 2 updated) |
| Phase 3 | Medium | 5 files |
| Phase 4 | Low | 2 files |

---

## Approval Required

Doctor Biz, please review this plan and let me know:

1. **Approve all phases?** → I'll proceed sequentially
2. **Approve specific phases?** → Tell me which ones
3. **Questions/concerns?** → I'll clarify before proceeding
4. **Modifications needed?** → I'll update the plan

**NOTE**: I will NOT make any code changes until you explicitly approve.
