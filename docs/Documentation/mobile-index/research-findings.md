# Mobile Volume Index — Research Findings

**Date:** 10 March 2026
**Data Period:** ~69 days (6 Aug – 13 Oct 2025 playout window)
**Source:** 99.87M frame-hours across 16,265 frames, 833 campaigns
**Database:** `route_poc` (local), tables `mobile_volume_index`, `cache_mi_daily`, `cache_mi_frame_totals`, `route_frame_details`

---

## Data Model

| Data Source | Date Range | Purpose |
|-------------|-----------|---------|
| **Ad playouts** | **6 Aug – 13 Oct 2025** | Actual campaign delivery period |
| **O2 mobile index** | Apr – Dec 2024 (272 days) | Hourly footfall index by Output Area, sourced from O2 |
| **Date mapping** | `date_2024` → `date_2025` | Day-of-week preserved, overlays 2024 footfall onto 2025 playouts |

The O2 data provides an hourly average footfall index at Output Area (OA) level. Each frame's index is the OA-level value for its location. The index is normalised per OA × day-of-week × hour so it measures deviation from typical behaviour. The playout-relevant O2 data covers **7 Aug – 14 Oct 2024** (69 days).

**Dates in this document use the `date_2025` playout mapping** (e.g., "21 May 2025" = mapped from the 22 May 2024 O2 data). Dates outside the playout window (Aug–Oct) validate data quality but do not affect campaign indexed impacts.

---

## Executive Summary

Mobile volume indexing — adjusting OOH audience impacts by real mobile device footfall at each frame — produces a **net +4.93% uplift** in total audience impacts across 833 campaigns (mean index), or +2.41% using the more conservative median index.

**73% of campaigns see positive uplift.** 44% gain 5% or more, while only 7.2% see decreases larger than 5%. The median campaign gains +4.1%. The mechanism: although the unweighted average index across all 100M frame-hours is exactly 1.0, the audience-weighted average is 1.049 — because high-footfall periods (peak commute, evenings, events) naturally coincide with higher raw audience volumes, amplifying the effect when used as a multiplier.

**Event-driven traffic is clearly visible in the data.** Frames near football stadia and major event venues show index values up to 35x on event days. The geographic hotspot map reads like a list of Premier League grounds — Manchester (Old Trafford/Etihad), Cardiff (Principality Stadium), Holloway (Emirates), Tottenham (Spurs), Stretford, Liverpool, Leeds, Brentford, Twickenham. A single frame near the Stadium of Light in Sunderland hit 35x at 10pm (O2 date: 22 May 2024, mapped to 21 May 2025), with a clear ingress-event-egress ramp from 3x at 3pm to 35x at 10pm across three adjacent frames. This was subsequently confirmed as **Bruce Springsteen & The E Street Band** at the Stadium of Light — outside the playout window but the strongest single validation of data quality.

Saturday and Sunday account for **62% of all extreme spikes** (index >3x), concentrated in the 18:00–23:00 event window. Venue verification confirmed **85% of top playout-window spike dates** match real-world events (Premier League GW1–7, Champions League, Notting Hill Carnival, Reading Festival, Billy Joel at Cardiff).

**Frame placement matters enormously.** Channel Four's 204-frame JCDecaux campaign gained +28.5% from mobile indexing — systematic co-location with event hotspots. Conversely, Red Bull's single Ocean Outdoor frame lost 35% — placed in a consistently below-average footfall location. This has direct implications for media planning and frame valuation: the same campaign budget delivers materially different real-world audiences depending on frame proximity to high-footfall locations.

---

## 1. Overall Impact on Audience

| Metric | Raw Impacts (000s) | Indexed (000s) | Change |
|--------|-------------------|----------------|--------|
| **Mean Index** | 6,284,671 | 6,594,430 | **+4.93%** |
| **Median Index** | 6,284,671 | 6,436,317 | **+2.41%** |

