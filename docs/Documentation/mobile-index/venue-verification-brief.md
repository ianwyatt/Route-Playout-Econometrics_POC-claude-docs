# Mobile Index Venue Verification — Research Brief

**Purpose:** Cross-reference mobile index spike locations and dates against real football fixtures, concert schedules, and venue coordinates to confirm the data genuinely captures event-driven footfall.

**For:** Standalone research session (no app development needed)

---

## What Needs Verifying

### 1. Frame Locations vs Venue Proximity

We have frame coordinates in the database. For each hotspot town, verify the spiking frames are genuinely near the suspected venues.

**Database query to get frame coordinates:**
```python
import psycopg2, psycopg2.extras
from src.db.queries.connection import get_db_connection
conn = get_db_connection(use_primary=False)
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("""
        SELECT DISTINCT r.frameid, r.town, r.region, r.latitude, r.longitude,
               r.address, r.postcode, r.poi, r.environment_name
        FROM route_frame_details r
        WHERE r.frameid IN (
            SELECT DISTINCT frameid FROM mobile_volume_index WHERE average_index > 5.0
        )
        ORDER BY r.town
    """)
    for row in cur.fetchall():
        print(dict(row))
conn.close()
```

### 2. Venues to Confirm

| Town | Suspected Venue | Verify Coordinates | Capacity |
|------|----------------|-------------------|----------|
| Sunderland | Stadium of Light | 54.9146, -1.3882 | 49,000 |
| Stretford | Old Trafford | 53.4631, -2.2913 | 74,310 |
| Manchester | Etihad Stadium | 53.4831, -2.2004 | 53,400 |
| Holloway | Emirates Stadium | 51.5549, -0.1084 | 60,704 |
| Tottenham | Tottenham Hotspur Stadium | 51.6033, -0.0662 | 62,850 |
| Liverpool | Anfield | 53.4308, -2.9608 | 61,276 |
| Liverpool | Goodison Park | 53.4387, -2.9663 | 39,414 |
| Cardiff | Principality Stadium | 51.4782, -3.1826 | 73,931 |
| Leeds | Elland Road | 53.7778, -1.5722 | 37,890 |
| Brentford | Brentford Community Stadium | 51.4907, -0.2886 | 17,250 |
| Glasgow North | Celtic Park | 55.8497, -4.2055 | 60,411 |
| Glasgow North | Ibrox Stadium | 55.8532, -4.3092 | 50,817 |
| Twickenham | Twickenham Stadium | 51.4559, -0.3415 | 82,000 |
| Birmingham | Villa Park | 52.5092, -1.8847 | 42,788 |
| Sheffield | Bramall Lane | 53.3703, -1.4709 | 32,050 |
| Bristol | Ashton Gate | 51.4400, -2.6201 | 27,000 |
| Norwich | Carrow Road | 52.6221, 1.3090 | 27,244 |
| Southampton | St Mary's Stadium | 50.9058, -1.3908 | 32,384 |
| Reading | Select Car Leasing Stadium | 51.4222, -0.9826 | 24,161 |
| Newcastle | St James' Park | 54.9756, -1.6216 | 52,305 |
| Middlesbrough | Riverside Stadium | 54.5781, -1.2170 | 34,742 |
| Stratford West Ham | London Stadium | 51.5386, -0.0166 | 62,500 |

**Task:** Calculate distance between each spiking frame's lat/lon and the nearest venue. Frames within ~500m strongly confirm; 500m–1km likely; >1km needs alternative explanation.

### 3. Football Fixture Dates to Cross-Reference

The source data maps 2024 dates to 2025. The `date_2024` column in `mobile_volume_index` has the original dates. Key spike dates to verify against 2024 fixtures:

**Top spike dates (shown as 2025, but original 2024 dates are in the data):**

```python
# Get the original 2024 dates for top spike days
cur.execute("""
    SELECT DISTINCT date_2025, date_2024,
           TO_CHAR(date_2024, 'Dy') AS day_name,
           COUNT(*) AS spike_count,
           COUNT(DISTINCT frameid) AS frames
    FROM mobile_volume_index
    WHERE average_index > 3.0
    GROUP BY date_2025, date_2024
    ORDER BY spike_count DESC
    LIMIT 30
""")
```

