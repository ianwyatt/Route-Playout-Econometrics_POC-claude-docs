# Briefing Document Update — Session Prompt

**Date:** 10 March 2026
**Purpose:** Update board and econometrician briefing documents with findings from the venue verification research session.

---

## What Happened

A research session completed the following investigations against the local PostgreSQL database (`route_poc`), cross-referencing mobile index (MI) data with real-world events:

1. **Playout window event verification** — cross-referenced the top 20 MI spike dates (7 Aug – 14 Oct 2024) against confirmed football fixtures, concerts, and cultural events. Result: **85% match rate** (17/20 dates have confirmed events).

2. **Stadium OA audit** — investigated why Wembley Stadium produces no MI spikes despite hosting 85,000-capacity events. Extended audit to Emirates, Stamford Bridge, and Etihad. Found a **systemic OA coverage gap** at all four major stadiums.

3. **Critical reframe of MI methodology** — corrected the narrative from "MI is broken at busy venues" to "MI correctly measures deviation from typical day-of-week patterns, consistent with how Route models audience."

---

## Updated Source Files (READ THESE FIRST)

The following research documents have been updated with all findings. They are the source of truth:

| File | What's In It |
|------|-------------|
| `docs/Research/venue-verification/13-playout-window-events.md` | **UPDATED** — Full playout window event verification. Date-by-date annotations for all 20 spike dates, Stretford/Cardiff venue verifications, Wembley Paradox investigation, stadium OA audit (all 4 venues), reframed MI methodology narrative |
| `docs/Research/venue-verification/00-SUMMARY.md` | **UPDATED** — Executive summary of all 13 investigations. Key findings, venue confidence table (with OA gap classifications), recommendations reframed around MI measuring deviation from typical patterns |
| `docs/Research/venue-verification/FOLLOW_UP_RESEARCH_BRIEF.md` | **UPDATED** — Index construction section reframed (removed "baseline contamination" language) |
| `docs/Research/venue-verification/PLAYOUT_WINDOW_RESEARCH_BRIEF.md` | **UPDATED** — Same reframe applied |
| `docs/Research/football-fixtures-aug-oct-2024.md` | Reference — PL GW1-7, Carabao Cup, Champions League, Europa League fixtures |
| `docs/Documentation/MOBILE_INDEX_SQL_AUDIT.md` | Unchanged — MI SQL construction audit |

---

## Documents to Update

### 1. Board Briefing: `docs/Documentation/BRIEF_BOARD_MI_OVERVIEW.md`

Incorporate:
- **85% event match rate** for the playout window — this is the headline validation number
- The MI is validated: spikes correspond to real Premier League fixtures, concerts (Billy Joel at Principality Stadium), cultural events (Notting Hill Carnival, Reading Festival)
- **Saturday Premier League dominates** — 55% of spike-hours, consistent with 3pm kickoff patterns
- **Stadium OA coverage gap** — simplified for board audience. All four major stadiums (Wembley, Emirates, Stamford Bridge, Etihad) lack MI data in their immediate area. This is a data availability limitation of the O2 source data, not a methodology flaw
- **The MI measures deviation from typical patterns** — this is consistent with how Route models audience. Where events are routine (Wembley every Saturday), the MI correctly shows no deviation because Route's base audiences already reflect that footfall. Where events are unusual (Sunderland concert, Cardiff one-off), the MI correctly flags large deviations
- Remove or soften any "baseline contamination" or "normalisation bias" language — the correct framing is that the MI is working as designed

### 2. Econometrician Briefing: `docs/Documentation/BRIEF_ECONOMETRICIAN_MI_CAMPAIGNS.md`

Incorporate:
- **Full technical detail** on the stadium OA audit — the econometrician needs to know which venues have reliable MI event signal and which don't:
  - Emirates: 70% match-day uplift on Holloway Rd frames (best of the four)
  - Stamford Bridge: 38% uplift on Fulham Broadway frames
  - Etihad: single MI frame (Asda Sport City, 404m) — treat with caution
  - Wembley: anti-correlated (displacement from road closures)
