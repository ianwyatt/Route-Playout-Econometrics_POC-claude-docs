Could not load DatabaseConfig, falling back to env vars: POSTGRES_HOST_PRIMARY environment variable must be set for primary database connection
# Non-Venue Spike Frames — Classification Analysis

Frames with `average_index > 5.0` where the nearest major stadium is **> 2 km** away.

Total frames with any hour > 5.0: **406**

> Note: 13 spike frame(s) have no coordinates in route_frame_details and are excluded.

## Summary

| Metric | Count |
|--------|-------|
| Frames with spike > 5.0 | 406 |
| Of those with coordinates | 393 |
| Near a venue (≤ 2.0 km) | 159 |
| **Non-venue spike frames** | **234** |

## Taxonomy Classification

| Category | Frames | Spike-Days | % of Non-Venue |
|----------|--------|------------|----------------|
| Transport Hub | 134 | 171 | 57.3% |
| City Centre / High St | 84 | 182 | 35.9% |
| Retail / Shopping | 16 | 43 | 6.8% |

## Example Frames by Category

### Transport Hub

| Frame | Town | Region | Env | POI | Peak | Spike Days | Nearest Venue (km) |
|-------|------|--------|-----|-----|------|------------|---------------------|
| 1234571069 | London WC1 and WC2 | Government Office Re | UndergroundStation-London | Charing Cross (LU) | 5.32 | 1 | 5.3 km |
| 1234571070 | London WC1 and WC2 | Government Office Re | UndergroundStation-London | Charing Cross (LU) | 5.32 | 1 | 5.3 km |
| 1234571071 | London WC1 and WC2 | Government Office Re | UndergroundStation-London | Charing Cross (LU) | 5.32 | 1 | 5.3 km |

### City Centre / High St

| Frame | Town | Region | Env | POI | Peak | Spike Days | Nearest Venue (km) |
|-------|------|--------|-----|-----|------|------------|---------------------|
| 1234844273 | Maida Vale | Government Office Re | Roadside | — | 12.91 | 2 | 6.9 km |
| 1234848273 | Stepney | Government Office Re | Roadside | — | 5.46 | 1 | 3.7 km |
| 1234849170 | Leeds | Government Office Re | Roadside | — | 5.87 | 1 | 5.0 km |

### Retail / Shopping

| Frame | Town | Region | Env | POI | Peak | Spike Days | Nearest Venue (km) |
|-------|------|--------|-----|-----|------|------------|---------------------|
| 1234849484 | Norwich | Government Office Re | SupermarketExterior | JS0706WilliamFrostWy | 7.32 | 8 | 9.1 km |
| 1234852190 | Ipswich | Government Office Re | SupermarketExterior | JS0422HadleighRd | 7.19 | 7 | 63.8 km |
| 1234852266 | North Kensington | Government Office Re | SupermarketExterior | JS0602LadbrokeGrv | 13.45 | 2 | 6.3 km |

## Top 20 Towns by Non-Venue Spike Frames

| Rank | Town | Frames | % of Non-Venue |
|------|------|--------|----------------|
| 1 | London WC1 and WC2 | 116 | 49.6% |
| 2 | Westminster | 16 | 6.8% |
| 3 | Rotherham | 12 | 5.1% |
| 4 | Glasgow North | 7 | 3.0% |
| 5 | Sheffield | 6 | 2.6% |
| 6 | Notting Hill | 6 | 2.6% |
| 7 | Derby | 5 | 2.1% |
| 8 | Battersea | 5 | 2.1% |
| 9 | Hatfield | 4 | 1.7% |
| 10 | South Shields | 3 | 1.3% |
| 11 | Airdrie | 3 | 1.3% |
| 12 | North Kensington | 2 | 0.9% |
| 13 | Hamilton | 2 | 0.9% |
| 14 | Walworth | 2 | 0.9% |
| 15 | Motherwell | 2 | 0.9% |
| 16 | Lytham St Annes | 2 | 0.9% |
| 17 | Taunton | 2 | 0.9% |
| 18 | Musselburgh | 2 | 0.9% |
| 19 | Chester Le Street Birtley | 2 | 0.9% |
| 20 | Leicester | 2 | 0.9% |

