# MS-01 Migration Quick Start Guide

**Last Updated**: 2025-10-17

This is a condensed version of the full migration plan. For complete details, see [MS01_MIGRATION_PLAN.md](./MS01_MIGRATION_PLAN.md).

---

## Quick Migration (5 Minutes)

### Step 1: Update .env File

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC

# Add to .env:
USE_MS01_DATABASE=true
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
MS01_DB_PASSWORD=<ask-pipeline-team>
```

### Step 2: Test Connection

```python
# test_ms01_connection.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="192.168.1.34",
    port=5432,
    database="route_poc",
    user="postgres",
    password=os.getenv('MS01_DB_PASSWORD')
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM mv_playout_15min LIMIT 1")
print("✅ Connected to MS-01!")
cursor.close()
conn.close()
```

Run test:
```bash
python test_ms01_connection.py
```

### Step 3: Update Your Queries

**Before (Local)**:
```python
query = "SELECT * FROM playout_data WHERE buyercampaignref = %s"
```

**After (MS-01)**:
```python
query = """
    SELECT * FROM mv_playout_15min
    WHERE buyercampaignref = %s
      AND time_window_start >= %s
      AND time_window_start < %s
"""
```

**Key changes**:
- Table: `playout_data` → `mv_playout_15min`
- **ALWAYS** add `time_window_start` filter
- Use `>=` and `<` for date ranges

### Step 4: Restart App

```bash
streamlit run src/ui/app.py
```

---

## Critical Rules

### ✅ DO

1. **Always filter by time_window_start**:
   ```sql
   WHERE time_window_start >= '2025-08-01'
     AND time_window_start < '2025-09-01'
   ```

2. **Use mv_playout_15min** (not playout_data)

3. **Use SUM(spot_count)** for total playouts (not COUNT(*))

4. **Test queries with EXPLAIN ANALYZE**

### ❌ DON'T

1. Query without time filter (will scan 700M rows!)
2. Use DATE() or BETWEEN functions
3. Try to access millisecond precision (data is 15-min aggregated)

---

## Quick Rollback

If something breaks:

```bash
# Edit .env
USE_MS01_DATABASE=false

# Restart app
pkill -f streamlit && streamlit run src/ui/app.py
```

---

## Performance Targets

| Query Type | Expected Time |
|------------|---------------|
| Campaign query (1 month) | < 1 second |
| Campaign summary | < 0.5 seconds |
| Window lookup | < 0.1 seconds |

If slower than this, check:
1. Is time filter present?
2. Run EXPLAIN ANALYZE
3. Add LIMIT for pagination

---

## Common Query Patterns

### Get Campaign Data for Route API

```python
query = """
    SELECT
        frameid,
        time_window_start as datetime_from,
        time_window_start + INTERVAL '15 minutes' as datetime_to,
        spot_count,
        playout_length_seconds,
        break_length_seconds
    FROM mv_playout_15min
    WHERE buyercampaignref = %s
      AND time_window_start >= %s
      AND time_window_start < %s
    ORDER BY frameid, time_window_start
"""
```

### Campaign Summary

```python
query = """
    SELECT
        COUNT(DISTINCT frameid) as total_frames,
        SUM(spot_count) as total_playouts,
        MIN(time_window_start) as start_date,
        MAX(time_window_start) as end_date
    FROM mv_playout_15min
    WHERE buyercampaignref = %s
"""
```

### Hourly Breakdown

```python
query = """
    SELECT
        DATE_TRUNC('hour', time_window_start) as hour,
        SUM(spot_count) as total_playouts
    FROM mv_playout_15min
    WHERE buyercampaignref = %s
      AND time_window_start >= %s
      AND time_window_start < %s
    GROUP BY DATE_TRUNC('hour', time_window_start)
    ORDER BY hour
"""
```

---

## Database Details

- **Host**: 192.168.1.34:5432
- **Database**: route_poc
- **Primary View**: mv_playout_15min
- **Records**: 700M aggregated windows (1.28B raw playouts)
- **Date Range**: Aug 6 - Oct 13, 2025
- **Refresh**: Daily at 2am UTC

---

## Need Help?

**Full Documentation**: [MS01_MIGRATION_PLAN.md](./MS01_MIGRATION_PLAN.md)

**Database Handover**: `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md`

**Quick Reference**: `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/POC_Handover/QUICK_REFERENCE.md`

**Contact**: ian@route.org.uk

---

**Status**: Ready to migrate!
