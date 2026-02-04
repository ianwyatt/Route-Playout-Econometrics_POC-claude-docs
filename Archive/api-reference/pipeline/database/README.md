# Pipeline Database Handover - POC Integration Guide

**Last Updated:** 2025-11-14
**Database:** Primary Production (your_host_here:5432/route_poc)
**Status:** ✅ PRODUCTION READY - All caches deployed and verified

---

## 🎯 Quick Start (5 Minutes)

### Step 1: Get Database Password
Contact pipeline team (ian@route.org.uk) for `DB_PASSWORD`

### Step 2: Test Connection
```python
import psycopg2

conn = psycopg2.connect(
    host='your_host_here',
    port=5432,
    database='route_poc',
    user='postgres',
    password=os.environ['DB_PASSWORD']  # Get from environment
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM cache_route_impacts_15min_by_demo;")
print(f"Cached records: {cursor.fetchone()[0]:,}")
# Expected output: Cached records: 252,660,891
```

### Step 3: Run First Cache Query
```python
# Get cached demographic data for campaign 18425
cursor.execute("""
    SELECT
        time_window_start,
        demographic_segment,
        impacts * 1000 as impacts  -- Convert from thousands
    FROM cache_route_impacts_15min_by_demo
    WHERE campaign_id = '18425'
      AND time_window_start::date = '2025-10-06'
    ORDER BY time_window_start, demographic_segment
    LIMIT 10;
""")

for row in cursor.fetchall():
    print(row)
```

**If this works, you're ready!** ✅

---

## 📚 Documentation Files

### 1. [CONNECTION.md](./CONNECTION.md) - Database Connection Details
- Primary production database connection
- Credentials and environment setup
- Connection pooling examples
- Security best practices

### 2. [CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md) - Querying Cached Data
- Complete guide to all three cache systems (252.7M records)
- 40+ SQL query examples with expected outputs
- Demographic cache (15-minute granularity, 7 segments)
- Campaign reach cache (daily/weekly/full aggregations)
- Brand reach cache (brand-level performance metrics)
- Performance best practices (<5ms query times)

### 3. [API_INTEGRATION_GUIDE.md](./API_INTEGRATION_GUIDE.md) ⭐ **CRITICAL - READ THIS**
- **🚨 Frame limits explained** (grouping vs non-grouping) - #1 pitfall!
- Cache-first integration workflow
- When to use cache vs call Route API directly
- Frame validation workflow (prevents error 220)
- Rate limiting and dual account strategy (6 calls/sec per account)
- Authentication and credentials
- Error handling with exponential backoff
- Complete working Python examples
- Common pitfalls and solutions

### 4. [SCHEMA_REFERENCE.md](./SCHEMA_REFERENCE.md) - Database Schema
- All cache table structures and columns
- Indexes and query optimization
- Materialized views (15min, 1hr, day aggregations)
- Raw playout data tables
- SPACE lookup tables

---

## 🚀 Cache Systems Overview

### Three Primary Caches (252.7M Records, 66.8GB)

| Cache System | Records | Size | Purpose |
|--------------|---------|------|---------|
| **Demographic Cache** | 252.7M | 66 GB | 15-min audience impacts, 7 demographics |
| **Campaign Reach** | 11,363 | 4.7 MB | Daily/weekly/full reach metrics |
| **Brand Reach** | 17,406 | 6.2 MB | Brand-level performance |
| **TOTAL** | **252.7M** | **66.8 GB** | **826 campaigns cached** |

### Performance Benefits

- **1,000-6,000x faster** than Route API calls
- **Sub-second queries** (<5ms typical)
- **99%+ API call reduction** for cached campaigns
- **No rate limits** or API costs

### Date Coverage

- **Primary Production**: 2025-08-06 to 2025-10-13 (69 days)
- **Secondary Development**: Last 7 days only (rolling retention)
- **Refresh Schedule**: Daily at 2am UTC

---

## 💡 Integration Workflow

### Cache-First Pattern (Recommended)

```python
def get_campaign_audience_data(campaign_id, date_range):
    """
    Recommended pattern: Check cache first, fall back to Route API
    """
    # Step 1: Try cache (sub-second response)
    cached_data = query_cache_demographic_table(campaign_id, date_range)

    if cached_data:
        logger.info(f"Cache HIT for campaign {campaign_id}")
        return cached_data  # 1,000-6,000x faster!

    # Step 2: Cache miss - call Route API
    logger.info(f"Cache MISS for campaign {campaign_id} - calling Route API")
    api_data = call_route_api(campaign_id, date_range)

    # Step 3: (Optional) Store API response for future use
    store_in_cache(api_data)

    return api_data
```

**See [INTEGRATION_PATTERNS.md](./INTEGRATION_PATTERNS.md) for complete examples**

---

## 🎯 Common Use Cases

