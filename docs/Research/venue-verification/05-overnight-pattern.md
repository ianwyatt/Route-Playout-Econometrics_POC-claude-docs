# Research: Overnight Mobile Index Pattern

Investigating frames that show consistent elevated index (>3.0) between 0–4am
but do NOT show the same spike in evening hours (18–22pm).
Goal: classify as nightlife signal, transport hub, or data artefact.

---

## 1. Overnight-Only Spiking Frames

Total overnight-only spiking frames found: **117**

## 2. Town Distribution

| Town                           | Region                    | Frames |
|-------------------------------|--------------------------|--------|
| Liverpool                      | Government Office Region - North West |     40 |
| Reading                        | Government Office Region -South East |     36 |
| Manchester                     | Government Office Region - North West |     12 |
| Cardiff                        | Government Office Region -Wales |      4 |
| Derby                          | Government Office Region -East Midlands |      1 |

## 3. Environment and POI Analysis

### 3a. By Environment Name

| Environment                              | Frames |
|-----------------------------------------|--------|
| Roadside                                 |     69 |
| Rail Station                             |     22 |
| RailStation                              |     22 |
| Shopping Centre Interior                 |      2 |
| ShoppingCentreInterior                   |      2 |

### 3b. Unique POI Values

| POI                                                | Frames |
|---------------------------------------------------|--------|
| None / NULL                                        |     69 |
| Reading                                            |     13 |
| Lime Street                                        |      9 |
| Reading - The Oracle                               |      2 |

## 4. Hourly Profile Comparison

> **Note on normalisation**: `average_index` is normalised per-frame so each frame's
> mean across all dates and hours equals exactly 1.0. Consequently, averaging across
> many frames always yields ~1.0 regardless of hour. The meaningful signal here is
> the **max** (spike magnitude) and **median** (typical behaviour) columns below,
> plus the day-of-week concentration in section 5.

### 4a. Overnight-Only Frames — Index Distribution by Hour

| Hour |      Avg |      Max |      P90 |   AvgMed | Frames |
|-----|---------|---------|---------|---------|--------|
|    0 |   1.0000 |   4.3588 |   1.7829 |   1.2885 |     94 | *
|    1 |   1.0000 |   4.3588 |   1.7829 |   1.2885 |     94 | *
|    2 |   1.0000 |   4.3588 |   1.7829 |   1.2885 |     94 | *
|    3 |   1.0000 |   4.3588 |   1.7829 |   1.2885 |     94 | *
|    4 |   1.0000 |   4.3588 |   1.7829 |   1.2885 |     94 | *
|    5 |   1.0000 |   3.3564 |   1.4056 |   1.0919 |     94 |
|    6 |   1.0000 |   3.3559 |   1.3069 |   1.0439 |     94 |
|    7 |   1.0000 |   3.2805 |   1.2831 |   1.0012 |     94 |
|    8 |   1.0000 |   3.2872 |   1.3508 |   0.9679 |     94 |
|    9 |   1.0000 |   3.3933 |   1.3325 |   0.9611 |     94 |
|   10 |   1.0000 |   3.4284 |   1.2735 |   0.9607 |     94 |
|   11 |   1.0000 |   3.2804 |   1.2294 |   0.9772 |     94 |
|   12 |   1.0000 |   3.2806 |   1.2180 |   0.9938 |     94 |
|   13 |   1.0000 |   2.9570 |   1.2201 |   1.0012 |     94 |
|   14 |   1.0000 |   2.7209 |   1.2437 |   1.0112 |     94 |
|   15 |   1.0000 |   2.7194 |   1.2658 |   1.0202 |     94 |
|   16 |   1.0000 |   2.4660 |   1.2701 |   1.0235 |     94 |
|   17 |   1.0000 |   2.5283 |   1.2821 |   1.0218 |     94 |
|   18 |   1.0000 |   2.5985 |   1.3433 |   1.0454 |     94 |
|   19 |   1.0000 |   2.6173 |   1.4169 |   1.0795 |     94 |
|   20 |   1.0000 |   2.6014 |   1.4743 |   1.1114 |     94 |
|   21 |   1.0000 |   2.8288 |   1.5658 |   1.1446 |     94 |
|   22 |   1.0000 |   2.9581 |   1.6470 |   1.1850 |     94 |
|   23 |   1.0000 |   3.2093 |   1.7070 |   1.2574 |     94 |

_\* Overnight hours (0–4am) that triggered frame selection._

### 4b. All Frames — Index Distribution by Hour (for comparison)

