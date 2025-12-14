# Code Review Archive Plan

**Created**: 10 December 2025
**Source**: Codex (ChatGPT) code review
**Status**: Logged for post-demo action - NO CODE CHANGES BEFORE DEMO

---

## Summary

Codex identified bugs in code paths that are **currently unused** in the production UI. The code exists from an earlier live-API architecture that was superseded by the cache-first approach. These files may be useful when we return to live API calls in the future.

---

## Findings from Codex Review

### 1. `calculate_reach_async` Signature Mismatch

**Location**: `src/ui/app.py:165-172`

**Issue**:
- Calls `reach_service.get_campaign_reach_daterange()` with `daily_breakdown=True` and `force_refresh=...`
- But `ReachService.get_campaign_reach_daterange()` only accepts `return_daily` (not `daily_breakdown`) and has no `force_refresh` parameter
- Would raise `TypeError` if called

**Current Status**: Dead code - never triggered from UI

**Fix Required**: Align parameter names when re-enabling live API calls

---

### 2. Response Shape Mismatch

**Location**: `src/ui/app.py:260-327`

**Issue**:
- Service returns `{'total': <dict>, 'daily': [...]}`
- UI expects `result['reach']`, `result['grp']`, `result['daily_breakdown']`
- Would render zero metrics and no table

**Current Status**: Same dead code path as #1

**Fix Required**: Either flatten service response or update UI to unwrap

---

### 3. TTLCache API Mismatch in RouteReleaseService

**Location**: `src/api/route_release_service.py:112, 157, 271, 291`

**Issue**:
- Calls `self.cache.set()`, `self.cache.get_stats()`, `self.cache.delete()`
- But `TTLCache` implements `put()`, `stats()`, `remove()`
- Would raise `AttributeError` on first use

**Current Status**: `RouteReleaseService` not used anywhere in UI

**Fix Required**: Update method names to match TTLCache API

---

## Files to Archive (Post-Demo)

These files contain potentially useful code for future live API work but are currently unused:

| File | Last Modified | Status | Notes |
|------|---------------|--------|-------|
| `src/services/reach_service.py` | 9 Dec 2025 | Unused by UI | Live API reach calculations |
| `src/api/route_release_service.py` | 17 Oct 2025 | Unused by UI | Release lookup with caching |
| `src/ui/app.py` lines 142-327 | - | Dead code | `calculate_reach_async` and related |

---

## Why Keep (Archive) Rather Than Delete

1. **Future live API work** - We may need to call Route API directly again for:
   - Real-time reach calculations
   - On-demand data for campaigns not in cache
   - New demographic segments not pre-cached

2. **Reference implementation** - Shows intended API contract and response handling

3. **Testing infrastructure** - May be useful for integration tests against live APIs

---

## Recommended Archive Location

```
src/archive/live_api_services/
├── reach_service.py          # From src/services/
├── route_release_service.py  # From src/api/
└── README.md                 # Explains why archived, how to restore
```

---

## Action Plan (Post-Demo)

1. [ ] Create `src/archive/live_api_services/` directory
2. [ ] Move `reach_service.py` to archive (update imports in app.py to remove)
3. [ ] Move `route_release_service.py` to archive
4. [ ] Remove dead code from `app.py` (lines 142-327) or move to archive
5. [ ] Update `src/services/__init__.py` to remove reach_service export
6. [ ] Create README in archive explaining restoration process
7. [ ] Run tests to confirm no regressions

---

## Current Production Architecture (What Actually Works)

```
User → Campaign Browser → PostgreSQL MVs → Display
                              ↑
                         Pipeline populates
                         (separate repo)
```

**No live API calls in production UI** - all data comes from pre-cached materialised views.

---

*This document logs findings only. No code changes to be made before demo on 11 December 2025.*