Across all 833 campaigns, mobile volume indexing produces a net **+4.93% uplift** (mean) or **+2.41%** (median) in total audience impacts.

---

## 2. The Weighting Mechanism

| Measure | Value |
|---------|-------|
| Unweighted average index (all frame-hours) | **1.000000** |
| Unweighted average median index | **1.003154** |
| Weighted average index (by audience volume) | **1.049288** |
| Weighted average median index | **1.024130** |
| Frame-hours with index ≥ 1.0 | 49,538,081 (49.6%) |
| Frame-hours with index < 1.0 | 50,332,599 (50.4%) |

The unweighted average of all index values is exactly 1.0 — roughly half of frame-hours are above average, half below. But high-index periods (peak commute, evenings, event times) coincide with higher raw audience volumes, so when used as a multiplier the result is a net positive. The **weighted** average is 1.049 — explaining the ~5% uplift.

---

## 3. Index Value Distribution

### Average Index

| Bucket | Frame-Hours | % of Total |
|--------|------------|------------|
| < 0.5 | 2,469,604 | 2.47% |
| 0.5 – 0.8 | 11,300,327 | 11.32% |
| 0.8 – 1.0 | 36,562,668 | 36.61% |
| 1.0 – 1.2 | 36,422,245 | 36.47% |
| 1.2 – 1.5 | 10,565,281 | 10.58% |
| 1.5 – 2.0 | 2,292,639 | 2.30% |
| 2.0 – 3.0 | 230,480 | 0.23% |
| 3.0 – 5.0 | 22,375 | 0.02% |
| 5.0 – 10.0 | 4,566 | 0.005% |
| ≥ 10.0 | 495 | 0.0005% |

The vast majority (83%) of frame-hours fall between 0.8 and 1.2 — normal variation. The extreme tail (>3.0) represents just 0.027% of all data but produces dramatic localised effects.

### Median Index

| Bucket | Frame-Hours | % of Total |
|--------|------------|------------|
| < 0.5 | 2,682,160 | 2.69% |
| 0.5 – 0.8 | 9,679,083 | 9.69% |
| 0.8 – 1.0 | 37,137,284 | 37.19% |
| 1.0 – 1.2 | 38,731,016 | 38.78% |
| 1.2 – 1.5 | 9,033,328 | 9.05% |
| 1.5 – 2.0 | 2,023,825 | 2.03% |
| ≥ 2.0 | 583,984 | 0.58% |

---

## 4. Campaign Distribution by % Change

### Mean Index

| Bucket | Campaigns | % of Total | Avg Change | Range |
|--------|-----------|------------|------------|-------|
| Large uplift (>10%) | 168 | 20.2% | +19.70% | +10.00% to +146.14% |
| Significant uplift (5–10%) | 199 | 23.9% | +7.15% | +5.02% to +10.00% |
| Moderate uplift (2–5%) | 162 | 19.5% | +3.50% | +2.03% to +4.99% |
| Small uplift (0–2%) | 81 | 9.7% | +1.05% | +0.01% to +1.99% |
| Small decrease (0 to -2%) | 73 | 8.8% | -1.04% | -2.00% to -0.01% |
| Moderate decrease (-2 to -5%) | 88 | 10.6% | -3.19% | -5.00% to -2.03% |
| Significant decrease (-5 to -10%) | 44 | 5.3% | -6.83% | -9.55% to -5.01% |
| Large decrease (< -10%) | 16 | 1.9% | -17.74% | -35.28% to -11.50% |

**Summary:** 610 campaigns (73.3%) show positive uplift, 221 (26.6%) show decrease.

### Statistical Summary

| Statistic | Mean Index | Median Index |
|-----------|-----------|--------------|
| Mean % change | +5.35% | +3.48% |
| Median % change | +4.10% | +2.84% |
| Standard deviation | 10.69% | 10.62% |
| Min | -35.28% | -37.75% |
| Max | +146.14% | +173.08% |
| P5 | -6.33% | — |
| P25 (Q1) | -0.36% | — |
| P75 (Q3) | +8.62% | — |
| P95 | +22.12% | — |

