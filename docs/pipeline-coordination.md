# Pipeline Team Coordination

Living record of cross-team coordination between the POC and the Route playout pipeline team. Captures schema contracts, open coordination items, resolved decisions, and operational gotchas. Intended to be appended to as new rounds happen, not archived.

**Last updated:** 2026-05-01 (MVs live, snapshot ready for rsync)

---

## Purpose

The pipeline team owns the data substrate (DuckDB build, cacher, MVs, dimension tables) and the POC consumes it read-only. Schema changes need cross-team coordination. This doc records:

- What we've asked for, what we've committed, what's deferred
- The schema contract per table and per phase
- Operational rules and quirks discovered during coordination
- TODOs parked for future phases so they're not lost

When picking up future-phase work, **read this doc first** — it's the single source of truth for what's already been agreed and what's still in flight.

## How to use this doc

- **New round of coordination starts** → add an entry to "Open coordination items" with date and summary
- **Round closes (decision reached or work landed)** → move it from "Open" to "Resolved rounds", with the agreed outcome
- **New gotcha discovered** → add to "Operational gotchas"
- **Phase boundary crossed** → update "Schema contract by phase"; if reach columns or other deferred items now have values, mark the v1 NULL state as superseded
- **New TODO surfaced for a future phase** → "Future-phase TODOs"

## Cross-references

- Pipeline team's canonical operational reference: `Claude/Handover/POC_INTEGRATION.md`
- POC migration plan: `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md`
- POC architectural spec: `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`

---

## Schema contract by phase

### Phase 4 (current — 2026-05-01)

**`cache_route_impacts_15min_by_demo` — full-year demographic impacts.** Ready, available read-only on `playout-db` DuckDB. ~2.32B rows, 339 days (2025-01-27 → 2025-12-31), 9 columns. `spot_break_id` dropped (audited zero readers).

| Column | Type | Notes |
|---|---|---|
| `frameid` | BIGINT NOT NULL | |
| `time_window_start` | TIMESTAMP NOT NULL | 15-min window start |
| `time_window_end` | TIMESTAMP | always start + 15 min |
| `campaign_id` | VARCHAR NOT NULL | post-sanitisation; matches `mv_campaign_browser.campaign_id` byte-for-byte |
| `buyer_id` | VARCHAR | |
| `demographic_segment` | VARCHAR NOT NULL | one of: `all_adults`, `abc1`, `age_15_34`, `age_35_plus`, `c2de`, `children_hh`, `main_shopper` |
| `impacts` | DOUBLE | summable (count-like) |
| `route_release_id` | INTEGER | bare release number (53/54/55/56), not the FK |
| `cached_at` | TIMESTAMP | |

PK: (frameid, time_window_start, demographic_segment, campaign_id)

**`cache_demographic_universes` — universe denominators for cover%.** Ready. 16 rows (4 releases × 4 demographic categories). Note: `demographic_code` here uses `ageband=1/2/3` / `ageband>=1` — different code space from the impacts table's `demographic_segment`.

**`mv_campaign_browser` (v1, partial)** — live as of 2026-05-01. **3,064 rows × 29 cols.** 22 columns populated, 7 NULL until Phase 5. Zero `'Unknown'` values after dim refresh (224 cold entity IDs resolved cleanly via Space API). 200 rows have `route_release_id = NULL` (non_route_measured_frames — see gotchas).

