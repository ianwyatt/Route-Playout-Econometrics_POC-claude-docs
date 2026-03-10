# Mobile Volume Index — Executive Summary & Key Findings

**Date:** 10 March 2026
**Data:** 99.87M frame-hours, 16,265 frames, 833 campaigns (~69 days, Aug–Sep 2025)

---

## Executive Summary

Mobile volume indexing adjusts OOH audience impacts by real mobile device footfall at each frame. Across 833 campaigns it produces a **net +4.93% uplift** in total impacts (mean index) or +2.41% (median). **73% of campaigns benefit**, with 44% gaining 5% or more. Only 7.2% see decreases larger than 5%.

The mechanism: although the unweighted average index across all 100M frame-hours is exactly 1.0, the audience-weighted average is **1.049**. High-footfall periods (peak commute, evenings, events) coincide with higher raw audience volumes, amplifying the effect when applied as a multiplier. Off-peak hours have low index AND low audience — so they contribute little to the weighted total.

Event-driven traffic is clearly visible. Frames near football stadia show index values up to **35x the national average** on match days. The geographic hotspot map reads like a list of Premier League grounds — Manchester, Cardiff, Holloway (Emirates), Tottenham, Stretford (Old Trafford), Liverpool, Leeds, Brentford, Twickenham. Saturday and Sunday account for 62% of all extreme spikes, concentrated in the 18:00–23:00 window.

Frame placement matters enormously. Channel Four's 204-frame JCDecaux campaign gained +28.5% from indexing — systematic co-location with event hotspots. Red Bull's single Ocean Outdoor frame lost 35% — consistently below-average footfall. The same budget delivers materially different real-world audiences depending on frame proximity to high-footfall locations.

---

## 1. Overall Impact

| Metric | Raw Impacts (000s) | Indexed (000s) | Change |
|---|---|---|---|
| **Mean Index** | 6,284,671 | 6,594,430 | **+4.93%** |
| **Median Index** | 6,284,671 | 6,436,317 | **+2.41%** |

- Unweighted average index across all 100M frame-hours = **exactly 1.000**
- Weighted average (by audience volume) = **1.049**
- Peak footfall hours carry disproportionately more audience → net positive

## 2. Campaign Distribution

| Bucket | Count | % |
|---|---|---|
| Large uplift (>10%) | 168 | 20.2% |
| Significant uplift (5–10%) | 199 | 23.9% |
| Moderate uplift (2–5%) | 162 | 19.5% |
| Small uplift (0–2%) | 81 | 9.7% |
| Small decrease (0 to -2%) | 73 | 8.8% |
| Moderate decrease (-2 to -5%) | 88 | 10.6% |
| Significant decrease (-5 to -10%) | 44 | 5.3% |
| Large decrease (<-10%) | 16 | 1.9% |

**610 campaigns (73.3%) positive, 221 (26.6%) negative.** Mean change +5.35%, median +4.10%.

## 3. Event-Driven Peaks — The Smoking Guns

The most extreme frame is in **Sunderland** — frame `1234860534` on 21 May 2025:

```
15:00  avg=  3.03  ██████
16:00  avg=  5.37  ██████████
17:00  avg= 10.93  █████████████████████
18:00  avg= 22.85  █████████████████████████████████████████████
19:00  avg= 27.11  ██████████████████████████████████████████████████████
20:00  avg= 29.34  ██████████████████████████████████████████████████████████
21:00  avg= 31.39  ██████████████████████████████████████████████████████████████
22:00  avg= 35.00  ██████████████████████████████████████████████████████████████████████
23:00  avg= 28.97  █████████████████████████████████████████████████████████
```

**35x the national average** at 10pm. A frame near the Stadium of Light — the ramp from 3x at 3pm to 35x at 10pm is textbook event ingress/event/egress. Three adjacent frames spike simultaneously, confirming a localised event rather than data noise.

### Geographic Hotspots (index > 3x)