---

## 5. Top 20 Campaigns by Positive Uplift (Mean Index)

| Campaign ID | Brand | Media Owner | Frames | Raw (000s) | Indexed (000s) | Mean % | Median % |
|-------------|-------|-------------|--------|-----------|---------------|--------|----------|
| ATLAS1776-4 | (unbranded) | Global | 2 | 2.5 | 6.1 | +146.14% | +173.08% |
| 17601 | iPlayer | Bauer Media Outdoor | 1 | 2.2 | 3.5 | +61.70% | +74.46% |
| Plato 18273 | Domino's Pizza | JCDecaux | 54 | 1.9 | 3.0 | +57.19% | +58.01% |
| 17061 | (unbranded) | JCDecaux | 20 | 0.7 | 1.1 | +56.29% | +57.53% |
| Plato 18188 | Intrepid Travel | JCDecaux | 1 | 1.5 | 2.3 | +48.56% | +38.69% |
| 18645 | (unbranded) | JCDecaux | 29 | 8.1 | 12.0 | +48.56% | +38.69% |
| 15892 | (unbranded) | Global | 4 | 4,399.4 | 6,409.0 | +45.68% | +33.39% |
| 17361 | Specsavers | JCDecaux | 52 | 2,431.7 | 3,481.2 | +43.16% | +28.19% |
| 18701 | Ladbrokes | Bauer Media Outdoor | 2 | 6.8 | 9.5 | +40.96% | +48.69% |
| 17207 | Shell | JCDecaux | 15 | 0.7 | 1.0 | +39.85% | +43.29% |
| 18488 | (unbranded) | JCDecaux | 4 | 3.1 | 4.3 | +39.81% | +58.40% |
| SM362539 | (unbranded) | Ocean Outdoor | 24 | 198.9 | 265.2 | +33.36% | +39.75% |
| 18993 | (unbranded) | JCDecaux | 12 | 9.5 | 12.5 | +30.96% | +11.39% |
| 17584 | (unbranded) | JCDecaux | 43 | 8.8 | 11.5 | +30.74% | +26.74% |
| 18645 | (unbranded) | JCDecaux | 32 | 3,670.2 | 4,789.4 | +30.50% | +23.87% |
| 18516 | MAC | JCDecaux | 18 | 2.4 | 3.0 | +28.67% | +23.74% |
| 18720 | Channel Four | JCDecaux | 204 | 18,727.8 | 24,056.8 | +28.46% | +20.17% |
| 17993 | (unbranded) | JCDecaux | 2 | 0.0 | 0.1 | +28.02% | +26.90% |

**Notable:** Campaign 15892 (Global, 4 frames) jumps from 4.4M to 6.4M impacts — a **+45.68%** uplift from just 4 frames in high-footfall locations. Campaign 18720 (Channel Four, 204 frames) gains **+28.5%**, suggesting systematic placement near event hotspots.

---

## 6. Bottom 20 Campaigns by Negative Change (Mean Index)

