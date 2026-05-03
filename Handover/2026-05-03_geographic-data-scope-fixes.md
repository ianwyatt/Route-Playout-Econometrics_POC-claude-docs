# Handover — Geographic data-scope fixes (C5 follow-up)

**Date:** 2026-05-03
**Branch state:** `fix/geographic-data-scope-mismatch` at `b89137b` (one commit, NOT merged, NOT pushed). Backed by `main` at `dd02243`.
**Suite:** 209/209 backend; 8/8 frontend; build clean.

This session started on review item C5 ("Mobile-Indexed Impacts ×1000 scale"), discovered the original review framing was wrong, and pivoted to a deeper investigation that found a different and bigger Geographic-tab issue. Two bugs fixed on a branch (not merged); third bug handed to the pipeline team. One unrelated regression spotted during visual QA, captured for next session.

---

## What was originally planned

Per `Claude/Handover/NEXT_SESSION_PROMPT_2026-05-09.md`, the suggested first move was item #1 — C5 forensics on Mobile-Indexed Impacts ×1000 scale. The hypothesis was that one of three Streamlit sites (Overview ×1000, campaign_analyzer ×1000, Geographic raw) had the wrong unit convention.

## What actually happened — three pivots

**Pivot 1 — C5 framing was wrong.** Initial empirical comparison found that `mv_campaign_browser.total_impacts_all_adults` matches canonical `SUM(impacts)` to floating-point precision. Misread that as "values are real impacts". Removed ×1000 from `precomputed.py:95-97` and `campaign_analyzer.py:79-81`. User caught visually — Overview's "Total Impacts" card showed "343,219" instead of the expected "343M" for campaign 17498. **Reverted both edits.** Memory rule saved: `feedback_route_audiences_in_thousands.md` — "Route source audiences are in thousands".

**Pivot 2 — Re-investigated with correct unit understanding.** With "values are in thousands" as the rule, Overview's existing ×1000 sites are correct, as are the "(000s)" labels on Executive Summary and Frame Audiences. Geographic was the one site neither doing ×1000 nor labelling "(000s)". User checked Geographic for campaign 17498: 863.0K / 2,360 frames, vs Overview 343M / 730 frames. **Mismatch ~397×, not a clean 1000×** — different problem entirely.

**Pivot 3 — Three layered bugs found.** Forensics revealed:
- **Bug 1** — `JOIN route_frames` in `src/db/queries/geographic.py` had no release filter, so frames appearing in multiple Route releases were duplicated in the result set. For 17498, 566 of 636 frames are listed in 4 releases each → 2,360 result rows, sum inflated ~3.7×.
- **Bug 2** — Display formula at 5 sites (top card, regional/towns tables, bar chart, map tooltip) divided raw thousands by 1M / 1K to produce "M"/"K" suffixes — under-displays by 1000×.
- **Bug 3** — `mv_cache_campaign_impacts_frame` is a stale snapshot truncating impacts at ~2025-10-13 (canonical goes to 2025-12-31). 30% per-frame undercount. **Pipeline-team work, not POC.**

User-observed factor `343M / 863K = 397×` reduces to `1000 (Bug 2) / (3.68 (Bug 1) × 0.683 (Bug 3)) = 398×`. Math closes.

User decisions:
1. Bug 1 → fix on POC side
2. Bug 2 → use Option β: "(000s)" labels (matches Executive Summary pattern)
3. Bug 3 → prep handover for pipeline team, not address on POC side

## What landed

### Code commit on branch (b89137b)

5 files modified, +22 / −20:

- `src/db/queries/geographic.py` — `get_frame_geographic_data_sync` rewritten with a CTE `latest_release` picking `MAX(release_id)` per frameid; eliminates the JOIN duplication.
- `src/ui/tabs/geographic/_render.py` — top metric card relabelled `"Total Impacts (000s)"` and reformatted to raw thousands (`f"{total_impacts:,.0f}"`); vestigial dead `total_avg_indexed`/`total_med_indexed` sums removed.
- `src/ui/tabs/geographic/regional.py` — bar chart Y-axis label, hover template, and table column headers `Total Impacts (000s)` / `Avg Impacts/Frame (000s)`; sort key updated.
- `src/ui/tabs/geographic/towns.py` — table column headers as above.
- `src/ui/tabs/geographic/map.py` — `labels={"total_impacts": "Total Impacts (000s)"}` for tooltip; colorbar title `Impacts (000s)`.

### Docs repo additions

