# MS-01 Database Quick Reference

**Database**: MS-01 PostgreSQL @ 192.168.1.34:5432
**Database Name**: route_poc
**Last Updated**: 2025-10-17

---

## Connection

```python
import psycopg2

conn = psycopg2.connect(
    host="192.168.1.34",
    port=5432,
    database="route_poc",
    user="postgres",
    password=os.getenv('MS01_DB_PASSWORD')
)
```

---

## Primary Tables/Views

| Name | Rows | Purpose | Use For |
|------|------|---------|---------|
| `playout_data` | 1.28B | Raw playout events | Debugging, millisecond analysis |
| `mv_playout_15min` ⭐ | 700M | 15-min aggregations | **Route API calls (PRIMARY)** |
| `mv_playout_15min_brands` | 750M | Brand tracking | Brand-level reporting |
| `route_releases` | 8 | Route metadata | Route release lookups |
| `playout_dates` | 35 | Daily summaries | Quick date checks |

⭐ = **Use this for POC development**

---

## Key Concepts

### 15-Minute Windows

```
Time boundaries: :00, :15, :30, :45 past each hour

Examples:
- 12:00:00, 12:15:00, 12:30:00, 12:45:00
- Spot at 12:14:59 → 12:00:00 window
- Spot at 12:15:00 → 12:15:00 window
```

### Aggregation Formula

```python
spot_count = COUNT(*)                               # Number of playouts
playout_length_seconds = ROUND(AVG(spotlength/1000)) # Avg duration (rounded)
break_length_seconds = ROUND((900 - total_content) / spot_count)
```

### Unique Constraint

`mv_playout_15min` guarantees **ONE row** per:
- (frameid, time_window_start, buyercampaignref)

---

## Most Common Queries

### 1. Get Campaign Data for Route API ⭐

```sql
SELECT
    frameid,
    time_window_start as datetime_from,
    time_window_start + INTERVAL '15 minutes' as datetime_to,
    spot_count,
    playout_length_seconds,
    break_length_seconds
FROM mv_playout_15min
WHERE buyercampaignref = '18295'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
ORDER BY frameid, time_window_start;
```

### 2. Campaign Summary Stats

```sql
SELECT
    COUNT(DISTINCT frameid) as frames,
    SUM(spot_count) as total_spots,
    MIN(time_window_start) as start_date,
    MAX(time_window_start) as end_date,
    ROUND(AVG(playout_length_seconds), 1) as avg_spot_length
FROM mv_playout_15min
WHERE buyercampaignref = '18295';
```

### 3. Route Release Lookup

```sql
SELECT release_number, name
FROM route_releases
WHERE '2025-09-15'::date BETWEEN trading_period_start AND trading_period_end;
-- Returns: R55, Q2 2025
```

### 4. Hourly Activity

```sql
SELECT
    DATE_TRUNC('hour', time_window_start) as hour,
    SUM(spot_count) as total_spots
FROM mv_playout_15min
WHERE buyercampaignref = '18295'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
GROUP BY DATE_TRUNC('hour', time_window_start)
ORDER BY hour;
```

### 5. Brand Split (if needed)

```sql
SELECT
    spacebrandid,
    SUM(spots_for_brand) as total_spots
FROM mv_playout_15min_brands
WHERE buyercampaignref = '18295'
  AND time_window_start >= '2025-08-01'
  AND time_window_start < '2025-09-01'
GROUP BY spacebrandid
ORDER BY total_spots DESC;
```

---

## Route Releases (R54-R61)

| Release | Name | Trading Period Start | Trading Period End |
|---------|------|----------------------|--------------------|
| R54 | Q1 2025 | 2025-04-07 | 2025-06-29 |
| R55 | Q2 2025 | 2025-06-30 | 2025-09-28 |
| R56 | Q3 2025 | 2025-09-29 | 2026-01-04 |
| R57 | Q4 2025 | 2026-01-05 | 2026-03-29 |
| R58 | Q1 2026 | 2026-03-30 | 2026-06-28 |
| R59 | Q2 2026 | 2026-06-29 | 2026-09-27 |
| R60 | Q3 2026 | 2026-09-28 | 2027-01-03 |
| R61 | Q4 2026 | 2027-01-04 | 2027-04-04 |

---

## Performance Rules

### ✅ DO

1. **Always filter by time_window_start**
   ```sql
   WHERE time_window_start >= '2025-08-01'
     AND time_window_start < '2025-09-01'
   ```

2. **Use >= and < for dates** (not BETWEEN or DATE())
   ```sql
   -- GOOD
   WHERE time_window_start >= '2025-08-01'
     AND time_window_start < '2025-09-01'

   -- BAD
   WHERE DATE(time_window_start) = '2025-08-01'
   ```

3. **Filter by campaign OR frame** (pick one)
   ```sql
   WHERE buyercampaignref = '18295'
     AND time_window_start >= ...
   ```

4. **Use LIMIT for pagination**
   ```sql
   LIMIT 1000 OFFSET 0
   ```