| Campaign ID | Brand | Media Owner | Frames | Raw (000s) | Indexed (000s) | Mean % | Median % |
|-------------|-------|-------------|--------|-----------|---------------|--------|----------|
| 18970 | Red Bull | Ocean Outdoor | 1 | 101.0 | 65.4 | -35.28% | -37.75% |
| 19198 | (unbranded) | JCDecaux | 53 | 34.2 | 25.9 | -24.18% | -21.85% |
| 16014 | Lipton | JCDecaux | 1 | 123.4 | 94.4 | -23.48% | -24.61% |
| Plato 16144 | McArthurGlen | JCDecaux | 1 | 0.0 | 0.0 | -20.99% | -21.52% |
| 18550 | (unbranded) | JCDecaux | 127 | 2,113.5 | 1,699.3 | -19.60% | -24.83% |
| 2025-08-21:RM2QC | (unbranded) | Ocean Outdoor | 3 | 293.3 | 241.6 | -17.63% | -15.49% |
| 17427 | McDonald's | Bauer Media Outdoor | 57 | 359.6 | 296.3 | -17.62% | -21.03% |
| 16654 | (unbranded) | JCDecaux | 2 | 34.6 | 28.6 | -17.40% | -18.65% |
| 18170 | (unbranded) | Ocean Outdoor | 1 | 29.4 | 24.7 | -15.98% | -17.25% |
| 18615 | Capital One | Bauer Media Outdoor | 7 | 198.5 | 167.0 | -15.84% | -18.70% |
| ATLAS1946-8 | Checkout | Global | 9 | 5.9 | 5.0 | -14.01% | -16.35% |
| 18630 | Transport for Wales | Bauer Media Outdoor | 18 | 1,515.0 | 1,318.6 | -12.97% | -7.46% |
| 16144 | McArthurGlen | Bauer Media Outdoor | 2 | 139.1 | 121.3 | -12.83% | -14.32% |
| 18461 | British Gas | JCDecaux | 3 | 8.4 | 7.4 | -12.68% | -9.93% |
| 18782 | (unbranded) | Bauer Media Outdoor | 986 | 15,419.1 | 13,645.8 | -11.50% | -15.40% |

**Notable:** Red Bull's single Ocean Outdoor frame loses 35% — placed in a consistently below-average footfall location. Campaign 18782 (986 frames, Bauer) loses 11.5% at scale, suggesting a frame portfolio skewed towards quieter locations.

---

## 7. Event-Driven Peaks

### Extreme Spike Thresholds

| Threshold | Frame-Hours | Unique Frames |
|-----------|------------|---------------|
| Index > 3.0 | 27,436 | 2,038 |
| Index > 5.0 | 5,061 | 406 |
| Index > 10.0 | 495 | 42 |
| Index > 20.0 | 8 | — |

### The Most Extreme Frame: Sunderland (O2 date: 22 May 2024)

Frame `1234860534` near the **Stadium of Light** hit **35x the national average** at 22:00. Confirmed as **Bruce Springsteen & The E Street Band** concert. This is outside the playout window but validates data quality:

```
Hour   Avg Index  Visualisation
─────────────────────────────────────────────────────────
06:00    1.20     ██
10:00    1.29     ██
12:00    1.37     ██
13:00    1.63     ███
14:00    1.96     ███
15:00    3.03     ██████
16:00    5.37     ██████████
17:00   10.93     █████████████████████
18:00   22.85     █████████████████████████████████████████████
19:00   27.11     ██████████████████████████████████████████████████████
20:00   29.34     ██████████████████████████████████████████████████████████
21:00   31.39     ██████████████████████████████████████████████████████████████
22:00   35.00     ██████████████████████████████████████████████████████████████████████
23:00   28.97     █████████████████████████████████████████████████████████
```

The ramp from ~1x at midday to 35x at 10pm is textbook event ingress → event → egress. Three adjacent frames (`1234860534`, `1234860069`, `1234860070`) all spike simultaneously, confirming a localised event rather than data noise.

A second cluster in **Glasgow North** (O2 date: 12–13 July 2024, likely TRNSMT Festival) shows 6+ frames spiking to 18x at 23:00. Outside the playout window — validates data quality only.

### Temporal Patterns for Spikes (index > 3.0)

**By Day of Week:**

| Day | Spikes | % of Total | Avg Spike Index |
|-----|--------|------------|-----------------|
| Saturday | 10,016 | 36.5% | 4.11 |
| Sunday | 7,077 | 25.8% | 4.19 |
| Friday | 2,979 | 10.9% | 4.22 |
| Tuesday | 2,965 | 10.8% | 4.27 |
| Wednesday | 1,904 | 6.9% | 4.88 |
| Thursday | 1,385 | 5.0% | 4.67 |
| Monday | 1,110 | 4.0% | 4.52 |

