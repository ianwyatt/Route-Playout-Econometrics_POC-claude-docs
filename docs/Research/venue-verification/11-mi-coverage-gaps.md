Could not load DatabaseConfig, falling back to env vars: POSTGRES_HOST_PRIMARY environment variable must be set for primary database connection
# Mobile Index Coverage Gap Analysis

Analysis of MI data coverage across the Route OOH frame estate,
with focus on the 22 sports venue locations.

## 1. Overall MI Coverage Summary

| Metric | Value |
|--------|-------|
| Total frames in route_frame_details | 387,165 |
| Frames with MI data | 14,639 |
| Overall MI coverage | 3.8% |

## 2. Per-Venue Coverage (frames within 1 km)

Fetching all frames with valid coordinates — this may take a moment...
Loaded 387,165 frames with valid coordinates.

| Town | Venue | Total Frames | MI Frames | Coverage % |
|------|-------|:------------:|:---------:|:----------:|
| Reading | Select Car Leasing Stadium | 13 | 0 | 0.0% |
| Norwich | Carrow Road | 1,038 | 4 | 0.4% |
| Tottenham | Tottenham Hotspur Stadium | 529 | 6 | 1.1% |
| Liverpool | Anfield | 80 | 1 | 1.2% |
| Birmingham | Villa Park | 84 | 1 | 1.2% |
| Manchester | Etihad Stadium | 53 | 1 | 1.9% |
| Leeds | Elland Road | 87 | 3 | 3.4% |
| Sheffield | Bramall Lane | 1,024 | 47 | 4.6% |
| Liverpool | Goodison Park | 72 | 4 | 5.6% |
| Sunderland | Stadium of Light | 496 | 31 | 6.2% |
| Holloway | Emirates Stadium | 462 | 29 | 6.3% |
| Middlesbrough | Riverside Stadium | 45 | 3 | 6.7% |
| Cardiff | Principality Stadium | 1,320 | 107 | 8.1% |
| Glasgow North | Ibrox Stadium | 123 | 10 | 8.1% |
| Glasgow North | Celtic Park | 75 | 9 | 12.0% |
| Twickenham | Twickenham Stadium | 31 | 4 | 12.9% |
| Newcastle | St James' Park | 766 | 109 | 14.2% |
| Stratford | London Stadium | 630 | 97 | 15.4% |
| Stretford | Old Trafford | 89 | 17 | 19.1% |
| Brentford | Brentford Community Stadium | 65 | 14 | 21.5% |
| Bristol | Ashton Gate | 25 | 7 | 28.0% |
| Southampton | St Mary's Stadium | 113 | 50 | 44.2% |

**Combined across all venues:** 554 of 7,220 frames (7.7%) have MI data.
- Venues with 0% coverage: 1
- Venues with <10% coverage: 14
- Venues with ≥50% coverage: 0

## 3. Regional Coverage

| Region | Total Frames | MI Frames | Coverage % |
|--------|:------------:|:---------:|:----------:|
| Government Office Region -London | 206,213 | 6,084 | 3.0% |
| Government Office Region -South East | 44,457 | 1,220 | 2.7% |
| Government Office Region -East of England | 27,984 | 673 | 2.4% |
| Government Office Region - North West | 25,395 | 1,544 | 6.1% |
| Government Office Region -West Midlands | 18,663 | 1,253 | 6.7% |
| Government Office Region -Scotland | 16,748 | 978 | 5.8% |
| Government Office Region -Yorkshire & The Humber | 15,822 | 876 | 5.5% |
| Government Office Region -South West | 11,115 | 670 | 6.0% |
| Government Office Region - North East                    | 7,951 | 539 | 6.8% |
| Government Office Region -Wales | 7,172 | 276 | 3.8% |
| Government Office Region -East Midlands | 5,646 | 527 | 9.3% |

## 4. BARB Region Coverage

| BARB Region | Total Frames | MI Frames | Coverage % |
|-------------|:------------:|:---------:|:----------:|
| London | 227,828 | 6,763 | 3.0% |
| South and South-East | 36,511 | 956 | 2.6% |
| Midlands | 24,305 | 1,718 | 7.1% |
| North West | 23,492 | 1,527 | 6.5% |
| East Of England | 19,254 | 446 | 2.3% |
| Yorkshire | 16,995 | 935 | 5.5% |
| Central Scotland | 14,055 | 808 | 5.7% |
| North East | 8,067 | 543 | 6.7% |
| Wales | 7,172 | 276 | 3.8% |
| South West | 3,985 | 193 | 4.8% |
| West | 3,710 | 286 | 7.7% |
| North Scotland | 2,539 | 169 | 6.7% |
| Border | 800 | 20 | 2.5% |

## 5. Coverage by Environment Type