| Column | v1 status | Source |
|---|---|---|
| `campaign_id` | populated | `mv_playout_15min` (sanitised) |
| `primary_brand`, `brand_count`, `brand_names` | populated (post dim-refresh) | `mv_playout_15min_brands × cache_space_brands` |
| `primary_media_owner`, `media_owner_count`, `media_owner_names` | populated (post dim-refresh) | `mv_playout_15min × cache_space_media_owners` |
| `total_playouts`, `total_frames` | populated | `mv_playout_15min` |
| `start_date`, `end_date`, `days_active`, `avg_spot_length`, `last_activity` | populated | `mv_playout_15min` |
| `total_impacts_all_adults` | populated | derived from `cache_route_impacts_15min_by_demo` (`SUM` where `demographic_segment='all_adults'`) |
| `avg_weekly_impacts_all_adults` | populated | `AVG(weekly_impacts)` over **full weeks only** (Mon–Sun), grouped per `(campaign_id, 'all_adults')`. NULL when no full weeks (e.g. <7 days or two partial-boundary weeks with no full week between). |
| `full_week_count` | populated | count of full weeks used in the avg |
| `route_release_id` | populated | release at `start_date` (cross-release campaigns inherit start-release for cover% denominator) |
| `buyer_name` | populated | `cache_space_buyers` (Talon-only by access scope; non-Talon = `'Unknown'`) |
| `can_cache_full`, `full_cache_limitation_reason`, `limitation_notes` | populated | `campaign_cache_limitations` |
| `total_reach_all_adults` | **NULL** | Phase 5 (`cache_campaign_reach_full`) |
| `total_grp_all_adults` | **NULL** | Phase 5 |
| `frequency_all_adults` | **NULL** | Phase 5 |
| `cover_pct_all_adults` | **NULL** | Phase 5 (`total_reach * 1000 / universe`) |
| `avg_weekly_reach_all_adults` | **NULL** | Phase 5 (`cache_campaign_reach_week`) |
| `is_approximate_reach` | **NULL** | Phase 5 (POC treats NULL as `false`) |
| `reach_approximation_method` | **NULL** | Phase 5 |

**`mv_campaign_browser_summary` (v1, partial)** — live as of 2026-05-01. **1 row × 24 cols.** Same partial-v1 pattern: non-reach aggregations populated, reach-derived sums/averages NULL.

| Column | v1 status |
|---|---|
| `total_campaigns`, `campaigns_with_route_data`, `total_playouts`, `total_unique_frames` | populated |
| `earliest_playout_date`, `latest_playout_date`, `total_days_with_playouts` | populated |
| `total_impacts_all_adults_sum`, `avg_impacts_all_adults`, `avg_days_active` | populated |
| `unique_brands_count`, `unique_brands_list`, `multi_brand_campaigns_count` | populated (post dim-refresh) |
| `unique_media_owners_count`, `unique_media_owners_list` | populated (post dim-refresh) |
| `unique_buyers_count`, `unique_buyers_list` | populated |
| `route_releases_used`, `demographic_count`, `refreshed_at` | populated |
| `total_reach_all_adults_sum`, `avg_reach_all_adults`, `avg_grp_all_adults`, `avg_frequency_all_adults` | **NULL** until Phase 5 |

**MI summary tables (`cache_mi_*`)** — frozen 2025-11-19 era snapshots, cover only the 69-day Phase 2 seed window. Extension to full year is requested but not yet scoped (see TODOs).

### Phase 5 (planned — Phase 5 estimate by ~2026-05-08)

When this lands:
- `cache_campaign_reach_full` rebuilt to full-year scope → enables fill-in of `total_reach_all_adults`, `total_grp_all_adults`, `frequency_all_adults`, `cover_pct_all_adults`, `is_approximate_reach`, `reach_approximation_method` in `mv_campaign_browser`
- `cache_campaign_reach_week` rebuilt → enables `avg_weekly_reach_all_adults`
- `cache_campaign_reach_day`, `cache_campaign_reach_day_cumulative`, `cache_campaign_brand_reach` rebuilt → POC's reach/GRP and exec summary tabs become accurate for full-year campaigns

Pipeline team has confirmed the column-fill is in-place (no schema change needed); POC will not need to redeploy contract.

### Phase 5a (planned)

Rsync replica fanout to `playout-frontend` LXC via `scripts/tools/duckdb_post_write_hook.py`. POC stops reading directly off `playout-db` and reads the local replica instead. Performance + operational improvement; not blocking.

---

## Open coordination items

| Item | Asked | Status | Next action |
|---|---|---|---|
| Ops note: Tailnet credentials, rsync command, read-only attach example | 2026-05-01 | Pending — within ~24h of snapshot delivery | Pipeline sends 2026-05-02 |
| Phase 5 timeline | 2026-05-01 | Tracking ~2026-05-08 | Pipeline confirms estimate then |
| MI summary tables — extend to full year | 2026-05-01 | Open, deferred | Will plan into Phase 5 or 5a |

---

## Resolved rounds

### 2026-05-01 (later) — MVs live, snapshot ready

