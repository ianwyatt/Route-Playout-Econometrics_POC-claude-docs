# Mobile Index Venue Verification — Playout Window Research Brief

**For:** Standalone research session
**Date:** 10 March 2026

---

## Critical Context: The Data Model

You MUST understand this before doing any research.

| Data | Date Range | What It Is |
|------|-----------|------------|
| **Ad playouts** | **6 Aug – 13 Oct 2025** | Real campaign delivery — ads actually shown on OOH frames |
| **O2 mobile index** | Apr – Dec 2024 (272 days) | Hourly footfall index per Output Area, from O2 mobile data |
| **Date mapping** | `date_2024` → `date_2025` | Maps 2024 O2 patterns onto 2025 playout dates (day-of-week preserved, -1 day leap year shift) |

**The app overlays 2024 footfall patterns onto 2025 ad playouts.** This is an approximation — we're using last year's footfall to index this year's campaigns. It's not perfect but demonstrates the concept.

**The playout-relevant O2 data is 7 Aug – 14 Oct 2024** (69 days). Only events in this 2024 window affect campaign-level indexed impacts. Events outside this window (e.g., May concerts, July festivals, December shopping) exist in the MI table but never intersect with playouts.

**The index** is an hourly average for a geography (Output Area) — not a per-frame measurement. It's normalised per-frame so each frame's mean = 1.0 across all dates/hours.

---

## What's Already Been Done

Two rounds of research (12 investigations) are complete. See `docs/Research/venue-verification/00-SUMMARY.md` for the full summary.

**Key validated findings:**
- The O2 data genuinely captures event footfall (Sunderland Springsteen concert = 35x index, Stretford/Old Trafford = 75% Man Utd fixture match)
- 49 frames within 500m of known venues, 234 high-spiking frames at transport hubs and city centres
- National MI coverage is only 3.8% (14,639 of 387,165 frames)
- 57% of non-venue spikes are London Underground stations

**What was done wrong:** Some previous research queried the FULL `mobile_volume_index` table (Apr–Dec 2024) without filtering to the playout window. This produced findings about July festivals and December shopping that are valid as O2 data validation but irrelevant to campaign analysis.

---

## Your Task: Playout-Window Event Verification

Cross-reference the top spike dates **within the playout window** (7 Aug – 14 Oct 2024) against real-world events. These are the dates that actually affect campaign indexed impacts.

### Top 20 Spike Dates (Already Extracted)

| # | date_2024 | Day | Spike Hours | Frames |
|---|-----------|-----|-------------|--------|
| 1 | 29 Sep 2024 | Sun | 523 | 107 |
| 2 | 09 Aug 2024 | Fri | 464 | 111 |
| 3 | 22 Sep 2024 | Sun | 459 | 102 |
| 4 | 21 Sep 2024 | Sat | 431 | 116 |
| 5 | 25 Aug 2024 | Sun | 423 | 72 |
| 6 | 24 Aug 2024 | Sat | 418 | 91 |
| 7 | 05 Oct 2024 | Sat | 383 | 108 |
| 8 | 14 Sep 2024 | Sat | 361 | 87 |
| 9 | 26 Aug 2024 | Mon | 356 | 69 |
| 10 | 28 Sep 2024 | Sat | 337 | 98 |
| 11 | 17 Aug 2024 | Sat | 325 | 78 |
| 12 | 13 Oct 2024 | Sun | 314 | 73 |
| 13 | 06 Oct 2024 | Sun | 308 | 54 |
| 14 | 31 Aug 2024 | Sat | 284 | 71 |
| 15 | 12 Oct 2024 | Sat | 267 | 58 |
| 16 | 15 Sep 2024 | Sun | 263 | 53 |
| 17 | 11 Aug 2024 | Sun | 238 | 55 |
| 18 | 10 Aug 2024 | Sat | 229 | 55 |
| 19 | 01 Oct 2024 | Tue | 185 | 48 |
| 20 | 07 Sep 2024 | Sat | 136 | 29 |

### For each date, verify:

1. **Premier League fixtures** — this is the start of the 2024/25 season:
   - GW1: 17 Aug 2024
   - GW2: 24 Aug 2024
   - GW3: 31 Aug 2024
   - GW4: 14 Sep 2024
   - GW5: 21-22 Sep 2024
   - GW6: 28-29 Sep 2024
   - GW7: 5-6 Oct 2024
   - GW8: 19-20 Oct 2024 (just outside window)
   - Note: Sep 7 and Oct 12-13 are international breaks

2. **EFL Championship fixtures** — check for Championship matchdays on the same Saturdays

