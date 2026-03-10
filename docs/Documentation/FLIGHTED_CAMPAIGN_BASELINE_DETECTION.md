# Flighted Campaign Analysis: Baseline Detection for MMM

**Date**: 10 February 2026
**Context**: Investigating whether OOH playout data contains the "off" periods econometric models need to establish advertising baselines.

---

## Background

Marketing Mix Models need periods with no advertising activity to establish a **baseline** — the level of sales that would occur without advertising. Without these "off" periods, the model can't cleanly measure OOH's true effect.

The question: **do our campaigns have enough gaps between waves of spend to give models the contrast they need?**

Source: Econometric baseline detection guidance (Q1 in the "questions to ask your econometrician" framework).

---

## Findings

### Summary

Out of **836 campaigns** in the POC dataset (69 days, Aug–Oct 2025):

- **30 campaigns** have at least one gap of **7+ days** with no playout activity
- **~10%** of campaigns show a flighted (on/off/on) scheduling pattern
- Gap lengths range from **7 to 29 days** — well within the range econometricians need for baseline estimation
- Several campaigns show **multiple gaps**, creating the pulsed spend pattern MMM models work best with

**This is a positive finding**: there IS sufficient variation in OOH scheduling to support baseline detection in econometric models.

---

## Best Examples

### Rockstar (`16026`) — Three-wave flighting

The textbook example from our dataset. Three distinct waves with two clear gaps.

| Period | Dates | Duration | Daily Impacts | Notes |
|--------|-------|----------|---------------|-------|
| Wave 1 | Aug 13–24 | 12 days | ~800/day peak | Ramp up |
| Gap 1 | Aug 24 – Sep 7 | **14 days** | Zero | |
| Wave 2 | Sep 7–21 | 15 days | ~600–825/day | Consistent |
| Gap 2 | Sep 21 – Oct 3 | **12 days** | Zero | |
| Wave 3 | Oct 3–13 | 11 days | ~735–807/day | Trailing off |

- **Media owners**: Bauer, Global, JCDecaux, Ocean
- **Total playouts**: 9.95M
- **Pattern**: Classic three-wave pulse. Weekday peaks and weekend dips visible within each wave.

### The AA (`17144`) — Declining second wave

Two waves with a 21-day gap. The second wave runs at roughly 65% of the first wave's intensity.

| Period | Dates | Duration | Daily Impacts |
|--------|-------|----------|---------------|
| Wave 1 | Aug 18–24 | 7 days | ~1,200/day peak |
| Gap | Aug 24 – Sep 14 | **21 days** | Zero |
| Wave 2 | Sep 14–28 | 15 days | ~808/day peak |

- **Media owners**: Global, JCDecaux
- **Total playouts**: 1.98M
- **Pattern**: Reduced intensity in second wave — budget reallocation or campaign tapering.

### Specsavers (`16913`) — Longest gap

Two waves separated by the longest gap in the dataset.

| Period | Dates | Duration | Daily Impacts |
|--------|-------|----------|---------------|
| Wave 1 | Aug 11–24 | 14 days | ~90–103/day |
| Gap | Aug 24 – Sep 22 | **29 days** | Zero |
| Wave 2 | Sep 22 – Oct 5 | 14 days | ~92–120/day |

- **Media owner**: Bauer Media Outdoor
- **Total playouts**: 790K
- **Pattern**: Two-burst flighting with nearly a month between waves. Likely seasonal promotion timing.

### London HIV Prevention Programme (`18139`) — Escalating second wave

Two waves with a 20-day gap. Unlike most flighted campaigns, the second wave *builds* in intensity.

| Period | Dates | Duration | Daily Impacts |
|--------|-------|----------|---------------|
| Wave 1 | Aug 17–24 | 8 days | ~189/day peak |
| Gap | Aug 24 – Sep 13 | **20 days** | Zero |
| Wave 2 | Sep 13 – Oct 5 | 23 days | Starts ~28, builds to ~82/day |

- **Media owners**: Global, JCDecaux
- **Total playouts**: 757K
- **Pattern**: Second wave is longer and escalates — a sustained awareness campaign rather than a burst.

### British Airways (`17979`) — Most pulsed

The most fragmented pattern in the dataset — 5 separate gaps creating scattered bursts of activity.

- **Media owners**: Bauer, Global, JCDecaux
- **Gap pattern**: 4–8 day gaps between each burst
- **Pattern**: Individual days or short runs of activity separated by gaps. Highly pulsed scheduling.

---

## Other Flighted Campaigns

| Campaign | Brand | Max Gap | Gaps | Media Owners |
|----------|-------|---------|------|-------------|
| `15215` | (not provided) | 22 days | 2 | Ocean |
| `17509` | Scottish & Southern Energy | 21 days | 2 | Global, JCDecaux |
| `18851` | The Economist | 18 days | 1 | JCDecaux |
| `B-00031368` | Jaguar | 16 days | 2 | JCDecaux |
| `18693` | comparethemarket.com | 16 days | 1 | Bauer, Global, JCDecaux |
| `17595` | The People's Pension | 15 days | 2 | Bauer, Global, JCDecaux, Ocean |

---

## Implications for MMM

### Positive
1. **Baseline detection is viable** — ~10% of campaigns have clear on/off patterns with gaps of 7–29 days
2. **Multi-wave campaigns exist** — Rockstar, Jaguar, People's Pension all show 2–3 distinct waves, giving models multiple baseline measurement opportunities
3. **Varying gap lengths** — from 7 to 29 days, providing different baseline windows for different model sensitivities
4. **Cross-media-owner coverage** — flighted campaigns appear across Global, JCDecaux, Bauer, and Ocean inventory

### Limitations
1. **69-day window** — our POC covers Aug–Oct 2025 only. Longer history would reveal more flighting patterns, especially seasonal campaigns
2. **Single buyer** — the dataset comes from one specialist buyer. Other buyers may have different scheduling patterns
3. **Route reach limitation** — flighted campaigns are the ~10% where Route can't calculate total campaign reach/GRPs (the gap breaks the weekly continuity the reach model needs). The new Route will resolve this.

### Recommendation for Econometricians
- **Use impacts as the primary metric** for flighted campaigns — always accurate regardless of gaps
- **Weekly impacts by demographic** is the most useful granularity for MMM
- **The gaps are the feature, not the bug** — they provide the contrast the model needs

---

## Query Used

Campaigns were identified by finding gaps of 3+ consecutive days with no records in `mv_cache_campaign_impacts_day`, then filtering to gaps of 7+ days and campaigns with 10,000+ total playouts.

---

*Last Updated: 10 February 2026*