**What to check for each date:**
- Premier League fixtures (use football-data.co.uk or similar)
- EFL Championship/League One/Two matches
- Rugby internationals (Twickenham)
- Concerts/festivals at major venues
- Bank holidays (known: 26 Aug 2024 = Summer Bank Holiday)

### 4. The Sunderland Smoking Gun

**Frame `1234860534` on 21 May 2025 (original 2024 date needed)**

Hit 35x index at 22:00 with clear ingress ramp from 15:00. Three adjacent frames (`1234860534`, `1234860069`, `1234860070`) all spike simultaneously.

**Verify:**
- Get the `date_2024` for this frame/date
- Check Sunderland AFC fixtures for that date
- Check Stadium of Light concert listings
- Confirm frame coordinates are within 500m of stadium

### 5. Glasgow North Cluster

**12–13 July 2025 (original 2024 dates needed)** — 6+ frames at 18x index at 23:00

**Verify:**
- Celtic Park or Ibrox match/event on the original 2024 date
- Could be a concert (both venues host summer concerts)

### 6. The Stretford Pattern

**9 frames near Old Trafford, spiking on 28 separate days**

**Verify:**
- How many of those 28 days correspond to Man Utd home fixtures?
- Cross-reference with 2024/25 Premier League + cup schedule
- If >80% match → very strong evidence

```python
# Get all spike dates for Stretford frames
cur.execute("""
    SELECT DISTINCT m.date_2025, m.date_2024,
           TO_CHAR(m.date_2024, 'Dy') AS day_name,
           COUNT(DISTINCT m.frameid) AS frames,
           ROUND(AVG(m.average_index)::numeric, 2) AS avg_index
    FROM mobile_volume_index m
    JOIN route_frame_details r ON m.frameid = r.frameid
    WHERE r.town = 'Stretford' AND m.average_index > 3.0
    GROUP BY m.date_2025, m.date_2024
    ORDER BY m.date_2024
""")
```

### 7. Overnight Flat Pattern (0–4am)

420 frames show consistent 3.5x index overnight. These could be:
- Near nightlife districts (not football)
- Near 24hr transport hubs
- Data artefact

**Verify:** Pull the towns for the overnight-only spiking frames and check if they cluster in city centres / nightlife areas rather than near stadia.

```python
# Frames that spike overnight but NOT during match hours
cur.execute("""
    WITH overnight_spikers AS (
        SELECT frameid FROM mobile_volume_index
        WHERE average_index > 3.0 AND hour BETWEEN 0 AND 4
        GROUP BY frameid
        HAVING COUNT(*) > 10
    ),
    evening_spikers AS (
        SELECT frameid FROM mobile_volume_index
        WHERE average_index > 3.0 AND hour BETWEEN 18 AND 22
        GROUP BY frameid
        HAVING COUNT(*) > 5
    )
    SELECT DISTINCT r.frameid, r.town, r.latitude, r.longitude, r.poi
    FROM overnight_spikers o
    JOIN route_frame_details r ON o.frameid = r.frameid
    WHERE o.frameid NOT IN (SELECT frameid FROM evening_spikers)
    ORDER BY r.town
""")
```

---

## How to Run

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
uv run python -c "<query code here>"
```

Database: local PostgreSQL, `get_db_connection(use_primary=False)`.

## Expected Output

A verification report confirming or refuting each hotspot, with:
- Distance calculations (frame → venue)
- Fixture date matches (% of spike dates that correspond to real events)
- Any surprising findings (spikes NOT near venues, venues WITHOUT spikes)
- Confidence rating for each location

---

*Source research: `docs/Documentation/mobile-index/research-findings.md`, `docs/Documentation/mobile-index/executive-summary.md`*
*Research scripts: `scripts/research_event_peaks.py`, `scripts/research_overall_impact.py`*