| Hour |      Avg |      Max |      P90 |   AvgMed | Frames |
|-----|---------|---------|---------|---------|--------|
|    0 |   1.0000 |   6.9490 |   1.2222 |   1.0450 |  15299 |
|    1 |   1.0000 |   6.9490 |   1.2222 |   1.0450 |  15299 |
|    2 |   1.0000 |   6.9490 |   1.2222 |   1.0450 |  15299 |
|    3 |   1.0000 |   6.9490 |   1.2222 |   1.0450 |  15299 |
|    4 |   1.0000 |   6.9490 |   1.2222 |   1.0450 |  15299 |
|    5 |   1.0000 |   6.7949 |   1.1600 |   1.0026 |  15299 |
|    6 |   1.0000 |   6.1964 |   1.1868 |   0.9862 |  15299 |
|    7 |   1.0000 |   5.1656 |   1.2454 |   0.9635 |  15299 |
|    8 |   1.0000 |   5.3540 |   1.3165 |   0.9479 |  15299 |
|    9 |   1.0000 |   8.8787 |   1.3170 |   0.9506 |  15299 |
|   10 |   1.0000 |   8.8802 |   1.2891 |   0.9602 |  15299 |
|   11 |   1.0000 |   8.6780 |   1.2637 |   0.9709 |  15299 |
|   12 |   1.0000 |   8.9110 |   1.2484 |   0.9784 |  15299 |
|   13 |   1.0000 |   9.0489 |   1.2425 |   0.9840 |  15299 |
|   14 |   1.0000 |  10.1421 |   1.2404 |   0.9885 |  15299 |
|   15 |   1.0000 |  12.5638 |   1.2403 |   0.9909 |  15299 |
|   16 |   1.0000 |  14.1554 |   1.2375 |   0.9921 |  15299 |
|   17 |   1.0000 |  15.3054 |   1.2363 |   0.9954 |  15299 |
|   18 |   1.0000 |  22.8512 |   1.2399 |   1.0064 |  15299 |
|   19 |   1.0000 |  27.1145 |   1.2408 |   1.0141 |  15299 |
|   20 |   1.0000 |  29.3389 |   1.2429 |   1.0189 |  15299 |
|   21 |   1.0000 |  31.3860 |   1.2489 |   1.0241 |  15299 |
|   22 |   1.0000 |  35.0013 |   1.2546 |   1.0324 |  15299 |
|   23 |   1.0000 |  28.9676 |   1.2557 |   1.0436 |  15299 |

### 4c. Sample Frame Hourly Profile (Liverpool Lime Street — frame 1234626091)

This rail station frame illustrates the per-frame pattern: index varies by date,
and the station's overnight spike is driven by a small number of outlier dates.

| Hour |      Min |      Max |      Avg | Dates |
|-----|---------|---------|---------|------|
|    0 |   0.1122 |   3.2792 |   1.0000 |   272 | <-- overnight
|    1 |   0.1122 |   3.2792 |   1.0000 |   272 | <-- overnight
|    2 |   0.1122 |   3.2792 |   1.0000 |   272 | <-- overnight
|    3 |   0.1122 |   3.2792 |   1.0000 |   272 | <-- overnight
|    4 |   0.1122 |   3.2792 |   1.0000 |   272 | <-- overnight
|    5 |   0.1809 |   2.4460 |   1.0000 |   272 |
|    6 |   0.1938 |   2.0179 |   1.0000 |   272 |
|    7 |   0.2102 |   1.7915 |   1.0000 |   272 |
|    8 |   0.1916 |   1.8248 |   1.0000 |   272 |
|    9 |   0.1552 |   1.7050 |   1.0000 |   272 |
|   10 |   0.1267 |   1.5507 |   1.0000 |   272 |
|   11 |   0.1148 |   1.4438 |   1.0000 |   272 |
|   12 |   0.1086 |   1.6107 |   1.0000 |   272 |
|   13 |   0.1090 |   1.7942 |   1.0000 |   272 |
|   14 |   0.1158 |   2.0159 |   1.0000 |   272 |
|   15 |   0.1152 |   2.1821 |   1.0000 |   272 |
|   16 |   0.1177 |   2.2734 |   1.0000 |   272 |
|   17 |   0.1202 |   2.3230 |   1.0000 |   272 |
|   18 |   0.1349 |   2.4421 |   1.0000 |   272 |
|   19 |   0.1492 |   2.4903 |   1.0000 |   272 |
|   20 |   0.1642 |   2.5265 |   1.0000 |   272 |
|   21 |   0.1555 |   2.5191 |   1.0000 |   272 |
|   22 |   0.1295 |   2.4982 |   1.0000 |   272 |
|   23 |   0.1189 |   2.7728 |   1.0000 |   272 |

## 5. Day-of-Week Analysis for Overnight Spikes

| Day | Spike Rows | Frames | Dates |  Avg Index |
|----|-----------|-------|------|-----------|
| Sun |      1,040 |     94 |    10 |     3.3188 | (73.8%)
| Mon |        180 |     36 |     1 |     4.3307 | (12.8%)
| Fri |          5 |      1 |     1 |     3.0631 | (0.4%)
| Sat |        185 |     37 |     2 |     3.4757 | (13.1%)

