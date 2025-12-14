# Pipeline Team Database Handover

**Created**: 2025-10-17
**Updated**: 2025-11-14
**Purpose**: Complete MS-01 database integration package for POC development
**Status**: ✅ **PRODUCTION READY** - All caches deployed (252.7M records, 66.8GB)

---

## 🎉 What's Ready for You

### ⭐ 252.7M Cached Records - 1,000-6,000x Faster Than API Calls

The pipeline team has deployed **three complete Route API cache systems** on MS-01 production database:

| Cache System | Records | Purpose | Speed Improvement |
|--------------|---------|---------|-------------------|
| **Demographic Cache** | 252.7M | 15-min audience impacts, 7 demographics | 1,000-6,000x |
| **Campaign Reach Cache** | 11,363 | Daily/weekly/full reach metrics | 1,000-6,000x |
| **Brand Reach Cache** | 17,406 | Brand-level performance | 1,000-6,000x |

**Result**: Your POC queries return in <5ms instead of 5-30s API calls. **99%+ API call reduction.**

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Database Password

Contact pipeline team (ian@route.org.uk) for `MS01_DB_PASSWORD`

### Step 2: Test Connection

```python
import psycopg2

conn = psycopg2.connect(
    host='192.168.1.34',
    port=5432,
    database='route_poc',
    user='postgres',
    password=os.getenv('POSTGRES_PASSWORD_MS01')  # Get from environment
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM cache_route_impacts_15min_by_demo;")
print(f"Cached records: {cursor.fetchone()[0]:,}")
# Expected: 252,660,891
```

### Step 3: Run Your First Cache Query

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

### 🎯 Start Here (Required Reading)

**For everyone new to the database:**

1. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Start here! (10 min read)
   - Connection details
   - Common queries
   - Performance rules
   - Route releases reference

2. **[CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md)** - ⭐ **PRIMARY GUIDE** (40+ examples)
   - Complete guide to all three cache systems
   - Demographic cache (252.7M records)
   - Campaign reach cache (11,363 records)
   - Brand reach cache (17,406 records)
   - 40+ SQL query examples with expected outputs
   - When to use cache vs call API directly
   - Performance best practices

3. **[API_INTEGRATION_GUIDE.md](./API_INTEGRATION_GUIDE.md)** - 🚨 **CRITICAL**
   - Frame limits explained (grouping vs non-grouping) - #1 pitfall!
   - Cache-first integration pattern
   - Rate limiting (6 calls/sec per account)
   - Frame validation workflow
   - Error handling with exponential backoff
   - 5 common pitfalls + 3 complete Python examples

4. **[PYTHON_EXAMPLES.py](./PYTHON_EXAMPLES.py)** - Copy & run (20 min)
   - Database connection management
   - Campaign data retrieval
   - Route release determination
   - Brand split functions
   - Working examples with output

---

### 📖 Complete Reference

5. **[DATABASE_HANDOVER_FOR_POC.md](./DATABASE_HANDOVER_FOR_POC.md)** - Deep dive
   - Complete database architecture
   - All table/view descriptions
   - Aggregation formulas
   - Performance optimization
   - Troubleshooting guide
   - Design decisions

6. **[ROUTE_API_LIMITS_GROUPING_VS_NON_GROUPING.md](./ROUTE_API_LIMITS_GROUPING_VS_NON_GROUPING.md)** - Critical
   - Route API frame limits explained in detail
   - WITH grouping: 10,000 frame limit (per-frame breakdown)
   - WITHOUT grouping: NO LIMIT (aggregate metrics)
   - Decision matrices
   - Common mistakes and solutions

---

### 🔄 Staying In Sync

7. **[CHANGELOG_FOR_POC.md](./CHANGELOG_FOR_POC.md)** - ⚠️ **CHECK WEEKLY**
   - Pipeline changes affecting POC
   - [BREAKING], [FEATURE], [FYI] updates
   - Migration guides
   - Action required items

8. **[SYNC_STRATEGY.md](./SYNC_STRATEGY.md)** - Communication
   - How to stay informed
   - Change notification methods
   - Contact information

9. **[FUTURE_ROADMAP.md](./FUTURE_ROADMAP.md)** - What's coming
   - Planned features
   - Implementation timeline
   - Impact on POC

---

## 🎯 Documentation Reading Order

### New Developers (First Time)

1. **QUICK_REFERENCE.md** (10 min) - Get oriented
2. **PYTHON_EXAMPLES.py** (20 min) - Run examples
3. **CACHE_USAGE_GUIDE.md** (45 min) - Learn cache queries
4. **API_INTEGRATION_GUIDE.md** (30 min) - Understand API patterns

**Total time**: ~2 hours to full productivity

### Architects & Tech Leads

1. **DATABASE_HANDOVER_FOR_POC.md** (45 min) - Complete architecture
2. **CACHE_USAGE_GUIDE.md** (30 min) - Cache capabilities
3. **API_INTEGRATION_GUIDE.md** (20 min) - Integration patterns
4. **ROUTE_API_LIMITS_GROUPING_VS_NON_GROUPING.md** (15 min) - Critical limits

**Total time**: ~2 hours for complete understanding

---

## 📊 Database Overview

### MS-01 Production Database

**Connection:**
```
Host: 192.168.1.34
Port: 5432
Database: route_poc
User: postgres
Password: [MS01_DB_PASSWORD env var]
```