### 1. Get Campaign Demographic Breakdown
```python
# Query: All demographics for campaign on specific date
query = """
    SELECT
        demographic_segment,
        SUM(impacts * 1000) as total_impacts
    FROM cache_route_impacts_15min_by_demo
    WHERE campaign_id = %s
      AND time_window_start::date = %s
    GROUP BY demographic_segment
    ORDER BY total_impacts DESC;
"""
cursor.execute(query, ('18425', '2025-10-06'))
```

### 2. Get Campaign Reach Metrics
```python
# Query: Daily reach, GRP, frequency for campaign
query = """
    SELECT date, reach, grp, frequency, total_impacts
    FROM cache_campaign_reach_day
    WHERE campaign_id = %s
    ORDER BY date;
"""
cursor.execute(query, ('18425',))
```

### 3. Compare Brand Performance
```python
# Query: Full campaign reach by brand
query = """
    SELECT
        brand_id,
        reach,
        grp,
        frequency,
        total_impacts
    FROM cache_campaign_brand_reach
    WHERE campaign_id = %s
      AND aggregation_level = 'full'
    ORDER BY reach DESC;
"""
cursor.execute(query, ('18425',))
```

**See [CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md) for 40+ complete examples**

---

## ⚡ Performance Tips

### DO ✅

1. **Query cache tables first** before calling Route API
2. **Use time filters** to leverage indexes (`WHERE time_window_start >= ...`)
3. **Use connection pooling** for multi-threaded apps
4. **Cache API responses** for frequently accessed campaigns
5. **Filter by campaign_id** to reduce result set

### DON'T ❌

1. **Don't call Route API** for cached campaigns (use cache!)
2. **Don't query without time filters** (scans entire table)
3. **Don't use DATE() function** on indexed columns (breaks index)
4. **Don't forget to multiply impacts by 1000** (stored as thousands)
5. **Don't assume data is real-time** (refreshed daily at 2am UTC)

---

## 🔑 Key Concepts

### 15-Minute Time Windows

All cached data is aggregated to 15-minute boundaries:
- `:00`, `:15`, `:30`, `:45` past each hour
- Spot at `12:14:59` → `12:00:00` window
- Spot at `12:15:00` → `12:15:00` window

### Demographic Segments (7 Total)

1. `all_adults` - All adults 15+
2. `age_15_34` - Young adults
3. `age_35_54` - Middle-aged adults
4. `age_55_plus` - Older adults
5. `abc1` - Higher socio-economic groups
6. `c2de` - Lower socio-economic groups
7. `housewife` - Main household shopper

### Impacts Stored in Thousands

**IMPORTANT**: All `impacts` values in cache tables are **divided by 1000**

```sql
-- WRONG: Returns impacts in thousands
SELECT impacts FROM cache_route_impacts_15min_by_demo;

-- CORRECT: Multiply by 1000 for actual impacts
SELECT impacts * 1000 as actual_impacts FROM cache_route_impacts_15min_by_demo;
```

---

## 📞 Support & Contact

### Questions About:

- **Database connection**: See [CONNECTION.md](./CONNECTION.md)
- **Cache queries**: See [CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md)
- **Integration patterns**: See [INTEGRATION_PATTERNS.md](./INTEGRATION_PATTERNS.md)
- **Schema details**: See [SCHEMA_REFERENCE.md](./SCHEMA_REFERENCE.md)
- **Route API calls**: See [../ROUTE_API_CACHING_GUIDE.md](../ROUTE_API_CACHING_GUIDE.md)

### Pipeline Team

**Contact**: ian@route.org.uk
**Database**: Primary @ your_host_here:5432/route_poc
**Credentials**: Request `DB_PASSWORD`

---

## 🔄 Data Refresh Schedule

- **Frequency**: Daily at 2am UTC
- **Duration**: ~50-60 minutes (materialized views + cache refresh)
- **Method**: Concurrent refresh (non-blocking)
- **Freshness**: Data may be up to 24 hours old

### Check Data Freshness

```python
cursor.execute("""
    SELECT MAX(cached_at) as last_cache_update
    FROM cache_route_impacts_15min_by_demo;
""")
print(f"Last cache update: {cursor.fetchone()[0]}")
```

---

## 🎉 You're Ready!

**Key Integration Steps:**

1. ✅ Get database credentials from pipeline team
2. ✅ Test connection with quick start example above
3. ✅ Read [INTEGRATION_PATTERNS.md](./INTEGRATION_PATTERNS.md) for cache-first workflow
4. ✅ Review [CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md) for query examples
5. ✅ Implement cache-first pattern in your POC application

**Questions?** Contact the pipeline team at ian@route.org.uk

**Good luck with POC development!** 🚀

---

**Document Version**: 1.0
**Created**: 2025-11-14
**Status**: ✅ PRODUCTION READY
**For**: Route Playout Econometrics POC Development Team
