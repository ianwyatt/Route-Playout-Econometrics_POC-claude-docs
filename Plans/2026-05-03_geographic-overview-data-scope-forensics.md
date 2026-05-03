# Geographic vs Overview data-scope mismatch — forensics

**Date:** 2026-05-03
**Branch:** `fix/c5-impacts-scale-overview` (zero commits — to be renamed once scope clarifies)
**Trigger:** Investigation of review item C5. Original review framing (×1000 unit mismatch) was wrong — Route source values are in thousands and the existing ×1000 sites are intentional. Visual check on campaign 17498 showed Overview = 343M / 730 frames vs Geographic = 863K / 2,360 frames — a different and bigger problem.

This document captures three independent bugs found during the investigation. Section 6 proposes options for the fix; **no code changes have been made**.

---

## TL;DR

The Geographic tab disagrees with Overview on the same campaign because of three layered problems:

1. **JOIN duplication** in the Geographic loader's SQL — `JOIN route_frames` has no release filter, so every frame that exists in multiple Route releases is counted multiple times. Fix on the POC side.
2. **Display formula under-by-1000×** in the Geographic top-line metric and tables — values are in thousands but the formula divides by 1M / 1K to produce "M"/"K" suffixes assuming real impacts. Fix on the POC side.
3. **`mv_cache_campaign_impacts_frame` is a stale snapshot** with a truncated date window relative to canonical impacts and `mv_campaign_browser`. Even after fixing 1 and 2, Geographic's totals would undercount by ~30% because the source MV itself is behind. **Pipeline-team-owned**.

The user-observed 397× factor between Overview's `343M` and Geographic's `863K` reduces cleanly: `1000 (Bug 2) / 2.5 (combined inflation from Bug 1)`, with the residual (Bug 3) absorbed into the `2.5×` factor.

---

## What was verified empirically

All against the local DuckDB snapshot (`/home/dev/data/route_poc_cache.duckdb`, identity `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb`).

### Baselines for campaign 17498 / `all_adults`

| Source | Frame count | Sum of impacts (thousands) | Sum of impacts (real) |
|---|---:|---:|---:|
| `mv_campaign_browser.total_impacts_all_adults` | 730 (`total_frames`) | 343,218.76 | 343M |
| `cache_route_impacts_15min_by_demo` (canonical sum) | 659 (distinct frameid) | 343,218.76 | 343M |
| `mv_cache_campaign_impacts_frame` (Geographic source) | 636 | 234,388.77 | 234M |
| Geographic loader after `JOIN route_frames` (no release filter) | 2,360 | 862,979.25 | 863M |

`mv_campaign_browser` and `cache_route_impacts_15min_by_demo` agree to floating-point precision on the campaign-total. Per pipeline-coordination doc line 67 — `total_impacts_all_adults` is computed as `SUM(impacts)`, both in thousands, both treat the same canonical impacts.

The Geographic loader sees only the stale `mv_cache_campaign_impacts_frame`; its 636 frames are a subset of canonical's 659 (23 small-impact frames missing), and per-frame the MV's `total_impacts` is ~28% less than canonical for those 636 (due to truncated date window — see Bug 3 below).

---

## Bug 1 — JOIN multi-release duplication

### Location

`src/db/queries/geographic.py:27-44` — `get_frame_geographic_data_sync`.

```sql
FROM mv_cache_campaign_impacts_frame mf
JOIN route_frames rf ON mf.frameid = rf.frameid
JOIN route_frame_details rfd ON rf.release_id = rfd.release_id AND rf.frameid = rfd.frameid
WHERE mf.campaign_id = ? AND mf.demographic_segment = ?
  AND rf.latitude IS NOT NULL
ORDER BY mf.total_impacts DESC
```

### Mechanism

