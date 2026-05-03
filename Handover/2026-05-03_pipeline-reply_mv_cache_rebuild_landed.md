# Pipeline reply — `mv_cache_campaign_impacts_frame` rebuild landed

**From:** Pipeline team
**To:** POC team
**Date:** 2026-05-03 (~15:13 UTC)
**Re:** `2026-05-03_pipeline-mv-cache-campaign-impacts-frame-stale.md`

---

## TL;DR

Rebuilt all six `mv_cache_campaign_impacts_*` MVs against current canonical (`cache_route_impacts_15min_by_demo`, ~2.31B rows). Your smoke-test SQL — verbatim from your handover — now returns **0 mismatches** for campaign 17498 / `all_adults`.

`route_poc_cache.latest.duckdb` is **updated** to point at the post-rebuild snapshot. Your next `rsync` will pick it up (delta-only, should be small — only the 6 MVs changed within the 92GB DB).

## What was done

1. New runner `scripts/tools/duckdb_mv_cache_rebuild.py` rebuilt the family on `playout-db`:

   ```
   mv_cache_campaign_impacts_15min:    25,095,581 rows  (79.4s)
   mv_cache_campaign_impacts_1hr:       6,304,179 rows  (11.5s)
   mv_cache_campaign_impacts_day:         358,246 rows  (6.0s)
   mv_cache_campaign_impacts_daypart:   1,360,590 rows  (8.6s)
   mv_cache_campaign_impacts_frame:     4,000,290 rows  (9.7s)
   mv_cache_campaign_impacts_week:         67,767 rows  (8.0s)
   ```
   Total: 6 MVs in 123 s.

2. Verified your exact handover SQL (campaign 17498, `all_adults`, full-outer `(campaign, frameid, demo)` parity) returns **0 mismatches**.

3. Snapshotted post-rebuild state and atomically updated the symlink:
   - `/var/lib/route/snapshots/route_poc_cache.post-mv-cache-rebuild.20260503T151304Z.duckdb`
   - `/var/lib/route/snapshots/route_poc_cache.latest.duckdb` → ↑ (md5 `7df6f527fb45efa3f359af91f8dfc3d0`)

## What you should do

`rsync` per `docs/POC_RSYNC_OPS.md` (no change to your procedure):

```bash
rsync -avP --partial --inplace \
    routeapp@playout-db:/var/lib/route/snapshots/route_poc_cache.latest.duckdb \
    /your/local/path/route_poc_cache.duckdb
```

Then re-run your `geographic.py` consumers — the per-frame undercount your handover documented should be gone.

## Recurrence prevention

`mv_cache_campaign_impacts_*` is now wired into the standard rebuild path. Going forward, after any operation that changes `cache_route_impacts_15min_by_demo` (cacher run, retry pass, manual cleanup), `duckdb_mv_cache_rebuild.py --views all` runs as a post-step (documented in `docs/CACHER_GUIDE.md`). The runner also fires the F4 post-write hook automatically (B2 snapshot + future fanout to `playout-frontend` once Phase 5a lands).

## Side-notes

- The 7 `mv_cache_campaign_impacts_*` rows in `docs/POC_INTEGRATION.md` were updated to "refreshed by `duckdb_mv_cache_rebuild.py`". Three rows that weren't in the original table (`_15min`, `_daypart`, `_week`) are noted in the explanatory paragraph below the table.
- Two follow-ups are tracked on our side: (a) `playout-frontend` host is offline on Tailscale (4d ago) — Phase 5a fanout target; (b) `B2_REGION` should move into the BWS shim so the script default isn't load-bearing.
- Pre-rebuild snapshot kept at `route_poc_cache.pre-mv-cache-rebuild.20260503T141026Z.duckdb` — rollback point if anything looks wrong on your end.

Spec + plan + design doc for the rebuild module:

- `Claude/Plans/2026-05-03_mv_cache_rebuild_module_design.md`
- `Claude/Plans/2026-05-03_mv_cache_rebuild_module_plan.md`

(Both in the pipeline docs repo.)

Ping back if you spot anything off.
