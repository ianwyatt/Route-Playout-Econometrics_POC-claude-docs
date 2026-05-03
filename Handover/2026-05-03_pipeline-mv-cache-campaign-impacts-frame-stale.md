# Pipeline handover — `mv_cache_campaign_impacts_frame` is stale

**From:** POC team
**To:** Pipeline team
**Date:** 2026-05-03
**Severity:** Functional bug visible to demo-flow stakeholders; not a data-substrate corruption.
**Type:** Materialised view appears not to have been included in the Phase 4 / 2026-05-01 substrate rebuild.

---

## Summary

`mv_cache_campaign_impacts_frame` truncates impacts at ~2025-10-13, while:

- `cache_route_impacts_15min_by_demo` (canonical) goes to 2025-12-31.
- `mv_campaign_browser.total_impacts_all_adults` (built from canonical) is full-year.

For per-frame consumers in the POC, this means the MV's per-frame totals undercount the canonical sum by ~30% on heavy campaigns. The discrepancy is consistent across campaigns and has the same shape as the MI cache freeze date — possibly the same snapshot was used for both at some point.

The POC has worked around the JOIN-duplication bug downstream of this MV (the route_frames join is now release-deduplicated, see `src/db/queries/geographic.py`). With the JOIN fix in place, the only remaining gap between the Geographic tab's totals and Overview's is this stale MV.

## Evidence

DuckDB snapshot used: `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb` (87 GB), pulled via rsync from `playout-db:/var/lib/route/snapshots/route_poc_cache.latest.duckdb`.

### Per-campaign sums for `all_adults` demographic

| campaign | mv_cache_campaign_impacts_frame sum | canonical sum | mv_campaign_browser.total_impacts_all_adults | undercount |
|---|---:|---:|---:|---:|
| 17498 | 234,388.77 | 343,218.76 | 343,218.76 | 31.7% |
| 18409 | 194,835.47 | 301,379.67 | 301,379.67 | 35.4% |

(All values in thousands of impacts.)

### Per-frame, per-day comparison (campaign 17498, frame 1234934039)

| Source | first slot | last slot | total slots | sum impacts |
|---|---|---|---:|---:|
| `cache_route_impacts_15min_by_demo` | 2025-09-08 04:00 | 2025-10-19 22:45 | 3,192 | 13,054.23 |
| `mv_cache_campaign_impacts_frame` | 2025-09-08 04:00 | **2025-10-13 12:45** | 2,557 | 9,006.31 |

Per-frame: same first slot, but the MV truncates the last slot ~6 days early. Confirmed across the top 5 impact frames of the campaign — same first-slot, same truncated last-slot pattern.

### Frame coverage

For 17498 / `all_adults`:
- Canonical distinct frames: **659**
- `mv_cache_campaign_impacts_frame` distinct frames: **636**
- 23 small-impact frames missing from the MV; total missing impact sum is ~1,080 thousand (i.e. negligible, ~0.3%).

The 23 missing frames are likely those that first appeared in canonical after the MV's freeze date.

## Hypothesis

`mv_cache_campaign_impacts_frame` was apparently rebuilt against an older canonical snapshot that ended ~mid-October 2025. The Phase 4 substrate rebuild (2026-05-01) refreshed `cache_route_impacts_15min_by_demo`, `mv_campaign_browser`, `mv_campaign_browser_summary`, and the dim tables, but `mv_cache_campaign_impacts_frame` wasn't picked up — possibly because it wasn't in the explicit rebuild list at `Claude/docs/pipeline-coordination.md` line 116 onwards (`mv_campaign_browser` rebuild round).

This is a guess — pipeline team has authoritative knowledge of which MVs were touched.

## Ask

A refresh of `mv_cache_campaign_impacts_frame` against the current canonical impacts table, so that:

- Per-frame `total_impacts` = `SUM(impacts)` from canonical for that (campaign_id, frameid, demographic_segment) over the campaign's full date range.
- `time_window_count` = canonical row count for the same scope.
- `first_playout` / `last_playout` = canonical min/max `time_window_start` for the same scope.
- Frame coverage matches canonical distinct frameids per campaign+demographic.

If the MV is intentionally frozen for some reason (e.g., reach-only campaigns, MI window alignment), please confirm and document the expected scope so the POC can either consume it as-is or fall back to a direct canonical aggregation.

## Smoke test the POC team can run after refresh

```sql
-- Should return zero rows
WITH per_frame_canonical AS (
    SELECT campaign_id, frameid, demographic_segment, SUM(impacts) AS canon_sum
    FROM cache_route_impacts_15min_by_demo
    WHERE campaign_id = '17498' AND demographic_segment = 'all_adults'
    GROUP BY campaign_id, frameid, demographic_segment
)
SELECT
    c.frameid,
    c.canon_sum,
    m.total_impacts AS mv_sum,
    c.canon_sum - m.total_impacts AS diff
FROM per_frame_canonical c
LEFT JOIN mv_cache_campaign_impacts_frame m USING (campaign_id, frameid, demographic_segment)
WHERE m.frameid IS NULL OR ABS(c.canon_sum - m.total_impacts) > 0.001
ORDER BY ABS(c.canon_sum - COALESCE(m.total_impacts, 0)) DESC
LIMIT 20;
```

After a clean refresh this should return zero rows; the same query against the current MV produces ~659 rows.

## POC-side context

- The Streamlit Geographic tab consumes this MV via `get_frame_geographic_data_sync` in `src/db/queries/geographic.py`.
- Branch `fix/geographic-data-scope-mismatch` (POC) addresses the route_frames JOIN duplication (separate bug) and adds "(000s)" labels to align Geographic's display unit with the rest of the app.
- Forensics doc capturing all three layered bugs (this Bug 3 + JOIN dup + display unit): `Claude/Plans/2026-05-03_geographic-overview-data-scope-forensics.md`.

No POC-side action item depends on this handover — the POC fix lands without it. This handover is so the next pipeline rebuild closes the residual ~30% per-frame undercount.
