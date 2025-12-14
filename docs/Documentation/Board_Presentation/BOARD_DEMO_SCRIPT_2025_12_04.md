# Board Demo Script - December 4th, 2025

**Presentation Reference**: `/Users/ianwyatt/Route Dropbox/Ian Wyatt/01-Projects/Route-Playout-Econometrics-POC/Board Presentation/20251126/Route - Playout POC Update - Board Version - 20251127.pptx`

---

## Demo Campaigns

| Campaign | Purpose | Key Points |
|----------|---------|------------|
| **16699** | Feature walkthrough | Standard test campaign, well-understood data |
| **16879** | Data quality issue | Shows cliff drop when combined campaign takes over |
| **16879 & 16882** | Overlap demonstration | Combined campaign that absorbs 16879's activity |
| **18409** | Backup (primary) | Waitrose - 1,126 frames, 14 days, 17.5% cover |
| **16860** | Backup (secondary) | Specsavers - 642 frames, 15 days, 25.8% cover |

---

## Campaign 16879 Overlap Issue

### The Problem (Visual Evidence)

**Campaign 16879 (Standalone)**
- Dates: 05 Sep - 10 Oct 2025 (28 days)
- Media Owners: Bauer Media Outdoor, JCDecaux, Ocean Outdoor
- Total Impacts: 25.99M
- Frames: 918
- **Key observation**: Impacts run ~2,000k/day until Sep 21-22, then DROP TO NEAR ZERO

**Campaign 16879 & 16882 (Combined)**
- Dates: 16 Sep - 05 Oct 2025 (20 days)
- Media Owner: Alight Media
- Total Impacts: 7.52M
- Frames: 98
- **Key observation**: Ramps up around Sep 22-23 to ~500-600k/day

### The Timeline

```
Sep 5  -------- Campaign 16879 starts (2M+ impacts/day)
Sep 16 -------- Campaign "16879 & 16882" starts
Sep 21-22 ----- Campaign 16879 impacts CLIFF DROP to near zero
Sep 22-23 ----- Campaign "16879 & 16882" ramps up to 500-600k/day
Oct 5  -------- Campaign "16879 & 16882" ends
Oct 10 -------- Campaign 16879 ends (but flat-lined since Sep 22)
```

### The Econometrician's Dilemma

When trying to assign advertising spend to measured impacts:

1. **Did the advertiser stop spending on Sep 21?**
   - The data suggests activity ceased

2. **Or was activity re-categorised into the combined campaign?**
   - Same frames/activity, different campaign ID

3. **The answer matters for spend attribution**
   - If spend continues but impacts disappear under one ID, the model breaks
   - Econometricians need consistent campaign IDs to match spend → impacts

### Demo Talking Points

> "Here's campaign 16879 - notice the healthy delivery through mid-September, then watch what happens around the 21st..."
>
> "The impacts fall off a cliff. Did the advertiser stop spending? Let's check..."
>
> "Now look at campaign '16879 & 16882' - a combined campaign that starts mid-September and ramps up exactly when 16879 drops off."
>
> "For an econometrician trying to match advertising spend to measured impacts, this is a nightmare. The activity didn't stop - it just got re-labelled."
>
> "This is exactly why we need this tool - to surface these data quality issues before they corrupt the econometric models."

---

## Demo Script - Feature Walkthrough (Campaign 16699)

### 1. Campaign Browser Landing
- Show the campaign browser with Route logo
- Highlight the two input methods: Browse vs Enter Campaign ID
- Click "Load Campaigns" to show the campaign list

### 2. Select Campaign 16699
- Either click from list or enter ID directly
- Show the campaign header card with:
  - Brand name, dates, media owners
  - Route logo in corner

### 3. Campaign Summary Cards (Header)
**Point to the 8 metric cards at the top of the analysis page:**
- **Top row** - Audience metrics: Total Impacts (52M), Total Reach (13M), Total GRPs (94.5), Frequency (4.0x)
- **Bottom row** - Delivery metrics: Total Playouts (9.2M), Unique Frames (452), Avg Spot Length (10s), Cover (23.4%)
- Emphasise: "Instant snapshot before diving into details"

### 4. Overview Tab
- **Audience Metrics section**: Expands the header cards with explanatory tooltips
- **Campaign Shape**: Daily impacts chart with average line
- Point out the summary stats at bottom (days, range, weekday/weekend avg)

### 5. Weekly Reach Tab
- Show reach build over time
- Demographic comparison charts
- Explain how reach differs from impacts (unique people vs total exposures)

### 6. Executive Summary Tab
- Quick overview for stakeholders
- Key metrics at a glance
- Reach & Impact Build chart

### 7. Detailed Analysis Tab (Daily & Hourly Patterns)
- **Daily Impacts**: Frame-day level data for econometric matching
- **Hourly Impacts**: Granular time-series data
- **Demographic Filter Demo**:
  - Change from "All Adults" to "ABC1" or "35-54"
  - Show charts updating instantly for that segment
  - "This demographic granularity at scale is what econometricians need"