- `Claude/Plans/2026-05-03_geographic-overview-data-scope-forensics.md` — full forensics on all three bugs with evidence, fix shapes, and proposed scope decisions.
- `Claude/Handover/2026-05-03_pipeline-mv-cache-campaign-impacts-frame-stale.md` — handover to pipeline team for Bug 3, with reproducible smoke test.
- `Claude/docs/pipeline-coordination.md` — open coordination item added for the MV refresh request, "Last updated" bumped to 2026-05-03.
- `Claude/Plans/2026-05-08_main-code-review.md` §C5 — appended `2026-05-03 update` block noting the original framing was wrong, pointing forward to forensics doc and pipeline handover.
- This handover doc.
- `Claude/Handover/NEXT_SESSION_PROMPT_2026-05-10.md` (next session's read-and-act).

### Auto-memory

- `feedback_route_audiences_in_thousands.md` — encodes "Route source audiences are in thousands" rule, the empirical pitfall (MV-equals-canonical doesn't mean unit is real), and the dual valid display conventions (×1000 OR "(000s)" label).

## Visual confirmation results — campaign 17498

User stepped through 6 checks; passed 5 cleanly. Sixth (regression sanity) flagged a separate finding (see below).

| # | Check | Result |
|---|---|---|
| 1 | Top metric card: "Total Impacts (000s) 234,389", "Total Frames 636" | ✓ |
| 2 | TV Regions table column headers: TV Region, Frames, Total Impacts (000s), Avg Impacts/Frame (000s), % of Total Impacts | ✓ |
| 3 | Towns table column headers: Town, Frames, Total Impacts (000s), Avg Impacts/Frame (000s), % of Total Impacts | ✓ |
| 4 | Regional bar chart: Y-axis "Impacts (000s)", hover tooltip "Impacts (000s):" | ✓ |
| 5 | UK map: colorbar "Impacts (000s)", hover tooltip "Total Impacts (000s):" | ✓ |
| 6 | Regression sanity on other tabs | ⚠ See "Unrelated finding" |

Note: Geographic's "Total Impacts (000s) 234,389" reads as 234M, vs Overview's 343M. The ~30% gap is Bug 3 (stale MV) — once the pipeline team refreshes `mv_cache_campaign_impacts_frame`, the gap closes without further POC code change.

## Unrelated finding — Daily Patterns demographic switch

During regression sanity (Check 6), user observed: on **Detailed Analysis → Daily Patterns** for campaign 17498, switching the demographic dropdown (e.g. `all_adults` → `abc1`) does not update the avg / weekly-avg metrics or the trends chart — they stay on the original demographic, looking like a total-campaign view. The Mobile Mean overlay (when MI is toggled) DOES update correctly.

Verified: my changes did NOT touch this code path. Daily Patterns lives in `src/ui/tabs/detailed_analysis/frame_daily.py`; my edits were entirely in `src/ui/tabs/geographic/` and `src/db/queries/geographic.py`. **Pre-existing bug.**

Likely root causes (preliminary, not investigated):
- `_load_frame_daily_data` may cache without including the demographic in its key.
- The SQL behind it may hard-code `'all_adults'` or drop the demographic param.
- Some intermediate layer may always pass `'all_adults'` regardless of the selector.

That the MI overlay updates correctly while raw daily data doesn't tells you the bug is in the non-MI loader, not in the demographic plumbing through the page state.

Captured as task #19 for next session.

## Branch & merge state

- `fix/geographic-data-scope-mismatch` exists locally only. **Not pushed, not merged.**
- One commit ahead of `main` (b89137b).
- User has not yet authorised merge or push — left for next session decision.
- `main` unchanged at `dd02243` (last post-sweep commit).

## Outstanding next-session work

In order:

1. **Daily Patterns demographic switch (task #19)** — investigate `_load_frame_daily_data` / `_render_frame_daily_impacts`. Pre-existing.
2. **Decide on Geographic branch** — merge into main, or hold for visual confirmation in production. The branch's commit is clean and tests pass; no reason to hold beyond a final eyes-pass.
3. **C1 — `/reach/weekly` endpoint contract** — original review CRITICAL, carried forward unchanged (task #16).
4. **H-batch (H3, H4, H5, H6, H7, H8, H9)** — small focused commits each (task #17).
5. **H2 CI workflow** (task #18).

Tasks #16–#19 are captured in the next-session prompt.

## Lessons / gotchas

- **Empirical equality between MV and canonical does not establish unit.** The MV stored `SUM(impacts)` from canonical — both are in thousands, both equal each other; that doesn't tell you what the unit is. The `from_thousands()` helper docstring already encoded the truth ("Database stores reach/impacts in thousands"); the right read would have been to read that docstring before trusting empirical equality.
- **Always validate display-unit assumptions visually before committing.** The intended Option B "fix" turned out to be the bug. Visual check by user in 30 seconds caught what an hour of code reading had missed.
- **`route_release_id` has three conventions** (per existing pipeline-coordination gotcha): `route_frames.release_id` is FK to `route_releases.id`; `cache_route_impacts_15min_by_demo.route_release_id` is bare number; `mv_campaign_browser.route_release_id` is bare number. The MV fix used `MAX(release_id)` directly on `route_frames`, sidestepping the conversion gymnastics.
- **JOIN duplication in DuckDB is silent and large.** No warning when a join multiplies rows. Worth a defensive pattern for any new geographic-style query: aggregate-then-join, never join-then-aggregate, when the joined table can have multiple rows per key.

## At the end of this session

This handover doc + the dated next-session prompt will be committed and pushed in the docs repo together once written. Don't forget to push the docs repo (per the dual-repo convention).