- **MI measures deviation from typical day-of-week behaviour** — the econometrician should understand that a 1.0x index on a match day means match days are typical for that OA, and Route's audience model should already capture that footfall. The MI adds value where events are atypical
- **If Route's models don't capture regular event footfall**, that's a limitation of Route's data inputs, not the MI methodology. This is an important distinction for econometric modelling
- **The MI is most valuable at infrequent-use venues** — Sunderland (35x for Springsteen), Cardiff (7x for Billy Joel), festival sites, Championship grounds. Less valuable at Wembley, Emirates, central London
- **Displacement effect** at Wembley — adjacent OAs show below-normal footfall on event days due to road closures. This is a real physical effect that may slightly reduce indexed impacts for campaigns with frames in surrounding areas
- **Playout window coverage**: campaigns cluster in Sep-Oct, missing early-August events (PL GW1, Notting Hill Carnival). The Aug events are documented in the research but don't directly appear in campaign datasets

### 3. Executive Summary: `docs/Documentation/MOBILE_INDEX_EXEC_SUMMARY.md`

Incorporate:
- Update validation section with the 85% match rate
- Add the stadium OA coverage finding as a known limitation
- Reframe any "bias" or "contamination" language to "working as designed"

### 4. Research Findings: `docs/Documentation/MOBILE_INDEX_RESEARCH_FINDINGS.md`

Incorporate:
- Add Investigation 13 findings (playout window event verification)
- Add the stadium OA audit results
- Ensure narrative consistency with the reframed methodology understanding

---

## Key Narrative Points

### The Route Data Limitation (Most Important Insight)

The MI research surfaced a question that goes beyond the MI itself: **do Route's audience models accurately capture regular event footfall at high-frequency venues?**

The MI correctly shows "no deviation" at Wembley on match days because matches are typical Saturday behaviour there. But this only works if Route's base audiences for Wembley-area frames already reflect match-day footfall levels. If Route's data inputs (pedestrian surveys, traffic counts, etc.) underestimate footfall at stadiums during regular events, then:
- Route's base audiences are too low at these venues
- The MI correctly shows no additional deviation
- The result is **both** Route and MI understate the true audience — but the gap is in Route's model, not the MI

This is a critical insight for the econometrician and potentially for the board. It positions the MI work as having uncovered a broader question about Route's audience accuracy at event venues, not just a limitation of the MI data.

### Framing

**DO use:**
- "The MI measures deviation from typical day-of-week behaviour"
- "Route models average behaviour — if events are typical at a venue, Route's audiences already capture that footfall"
- "The MI adds the most value where events are atypical for a location"
- "OA coverage gap" (for the missing stadium data)
- "Working as designed" (for the normalisation behaviour)
- "If Route's models don't fully capture regular event footfall, that is a limitation of Route's data inputs" — this is a key finding, not a throwaway caveat

**DO NOT use:**
- ~~"Baseline contamination"~~ — this implies the data is flawed
- ~~"Normalisation bias"~~ or ~~"normalisation trap"~~ — same issue
- ~~"Understated" or "suppressed" spikes~~ — the MI is correctly measuring deviation, not absolute uplift
- ~~"The MI is broken at busy venues"~~ — it's working correctly; the question is whether Route captures typical behaviour

---

## Important Context

- British English spelling throughout
- The data model: O2 mobile data (2024) overlaid on ad playouts (2025) via day-of-week preserved date mapping
- Playout window: 7 Aug – 14 Oct 2024 (69 days) = 6 Aug – 13 Oct 2025 playouts
- National MI coverage: 3.8% (14,639 of 387,165 frames), biased toward supermarket/shopping centre formats
- The research is complete — this is a documentation/presentation task, not further investigation
