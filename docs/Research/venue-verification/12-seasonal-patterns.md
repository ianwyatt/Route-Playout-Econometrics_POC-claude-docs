---
title: Seasonal Patterns in Mobile Volume Index — Non-Venue Frames
date: 2026-03-10
---

# Seasonal Patterns in Mobile Volume Index — Non-Venue Frames

This report analyses whether mobile index spikes in frames located >2 km from all 22 major sports/event venues correlate with seasons or are purely event-driven. Because `average_index` is normalised per-frame (each frame's mean across all dates and hours = 1.0), we measure spike **frequency** (% of frame-hours exceeding fixed thresholds) rather than raw averages.

## Non-Venue Frame Identification

Frames with `average_index > 5.0` at some point and located >2 km from all 22 venues:

- **234 non-venue high-spike frames** identified

## Monthly Spike Frequency (Non-Venue Frames)

| Month | Total Hours | >1.5 | >2.0 | >3.0 | >5.0 | % >2.0 | % >3.0 |
|-------|-------------|------|------|------|------|--------|--------|
|   Apr |     168,480 | 8,308 |  597 |  247 |   49 |   0.35% |   0.15% |
|   May |     174,096 | 11,334 |  509 |  280 |  108 |   0.29% |   0.16% |
|   Jun |     168,480 | 4,414 |  649 |  309 |  120 |   0.39% |   0.18% |
|   Jul |     174,096 | 7,878 | 1,754 |  957 |  484 |   1.01% |   0.55% |
|   Aug |     174,096 | 2,559 | 1,156 |  672 |  202 |   0.66% |   0.39% |
|   Sep |     168,480 | 11,505 |  448 |  193 |   70 |   0.27% |   0.11% |
|   Oct |     174,096 | 14,407 |  605 |  240 |   69 |   0.35% |   0.14% |
|   Nov |     168,480 | 16,243 |  503 |  148 |   51 |   0.30% |   0.09% |
|   Dec |     157,248 | 14,619 | 1,127 |  395 |  175 |   0.72% |   0.25% |

## Day-of-Week Spike Frequency (Non-Venue Frames)

| Day  | Total Hours | >2.0 | >3.0 | % >2.0 | % >3.0 |
|------|-------------|------|------|--------|--------|
|  Sun |     213,408 | 1,608 |  782 |   0.75% |   0.37% |
|  Mon |     224,640 |  303 |  163 |   0.13% |   0.07% |
|  Tue |     224,640 |  708 |  414 |   0.32% |   0.18% |
|  Wed |     219,024 |  374 |  149 |   0.17% |   0.07% |
|  Thu |     219,024 |  468 |  179 |   0.21% |   0.08% |
|  Fri |     213,408 | 1,107 |  530 |   0.52% |   0.25% |
|  Sat |     213,408 | 2,780 | 1,224 |   1.30% |   0.57% |

## Month × Day-of-Week Heatmap — % Frame-Hours Above 3.0 (Non-Venue Frames)

| Month  |    Sun |    Mon |    Tue |    Wed |    Thu |    Fri |    Sat |
|--------|--------|--------|--------|--------|--------|--------|--------|
|   Apr  |  0.11% |  0.06% |  0.07% |  0.12% |  0.03% |  0.31% |  0.37% |
|   May  |  0.26% |  0.08% |  0.08% |  0.00% |  0.04% |  0.10% |  0.66% |
|   Jun  |  0.31% |  0.03% |  0.07% |  0.09% |  0.12% |  0.16% |  0.41% |
|   Jul  |  1.02% |  0.02% |  0.08% |  0.14% |  0.25% |  0.89% |  1.80% |
|   Aug  |  0.71% |  0.42% |  0.09% |  0.04% |  0.12% |  0.38% |  0.88% |
|   Sep  |  0.24% |  0.04% |  0.09% |  0.02% |  0.02% |  0.16% |  0.22% |
|   Oct  |  0.44% |  0.02% |  0.10% |  0.02% |  0.04% |  0.09% |  0.33% |
|   Nov  |  0.12% |  0.00% |  0.14% |  0.12% |  0.00% |  0.03% |  0.20% |
|   Dec  |  0.15% |  0.02% |  0.85% |  0.08% |  0.13% |  0.15% |  0.26% |

## Seasonal Hourly Profiles — % Frame-Hours Above 2.0 (Non-Venue Frames)

Note: seasons are defined on date_2024. Spring = Mar–May, Summer = Jun–Aug, Autumn = Sep–Nov, Winter = Dec.

| Hour |   Spring |   Summer |   Autumn |   Winter |
|------|----------|----------|----------|----------|
|  0:00 |   0.02%  |   0.35%  |   0.09%  |   0.08%  |
|  1:00 |   0.02%  |   0.35%  |   0.09%  |   0.08%  |
|  2:00 |   0.02%  |   0.35%  |   0.09%  |   0.08%  |
|  3:00 |   0.02%  |   0.35%  |   0.09%  |   0.08%  |
|  4:00 |   0.02%  |   0.35%  |   0.09%  |   0.08%  |
|  5:00 |   0.00%  |   0.15%  |   0.01%  |   0.00%  |
|  6:00 |   0.03%  |   0.15%  |   0.02%  |   0.00%  |
|  7:00 |   0.04%  |   0.20%  |   0.04%  |   0.00%  |
|  8:00 |   0.11%  |   0.23%  |   0.07%  |   0.00%  |
|  9:00 |   0.13%  |   0.26%  |   0.13%  |   0.00%  |
| 10:00 |   0.20%  |   0.31%  |   0.16%  |   0.00%  |
| 11:00 |   0.32%  |   0.44%  |   0.22%  |   0.06%  |
| 12:00 |   0.36%  |   0.53%  |   0.20%  |   0.06%  |
| 13:00 |   0.48%  |   0.72%  |   0.27%  |   0.18%  |
| 14:00 |   0.57%  |   0.85%  |   0.46%  |   0.43%  |
| 15:00 |   0.64%  |   0.89%  |   0.54%  |   0.49%  |
| 16:00 |   0.71%  |   1.07%  |   0.60%  |   0.73%  |
| 17:00 |   0.74%  |   1.41%  |   0.77%  |   0.99%  |
| 18:00 |   0.60%  |   1.32%  |   0.54%  |   1.30%  |
| 19:00 |   0.55%  |   1.33%  |   0.63%  |   2.24%  |
| 20:00 |   0.55%  |   1.41%  |   0.70%  |   1.53%  |
| 21:00 |   0.64%  |   1.39%  |   0.68%  |   2.17%  |
| 22:00 |   0.67%  |   1.25%  |   0.54%  |   3.13%  |
| 23:00 |   0.33%  |   0.88%  |   0.22%  |   3.51%  |

## Weekend vs Weekday Comparison by Month — % Frame-Hours Above 2.0 (Non-Venue Frames)

| Month | Weekday % >2.0 | Weekend % >2.0 | Weekend Premium (pp) |
|-------|----------------|----------------|----------------------|
|   Apr |           0.19% |           0.82% |                +0.63pp |
|   May |           0.11% |           0.81% |                +0.70pp |
|   Jun |           0.19% |           0.78% |                +0.59pp |
|   Jul |           0.49% |           2.48% |                +1.99pp |
|   Aug |           0.36% |           1.40% |                +1.04pp |
|   Sep |           0.11% |           0.63% |                +0.52pp |
|   Oct |           0.14% |           0.96% |                +0.82pp |
|   Nov |           0.17% |           0.60% |                +0.43pp |
|   Dec |           0.66% |           0.88% |                +0.22pp |

## Assessment: Seasonal Footfall Variation vs Event-Driven Spikes

**Non-venue frames analysed:** 234

### Spike Frequency Variability Across Months

- % above 2.0 — mean: 0.48%, SD: 0.26%, CV: 53.2%, range: 0.27–1.01%
- % above 3.0 — mean: 0.22%, SD: 0.15%, CV: 67.4%

### Interpretation

**Strong** seasonal variation detected (CV of monthly spike frequency: 53.2%).

The `average_index` is normalised per-frame (each frame's grand mean = 1.0), so comparing raw averages across months is uninformative — they all converge to ~1.0. Spike *frequency* (% of frame-hours exceeding fixed thresholds) is the correct metric because it captures the shape of the distribution independently of the mean.

If seasonal variation is strong (high CV), the mobile index is picking up genuine footfall seasonality (e.g. summer leisure, Christmas retail). If variation is weak, spikes are sporadic and likely tied to one-off events even at non-venue locations (markets, festivals, local events).

---
*Report generated by `scripts/research_seasonal_patterns.py`*