Saturday and Sunday together account for **62.3%** of all extreme spikes.

**By Hour of Day:**

| Period | Spikes | Notes |
|--------|--------|-------|
| 00:00–04:00 | 5,250 | Post-event dispersal (consistent 1,050/hr across 420 frames) |
| 05:00–09:00 | 458 | Quiet |
| 10:00–13:00 | 1,846 | Building (daytime events, markets) |
| 14:00–17:00 | 5,011 | Pre-event build, afternoon fixtures |
| 18:00–23:00 | **14,871** | **Peak event window** — 54% of all spikes |

The 18:00–23:00 window captures evening football matches, concerts, and nightlife. The flat overnight pattern (0–4am, exactly 1,050 per hour) suggests frames near venues where post-event crowds linger.

**Top Spike Dates (full O2 dataset, `date_2025` mapped values):**

Note: Only dates within the playout window (6 Aug – 13 Oct 2025) affect campaign indexed impacts. Dates outside this range validate data quality only.

| Date (2025) | O2 Date (2024) | Day | Spikes | Max Index | Playout? | Context |
|------|------|-----|--------|-----------|:---:|----------------|
| 26 Oct | 27 Oct | Sun | 735 | 7.19 | ✅ | Partly BST→GMT artefact + Arsenal vs Liverpool + Trafford Centre half-term |
| 29 Nov | 30 Nov | Sat | 722 | 6.12 | ❌ | Football Saturday (outside playout window) |
| 4 May | 5 May | Sun | 576 | 6.99 | ❌ | Bank Holiday / end of season (outside playout window) |
| 1 Nov | 2 Nov | Sat | 561 | 7.36 | ❌ | Football Saturday (outside playout window) |
| 28 Sep | 29 Sep | Sun | 523 | 8.90 | ✅ | **PL GW6: Man Utd vs Spurs** (confirmed) |
| 8 Aug | 9 Aug | Fri | 464 | 9.70 | ✅ | **Billy Joel at Principality Stadium, Cardiff** (confirmed) |
| 25 Aug | 26 Aug | Mon | 356 | 13.45 | ✅ | **Notting Hill Carnival** (main parade) + Bank Holiday (confirmed) |

---

## 8. Geographic Hotspots

### Towns with Most Extreme Spikes (index > 3.0)