| Town | Spikes | Frames | Max Index | Likely Venue |
|---|---|---|---|---|
| **Manchester** | 3,932 | 86 | 6.90 | Old Trafford / Etihad |
| **Cardiff** | 2,718 | 102 | 9.82 | Principality Stadium |
| **Birmingham** | 1,385 | 192 | 8.42 | Villa Park / NEC |
| **Stretford** | 1,345 | 18 | 11.31 | Old Trafford (adjacent) |
| **Glasgow North** | 993 | 49 | 18.60 | Celtic Park / Ibrox area |
| **Holloway** | 902 | 10 | 9.45 | Emirates Stadium |
| **Liverpool** | 851 | 79 | 8.56 | Anfield / Goodison |
| **Leeds** | 672 | 104 | 12.11 | Elland Road |
| **Brentford** | 474 | 5 | 10.29 | Brentford Community Stadium |
| **Tottenham** | 276 | 2 | 8.90 | Tottenham Hotspur Stadium |
| **Twickenham** | 262 | 11 | 9.20 | Twickenham Stadium |
| **Sunderland** | 273 | 5 | **35.00** | Stadium of Light |

Essentially a **map of Premier League grounds and major event venues**. Stretford's 18 frames near Old Trafford show 6.54 avg spike index across 28 separate days — match day after match day.

### Temporal Patterns

- **Saturday** dominates: 10,016 spikes (36.5%)
- **Sunday** second: 7,077 (25.8%)
- Peak hours: **19:00–22:00** (the match/event window)
- Overnight 0–4am shows elevated flat spikes (420 frames) — post-event dispersal

**Top spike dates:**

| Date | Day | Spikes | Max Index | Context |
|---|---|---|---|---|
| 26 Oct | Sun | 735 | 7.19 | Premier League fixtures |
| 29 Nov | Sat | 722 | 6.12 | Football Saturday |
| 4 May | Sun | 576 | 6.99 | Bank Holiday / end of season |
| 1 Nov | Sat | 561 | 7.36 | Football Saturday |
| 8 Aug | Fri | 464 | 9.70 | Opening weekend of season |
| 25 Aug | Mon | 356 | 13.45 | **Bank Holiday Monday** |

## 4. Most Affected Campaigns

Campaigns with the most high-spike frames — predictably the large national ones:

| Campaign | Brand | Spike Frames | Uplift |
|---|---|---|---|
| 18531 | (unbranded, Global) | 474 | +0.4% |
| 18604 | (unbranded, Global) | 448 | +6.8% |
| 19033 | **McDonald's** | 322 | +7.3% |
| 17827 | (unbranded, Global) | 228 | +2.9% |
| 16693 | **Channel Four** | 227 | +10.2% |
| 17932 | (unbranded, Bauer) | 159 | **+11.8%** |
| **18720** | **Channel Four** | 204 | **+28.5%** |
| 18409 | **Waitrose** | 167 | +2.6% |

Channel Four campaign 18720 — 204 frames with +28.5% uplift. Their frames are disproportionately located near event hotspots.

## 5. Biggest Losers

| Campaign | Brand | Frames | Change |
|---|---|---|---|
| 18970 | Red Bull | 1 | **-35.3%** |
| 19198 | (unbranded) | 53 | -24.2% |
| 16014 | Lipton | 1 | -23.5% |
| 18550 | (unbranded) | 127 | -19.6% |
| 17427 | McDonald's | 57 | -17.6% |
| 18782 | (unbranded) | 986 | -11.5% |

Red Bull's single frame sits in a location with consistently below-average footfall. The large-decrease campaigns tend to have frames in quieter suburban, off-peak locations.

---

## Key Takeaways

1. **+4.93% net uplift** across all campaigns — mobile indexing captures real-world footfall that Route's standard model misses.

2. **73% of campaigns benefit.** The effect is broadly positive, not a zero-sum redistribution.

3. **Event traffic is unmistakably visible** — the geographic hotspot map aligns with Premier League grounds and major venues. This is strong evidence the index captures genuine real-world footfall.

4. **Frame placement drives the variance.** Campaigns near event venues gain 10–30%; those in quiet locations lose 10–20%. Direct implications for media planning and frame valuation.

5. **The paradox resolved:** Unweighted average = 1.0, but audience-weighted average = 1.049. Off-peak hours (low index, low audience) contribute little. Peak hours (high index, high audience) dominate.

---

*Full detailed analysis: `MOBILE_INDEX_RESEARCH_FINDINGS.md`*
*Research scripts: `scripts/research_event_peaks.py`, `scripts/research_overall_impact.py`*