3. **League Cup (Carabao Cup)** — R2 late Aug, R3 mid-Sep, R4 late Oct

4. **UEFA competitions** — Champions League/Europa League matchdays (Tuesdays/Wednesdays), especially 1 Oct 2024

5. **International breaks** — Sep 2-10, Oct 7-15 (Nations League)

6. **Bank Holiday** — 26 Aug 2024 (Summer Bank Holiday) ✓ already confirmed

7. **Specific venue focus** — for each date, which towns have the most spikes? Cross-reference with which clubs were at home. The previous research found town-level breakdowns in `06-top-spike-dates.md`.

### Also Verify: Stretford/Old Trafford Playout-Window Fixtures

From the existing Stretford research (`03-stretford-old-trafford.md`), the following Man Utd home fixtures fall IN the playout window:

| date_2024 | Competition | Opponent |
|-----------|------------|---------|
| 16 Aug 2024 | Premier League | Fulham |
| 01 Sep 2024 | Premier League | Liverpool |
| 17 Sep 2024 | Carabao Cup R3 | Barnsley |
| 25 Sep 2024 | Europa League | FC Twente |
| 29 Sep 2024 | Premier League | Tottenham |

Confirm these fixtures are correct and check if any are missing.

### Also Verify: Cardiff Playout-Window Events

The Cardiff research (`10-cardiff-deep-dive.md`) found concerts dominate, but most are in May–June (outside window). Check specifically for Aug–Oct 2024 events at Principality Stadium — are there any Autumn Nations rugby matches or concerts in this window?

---

## How the Index Is Constructed

Understanding the index construction is critical for interpreting spike patterns.

**Pipeline:** O2 people counts per OA per hour → overnight smoothing (midnight count ÷ 5 across hours 0–4) → day-of-week baseline (mean/median of all same-day-of-week hours across Apr–Dec 2024) → index = actual / baseline → mapped to frames via OA.

**Key implications:**
- **Day-of-week normalisation (by design)**: Saturday spikes are measured against the average *Saturday*, not the average day. This is intentional — Route models average behaviour, so the MI correctly measures deviation from what is typical. Venues with frequent Saturday events (Wembley) show modest deviation because events are normal there. Venues rarely busy on Saturdays (Sunderland) show large deviations because events are atypical. The MI adds the most value where events are unusual for that location.
- **Event days in the baseline**: Event days are included in the day-of-week baseline. Old Trafford's ~10 Saturday home matches are part of the Saturday average. This is consistent with Route modelling typical behaviour — the MI flags deviation above the norm, not absolute uplift. If Route's base audiences do not fully capture regular event footfall, that is a limitation of Route's data inputs, not the MI.
- **OA sharing**: Old Trafford and Trafford Centre share an OA — football and retail produce identical index values.
- **Overnight smoothing**: Post-event egress (23:00–01:00) appears spread evenly across 00:00–04:00.

Full SQL and detailed analysis: `docs/Documentation/mobile-index/sql-construction-audit.md`

---

## Database Access

```python
import psycopg2, psycopg2.extras
from src.db.queries.connection import get_db_connection
conn = get_db_connection(use_primary=False)
```

**Filter to playout window:**
```sql
WHERE date_2025 >= '2025-08-06' AND date_2025 <= '2025-10-13'
-- OR equivalently:
WHERE date_2024 >= '2024-08-07' AND date_2024 <= '2024-10-14'
```

**Key tables:**
- `mobile_volume_index` — `frameid, date_2024, date_2025, hour, average_index, median_index`
- `route_frame_details` — `frameid, town, region, latitude, longitude, address, poi, environment_name`
- `mv_campaign_browser` — `campaign_id, primary_brand, primary_media_owner`

**Existing research scripts** in `scripts/research_*.py` provide the established pattern.

---

## Output

Save results to `docs/Research/venue-verification/13-playout-window-events.md`.

Structure:
1. Date-by-date event annotations (table)
2. Venue-specific verifications (Stretford, Cardiff)
3. Match percentage (how many of the top 20 dates correspond to confirmed events)
4. Summary of which events most affect campaign indexed impacts
5. Any dates that remain unexplained

---

## Important Notes

- Use **British English** spelling throughout
- All Python files need **ABOUTME** headers
- `route_frame_details` has duplicate rows per frame — use `DISTINCT`
- The Sunderland smoking gun (May 2024) and Glasgow TRNSMT (July 2024) are OUTSIDE the playout window — don't re-investigate these
- Focus on **what affects campaigns**, not what validates the data
- The econometrician and board need to understand that we're using 2024 footfall overlaid on 2025 playouts — frame any findings with this caveat