| Town | Region | Spikes | Frames | Avg Index | Max Index | Verified Source |
|------|--------|--------|--------|-----------|-----------|-------------|
| **Manchester** | North West | 3,932 | 86 | 3.64 | 6.90 | Old Trafford / Etihad (OA gap at Etihad — single MI frame) |
| **Cardiff** | Wales | 2,718 | 102 | 3.95 | 9.82 | Principality Stadium ✅ (concerts + football) |
| **Birmingham** | West Midlands | 1,385 | 192 | 4.02 | 8.42 | City centre / NEC (Villa Park has zero spike activity — 1 MI frame) |
| **Stretford** | North West | 1,345 | 18 | 6.23 | 11.31 | Old Trafford ✅ + Trafford Centre (same OA, indistinguishable) |
| **Glasgow North** | Scotland | 993 | 49 | 6.84 | 18.60 | Celtic Park / Ibrox area |
| **Holloway** | London | 902 | 10 | 4.54 | 9.45 | Emirates Stadium spillover ✅ (OA gap — 70% match-day uplift on adjacent frames) |
| **Liverpool** | North West | 851 | 79 | 3.67 | 8.56 | City centre transport hubs + Anfield (sparse MI near ground) |
| **Leeds** | Yorkshire | 672 | 104 | 4.14 | 12.11 | Elland Road (plausible — no frames within 500m) |
| **Reading** | South East | 664 | 39 | 3.91 | 5.27 | Train station + Oracle shopping centre (0 MI frames near stadium) |
| **Southampton** | South East | 642 | 58 | 3.46 | 5.24 | St Mary's Stadium (plausible) |
| **Westminster** | London | 525 | 37 | 4.02 | 8.37 | West End / event district |
| **Stratford West Ham** | London | 497 | 100 | 3.54 | 6.50 | London Stadium ✅ (96 spiking frames, dense coverage) |
| **Brentford** | London | 474 | 5 | 4.78 | 10.29 | Brentford Community Stadium ✅ |
| **Bristol** | South West | 471 | 15 | 4.58 | 9.39 | Ashton Gate (likely) |
| **Blackpool** | North West | 469 | 23 | 3.55 | 4.98 | Seaside tourism / Pleasure Beach |
| **Sheffield** | Yorkshire | 373 | 33 | 3.88 | 9.73 | City centre (Bramall Lane 4km away — no nearby MI frames) |
| **Glasgow South** | Scotland | 361 | 23 | 4.62 | 8.54 | Hampden Park / Ibrox |
| **Newcastle** | North East | 333 | 21 | 3.72 | 6.13 | St James' Park (likely — nearest MI frame 687m) |
| **Middlesbrough** | North East | 298 | 27 | 4.70 | 13.00 | City centre (Riverside Stadium 955m away) |
| **Sunderland** | North East | 273 | 5 | 7.22 | **35.00** | Stadium of Light ✅ (Springsteen concert confirmed) |
| **Tottenham** | London | 276 | 2 | 6.02 | 8.90 | Tottenham Hotspur Stadium (likely — nearest MI frame 158m) |
| **Twickenham** | London | 262 | 11 | 5.05 | 9.20 | Twickenham Stadium (plausible — no frames within 500m) |

This is essentially a **map of Premier League grounds, transport hubs, and major event venues**. Stretford's 18 frames near Old Trafford show a 6.23 average spike index across 28 separate days — match day after match day. Note that some town-level spikes are driven by transport/retail rather than stadiums (Reading, Sheffield, Liverpool partly).

### Frames with Most Recurring Spikes

| Frame | Spikes | Days | Avg | Max | Town | Notes |
|-------|--------|------|-----|-----|------|-------|
| 1234935078/79 | 170 each | 27 | 7.08 | 13.37 | Unknown | Consistently high — near a major venue |
| 1234849484 | 152 | 14 | 4.61 | 7.32 | Norwich | Carrow Road area |
| 2000100053 | 140 | 24 | 5.91 | 8.56 | Liverpool | Near Anfield/Goodison |
| 1234859751/52 | 138 each | 28 | 6.02 | 8.90 | Tottenham | Near Spurs stadium |
| 1234855498+ (9 frames) | 132 each | 28 | 6.54 | 11.31 | Stretford | Old Trafford cluster |
| 2000102979/80 | 129 each | 26 | 5.85 | 9.45 | Holloway | Emirates Stadium area |

---

## 9. Most Affected Campaigns (by number of high-spike frames)

| Campaign | Brand | Owner | Total Frames | Spike Frames | Raw (000s) | Indexed (000s) | Uplift |
|----------|-------|-------|-------------|-------------|-----------|---------------|--------|
| 18531 | (unbranded) | Global | 3,627 | 474 | 15,836 | 15,901 | +0.4% |
| 18604 | (unbranded) | Global | 3,145 | 448 | 13,566 | 14,481 | +6.8% |
| 19038 | (unbranded) | Global | 2,775 | 326 | 2,144 | 2,371 | +10.6% |
| 19033 | McDonald's | Bauer | 2,163 | 322 | 2,961 | 3,176 | +7.3% |
| 17505 | Lotto | Bauer | 1,736 | 273 | 1,366 | 1,406 | +3.0% |
| 17827 | (unbranded) | Global | 1,451 | 228 | 29,839 | 30,694 | +2.9% |
| 16693 | Channel Four | JCDecaux | 1,886 | 227 | 2,217 | 2,443 | +10.2% |
| 18720 | Channel Four | JCDecaux | 204 | — | 18,728 | 24,057 | **+28.5%** |
| 17932 | (unbranded) | Bauer | 393 | 159 | 80,936 | 90,477 | **+11.8%** |
| 18409 | Waitrose | Bauer | 1,126 | 167 | 86,183 | 88,415 | +2.6% |

