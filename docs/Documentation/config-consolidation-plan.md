# Config Consolidation Plan

**Branch**: `refactor/config-consolidation`
**Date**: 6 December 2025
**Status**: ✅ COMPLETED

---

## Current State Analysis

### Three Config Systems Exist

| File | Lines | Imports | Status |
|------|-------|---------|--------|
| `src/config.py` | 481 | **15 files** (13 active + 2 archived) | PRIMARY - actively used |
| `src/config_consolidated.py` | 246 | **0 files** | DEAD CODE - never adopted |
| `src/config_package/` | 1,372 | **2 files** (only DatabaseConfig) | PARTIAL USE |

### What Each Contains

**`config.py`** (the primary):
- RouteAPIConfig, SpaceAPIConfig
- CampaignProcessingConfig, FrameConfig, EntityConfig
- DemoConfig, SpotConfig, CacheConfig
- RoutePlayoutConfig (main container)
- Helper functions: `get_config()`, `use_demo_config()`, `use_production_config()`
- **GAP: No database configuration!**

**`config_consolidated.py`** (unused):
- Attempted simplification of config.py
- Never integrated - zero imports
- **Safe to archive**

**`config_package/`** (partially used):
- Only `DatabaseConfig` is imported (by `brand_split_service.py` and `route_releases.py`)
- Contains sophisticated MS-01/local database switching logic
- Other modules (APIConfig, UIConfig, LoggingConfig, ProcessingConfig) **duplicate** what's in config.py
- **Keep DatabaseConfig, archive the rest**

---

## The Root Problem

The main `config.py` is missing database configuration. Two files that need DB config had to import from the separate `config_package/` instead, creating architectural inconsistency.

---

## Proposed Solution: Consolidate to Single config.py

### Phase 1: Archive Dead Code
1. Move `config_consolidated.py` → `src/archive/config_consolidated.py`

### Phase 2: Migrate DatabaseConfig to config.py
1. Copy `DatabaseConfig` and `PostgreSQLConfig` from `config_package/database.py` to `config.py`
2. Add `database: DatabaseConfig` to `RoutePlayoutConfig` main container
3. Add `get_database_config()` helper function

### Phase 3: Update Imports
1. Update `src/services/brand_split_service.py`:
   - Change: `from src.config_package.database import DatabaseConfig`
   - To: `from src.config import get_database_config` (or `get_config().database`)

2. Update `src/db/route_releases.py`:
   - Same change as above

### Phase 4: Archive config_package
1. Move entire `config_package/` → `src/archive/config_package/`
   - Preserves history if ever needed
   - Removes confusion about which config to use

---

## Files Changed

| Action | File | Change |
|--------|------|--------|
| Archive | `src/config_consolidated.py` | Move to archive |
| Edit | `src/config.py` | Add DatabaseConfig (~80 lines) |
| Edit | `src/services/brand_split_service.py` | Update import |
| Edit | `src/db/route_releases.py` | Update import |
| Archive | `src/config_package/` | Move entire directory to archive |

---

## Result

**Before**: 3 config systems, unclear which to use, 2,099 total lines
**After**: 1 config file (~560 lines), clear single source of truth

### Benefits
1. **Single source of truth** - all config in one place
2. **Clear imports** - always `from src.config import ...`
3. **No duplication** - removes redundant config definitions
4. **Discoverable** - new developers find everything in config.py
5. **Testable** - one config to validate

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking database connections | Copy DatabaseConfig exactly, test MS-01 + local connections |
| Missing environment variables | DatabaseConfig already handles env vars correctly |
| Import errors | Only 2 files to update, easy to verify |

---

## Verification Steps

1. After Phase 2: `python -c "from src.config import get_config; print(get_config().database.postgres.host)"`
2. After Phase 3: Run app, verify database connection works
3. After Phase 4: `grep -r "config_package" src/` should return nothing

---

## Approval Required

---

## Completion Summary

**Executed**: 6 December 2025

### Changes Made
1. ✅ Archived `src/config_consolidated.py` → `src/archive/`
2. ✅ Added `PostgreSQLConfig` and `DatabaseConfig` dataclasses to `src/config.py`
3. ✅ Added `get_database_config()` lazy-loader function
4. ✅ Updated `src/services/brand_split_service.py` import
5. ✅ Updated `src/db/route_releases.py` import
6. ✅ Updated `tests/services/test_brand_split.py` import
7. ✅ Archived entire `src/config_package/` → `src/archive/`

### Verification
- MS-01 database mode: Tested with `POSTGRES_HOST_MS01=192.168.1.34` ✅
- Local database mode: Tested with `USE_MS01_DATABASE=false` ✅
- No `config_package` references in `src/` directory ✅

### Notes
- DatabaseConfig uses lazy initialization via `get_database_config()` rather than being included in `RoutePlayoutConfig` directly, because it requires environment variables at instantiation time
- This matches the original usage pattern where files instantiated `DatabaseConfig()` directly when needed
