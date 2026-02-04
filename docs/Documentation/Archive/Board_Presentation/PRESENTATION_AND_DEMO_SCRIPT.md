# Board Presentation + Demo Script
**Date:** December 4th, 2025 (Morning)
**Duration:** ~15-20 minutes total (10 min presentation + 5-10 min demo)

**PowerPoint**: `Route - Playout POC Update - Board Version - 20251127.pptx`

---

# PART 1: PRESENTATION (7 Slides)

---

## Slide 1: TITLE
**Route POC Progress Update**

**Script:**
> "This project is about improving how OOH is used in Marketing Mix Models. The ask: can we match playout data with Route audiences, and build a tool for econometricians to access it? Here's where we are."

*[Move to next slide]*

---

## Slide 2: EXECUTIVE SUMMARY (~2 min)

**Key Numbers to Highlight:**
- 11+ Billion playout records accessed (data back to 2024)
- 1.2 Billion records in POC build (69 days Aug-Oct 2025)
- 836 campaigns analysed (single buyer, multiple media owners)

**Script:**
> "This slide gives you the scale of what we've been working with.
>
> We've accessed over 11 billion playout records going back to 2024. For this POC, we focused on 69 days of data - August through mid-October this year - which gave us 1.2 billion records to work with.
>
> That translated into 836 unique campaigns from a single buyer across multiple media owners.
>
> On the right, you'll see three key challenges we've identified - data history limitations, digital-only coverage, and data quality issues. I'll dive into the data quality findings shortly."

---

## Slide 3: WHAT WE'VE DONE (~2 min)

**Key Points:**
- 1.28B raw records → 416M audience records (7 demographics)
- 91,000 Route API calls, 23 hours processing
- Front End UI: Campaign Browser, Frame-Level Analysis, Export to CSV

**Script:**
> "Here's what we built.
>
> On the data processing side, we took 1.28 billion raw playout records and converted them to 416 million audience records across 7 demographic segments.
>
> This required 91,000 calls to the Route API and about 23 hours of processing time. The pipeline converts millisecond-level playout timestamps into Route's 15-minute time slots.
>
> On the front end, we've built an interactive campaign browser that lets you analyse any campaign's playout audiences. You can drill down to frame-level detail by hour and day, and export everything to CSV for MMM integration.
>
> I'll show you this in the demo."

---

## Slide 4: DATA CHALLENGES - CAMPAIGN IDs (~2 min)

**Key Stats:**
- 97.75% valid by playout VOLUME (1.25B of 1.28B)
- 26.5% invalid by unique ID (222 of 837 campaign IDs)

**Script:**
> "Now to the data quality findings. This is important.
>
> When we look at campaign IDs, there's a tale of two metrics.
>
> By playout volume, 97.75% of records have valid campaign IDs - that's good news for the bulk of the data.
>
> But by unique campaign ID, 26.5% - over a quarter - have issues. That's 222 out of 837 campaigns.
>
> The examples on the right show what we're dealing with: 16 million playouts with NULL or 'No Data' values, 2.7 million with multiple IDs concatenated in a single field, and my personal favourite - 234,000 playouts where someone typed 'WILL BE ADDED NEXT WEEK' as the campaign ID.
>
> The root cause is clear: campaign IDs aren't validated at entry in the playout systems."

---

## Slide 5: DATA CHALLENGES - BRAND ATTRIBUTION (~1.5 min)

**Key Stats:**
- 42% fully branded
- 22% mixed attribution
- 35% no brand data
- 57.6% cannot be fully attributed to a brand

**Script:**
> "Brand attribution tells a similar story.
>
> Only 42% of campaigns have complete brand data. 22% have mixed attribution - some playouts have brands, others don't. And 35% have no brand data at all.
>
> That means 57.6% of campaigns cannot be fully attributed to a brand.
>
> The most common value in the brand field is 'not provided at point of trade' - meaning the brand was unknown when the ad was booked.
>
> For MMM, this matters. Without brand data, we can't measure effectiveness at brand level."