### 8. Geographic Tab
- Impacts by TV Region
- Map visualisation (if time permits)

### 9. Frame Audiences Tab
- Frame-level brand breakdown
- Daily and hourly audience per frame

### 10. Export Demo (Executive Summary Tab)
- Click "Export Data" button
- Show multi-sheet Excel download starting
- Highlight: "Summary, frame-level daily, hourly, weekly reach, regional - all in one file"
- "One click, complete dataset ready for econometric models"

---

## Demo Script - Data Quality Issue (Campaigns 16879 / 16879 & 16882)

### Setup
"Now let me show you why this tool is so valuable for catching data quality issues..."

### Step 1: Load Campaign 16879
- Enter "16879" in the campaign ID field
- Show the overview - note the 25.99M impacts, 918 frames
- **Point to the Campaign Shape chart** - "See the healthy delivery in early September?"

### Step 2: The Cliff
- "Now watch what happens around September 21st..."
- Point to the dramatic drop in the Campaign Shape chart
- "The impacts fall off a cliff. Did the advertiser stop spending?"

### Step 3: Load Campaign "16879 & 16882"
- Navigate back to campaign browser
- Enter "16879 & 16882"
- Show the overview - note the 7.52M impacts, 98 frames, Alight Media only

### Step 4: The Reveal
- **Point to the Campaign Shape chart** - "Look at the timing..."
- "This combined campaign ramps up exactly when 16879 drops off"
- "The activity didn't stop - it got re-categorised under a different campaign ID"

### Step 5: The Implication
- "For an econometrician trying to match spend to impacts, this creates a serious problem"
- "If they're tracking campaign 16879, they'd see impacts disappear mid-campaign"
- "Without this tool, they might assume the advertising stopped working"
- "In reality, the playout data just moved to a different campaign identifier"

### Closing
- "This is exactly the kind of data quality issue we can now surface and investigate"
- "Before this tool, these problems would silently corrupt econometric models"

---

## Backup Campaign Options

Candidates with recognizable UK brands:

| Campaign | Brand | Frames | Days | Media Owner | Notes |
|----------|-------|--------|------|-------------|-------|
| **18409** | Waitrose | 1,126 | 14 | Bauer Media Outdoor | ✅ Recommended - UK supermarket |
| **17902** | LNER | 889 | 45 | JCDecaux | ✅ Recommended - UK train operator |
| **17950** | H&M | 588 | 22 | Ocean Outdoor | Fashion retail |
| **18143** | Uber | 786 | 41 | Global | Tech/transport |
| **18295** | Uber Eats | 1,390 | 45 | Global | Food delivery |

**Selected Backups** (verified with real reach data):
1. **18409 (Waitrose)** ✅ - 1,126 frames, 14 days, 17.5% cover, 19.1x freq
2. **16860 (Specsavers)** ✅ - 642 frames, 15 days, 25.8% cover, 2.7x freq

---

## API Limitation Notes (Campaigns to Avoid)

The following campaigns trigger Route API limitations where 15-min data exceeds API limits, causing Reach/Cover/Frequency to show 0:

| Campaign | Brand | Frame×Days | Issue |
|----------|-------|------------|-------|
| 17902 | LNER | 40,005 | ⚠️ Reach = 0 |
| 18279 | Starbucks | 19,712 | ⚠️ Reach = 0 |
| 17543 | National Lottery | 19,260 | ⚠️ Reach = 0 |

**Pattern**: Campaigns with high frame×days volume can exceed Route API limits. Worth mentioning briefly in board presentation as a known limitation we're aware of, but not for live demo.

**Threshold**: Appears to be around 15,000-20,000 frame-days, but inconsistent - some campaigns under this still fail.

---

## Technical Setup for Demo Day

### Primary Setup (Main Mac)
- Streamlit running on port 8504
- Connected to MS-01 database
- Browser at http://localhost:8504

### Backup Setup (M1 Max)
- Clone repo and install dependencies
- Configure .env with MS-01 connection
- Terminal aliases: `stopstream`, `startstream`
- Test connection before demo

### Pre-Demo Checklist
- [ ] Verify MS-01 database accessible
- [ ] Test campaign 16699 loads correctly
- [ ] Test campaign 16879 loads correctly
- [ ] Test campaign "16879 & 16882" loads correctly
- [ ] Verify all tabs render properly
- [ ] Check export functionality works
- [ ] M1 Max backup tested and ready

---

## Screenshots Reference

Screenshots showing the overlap issue are in the chat context:
- **Image 1**: Campaign "16879 & 16882" - Shows 20-day campaign with ramp-up around Sep 22-23
- **Image 2**: Campaign "16879" - Shows 28-day campaign with cliff drop around Sep 21-22

---

*Last Updated: 2025-11-30*
*Demo Date: December 4th, 2025 (morning)*