**Data Scale:**
- **1.28 billion** raw playout records (500GB)
- **252.7 million** cached demographic records (66GB)
- **11,363** campaign reach cache records (4.7MB)
- **17,406** brand reach cache records (6.2MB)
- **826 campaigns** fully cached
- **69 days** coverage (Aug 6 - Oct 13, 2025)
- **Daily refresh** at 2am UTC

**Total storage**: ~567GB (500GB playout + 67GB cache)

---

## 💡 Key Use Cases

### 1. Query Cached Demographics (Recommended)

```python
# Get all demographics for a campaign on a specific date
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

### 2. Query Campaign Reach Metrics

```python
# Get daily reach, GRP, frequency for campaign
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
# Get full campaign reach by brand
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

**See CACHE_USAGE_GUIDE.md for 40+ complete examples**

---

## ⚡ Performance Tips

### DO ✅

1. **Query cache tables first** - 1,000-6,000x faster than API
2. **Use time filters** - `WHERE time_window_start >= '2025-08-01'`
3. **Use connection pooling** - For multi-threaded apps
4. **Multiply impacts by 1000** - Stored as thousands in cache
5. **Filter by campaign_id** - Reduces result set

### DON'T ❌

1. **Don't call Route API** for cached campaigns
2. **Don't query without time filters** - Scans entire table
3. **Don't use DATE() function** on indexed columns
4. **Don't forget impacts are in thousands** - Multiply by 1000!
5. **Don't assume real-time data** - Refreshed daily at 2am UTC

---

## 🔑 Key Concepts

### 15-Minute Time Windows

All data aggregated to 15-minute boundaries:
- `:00`, `:15`, `:30`, `:45` past each hour
- Spot at `12:14:59` → `12:00:00` window
- Spot at `12:15:00` → `12:15:00` window

### 7 Demographic Segments

1. `all_adults` - All adults 15+
2. `age_15_34` - Young adults
3. `age_35_54` - Middle-aged adults
4. `age_55_plus` - Older adults
5. `abc1` - Higher socio-economic groups
6. `c2de` - Lower socio-economic groups
7. `housewife` - Main household shopper

### Impacts Stored in Thousands

**CRITICAL**: All `impacts` values are **divided by 1000**

```sql
-- WRONG: Returns impacts in thousands
SELECT impacts FROM cache_route_impacts_15min_by_demo;

-- CORRECT: Multiply by 1000
SELECT impacts * 1000 as actual_impacts FROM cache_route_impacts_15min_by_demo;
```

---

## 🎯 Typical POC Workflow

```
1. User selects campaign + date range in UI
           ↓
2. Check cache first (query cache tables) ← RECOMMENDED
           ↓ (if cache miss)
3. Query mv_playout_15min (get frames)
           ↓
4. Validate frames exist in Route
           ↓
5. Determine Route release
           ↓
6. Build Route API payload
           ↓
7. POST to Route API
           ↓
8. Store in cache for future use (optional)
           ↓
9. Display results in POC application
```

**Performance**: Cache query (<5ms) vs API call (5-30s) = **1,000-6,000x faster**

---

## 📞 Support & Contact

### Questions About:

- **Database connection**: See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **Cache queries**: See [CACHE_USAGE_GUIDE.md](./CACHE_USAGE_GUIDE.md)
- **Route API integration**: See [API_INTEGRATION_GUIDE.md](./API_INTEGRATION_GUIDE.md)
- **Python examples**: See [PYTHON_EXAMPLES.py](./PYTHON_EXAMPLES.py)
- **Database issues**: Pipeline team (ian@route.org.uk)

### Pipeline Team

**Contact**: ian@route.org.uk
**Database**: MS-01 @ 192.168.1.34:5432/route_poc
**Credentials**: Request `MS01_DB_PASSWORD`

---

## 🔄 Data Refresh Schedule

- **Frequency**: Daily at 2am UTC
- **Duration**: ~50-60 minutes
- **Method**: Concurrent refresh (non-blocking)
- **Freshness**: Data may be up to 24 hours old

**Check freshness:**
```python
cursor.execute("SELECT MAX(cached_at) FROM cache_route_impacts_15min_by_demo;")
print(f"Last update: {cursor.fetchone()[0]}")
```

---

## ⚠️ Important Notes

1. **Data Freshness**: Refreshed daily, may be up to 24 hours old
2. **Impacts in Thousands**: Always multiply by 1000 in queries
3. **Time Boundaries**: Strict 15-minute boundaries (:00, :15, :30, :45)
4. **Frame Limits**: WITH grouping = 10,000 frame max, WITHOUT = no limit
5. **Rate Limiting**: 6 calls/sec per API account (use cache first!)

---

## 🎉 You're Ready!

If you can successfully run the quick start queries above, you're ready to integrate the MS-01 database.

**Next Steps:**
1. ✅ Read QUICK_REFERENCE.md for common queries
2. ✅ Run examples from PYTHON_EXAMPLES.py
3. ✅ Study CACHE_USAGE_GUIDE.md for cache integration
4. ✅ Implement cache-first pattern in your POC
5. ✅ Check CHANGELOG_FOR_POC.md weekly

**Questions?** Contact the pipeline team at ian@route.org.uk

**Good luck with POC development!** 🚀

---

**Package Version**: 2.0
**Last Updated**: 2025-11-14
**Status**: ✅ PRODUCTION READY
**For**: Route Playout Econometrics POC Development Team
