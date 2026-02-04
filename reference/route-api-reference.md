# Route API Reference

> **Note**: This is reference material only. The POC never calls APIs directly — it reads from PostgreSQL cache populated by the `route-playout-pipeline` repo.

---

## Route API

- **Endpoint**: `https://route.mediatelapi.co.uk/`
- **Playout Endpoint**: `https://route.mediatelapi.co.uk/rest/process/playout`
- **Purpose**: Audience measurement (impacts per frame playout)
- **Important**: Only use playout audiences endpoint. Do NOT retrieve reach-only data.
- **Frames not in Route**: Assign zero audience (impacts = 0)

### Pipeline Process
1. Group frames by 15-minute intervals
2. Call Route API with grouped frames
3. Retrieve impacts per frame
4. Cache results in PostgreSQL

### API Request Example
```json
{
  "route_release_id": "55",
  "route_algorithm_version": "10.2",
  "algorithm_figures": ["impacts"],
  "grouping": "frame_ID",
  "demographics": ["ageband>=1"],
  "campaign": [{
    "schedule": [{"datetime_from": "2025-07-28 00:00", "datetime_until": "2025-07-28 00:14"}],
    "spot_length": 10,
    "spot_break_length": 50,
    "frames": [1234723633, 2000032505]
  }],
  "target_month": 1
}
```

---

## SPACE API

- **Endpoint**: `https://oohspace.co.uk/api`
- **Purpose**: Decode playout data IDs
- **Lookups**: `spacemediaownerid` → Media Owner, `spacebuyerid` → Buyer, `spaceagencyid` → Agency, `spacebrandid` → Brand, `frameid` → Frame Metadata

---

## Route Releases

**Query Available Releases**: `POST https://route.mediatelapi.co.uk/rest/version` (last 5 releases only)

| Name    | Release | Trading Period Start | Trading Period End |
|---------|---------|---------------------|-------------------|
| Q1 2025 | R54     | 07/04/2025          | 29/06/2025        |
| Q2 2025 | R55     | 30/06/2025          | 28/09/2025        |
| Q3 2025 | R56     | 29/09/2025          | 04/01/2026        |
| Q4 2025 | R57     | 05/01/2026          | 29/03/2026        |
| Q1 2026 | R58     | 30/03/2026          | 28/06/2026        |
| Q2 2026 | R59     | 29/06/2026          | 27/09/2026        |
| Q3 2026 | R60     | 28/09/2026          | 03/01/2027        |
| Q4 2026 | R61     | 04/01/2027          | 04/04/2027        |

---

*Moved from CLAUDE.md — February 2026*