| Environment Type | Total Frames | MI Frames | Coverage % |
|------------------|:------------:|:---------:|:----------:|
| TubeCarriageInterior | 96,127 | 0 | 0.0% |
| Tube Carriage Interior | 96,127 | 0 | 0.0% |
| Roadside | 86,797 | 9,091 | 10.5% |
| Train Carriage Interior | 71,427 | 0 | 0.0% |
| Bus | 70,555 | 0 | 0.0% |
| TrainCarriageInterior | 69,701 | 0 | 0.0% |
| UndergroundStation-London | 30,430 | 2,162 | 7.1% |
| Rail Station | 11,719 | 1,267 | 10.8% |
| RailStation | 11,500 | 1,117 | 9.7% |
| Taxi | 7,784 | 0 | 0.0% |
| Tram LR Carriage Interior | 5,512 | 0 | 0.0% |
| TramLRCarriageInterior | 5,512 | 0 | 0.0% |
| Shopping Centre Interior | 2,180 | 1,085 | 49.8% |
| ShoppingCentreInterior | 2,114 | 1,049 | 49.6% |
| Supermarket Exterior | 1,487 | 936 | 62.9% |
| SupermarketExterior | 1,476 | 916 | 62.1% |
| Motorway Service Station | 1,418 | 10 | 0.7% |
| MotorwayServiceStation | 1,418 | 10 | 0.7% |
| UndergroundStation-Glasgow | 778 | 33 | 4.2% |
| AirportEnclosed | 666 | 0 | 0.0% |
| Shopping Centre Exterior | 177 | 55 | 31.1% |
| ShoppingCentreExterior | 172 | 55 | 32.0% |
| AirportOpen | 45 | 0 | 0.0% |

## 6. Analysis

### Geographic Bias

**Lowest coverage regions:**
- Government Office Region -East of England: 2.4% (673 of 27,984 frames)
- Government Office Region -South East: 2.7% (1,220 of 44,457 frames)
- Government Office Region -London: 3.0% (6,084 of 206,213 frames)

**Highest coverage regions:**
- Government Office Region -East Midlands: 9.3% (527 of 5,646 frames)
- Government Office Region - North East                   : 6.8% (539 of 7,951 frames)
- Government Office Region -West Midlands: 6.7% (1,253 of 18,663 frames)

### Urban vs Rural Bias

Environment types with the highest coverage are likely to be high-footfall
urban formats (shopping centres, airports, transport hubs) where mobile data
collection is densest. Lower coverage in roadside or rural environments reflects
sparser mobile signal and panel coverage in those locations.

**Lowest coverage environments:**
- TubeCarriageInterior: 0.0% (0 of 96,127 frames)
- Tube Carriage Interior: 0.0% (0 of 96,127 frames)
- Train Carriage Interior: 0.0% (0 of 71,427 frames)

**Highest coverage environments:**
- Supermarket Exterior: 62.9% (936 of 1,487 frames)
- SupermarketExterior: 62.1% (916 of 1,476 frames)
- Shopping Centre Interior: 49.8% (1,085 of 2,180 frames)

### Venue-Specific Gaps

Of the 22 venues analysed, 1 have zero MI coverage and
18 have below 20% coverage within 1 km.

**Venues with no MI data within 1 km:**
- Select Car Leasing Stadium (Reading): 13 frames, 0 with MI

**Venues with <20% MI coverage:**
- Carrow Road (Norwich): 0.4% (4 of 1,038 frames)
- Tottenham Hotspur Stadium (Tottenham): 1.1% (6 of 529 frames)
- Anfield (Liverpool): 1.2% (1 of 80 frames)
- Villa Park (Birmingham): 1.2% (1 of 84 frames)
- Etihad Stadium (Manchester): 1.9% (1 of 53 frames)
- Elland Road (Leeds): 3.4% (3 of 87 frames)
- Bramall Lane (Sheffield): 4.6% (47 of 1,024 frames)
- Goodison Park (Liverpool): 5.6% (4 of 72 frames)
- Stadium of Light (Sunderland): 6.2% (31 of 496 frames)
- Emirates Stadium (Holloway): 6.3% (29 of 462 frames)
- Riverside Stadium (Middlesbrough): 6.7% (3 of 45 frames)
- Principality Stadium (Cardiff): 8.1% (107 of 1,320 frames)
- Ibrox Stadium (Glasgow North): 8.1% (10 of 123 frames)
- Celtic Park (Glasgow North): 12.0% (9 of 75 frames)
- Twickenham Stadium (Twickenham): 12.9% (4 of 31 frames)
- St James' Park (Newcastle): 14.2% (109 of 766 frames)
- London Stadium (Stratford): 15.4% (97 of 630 frames)
- Old Trafford (Stretford): 19.1% (17 of 89 frames)

## 7. Recommendations for Coverage Expansion

1. **Prioritise high-footfall venue catchment areas** — venues with zero or
   near-zero MI coverage within 1 km represent the highest-value expansion
   targets. These are locations where index data would most directly improve
   campaign evaluation accuracy for event-driven campaigns.

2. **Focus on underrepresented regions** — regions with the lowest overall
   coverage percentages should be prioritised in data acquisition negotiations
   with the mobile data provider. Coverage gaps in Scotland and the North East
   are particularly notable given the venue concentration there.

3. **Roadside and transport environments** — if roadside formats show lower
   coverage, these should be flagged: roadside is typically the highest-volume
   OOH format and under-indexing there will skew aggregate results.

4. **Verify frame matching methodology** — only 16,265 of the imported frames
   matched the Route frame estate. Review the frame ID mapping between the
   analyst DB source (`cristina.oa_frames_hourly_index_v2`) and route_frame_details
   to confirm no additional frames can be matched with a looser join strategy
   (e.g. spatial proximity rather than exact frame ID match).

5. **Consider date-range extension** — the current MI data covers 2024. If more
   recent data is available from the analyst DB, re-importing with 2025 dates
   would improve coverage of recently installed frames.

---
_Analysis generated by `scripts/research_mi_coverage_gaps.py`_