Weekend (Fri+Sat) share of overnight spikes: **13.5%**
Weekday share: **86.5%**

_Even distribution across week suggests transport hub or data artefact._

## 6. Sample Frames — Address Detail (top 30 by frame ID)

|      Frame | Town                 | Address                                  | Environment                    | POI                            |
|-----------|---------------------|-----------------------------------------|-------------------------------|-------------------------------|
| 1234853705 | Cardiff              | High Street adj Quay Street Cardiff      | Roadside                       |                                |
| 1234855934 | Cardiff              | o/s St Mary Street Cardiff               | Roadside                       |                                |
| 2000138301 | Cardiff              | St Mary St (OS No.114-116 Sainsburys)    | Roadside                       |                                |
| 2000138303 | Cardiff              | St Mary St (OS No.114-116 Sainsburys)    | Roadside                       |                                |
| 1234860293 | Derby                | (Lr) Shardlow Road Shardlow Road, Near H | Roadside                       |                                |
| 1234626091 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | Rail Station                   | Lime Street                    |
| 1234626091 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | RailStation                    | Lime Street                    |
| 1234848402 | Liverpool            | Roe Street o/s Royal Court Theatre City  | Roadside                       |                                |
| 1234848403 | Liverpool            | Roe Street nr St JOhns market entrance C | Roadside                       |                                |
| 1234849007 | Liverpool            | Ranelagh Street Church Street Liverpool  | Roadside                       |                                |
| 1234849033 | Liverpool            | Church Street o/s 9-15 H M Liverpool     | Roadside                       |                                |
| 1234849037 | Liverpool            | Church Street o/s 51-53 T K Maxx Liverpo | Roadside                       |                                |
| 1234849181 | Liverpool            | Lord Street o/s 67-79 Liverpool          | Roadside                       |                                |
| 1234853441 | Liverpool            | Parker Street o/s Tesco Liverpool        | Roadside                       |                                |
| 1234853442 | Liverpool            | Parker Street o/s Superdrug Liverpool    | Roadside                       |                                |
| 1234854479 | Liverpool            | o/s 83 Lord Street Liverpool             | Roadside                       |                                |
| 1234854483 | Liverpool            | o/s 45 Lord Street Liverpool             | Roadside                       |                                |
| 1234855614 | Liverpool            | Parker Street o/s Tesco Liverpool        | Roadside                       |                                |
| 1234855616 | Liverpool            | Ranelagh Street Church Street Liverpool  | Roadside                       |                                |
| 1234855618 | Liverpool            | Parker Street o/s Superdrug Liverpool    | Roadside                       |                                |
| 1234855620 | Liverpool            | Church Street o/s 51-53 T K Maxx Liverpo | Roadside                       |                                |
| 1234855622 | Liverpool            | Church Street o/s 9-15 H M Liverpool     | Roadside                       |                                |
| 1234855632 | Liverpool            | Lord Street o/s 67-79 Liverpool          | Roadside                       |                                |
| 1234861940 | Liverpool            | Roe Street o/s Royal Court Theatre City  | Roadside                       |                                |
| 1234933230 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | Rail Station                   | Lime Street                    |
| 1234933230 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | RailStation                    | Lime Street                    |
| 1234933231 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | Rail Station                   | Lime Street                    |
| 1234933231 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | RailStation                    | Lime Street                    |
| 1234933232 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | Rail Station                   | Lime Street                    |
| 1234933232 | Liverpool            | LIVERPOOL LIME STREET STN,SKELHORNE STRE | RailStation                    | Lime Street                    |

_... and 87 more frames not shown._

## 7. Frame Classification

| Classification                           | Frames | % of total |
|-----------------------------------------|-------|-----------|
| City centre / nightlife                  |      0 |       0.0% |
| Transport hub                            |     44 |      37.6% |
| Residential (possible artefact)          |      0 |       0.0% |
| Other / unknown                          |     73 |      62.4% |

## 8. Assessment

- Total overnight-only spiking frames: **117**
- Transport classification: **37.6%** of frames
- Nightlife classification: **0.0%** of frames
- Unclassified (other/unknown): **62.4%** of frames

### Conclusion

**LIKELY DATA ARTEFACT** — more than half of frames are unclassified, suggesting a systematic data anomaly rather than a real-world signal. Uniform day-of-week distribution (13.5% weekend) is inconsistent with nightlife and suggests transport or artefact.

### Recommended Next Steps

1. Cross-reference transport-classified frames against known UK station/airport locations.
2. For unclassified frames, inspect the raw `average_index` vs `median_index` divergence — large divergence suggests a few extreme outlier dates rather than consistent overnight elevation.
3. If median_index is near 1.0 for the same frames, the overnight spike is driven by a handful of extreme dates (likely artefact or one-off events) rather than systematic footfall.
4. Consider excluding frames with >3.0 average but <1.5 median from the mobile index application, as the median is a more robust measure.

---

_Research complete._