**Pipeline delivered:**
- `mv_campaign_browser` rebuilt: **3,064 rows × 29 cols**
- `mv_campaign_browser_summary` rebuilt: 1 row × 24 cols
- Dim refresh resolved 224 cold entity IDs (2 buyers, 1 media owner, 221 brands) via Space API; zero `'Unknown'` values. Final dim sizes: `cache_space_brands` 408 rows, `cache_space_media_owners` 7 rows, `cache_space_buyers` 3 rows (Talon Outdoor Limited, Talon Outdoor Limited (Atlas), Havas Media Limited).
- Snapshot live at `/var/lib/route/snapshots/route_poc_cache.latest.duckdb` (~87 GB, md5-verified bit-perfect against live DB)
- Reach cols all NULL as agreed; 200 rows have `route_release_id = NULL` (non_route_measured_frames — campaigns whose start_date had no Route-measured frames at that release)

**Pipeline correction (significant):**
- Buyer 15921 is **Havas Media Limited, not Talon**. The earlier `POC_INTEGRATION.md` claim that `cache_space_buyers` was access-capped to Talon-only is wrong — non-Talon buyers do exist in the data. POC will surface buyer names verbatim from the dim table; no Talon-specific code paths.

**POC reply:** acknowledged; existing flighted-campaign N/A handling will render the 200 NULL-release rows gracefully (NULL reach + NULL release naturally sort to bottom under `NULLS LAST`); waiting for ops note before pulling snapshot; Phase 5 timeline noted; will ping when parity test runs cleanly.

**Outcome:** MVs live and contract-compliant. POC migration scaffolding can begin immediately; full parity test runs once rsync target is available (within ~24h pending ops note).

### 2026-05-01 (earlier) — `mv_campaign_browser` rebuild + read access

**Asked:**
- POC: rebuild `mv_campaign_browser` from new 2.32B-row impacts table; full 29-column list provided; rebuild `mv_campaign_browser_summary` (24 cols)
- POC: extend MI summary tables to full year (deferred)
- POC: Phase 5 (campaign-reach) when unblocked
- POC: read access mechanism for development

**Pipeline questions back:**
- Actual SQL queries the POC executes against `mv_campaign_browser` (filter columns? sort columns?)
- Confirm full column list — pipeline's 2025-11-22 baseline had ~30 columns; check ours doesn't omit any consumed columns
- Reach columns — partial v1 with NULL/0 acceptable, or wait for Phase 5?
- Existing definition we'd offer to share
- JOIN consumers (do other queries `JOIN` to `mv_campaign_browser.campaign_id` from elsewhere?)

**POC reply:**
- Q1: shared four query patterns — list (Q1, no WHERE, ORDER BY `cover_pct_all_adults DESC NULLS LAST`), by-id lookup (Q2/Q3/Q4 on `campaign_id`), fallback `COUNT(*)`. Filter dominance = `campaign_id`. Sort dominance = `cover_pct_all_adults`. Recommended zone-map clustering on `campaign_id`.
- Q2: corrected to 29 columns (original list was 12); enumerated full column set
- Q3: **partial v1 acceptable** — POC's immediate goal is stakeholder demos of advertiser-trends views, which derive entirely from impacts (not reach). Reach absence is acceptable for v1; existing flighted-campaign N/A handling renders missing reach gracefully.
- Q4: no local-edited definition — POC consumes the MV as-is; pipeline's 2025-11-22 baseline is the contract
- Q5: no SQL-level joins; application-level lookup pattern — fetch `campaign_id` from `mv_campaign_browser`, parameterise downstream queries against `cache_route_impacts_15min_by_demo` etc.

**Pipeline second response:**
- Flagged dim-refresh blocker: 2,973 distinct campaigns in new universe vs 836 in stale `mv_campaign_browser`; `cache_space_brands` (187 rows) and `cache_space_media_owners` (6 rows) stale, lazy-populated during 69-day Mac-cache era
- Sequence: pre-step (Space API bulk-populate brands + media_owners), then MV rebuild
- Per-column status: 22/29 columns populated v1, 7 NULL until Phase 5
- Asked back: confirm `avg_weekly_impacts_all_adults` semantics, confirm `route_release_id` rule, share parity-test runner, accept partial v1 reach

**POC second reply:**
- Acknowledged dim-refresh as right call
- `avg_weekly_impacts_all_adults` semantics: AVG over **full weeks only** (Mon–Sun fully covered, partial boundary weeks excluded), matching `full_week_count`. NULL when zero full weeks. Must match `avg_weekly_reach_all_adults` semantics post-Phase 5 so sortable comparisons stay coherent.
- `route_release_id = release at start_date` — confirmed locked
- Parity-test runner — design pattern shared (parametrised pytest, `QUERY_FIXTURES` over every `get_*_sync` function, `[backend, postgres|duckdb]` matrix, asserts shape consistency). Full runner shared when written.
- Caught typo: pipeline's per-column note had `demographic_segment='ageband>=1'`; correct value is `'all_adults'`. Pipeline confirmed and corrected.
- Read access: rsync preferred over SSH tunnel
- One adjacent ask: `mv_campaign_browser_summary` is part of the same rebuild