---

## Slide 6: DATA CHALLENGES - CAMPAIGN REACH & GRPs (~2 min)

**Key Points:**
- Flighted campaigns (on/off patterns) break Route's reach model
- Affects ~10% of campaigns
- Impacts still work; daily/weekly reach still works
- *Technical note: API size limits (10MB) mean large campaigns use 1hr segments instead of 15min for reach (~1-2% variance). Very large campaigns may not run at all.*

**Script:**
> "The final challenge is technical: Route's reach model and flighted campaigns.
>
> Route calculates reach based on frame exposure patterns within a week. When a campaign runs on-and-off with breaks between weeks, that model doesn't work properly.
>
> This affects about 10% of campaigns in our sample.
>
> But here's what still works: Impacts are always accurate - total audience impressions are fine. And we can calculate reach for individual days or weeks when the campaign was continuously running.
>
> One technical footnote: for very large campaigns, API size limits mean we use hourly rather than 15-minute segments for reach - adds about 1-2% variance. Some extremely large campaigns can't run at all.
>
> Our recommendation for MMM: use impacts as your primary metric. Only use reach and frequency for continuous periods or single weeks."

---

## Slide 7: THANK YOU

**Script:**
> "That's the presentation. Before we wrap up, let me show you the tool in action."

*[Transition to demo]*

---

# PART 2: LIVE DEMO (~5-10 min)

## Demo Setup
- Browser open at http://localhost:8504
- Campaign browser landing page visible
- Brands anonymised (Brand 1, Brand 2, etc.)

---

## Demo 1: Feature Walkthrough (~3-4 min)

### Load a Campaign
**Action:** Enter campaign 16699 (or select from list)

**Script:**
> "This is the campaign browser. I can either browse campaigns or enter a specific ID.
>
> Let me load one to show you the interface..."

*[Wait for load]*

---

### Campaign Summary Cards (Header)
**Action:** Point to the 8 metric cards at the top

> "First, notice these summary cards at the top - they give you an instant snapshot of the campaign:
>
> **Top row** - the audience metrics: 52 million Impacts, 13 million Reach, 94 GRPs, and 4x Frequency.
>
> **Bottom row** - the delivery metrics: 9 million Playouts across 452 Frames, 10-second average spot, reaching 23% Cover of GB Adults.
>
> These update for every campaign - instant context before you dive into the details."

---

### Tab 1: 📊 Overview
**Action:** Click Overview tab, point to detailed metrics

> "The Overview tab expands on this. The Audience Metrics section breaks down the same figures with explanatory tooltips.
>
> Below that - the Campaign Shape chart shows daily impacts over the flight. You can immediately see the delivery pattern - weekday vs weekend, any gaps or spikes."

---

### Tab 2: 📈 Weekly Reach, Impacts & GRPs
**Action:** Click to Weekly Reach tab

> "The Weekly Reach tab is where econometricians spend their time.
>
> This table shows each week's individual performance - Reach, GRP, Frequency, and Impacts.
>
> These bar charts compare week-on-week delivery.
>
> And crucially - the Cumulative Build chart shows how reach accumulates over time. This is the curve econometricians need for their models."

---

### Tab 3: ⏰ Daily & Hourly Patterns
**Action:** Click to Daily & Hourly Patterns tab

> "Daily and Hourly Patterns gives you the time-based analysis.
>
> At the top - campaign averages and peak performance metrics. You can see the peak hour and peak day at a glance.
>
> These charts show the daily trends and day-of-week comparison - important for understanding delivery patterns.
>
> And this heatmap - day of week by hour - shows exactly when the campaign is delivering. You can immediately spot the busy periods."

**Action:** Change demographic filter (e.g., from "All Adults" to "ABC1" or "35-54")

> "Watch what happens when I change the demographic filter...
>
> The charts update instantly to show impacts for just that audience segment. This is crucial for econometricians who need to match advertising exposure to specific target audiences - not just 'all adults'.
>
> The Route data gives us this demographic granularity at scale."

