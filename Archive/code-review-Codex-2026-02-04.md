# Code Review – Reusability, Modularity, Code Quality

Date: 2026-02-04

## Overall Assessment Score
**6.5 / 10**

**Rationale:** The codebase shows solid modular intent (services, UI components, query facades), but several cross‑module contracts are inconsistent or broken (reach API call signature/shape, TTLCache API usage). These issues reduce reliability and reusability because modules can’t be safely composed. Fixing the top contract breaks should lift the score notably.

## Findings (from review)

### 1) Cache stats check never true (P3)
**File:** `src/ui/app.py:313`

- `result` is a dict, so `hasattr(result, 'cache_stats')` is always false.
- Impact: Cache stats UI never renders; reduces observability.
- Fix: Use `'cache_stats' in result` or `result.get('cache_stats')`.

### 2) ReachService call signature mismatch (P1)
**File:** `src/ui/app.py:165`

- `get_campaign_reach_daterange` doesn’t accept `daily_breakdown` or `force_refresh`.
- Impact: Multi‑day reach calculation raises `TypeError` and blocks functionality.
- Fix: Align signature or adjust call to `return_daily` and add `force_refresh` to the service API.

### 3) Daterange response shape doesn’t match UI (P1)
**File:** `src/services/reach_service.py:500`

- Service returns `{'total': ..., 'daily': ...}` while UI expects top‑level `reach/grp/total_impacts` and `daily_breakdown`.
- Impact: UI renders zeros and no breakdown even if the call succeeds.
- Fix: Flatten totals and rename/duplicate daily list to `daily_breakdown`, or update UI consumers.

### 4) TTLCache API mismatch (P1)
**File:** `src/api/route_release_service.py:112`

- `TTLCache` implements `put`, `stats`, `remove` but code calls `set/get_stats/delete`.
- Impact: Release caching fails with `AttributeError`, so cache is unusable.
- Fix: Replace with the correct methods and add a small test that exercises lookup + refresh + stats.

### 5) Manual input ignores selected DB (P2)
**File:** `src/ui/components/campaign_browser/manual_input.py:32`

- Manual lookup doesn’t pass `use_ms01`, relying on env default instead of session selection.
- Impact: Inconsistent results vs browse tab; reduces modular consistency.
- Fix: Pass `st.session_state.use_ms01_database` into `get_campaign_from_browser_by_id_sync`.

### 6) Sync HTTP call in async path (P2)
**File:** `src/api/route_client.py:245`

- `validate_frames` uses `requests` (blocking) inside an async method.
- Impact: Blocks event loop; hurts concurrency and modular reuse in async contexts.
- Fix: Make validation async or run in a thread executor.

## Suggested Next Steps
1) Fix the reach service contract (signature + response shape) and add a regression test.
2) Correct TTLCache usage in `RouteReleaseService` and add coverage for cache stats + refresh.
3) Align manual campaign lookup with the selected DB toggle.
4) Remove blocking calls from async paths (either async HTTP or offload to threads).

---
If you want, I can prepare a patch implementing the top 3 fixes and add targeted tests.