**Pipeline final response:**
- All confirmations accepted
- Demographic segment correction accepted; `'ageband>=1'` exists only in `cache_demographic_universes.demographic_code` (different code space)
- `avg_weekly_impacts_all_adults` locked: full weeks only, NULL when zero full weeks (with `full_week_count = 0`)
- `route_release_id = release at start_date` locked
- Parity-test runner design accepted; pipeline will mirror on cacher side at `tests/integration/cachers/`
- Read access plan: snapshot symlink at `/var/lib/route/snapshots/route_poc_cache.latest.duckdb`; **never rsync the live `/var/lib/route/route_poc_cache.duckdb`** (mid-write during cacher rebuilds); per-event snapshot cadence; pings on symlink update; on-demand re-rsync from POC side

**POC final confirmation:**
- NULL semantics for `avg_weekly_impacts_all_adults` confirmed — `NULLS LAST` sort handles it; "—" / blank cell display
- `'ageband>=1'` clarification noted for Phase 5 cover% rejoin
- Buyer 15921 / 16591: no POC visibility; canonical Space API lookup is correct approach
- POC starts migration scaffolding immediately so parity test can run the moment MVs land

**Outcome:** `mv_campaign_browser` (v1) and `mv_campaign_browser_summary` (v1) contracts locked. Pipeline executing dim-refresh → MV rebuild → snapshot. POC executing migration scaffolding in parallel.

### 2026-05-01 — `spot_break_id` audit

**Asked:** Pipeline asked POC to audit if `spot_break_id` column was used in any POC query. Legacy 415M rows had real values; new 2.32B rebuild would have NULL; if POC filtered `IS NOT NULL` it'd silently return zero rows. Considering dropping the column entirely.

**POC reply:** Comprehensive grep across `*.py`, `*.sql`, `*.md`, `*.toml`, `*.yaml`. Zero references to `spot_break_id`. Only `spot_break*` hit was `spot_break_length` in a Route API smoke test (unrelated request parameter, not the database column). Safe to drop.

**Outcome:** Pipeline dropped `spot_break_id` from the 2025 rebuild. POC's parity test in upcoming migration will catch any silent schema divergence as a backstop.

---

## Operational gotchas

### `route_release_id` has two conventions
- `route_frames.release_id`: **FK** to `route_releases.id` (e.g. `10` for R53)
- `cache_route_impacts_15min_by_demo.route_release_id`: **bare number** (e.g. `53` for R53)
- `cache_demographic_universes.route_release_id`: **bare number** (post-fix `64b1a47`)
- `mv_campaign_browser.route_release_id` (v1): **bare number**, set to release at `start_date` per pipeline convention

When writing new joins or filters, check which side you're on. Tracked as pipeline's TODO #17 to unify.

### `buyercampaignref` sanitisation
DuckDB's `TRIM()` only strips spaces. The legacy data has TAB suffixes on some `buyercampaignref` values. Use:

```sql
TRIM(REGEXP_REPLACE(buyercampaignref, '[\t\n\r]', '', 'g'))
```

Pipeline applies this at MV build time, so `mv_campaign_browser.campaign_id` matches `cache_route_impacts_15min_by_demo.campaign_id` byte-for-byte. POC honours the same pattern when querying `mv_playout_15min` directly.

### Snapshot symlink — never rsync the live file
The live DuckDB at `/var/lib/route/route_poc_cache.duckdb` can be mid-write during cacher / MV rebuilds. Always rsync from `/var/lib/route/snapshots/route_poc_cache.latest.duckdb` (stable symlink → most recent immutable snapshot). Pipeline pings when the symlink updates.

### Single-writer constraint
DuckDB allows only one writer at a time. During cacher rebuilds (~10–30 min wall) or MV rebuilds, the file is exclusive-locked. Reads during that window fail with `IO Error: Could not set lock on file …`. Plan around this — graceful retry-with-backoff if the POC ever reads playout-db directly.