**Channel Four campaign 18720** stands out: 204 JCDecaux frames producing a **+28.5% uplift** — their frame portfolio appears disproportionately co-located with event venues.

---

## 10. Key Takeaways

1. **Mobile indexing produces a net +4.93% uplift** across all campaigns, driven by the correlation between high footfall periods and high audience volumes.

2. **73% of campaigns benefit**, with 44% seeing uplift of 5% or more. Only 7.2% see decreases larger than 5%.

3. **Event-driven traffic is clearly visible** — frames near football stadia (Old Trafford, Emirates, Spurs, Celtic Park, Stadium of Light) show index values up to 35x on event days.

4. **Saturday/Sunday account for 62% of all extreme spikes**, concentrated in the 18:00–23:00 event window.

5. **The geographic hotspot map aligns almost perfectly with Premier League grounds and major venues** — this is strong evidence that the mobile volume index captures real-world event footfall.

6. **Frame placement matters enormously** — campaigns with frames near event venues gain 10–30% uplift, while those in quiet suburban locations lose 10–20%. This has direct implications for media planning and frame valuation.

7. **The MI measures deviation from typical day-of-week behaviour.** The unweighted average index is exactly 1.0, but the audience-weighted average is 1.049. Off-peak hours have low index AND low audience — so they contribute little. Peak hours have high index AND high audience — so they dominate. The MI adds the most value where events are atypical for a location.

---

## 11. Venue Verification (March 2026)

Thirteen independent investigations cross-referenced MI spikes against real-world events across 22 UK stadiums, concert venues, and transport hubs.

### Playout Window Event Verification

**85% of the top 20 playout-window spike dates matched confirmed events** — Premier League GW1–7, Champions League/Europa League, Notting Hill Carnival (13.45x), Reading Festival, Billy Joel at Cardiff. Premier League drives 55% of spike-hours; cultural events drive 20%.

### Stadium OA Coverage Audit

All four major stadiums audited (Wembley, Emirates, Stamford Bridge, Etihad) have OOH frames within 200m but none carry MI data — stadiums lack retail/supermarket formats. Where adjacent OA data exists:
- **Emirates** — Holloway Rd frames show 70% match-day uplift (1.69x vs 0.98x baseline), max 9.45x
- **Stamford Bridge** — Fulham Broadway frames show 38% match-day uplift (1.34x vs 0.97x), max 3.47x
- **Etihad** — single MI frame (Asda Sport City, 404m), match-day avg 1.18x vs 0.84x, max 6.31x — treat with caution
- **Wembley** — anti-correlated: adjacent OAs show below-normal footfall on event days (displacement from road closures)

### MI Methodology

The MI measures deviation from typical day-of-week behaviour. At venues with frequent events, the MI correctly shows modest deviation because events are a normal part of the weekly pattern — Route's base audiences should already capture that footfall. At infrequent-event venues, the MI shows large deviation because events are atypical. If Route's audience models do not fully capture regular event footfall at high-frequency stadiums, that is a limitation of Route's data inputs, not the MI methodology.

Full venue verification research: `docs/Research/venue-verification/00-SUMMARY.md` (13 investigations)

---

*Research scripts: `scripts/research_event_peaks.py`, `scripts/research_overall_impact.py`, `scripts/research_playout_window_events.py`*