## Region Distribution

| Region | Frames | % |
|--------|--------|---|
| Government Office Region -London | 156 | 66.7% |
| Government Office Region -Yorkshire & The Humber | 20 | 8.5% |
| Government Office Region -Scotland | 18 | 7.7% |
| Government Office Region -South East | 8 | 3.4% |
| Government Office Region -East Midlands | 7 | 3.0% |
| Government Office Region -East of England | 6 | 2.6% |
| Government Office Region -South West | 6 | 2.6% |
| Government Office Region - North West | 6 | 2.6% |
| Government Office Region - North East                    | 5 | 2.1% |
| Government Office Region -West Midlands | 2 | 0.9% |

## Environment Name Breakdown

| Environment | Frames | Spike-Days | % of Non-Venue |
|-------------|--------|------------|----------------|
| UndergroundStation-London | 111 | 132 | 47.4% |
| Roadside | 84 | 182 | 35.9% |
| RailStation | 23 | 39 | 9.8% |
| SupermarketExterior | 15 | 41 | 6.4% |
| Supermarket Exterior | 1 | 2 | 0.4% |

## POI Analysis (Top 25 Named Locations)

| POI | Frames |
|-----|--------|
| Charing Cross (LU) | 61 |
| Embankment | 39 |
| Charing Cross (Rail) | 15 |
| Westminster | 5 |
| Hatfield | 4 |
| Knightsbridge | 4 |
| Herne Hill | 2 |
| JS0706WilliamFrostWy | 1 |
| JS0422HadleighRd | 1 |
| JS0602LadbrokeGrv | 1 |
| ASDAHESSLE-HULL | 1 |
| ASDASMALLHEATH | 1 |
| AS4923HAMILTON | 1 |
| ASDAPROSPECTHILL | 1 |
| ASDAOLDKENTROAD | 1 |
| ASDAMILTONKEYNES | 1 |
| ASDAWOODSPRING | 1 |
| Blackheath | 1 |
| WaitroseReading | 1 |
| WaitroseHenley | 1 |
| TescoReadingWest | 1 |
| THorwich | 1 |
| TBuckingham | 1 |
| TLewes | 1 |
| Ladbroke Grove | 1 |

## Spike Characteristics

| Metric | Value |
|--------|-------|
| Average peak index (across frames) | 6.73 |
| Average mean index (during spikes) | 6.01 |
| Highest single peak index | 18.60 |
| Average spike days per frame | 1.7 |
| Maximum spike days (one frame) | 18 |
| Frames spiking on > 1 day | 52 (22.2%) |

## Clustering Assessment

Non-venue spike frames are spread across **49 towns**.

The top 3 towns account for **62%** of frames (London WC1 and WC2, Westminster, Rotherham), indicating a **concentrated cluster**.

## Commercial Value Assessment

Non-venue spike frames with `average_index > 5.0` and no stadium within 2 km represent persistent elevated footfall driven by non-sporting causes. Possible drivers include:

- **Retail & shopping destinations** — high dwell-time environments where mobile data reflects genuine footfall concentration (shopping centres, supermarket car parks, retail parks).
- **Transport hubs** — rail and bus stations create predictable peaks tied to commuting patterns; these frames may command premiums for time-of-day targeting.
- **Leisure & entertainment venues** — cinemas, arenas, and hospitality clusters generate event-driven spikes without the explicit stadium tagging.
- **City centre hotspots** — high-footfall pedestrian areas and high streets with natural audience concentration independent of any single venue.

These frames are commercially attractive because the footfall signal is:

1. **Repeatable** — not tied to a single event calendar, reducing scheduling risk.
2. **Commercially qualified** — shoppers and commuters represent high-value audiences.
3. **Diverse in geography** — national spread means multiple media owner inventory benefits.

---
*Generated by `scripts/research_non_venue_spikes.py`*