For the rsync workflow this isn't a concern — we read from a snapshot, not the live file.

### Two demographic code spaces
- `cache_route_impacts_15min_by_demo.demographic_segment`: 7 values — `all_adults, abc1, age_15_34, age_35_plus, c2de, children_hh, main_shopper`
- `cache_demographic_universes.demographic_code`: 4 values — `ageband=1, ageband=2, ageband=3, ageband>=1`

The cover% calculation in the original Postgres MV joined `cache_demographic_universes` for the universe denominator. When Phase 5 lands and we wire reach back in, the join needs to map between code spaces. Confirm the mapping with pipeline team at that point.

### Inherent gaps (`data_quality_skip`)
562 (campaign × date) pairs in 2025 have playouts whose frames aren't in `route_frames` for the per-date release. These are inherent — some OOH frames aren't measured by Route. Cacher classifies as `data_quality_skip` and writes nothing. ~98.5% pair coverage is the real ceiling, not 100%.

### Buyer scope — non-Talon buyers exist
~~`cache_space_buyers` is access-capped to Talon~~ **Corrected 2026-05-01:** non-Talon buyers exist in the data. Post dim-refresh, `cache_space_buyers` has 3 rows: Talon Outdoor Limited, Talon Outdoor Limited (Atlas), Havas Media Limited. All buyer entity IDs resolve to canonical names via Space API. Surface buyer names verbatim — no Talon-specific code paths. The earlier "access-capped to Talon" framing in `POC_INTEGRATION.md` was incorrect; pipeline team has corrected it.

### `route_release_id = NULL` for non-route-measured campaigns
200 rows in `mv_campaign_browser` (v1) have `route_release_id = NULL` — these are campaigns whose `start_date` had no Route-measured frames at the corresponding release. Pipeline's `non_route_measured_frames` convention. Their impacts cols are also NULL or partially populated. Existing flighted-campaign N/A handling renders them gracefully — they appear in the browser list with NULL reach + NULL release, sorting to the bottom under `NULLS LAST`. Cover% join to `cache_demographic_universes` will skip them (NULL release ID can't match any universe row), which is the correct behaviour.

---

## Future-phase TODOs

### Phase 5 readiness (tracked here so the round-trip work isn't lost)

When pipeline confirms Phase 5 timeline (~2026-05-08):

- Confirm `avg_weekly_reach_all_adults` will use the **same week set** as `avg_weekly_impacts_all_adults` (full weeks only, matching `full_week_count`). Sortable comparisons depend on it.
- Re-enable campaign-browser sort meaningfulness — `ORDER BY cover_pct_all_adults DESC NULLS LAST` becomes meaningful again once cover% is populated.
- Confirm cover% computation uses `route_release_id`-matched universe from `cache_demographic_universes` (cross-release campaigns inherit start-release universe per locked rule).
- Re-enable Streamlit campaign drill-down for the demo flow (Overview tab, Executive Summary tab) — currently degraded with N/A reach metrics.
- Re-enable Excel export's reach columns (currently NULL/0).

### MI summary tables extension
`cache_mi_*` tables currently cover only the 69-day Phase 2 seed window. POC's advertiser-trends views overlay MI on full-year impacts, so without extension we show 339 days of impacts against 69 days of MI — visually confusing.

Needed before any external demo. Pipeline considering Phase 5 or Phase 5a slot. Re-raise after Phase 5 lands if not picked up.

### Phase 5a rsync replica
Once Phase 5a wires the post-write hook to `playout-frontend`, switch POC's `DUCKDB_PATH` from the rsync'd local snapshot to the locally-replicated path on `playout-frontend`. No code change needed — env var update only.

### Audit `is_approximate_reach` / `reach_approximation_method` warning logic
POC's existing UI shows tooltips when `is_approximate_reach=true`. After Phase 5 fills these columns, sanity-check the tooltip thresholds against the new approximation methods (which may differ from the legacy 1hr-aggregation approximation that produced the original values).

---

## When updating this doc

- Move closed items from "Open coordination items" to "Resolved rounds" with a clear Outcome line
- Update "Schema contract by phase" when a phase boundary is crossed (e.g. Phase 5 fills in reach columns → mark v1 NULL state as superseded, add a "Phase 5 (current)" subsection)
- Add new gotchas as they're discovered, even if they seem obvious — future-Ian and future-Claude won't have the context
- Future-phase TODOs should be specific enough to act on, not vague reminders
