# Session Handover: Venue Research & MI Methodology Reframe

**Date:** 11 March 2026
**Branch:** `feature/mobile-volume-index` (docs repo changes only — no code changes)

---

## What Was Done

### 1. Playout Window Event Verification (Investigation 13)

Cross-referenced top 20 MI spike dates (7 Aug – 14 Oct 2024) against confirmed real-world events using database queries and web-searched fixture data.

**Result:** 85% match rate (17/20 dates have confirmed events)
- 55% Premier League (GW1-GW7, 8 simultaneous home matches on Saturdays)
- 20% cultural events (Notting Hill Carnival, Reading Festival, Billy Joel at Cardiff)
- 15% non-event retail/leisure (international break weekends)
- 10% unexplained

Output: `docs/Research/venue-verification/13-playout-window-events.md`

### 2. Wembley Paradox Investigation

Investigated why Wembley Stadium produces no MI spikes despite 85,000-capacity events. Found:
- **Primary cause: OA data gap** — only 1 OOH frame within 300m (Wembley Car Park), and it has NO MI data
- 34 MI frames within 1.5km are spread across 13 different Output Areas, none containing the stadium
- Adjacent OAs show **anti-correlation** (below-normal footfall on event days) — displacement from road closures

### 3. Stadium OA Audit (Emirates, Stamford Bridge, Etihad)

Extended the Wembley investigation to three other major PL stadiums. All four show the same pattern:

| Venue | Nearest OOH Frame | Has MI? | Nearest MI Frame | Match-Day Uplift |
|-------|:-----------------:|:-------:|:-----------------:|:----------------:|
| Wembley | 225m | No | 520m | -8% (anti-correlated) |
| Etihad | 163m | No | 404m (1 frame only) | ~40% |
| Emirates | 173m | No | 378m | ~70% |
| Stamford Bridge | 178m | No | 243m | ~38% |

**Systemic finding:** Stadiums are purpose-built zones without the retail/supermarket OOH formats that dominate MI coverage (national coverage 3.8%, biased to supermarket formats).

### 4. MI Methodology Reframe (Most Important)

Doctor Biz corrected a fundamental misunderstanding in our research narrative:

**Before:** "The MI has a normalisation bias — busy venues produce suppressed/understated spikes. Baseline contamination from event days inflates the denominator."

**After:** "The MI correctly measures deviation from typical day-of-week behaviour. Route models average behaviour, so if events are typical at a venue, Route's audiences already capture that footfall. The MI adds value where events are atypical. If Route's models don't capture regular event footfall, that's a limitation of Route's data inputs, not the MI."

This reframe was applied across all research documents and briefs:
- `13-playout-window-events.md` — normalisation section rewritten
- `00-SUMMARY.md` — key finding #7, recommendation #6, venue confidence table
- `FOLLOW_UP_RESEARCH_BRIEF.md` — removed "baseline contamination" language
- `PLAYOUT_WINDOW_RESEARCH_BRIEF.md` — same treatment

### 5. Briefing Update Prompt

Created `docs/Documentation/2026-03-10_MI_VENUE_RESEARCH_BRIEFING_UPDATE_PROMPT.md` — a self-contained prompt for a separate session to update the board and econometrician briefing documents with all findings from this research.

---

## Files Modified

| File | Changes |
|------|---------|
| `docs/Research/venue-verification/13-playout-window-events.md` | Created, then updated with stadium OA audit + MI reframe |
| `docs/Research/venue-verification/00-SUMMARY.md` | Updated with Investigation 13, stadium audit, MI reframe |
| `docs/Research/venue-verification/FOLLOW_UP_RESEARCH_BRIEF.md` | Reframed MI methodology narrative |
| `docs/Research/venue-verification/PLAYOUT_WINDOW_RESEARCH_BRIEF.md` | Reframed MI methodology narrative |
| `docs/Documentation/2026-03-10_MI_VENUE_RESEARCH_BRIEFING_UPDATE_PROMPT.md` | Created — prompt for briefing doc update session |
| `todo/upcoming_tasks.md` | Updated venue research section with round 2 findings |

---

## What Needs Doing Next

1. **Update briefing documents** — use `docs/Documentation/2026-03-10_MI_VENUE_RESEARCH_BRIEFING_UPDATE_PROMPT.md` in a separate session to update:
   - `docs/Documentation/BRIEF_BOARD_MI_OVERVIEW.md`
   - `docs/Documentation/BRIEF_ECONOMETRICIAN_MI_CAMPAIGNS.md`
   - `docs/Documentation/MOBILE_INDEX_EXEC_SUMMARY.md`
   - `docs/Documentation/MOBILE_INDEX_RESEARCH_FINDINGS.md`

2. **No code changes were made** — all work was documentation/research only

---

## Key Insight to Carry Forward

The MI measures **deviation from typical day-of-week patterns**. This is by design and consistent with how Route models audience. The critical question for the econometrician is: **do Route's base audience models fully capture regular event footfall at high-frequency venues?** If they don't, that's a Route data inputs limitation — and the MI research has surfaced it.