`route_frames` has one row per `(frameid, release_id)`. The same `frameid` appears in `route_frames` for every Route release that lists it (4 releases active in the snapshot's frame catalogue: R52/R53/R54/R55/R56/R57 etc.). The JOIN doesn't restrict `release_id`, so each `mf` row gets multiplied by the number of releases the frame appears in.

For campaign 17498 / `all_adults`:

| Frames in N releases | Count |
|---:|---:|
| 1 release | 50 |
| 2 releases | 14 |
| 3 releases | 6 |
| 4 releases | 566 |

Total joined rows: `50·1 + 14·2 + 6·3 + 566·4 = 2,360`. Sum of `mf.total_impacts` is multiplied by the same factor per-frame: `234,388.77 × ~3.69 = 862,979.25`.

Confirmed on a second campaign (18409): 964 unique frames in `mv_cache_campaign_impacts_frame` → 3,783 rows after JOIN, sum 194,835 → 750,581 (≈3.85× inflation). Same pattern.

### Fix shape

Filter the join to the campaign's release. Multiple options:

- Use `mv_campaign_browser.route_release_id` (the campaign's start-date release per pipeline contract): bare-number, e.g. `55`.
- Map to `route_releases.release_number`: e.g. `'R55'` (a `VARCHAR`).
- Filter `route_frames.release_id` (FK to `route_releases.id`).

Cleanest single-query shape:

```sql
JOIN route_frames rf
  ON rf.frameid = mf.frameid
 AND rf.release_id = (
   SELECT id FROM route_releases
   WHERE release_number = 'R' || (
     SELECT route_release_id::VARCHAR FROM mv_campaign_browser WHERE campaign_id = mf.campaign_id
   )
 )
```

…but uglier than passing `route_release_id` in as a query parameter from the loader. Loader signature already takes `campaign_id`; can fetch the release once and pass both to the SQL.

Verified preview on 17498: `JOIN ... WHERE rr.release_number = 'R55'` produces 584 rows / sum 231,446 (rather than 2,360 / 862,979). Note the row count drops to 584 (not 636) — 52 of the 636 mv_cache frames don't have a `route_frames` row for R55 specifically; they're in earlier/later releases only. That itself is an odd subtlety — flagged in Bug 1 follow-ups.

### Bug 1 follow-ups (worth noting)

- 52 of the 636 mv_cache frames are absent from `route_frames` for R55. These frames played out and have impact data attributed to 17498, but the Route frame catalogue doesn't list them under R55 — they exist under R54 or R56. Filtering strictly to R55 drops them. The right answer probably is "show all frames the campaign played on, take geo attributes from whichever release the frame appears in, take impacts once". The query becomes a `DISTINCT ON (frameid)` shape or a subquery approach.
- The pipeline-coordination doc gotcha "`route_release_id` has two conventions" applies here. Any fix must navigate `mv_campaign_browser.route_release_id` (bare) → `route_releases.release_number` (`'R55'`) → `route_frames.release_id` (FK = `route_releases.id`) carefully.

---

## Bug 2 — Display under-by-1000×

### Locations

| File:line | Surface | Display formula | Effect on values-in-thousands |
|---|---|---|---|
| `src/ui/tabs/geographic/_render.py:150-155` | Top "Total Impacts" metric card | `total/1_000_000` "M" if ≥1M else `total/1_000` "K" | shows "0.3M" or "863.0K" when actual is 343M / 863M |
| `src/ui/tabs/geographic/regional.py:69` | "Total Impacts" column in TV Regions table | `f"{x:,.0f}"` raw | column header `Total Impacts`, no "(000s)" hint, raw thousands shown |
| `src/ui/tabs/geographic/regional.py:20` | Regional bar chart text labels | `text="total_impacts"` raw | same |
| `src/ui/tabs/geographic/towns.py:49` | "Total Impacts" column in Towns table | `f"{x:,.0f}"` raw | same |
| `src/ui/tabs/geographic/map.py:41` | UK map tooltip | `"total_impacts": ":,.0f"` raw | same |

The pattern across the rest of the app is either **multiply by 1000 for display** (Overview, campaign browser) or **add "(000s)" label and show raw** (Executive Summary, Frame Audiences). Geographic does neither.

### Fix shape

Two equally valid options — both align Geographic with the rest of the app:

- **Option α (×1000 everywhere):** multiply at display sites and the formula displays real impacts. Top card divides by 1M/1K of the multiplied value, regional/towns/tooltip multiply before formatting.
- **Option β ("(000s)" labels):** keep raw values, add "(000s)" to the top card label, the table column headers, and the map tooltip. Bar chart text labels need a unit hint too.

Option α matches Overview's pattern (no "(000s)" labels in headlines). Option β matches Executive Summary's pattern. Either is consistent — just pick one.

### Bug 2 follow-ups

- The dead `total_avg_indexed`/`total_med_indexed` computation at `_render.py:139-140` is never displayed anywhere. Vestigial code from an earlier version of the Geographic tab. Trivial cleanup, can be bundled with the Bug 2 fix.

---

## Bug 3 — `mv_cache_campaign_impacts_frame` is stale

### Evidence

For campaign 17498 / `all_adults`:

- Canonical (`cache_route_impacts_15min_by_demo`): 659 distinct frames, sum 343,218.76, last impact at `2025-10-19 22:45`.
- `mv_cache_campaign_impacts_frame`: 636 frames, sum 234,388.77, last `last_playout` at `2025-10-13 12:45`.

Per-frame spot check (top 5 impact frames):

| frameid | mv_sum | canon_sum | mv_slots | canon_slots | mv_last | canon_last |
|---|---:|---:|---:|---:|---|---|
| 1234934039 | 9,006 | 13,054 | 2,557 | 3,192 | 2025-10-13 12:45 | 2025-10-19 22:45 |
| 1234934040 | 7,983 | 11,904 | 2,557 | 3,192 | 2025-10-13 12:45 | 2025-10-19 22:45 |
| 2000114951 | 8,419 | 11,403 | 2,376 | 3,024 | 2025-10-12 22:45 | 2025-10-19 22:45 |
| 2000117661 | 4,960 | 6,813 | 2,376 | 3,024 | 2025-10-12 22:45 | 2025-10-19 22:45 |
| 2000114953 | 3,715 | 5,958 | 2,376 | 3,024 | 2025-10-12 22:45 | 2025-10-19 22:45 |

Per-frame the MV has the **same first slot** but a **truncated last slot** ~6 days earlier than canonical. The truncation gives a ~30% sum reduction.

### Mechanism (hypothesised)

`mv_cache_campaign_impacts_frame` was apparently built from a snapshot that froze around `2025-10-13`. The full-year canonical impacts table (`cache_route_impacts_15min_by_demo`, ~2.32B rows) was rebuilt for Phase 4 (2026-05-01) but `mv_cache_campaign_impacts_frame` doesn't appear to have been refreshed against the new data. Same date pattern as the MI cache (`cache_mi_daily` for 17498 ends 2025-10-13) — both possibly frozen at the same prior snapshot.

The pipeline-coordination doc lists the v1 `mv_campaign_browser` rebuild as 2026-05-01 with 3,064 rows × 29 cols. It does not list `mv_cache_campaign_impacts_frame` as part of that rebuild. So this MV may simply have been missed in the Phase 4 substrate work.

### Fix shape

This is **pipeline-team work, not POC**. POC options short of a pipeline rebuild:

- Geographic loader queries `cache_route_impacts_15min_by_demo` directly with `GROUP BY frameid` for its frame totals, instead of reading the stale MV. Cost: a per-campaign aggregation over up to ~1.7M canonical rows (for a heavy campaign) — still fast on DuckDB but slower than reading a pre-aggregated MV. Eliminates Bug 3 entirely.
- Wait for the pipeline team to refresh `mv_cache_campaign_impacts_frame` to full-year scope. Cleaner for POC code, but blocks the fix.

Either is reasonable. Recommend the loader rewrite (POC-side, immediate) if Bug 1 is being fixed anyway — the SQL rewrite for Bug 1 already touches the same loader, so adding an aggregation in the same change is cheap.

### Bug 3 follow-ups

- Surface this to the pipeline team via `Claude/docs/pipeline-coordination.md` "Open coordination items". Phrase: "`mv_cache_campaign_impacts_frame` truncated at ~2025-10-13 — confirm intentional vs missed Phase 4 rebuild".
- The 23 frames missing entirely from `mv_cache_campaign_impacts_frame` (sum ~1,080) may correspond to frames added to the canonical table after the freeze. Same root cause.

---

## Combined arithmetic — why the user saw 343M vs 863K

| Component | Effect |
|---|---|
| Real impacts (Overview, correct) | 343,218 thousand |
| Bug 3 alone (mv_cache stale): per-frame sum drops from 343,218 to 234,388 | 234,388 thousand |
| Bug 1 (JOIN duplication, ×3.68 average): | 862,979 thousand |
| Bug 2 (display ÷1000): "863.0K" rendered | user reads 863,000 |
| Overview (correct, ×1000 applied): "343,218,764" rendered | user reads 343M |

User-observed factor: `343,218,764 / 863,000 ≈ 397×`. Predicted from bugs: `1000 / (3.68 × 0.683) = 1000 / 2.51 = 398×`. Math closes.

---

## Proposed fix scope

### Recommended (single PR, all on POC side)

1. **Rewrite `get_frame_geographic_data_sync`** in `src/db/queries/geographic.py` to:
   - Aggregate impacts directly from `cache_route_impacts_15min_by_demo` (`GROUP BY frameid`) — eliminates Bug 3.
   - JOIN to `route_frames` with release filter via the campaign's `route_release_id` from `mv_campaign_browser` — eliminates Bug 1, with the "frame in earlier/later release" subtlety handled by either a `DISTINCT ON` or a subquery picking the campaign's release first then falling back to whichever release lists the frame.
   - Return the same column shape so consumers don't need changes.
2. **Apply Bug 2 fix** at all five Geographic display sites — pick Option α or β and apply consistently.
3. **Clean up vestigial `total_avg_indexed` / `total_med_indexed`** at `_render.py:139-140`.
4. **Visual confirmation** before commit — Overview's "Total Impacts" should match Geographic's top card and the regional/town table sums (within rounding) for the same campaign+demographic.
5. **Surface Bug 3 to pipeline team** via `pipeline-coordination.md` open-items so they can refresh the MV and POC can later switch back to consuming it (smaller query cost, single source of truth).

### Smaller alternative (if user wants minimum surface)

- Bug 1 + Bug 2 only. Geographic still undercounts by ~30% because of Bug 3 but at least the magnitudes will be in the right ballpark. Faster to ship, defers the loader rewrite.

### Branch hygiene

`fix/c5-impacts-scale-overview` no longer matches the work. Rename to `fix/geographic-data-scope-mismatch` (or similar) before any commits land. The branch currently has zero commits — `git branch -m` is safe.

### Update to the main code review

`Claude/Plans/2026-05-08_main-code-review.md` §C5 was based on a wrong premise (×1000 unit mismatch). Append a note pointing forward to this forensics document and reframing the actual finding. Do NOT delete the original entry — it's a record of how the review was wrong, useful context for future review work.

---

## Status

**No code changes made.** Three bugs documented, three fix options proposed. Awaiting user decision on:

1. Which fix scope — recommended (loader rewrite + display + cleanup) vs minimum (Bug 1 + Bug 2 only).
2. Bug 2 style — Option α (×1000 everywhere) vs Option β ("(000s)" labels).
3. Whether to surface Bug 3 to the pipeline team now or wait until after POC fix lands.

Once decided, proceed with branch rename, code changes, visual confirmation, then commit + handover doc.
