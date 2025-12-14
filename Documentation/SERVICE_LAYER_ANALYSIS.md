# Service Layer Architecture Analysis

**Date**: 6 December 2025
**Branch**: `refactor/config-consolidation`
**Status**: Analysis Complete

---

## Executive Summary

The codebase has **two parallel layers** (`src/api/` and `src/services/`) with significant dead code in the services layer. Only **4 of 10** services layer classes are actually used.

---

## Current Usage Map

### UI (app.py) Imports

| Source | Class | Status |
|--------|-------|--------|
| `src.api.route_client` | `RouteAPIClient` | ✅ ACTIVE |
| `src.api.playout_processor` | `PlayoutProcessor` | ✅ ACTIVE |
| `src.api.campaign_service` | `CampaignService` | ✅ ACTIVE |
| `src.services.reach_service` | `ReachService` | ✅ ACTIVE |

### Services Layer (src/services/)

| File | Class | Used By | Status |
|------|-------|---------|--------|
| `reach_service.py` | `ReachService` | app.py | ✅ ACTIVE |
| `cache_service.py` | `CacheService` | ReachService, SpaceServiceLayer | ✅ ACTIVE |
| `brand_split_service.py` | `BrandSplitService` | tests, examples | 🔶 DEVELOPED (not yet integrated) |
| `campaign_service.py` | `CampaignServiceLayer` | **Nothing** | ❌ DEAD CODE |
| `route_service.py` | `RouteServiceLayer` | **Nothing** | ❌ DEAD CODE |
| `space_service.py` | `SpaceServiceLayer` | **Nothing** | ❌ DEAD CODE |
| `playout_service.py` | `PlayoutServiceLayer` | **Nothing** | ❌ DEAD CODE |
| `monitoring_service.py` | `MonitoringService` | **Nothing** | ❌ DEAD CODE |
| `base.py` | `BaseService` | All *ServiceLayer classes | 🔶 Used by dead code only |

### API Layer (src/api/)

| File | Class | Used By | Status |
|------|-------|---------|--------|
| `route_client.py` | `RouteAPIClient` | app.py | ✅ ACTIVE |
| `campaign_service.py` | `CampaignService` | app.py | ✅ ACTIVE |
| `playout_processor.py` | `PlayoutProcessor` | app.py | ✅ ACTIVE |
| `space_client.py` | `SpaceAPIClient` | PlayoutProcessor, data_processor | ✅ ACTIVE (indirect) |
| `base_client.py` | `BaseAPIClient` | RouteAPIClient, SpaceAPIClient | ✅ ACTIVE |
| `frame_service.py` | `FrameMetadataService` | **Nothing** | ❌ DEAD CODE |
| `route_release_service.py` | `RouteReleaseService` | ? | Need to verify |
| `strategy.py` | Various strategies | ? | Need to verify |
| `api_fallback_handler.py` | `APIFallbackHandler` | ? | Need to verify |

---

## Architectural Pattern (Intended vs Actual)

### Intended Pattern
```
UI Layer (Streamlit)
       ↓
Services Layer (business logic, caching, orchestration)
       ↓
API Layer (external API calls, low-level clients)
       ↓
External APIs (Route, SPACE)
```

### Actual Pattern
```
UI Layer (Streamlit)
       ↓
┌──────────────────────────────────────┐
│  Mixed: API Layer + Some Services    │
│  - RouteAPIClient (api/)             │
│  - CampaignService (api/)            │
│  - PlayoutProcessor (api/)           │
│  - ReachService (services/)          │
└──────────────────────────────────────┘
       ↓
External APIs / PostgreSQL Cache
```

---

## Dead Code Summary

### Total Lines of Dead Code

| File | Lines | Status |
|------|-------|--------|
| `services/campaign_service.py` | 330 | Archive candidate |
| `services/route_service.py` | 390 | Archive candidate |
| `services/space_service.py` | 348 | Archive candidate |
| `services/playout_service.py` | 387 | Archive candidate |
| `services/monitoring_service.py` | 490 | Archive candidate |
| `api/frame_service.py` | 250 | Archive candidate |
| **Total** | **2,195** | |

### Note on BaseService

`services/base.py` (192 lines) provides the `BaseService` abstract class used by:
- Dead *ServiceLayer classes
- `BrandSplitService` (kept for future integration)
- `ReachService` (active)

**Recommendation**: Keep `base.py` as it's used by active services.

---

## Recommendations

### Phase 1: Archive Dead Services Layer Code

Archive these unused *ServiceLayer classes:
```
src/services/campaign_service.py → src/archive/services/
src/services/route_service.py    → src/archive/services/
src/services/space_service.py    → src/archive/services/
src/services/playout_service.py  → src/archive/services/
src/services/monitoring_service.py → src/archive/services/
```

### Phase 2: Archive Dead API Layer Code

Archive unused API services:
```
src/api/frame_service.py → src/archive/api/
```

### Phase 3: Update __init__.py Exports

Remove archived classes from:
- `src/services/__init__.py`
- `src/api/__init__.py`

### Phase 4: Document the Architecture

After cleanup, the layers become clear:

**API Layer** (`src/api/`): External API clients
- `RouteAPIClient` - Route API calls
- `SpaceAPIClient` - SPACE API calls
- `CampaignService` - Campaign orchestration with API enrichment
- `PlayoutProcessor` - Playout data processing with API enrichment

**Services Layer** (`src/services/`): Business logic & caching
- `ReachService` - Reach/GRP calculations
- `CacheService` - PostgreSQL cache management
- `BrandSplitService` - Brand attribution (future integration)
- `BaseService` - Abstract base class

---

## Files to Keep

### API Layer (src/api/) - KEEP
- `route_client.py` ✅
- `space_client.py` ✅
- `campaign_service.py` ✅
- `playout_processor.py` ✅
- `base_client.py` ✅
- `api_fallback_handler.py` ✅
- `route_release_service.py` (verify usage)
- `strategy.py` (verify usage)

### Services Layer (src/services/) - KEEP
- `reach_service.py` ✅
- `cache_service.py` ✅
- `brand_split_service.py` ✅ (future)
- `base.py` ✅

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking imports | Search for all imports before archiving |
| Future need for archived code | Keep in archive, not delete |
| BrandSplitService needs BaseService | Keep base.py |

---

## Approval Required

Doctor Biz, shall I proceed with archiving the dead code?

- **Yes, proceed** - Archive 6 files (~2,195 lines)
- **Partial** - Archive only services layer (5 files)
- **Hold** - More investigation needed