---

### Tab 4: 🗺️ Geographic
**Action:** Click to Geographic tab

> "The Geographic tab gives you regional analysis.
>
> Summary metrics at the top - frames, impacts, TV regions, and towns covered.
>
> These charts show regional and environment distribution - where the campaign is running.
>
> And this interactive map shows frame locations across the UK. You can zoom in, hover for details. The marker size indicates impact volume."

---

### Tab 5: 🔬 Frame Audiences
**Action:** Click to Frame Audiences tab

> "Frame Audiences is the export data for MMM integration.
>
> Three views: Campaign totals, Daily breakdown, and Hourly breakdown.
>
> Each table shows frame-level impacts across all 7 demographics - All Adults, ABC1, C2DE, Age bands, Main Shopper, and Households with Children.
>
> Click Download CSV to export for your econometric model. This is the data you'd feed into your MMM."

---

### Tab 6: 📑 Executive Summary
**Action:** Click to Executive Summary tab

> "Finally, the Executive Summary - a one-page view of the whole campaign.
>
> Key media metrics at the top: GRP, Reach, Cover, Frequency.
>
> Delivery and Peak Performance tables give you the numbers at a glance.
>
> The Reach & Impact Build chart shows cumulative growth over time.
>
> And these supporting charts - Daily Impacts, Day of Week, and Regional breakdown.
>
> This is what you'd screenshot for a report."

---

### Export & Download
**Action:** Click "Export Data" button in Executive Summary tab

> "And critically - all of this is exportable.
>
> Click Export Data and you get a multi-sheet Excel file with everything: summary metrics, frame-level daily data, hourly data, weekly reach figures, regional breakdown.
>
> This is the format econometricians need - they can drop it straight into their models or join it to spend data."

**Action:** Show the download starting (don't need to wait for completion)

> "The export includes all demographics, all time periods, all frames. One click, complete dataset."

---

## Demo 2: Data Quality Example (~2-3 min)

### The Setup
**Script:**
> "Now let me show you a real example of the campaign ID issue I mentioned..."

### Load Campaign 16879
**Action:** Enter "16879" and load

> "Here's a campaign running September through October. Look at the campaign shape..."
>
> "See the healthy delivery in early September? Now watch what happens around September 21st. The impacts fall off a cliff."

### The Question
> "If you're matching this to spend data, you'd think: did they stop spending?"

### Load the Combined Campaign
**Action:** Navigate back, enter "16879 & 16882"

> "Now look at this..."

*[Wait for load]*

**Action:** Point to chart

> "This combined campaign ramps up exactly when the other drops off.
>
> The activity didn't stop - it got re-categorised under a different campaign ID.
>
> This is exactly the kind of data quality issue that would corrupt an MMM if not caught."

---

## Closing

**Script:**
> "So that's the POC - the tool works, the data is flowing, but we've surfaced real data quality challenges that need addressing for this to scale.
>
> Any questions?"

---

# BACKUP CAMPAIGNS

If needed:

| Campaign | Brand | Notes |
|----------|-------|-------|
| **18409** | Waitrose | 1,126 frames, clean data |
| **16860** | Specsavers | 642 frames, highest cover |

---

# TECHNICAL NOTES

## Pre-Demo Checklist
- [ ] Streamlit running on port 8504
- [ ] Connected to MS-01 database
- [ ] Test campaigns 16699, 16879, "16879 & 16882" load correctly
- [ ] M1 Max backup ready (if needed)

## If Something Goes Wrong
1. **Campaign won't load**: Try backup campaign (18409 or 16860)
2. **App crashes**: `stopstream && startstream`
3. **Database unavailable**: Switch to M1 Max

## Key URLs
- Demo: http://localhost:8504
- Health: http://localhost:8504/_stcore/health

---

*Last Updated: 2025-11-30*
*Demo Date: December 4th, 2025 (morning)*