### ❌ DON'T

1. **Query without time filter**
   ```sql
   -- BAD: Scans 700M rows!
   WHERE buyercampaignref = '18295'
   ```

2. **Use functions on indexed columns**
   ```sql
   -- BAD: Can't use index
   WHERE DATE(time_window_start) = '2025-08-01'
   ```

3. **Use OR on different columns**
   ```sql
   -- BAD: Can't use composite indexes
   WHERE buyercampaignref = '18295' OR frameid = '1234567890'
   ```

---

## Indexes

### mv_playout_15min

```sql
-- UNIQUE (required for concurrent refresh)
idx_mv_playout_15min_pk
    (frameid, time_window_start, buyercampaignref)

-- Campaign queries
idx_mv_playout_15min_campaign_time
    (buyercampaignref, time_window_start)

-- Frame queries
idx_mv_playout_15min_frame_time
    (frameid, time_window_start)

-- Time-only queries
idx_mv_playout_15min_time
    (time_window_start)

-- Media owner filtering
idx_mv_playout_15min_mediaowner
    (spacemediaownerid)
```

---

## Data Volume

- **Date Range**: Aug 6 - Oct 13, 2025 (69 days)
- **Total Records**: 1.28 billion raw playouts
- **Aggregated**: ~700 million 15-minute windows
- **Database Size**: 596 GB
- **Refresh**: Daily at 2am UTC (~30 minutes)

---

## Field Reference

### mv_playout_15min Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `frameid` | VARCHAR(50) | Digital frame identifier |
| `buyercampaignref` | VARCHAR(50) | Campaign ID (can be NULL) |
| `time_window_start` | TIMESTAMP | 15-min boundary (:00, :15, :30, :45) |
| `spot_count` | INTEGER | Number of playouts in window |
| `playout_length_seconds` | INTEGER | Avg spot duration (rounded) |
| `break_length_seconds` | INTEGER | Avg break duration (rounded) |
| `spacemediaownerid` | VARCHAR(50) | Media owner ID |
| `spacebuyerid` | VARCHAR(50) | Buyer organization ID |
| `spaceagencyid` | VARCHAR(50) | Agency ID |

---

## Python Helper Functions

### Get Campaign Data

```python
def get_route_api_data(campaign_id, start_date, end_date):
    """Fetch aggregated data for Route API."""
    query = """
        SELECT frameid, time_window_start, spot_count,
               playout_length_seconds, break_length_seconds
        FROM mv_playout_15min
        WHERE buyercampaignref = %s
          AND time_window_start >= %s
          AND time_window_start < %s
        ORDER BY frameid, time_window_start
    """
    return execute_query(query, (campaign_id, start_date, end_date))
```

### Get Route Release

```python
def get_route_release(playout_date):
    """Determine Route release for a date."""
    query = """
        SELECT release_number, name
        FROM route_releases
        WHERE %s::date BETWEEN trading_period_start AND trading_period_end
    """
    result = execute_query(query, (playout_date,))
    return result[0] if result else None
```

### Split Audience by Brand

```python
def split_audience_by_brand(frame_id, campaign_id, window_start, total_impacts):
    """Split impacts proportionally by brand."""
    query = """
        SELECT spacebrandid,
               spots_for_brand,
               spots_for_brand::FLOAT / SUM(spots_for_brand) OVER () as proportion
        FROM mv_playout_15min_brands
        WHERE frameid = %s
          AND buyercampaignref = %s
          AND time_window_start = %s
    """
    brands = execute_query(query, (frame_id, campaign_id, window_start))

    return [{
        'brand_id': b['spacebrandid'],
        'spots': b['spots_for_brand'],
        'impacts': total_impacts * b['proportion']
    } for b in brands]
```

---

## Troubleshooting

### Query is Slow

1. Check time filter exists
2. Run `EXPLAIN ANALYZE` to check index usage
3. Add LIMIT for pagination
4. Use connection pooling

### No Data Returned

1. Verify campaign exists: `SELECT COUNT(*) FROM mv_playout_15min WHERE buyercampaignref = 'XXX'`
2. Check date range: `SELECT MIN(time_window_start), MAX(time_window_start) FROM mv_playout_15min WHERE buyercampaignref = 'XXX'`
3. Check for NULL campaign (house ads)

### Unexpected Counts

Remember: 150 raw spots = 1 aggregated row with spot_count=150

---

## Important Notes

1. **Data Freshness**: Refreshed daily, may be up to 24 hours old
2. **Normalized Values**: playout_length and break_length are rounded averages
3. **Time Boundaries**: Strict 15-minute boundaries (:00, :15, :30, :45)
4. **NULL Campaigns**: ~5-10% of records have NULL buyercampaignref (house ads)
5. **Brand Changes**: Some windows have multiple brands (use mv_playout_15min_brands)

---

## Support

**Full Documentation**: `Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md`

**Pipeline Team**: ian@route.org.uk

---

**Status**: ✅ PRODUCTION READY
**Last Updated**: 2025-10-17
