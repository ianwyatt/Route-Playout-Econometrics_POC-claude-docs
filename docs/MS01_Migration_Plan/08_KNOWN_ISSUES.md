# Known Issues & Limitations - MS-01 Migration

**Date**: 2025-10-17
**Purpose**: Document current limitations, known issues, and their workarounds
**Status**: Comprehensive issue tracking

---

## Table of Contents

1. [Current Limitations](#current-limitations)
2. [Known Bugs](#known-bugs)
3. [Workarounds](#workarounds)
4. [Future Improvements](#future-improvements)
5. [When to Use Local vs MS-01](#when-to-use-local-vs-ms-01)

---

## Current Limitations

### L1: POC is Currently CSV-Based

**Description**: Main POC application still loads sample CSV files, not database

**Impact**:
- MS-01 helper functions exist but not used by UI yet
- Database switching works but UI doesn't benefit yet
- Need to manually integrate functions into services

**Severity**: Medium (expected for POC phase)

**Status**: Working as designed (WAD)

**Explanation**:
This is intentional POC architecture:
- CSV files faster for UI development and demos
- Database queries ready for when needed
- Migration to database is Phase 2 work

**Timeline**: Next sprint (integrate into UI)

**Workaround**: None needed - this is expected behavior

---

### L2: Connection Pooling Infrastructure Not Wired

**Description**: Connection pool code exists but not connected to main application

**Impact**:
- Pool initialized but never used by services
- Services receive `None` for database connections
- Missing performance benefits of pooling

**Severity**: Low (no impact until database integration)

**Status**: Deferred to integration phase

**Technical Details**:
```python
# Current state
class BrandSplitService:
    def __init__(self, db_config=None):
        self.db_config = db_config or DatabaseConfig()
        self._pool = None  # Created but not passed from main app

# Desired state (future)
# Main app creates pool once
await initialize_ms01_database()

# Services use shared pool
brand_service = BrandSplitService()  # Uses global pool
```

**Timeline**: This sprint (30 min effort)

**Workaround**: Services create their own pools (works but less efficient)

---

### L3: Database Switching Requires Restart

**Description**: Changing USE_MS01_DATABASE env var requires application restart

**Impact**:
- Cannot switch databases at runtime
- Must stop and restart to switch
- Less convenient for demos

**Severity**: Low (minor inconvenience)

**Status**: Working as designed

**Technical Details**:
- Environment variables loaded at startup
- Connection pools initialized once
- Restart required to reload config

**Timeline**: UI switcher in next sprint (will still require restart)

**Workaround**:
```bash
# Quick restart script
export USE_MS01_DATABASE=true
python main.py
```

**Future Enhancement**: Runtime database switching (production feature)

---

### L4: Data Freshness (24 Hour Lag)

**Description**: MS-01 materialized views refreshed daily at 2am UTC

**Impact**:
- Data may be up to 24 hours old
- Yesterday's playouts may not appear until tomorrow
- Real-time data not available

**Severity**: Low (acceptable for econometric analysis)

**Status**: Working as designed (managed by pipeline)

**Technical Details**:
- Views refreshed by pipeline cron job
- Full refresh takes ~2-3 hours
- Trade-off: freshness vs query performance

**Check Data Age**:
```python
from src.db.ms01_helpers import check_data_freshness

freshness = await check_data_freshness()
print(f"Data is {freshness['hours_old']:.1f} hours old")
```

**Timeline**: No change planned (acceptable for use case)

**Workaround**: Use local database with CSV for real-time testing

---

### L5: MS-01 Requires VPN/Network Access

**Description**: MS-01 at 192.168.1.34 requires VPN or local network

**Impact**:
- Cannot access MS-01 when not connected to VPN
- Remote work requires VPN setup
- Network issues block development

**Severity**: Medium (blocks offline work)

**Status**: Infrastructure constraint

**Affected Users**:
- Remote developers
- Demo presentations without VPN
- Offline development

**Timeline**: No change planned (security requirement)

**Workaround**:
1. **Always have local database ready**
   ```bash
   USE_MS01_DATABASE=false
   ```

2. **Use sample CSV files for demos**
   ```python
   # Fallback to CSV if MS-01 unavailable
   try:
       data = await get_campaign_for_route_api(...)
   except ConnectionError:
       data = pd.read_csv('playout_sample.csv')
   ```

3. **VPN auto-connect**
   ```bash
   # Add to shell profile
   alias ms01-connect="connect-vpn && export USE_MS01_DATABASE=true"
   ```

---

### L6: No UI Database Switcher Yet

**Description**: Can only switch databases by editing .env file

**Impact**:
- Non-technical users cannot switch databases
- Must edit file and restart
- Not user-friendly

**Severity**: Low (developer tool currently)

**Status**: Planned for next sprint

**Timeline**: 1-2 hours to implement (see 07_NEXT_STEPS.md)

**Workaround**:
```bash
# CLI helper script
./scripts/switch-database.sh ms01
./scripts/switch-database.sh local
```

---

### L7: Limited Route Release Coverage

**Description**: Only R54-R61 (Q1 2025 - Q4 2026) in database

**Impact**:
- Cannot query campaigns before April 2025
- Cannot query campaigns after April 2027
- Historical analysis limited

**Severity**: Low (covers current needs)

**Status**: Working as designed

**Date Coverage**:
- **Start**: 2025-04-07 (R54 trading period start)
- **End**: 2027-04-04 (R61 trading period end)
- **Gap**: Any date outside this range returns error

**Check Coverage**:
```python
from src.db.route_releases import validate_release_coverage

result = await validate_release_coverage(start_date, end_date)
if not result['has_coverage']:
    print(f"❌ {result['message']}")
    for gap in result['gaps']:
        print(f"   Gap: {gap[0]} to {gap[1]}")
```

**Timeline**: Add releases as they become available

**Workaround**: Use earliest/latest available dates

---

## Known Bugs

### B1: None Currently Identified

**Status**: No bugs found during testing

**Note**: Report new bugs through GitHub Issues or team Slack

---

## Workarounds

### W1: MS-01 Connection Timeout

**Symptom**:
```
❌ Connection Timeout
asyncio.exceptions.TimeoutError
```

**Cause**:
- Not connected to VPN
- Firewall blocking port 5432
- MS-01 server offline

**Workaround 1: Check VPN**
```bash
# Check VPN status
ifconfig | grep -A 5 tun0

# Reconnect VPN
sudo vpn-connect

# Test connectivity
ping -c 3 192.168.1.34
nc -zv 192.168.1.34 5432
```

**Workaround 2: Use Local Database**
```bash
# Edit .env
USE_MS01_DATABASE=false

# Restart application
```

**Workaround 3: Increase Timeout**
```bash
# Add to .env
DB_CONNECTION_TIMEOUT=30  # Increase from 10 to 30 seconds
```

---

### W2: Views Not Found

**Symptom**:
```
❌ relation "mv_playout_15min" does not exist
```

**Cause**:
- Materialized views not created yet
- Connected to wrong database
- Views dropped accidentally

**Workaround 1: Verify Database**
```python
from src.config.database import DatabaseConfig

config = DatabaseConfig()
info = config.get_active_database_info()
print(f"Connected to: {info['host']}/{info['database']}")

# Should show MS-01 if expecting views
```

**Workaround 2: Check Views Exist**
```sql
SELECT matviewname FROM pg_matviews
WHERE matviewname IN ('mv_playout_15min', 'mv_playout_15min_brands');
```

**Workaround 3: Contact Pipeline Team**
- Views should be created by pipeline setup
- SQL scripts in pipeline repository
- Team can recreate in 1-2 hours

**Temporary Workaround**: Use local database with CSV files

---

### W3: Permission Denied

**Symptom**:
```
❌ permission denied for table mv_playout_15min
```

**Cause**:
- User lacks SELECT permission on views
- User lacks INSERT permission on route_releases

**Workaround: Grant Permissions**
```sql
-- Run as postgres superuser
GRANT SELECT ON mv_playout_15min TO postgres;
GRANT SELECT ON mv_playout_15min_brands TO postgres;
GRANT ALL ON route_releases TO postgres;
GRANT USAGE, SELECT ON SEQUENCE route_releases_id_seq TO postgres;
```

**Temporary Workaround**: Use superuser credentials (not recommended for production)

---

### W4: Brand Split Doesn't Sum to 100%

**Symptom**:
```
⚠️  Brand split total: 999,999 (expected: 1,000,000)
```

**Cause**:
- Floating point precision errors
- Very rare with current implementation

**Expected Behavior**:
- Sum should equal total impacts within 1% (floating point tolerance)
- Difference <0.01% is acceptable

**Workaround: Normalize Proportions**
```python
# If you encounter this issue
total = sum(brand_impacts.values())
normalized = {
    brand: (impacts / total) * total_impacts
    for brand, impacts in brand_impacts.items()
}

# Verify sum
assert abs(sum(normalized.values()) - total_impacts) < 1.0
```

**Status**: Not observed in testing, but included for completeness

---

### W5: Route Release Not Found

**Symptom**:
```
❌ No Route release found for date 2024-03-15
```

**Cause**:
- Date outside available release coverage
- Release not in database

**Workaround 1: Check Coverage**
```python
from src.db.route_releases import get_all_releases

releases = await get_all_releases()
for r in releases:
    print(f"{r.release_number}: {r.trading_period_start} to {r.trading_period_end}")

# Use dates within range
```

**Workaround 2: Use Nearest Release**
```python
from datetime import date

# User wants 2024-03-15 (before R54)
# Use earliest available release instead
earliest_release = 'R54'
print(f"⚠️  Date outside coverage, using {earliest_release}")
```

**Timeline**: Add historical releases if needed

---

### W6: Query Timeout

**Symptom**:
```
❌ Query timeout after 60 seconds
```

**Cause**:
- Very large campaign (100K+ playouts)
- Network latency
- Database under load

**Workaround 1: Increase Timeout**
```bash
# Add to .env
DB_COMMAND_TIMEOUT=180  # Increase from 60 to 180 seconds
```

**Workaround 2: Narrow Date Range**
```python
# Instead of full campaign
data = await get_campaign_for_route_api(
    campaign_id,
    '2025-08-01',
    '2025-08-31'  # Full month: might timeout
)

# Break into chunks
chunks = []
for week in date_range('2025-08-01', '2025-08-31', weeks=1):
    chunk = await get_campaign_for_route_api(
        campaign_id,
        week['start'],
        week['end']
    )
    chunks.append(chunk)

data = pd.concat(chunks)
```

**Workaround 3: Use Pagination**
```python
# Future enhancement: add pagination to queries
# Current: not implemented, defer to performance optimization phase
```

---

## Future Improvements

### FI1: Runtime Database Switching

**Current**: Restart required to switch databases

**Improvement**:
- Switch databases at runtime
- Close old pool, open new pool
- No application restart

**Benefit**:
- Better demo experience
- Faster development iteration
- A/B testing databases

**Effort**: 1-2 days
**Priority**: Medium
**Timeline**: After production deployment

---

### FI2: Read Replicas for Scaling

**Current**: Single MS-01 database for reads and writes

**Improvement**:
- Add read replicas for MS-01
- Load balance queries across replicas
- Primary for writes, replicas for reads

**Benefit**:
- Support 100+ concurrent users
- Faster query response
- Better fault tolerance

**Effort**: 1 week (infrastructure + code)
**Priority**: Low (not needed until production scale)
**Timeline**: When concurrent users > 20

---

### FI3: Advanced Caching Layer

**Current**: Simple TTL cache (5-60 min)

**Improvement**:
- Redis cache layer
- Smarter cache invalidation
- Pre-warming for common queries

**Benefit**:
- 90%+ cache hit rate (vs current 70%)
- <10ms response time (vs current 100ms)
- Reduced database load

**Effort**: 3-5 days
**Priority**: Medium
**Timeline**: After CSV migration complete

---

### FI4: Query Result Pagination

**Current**: Return all results (may be large)

**Improvement**:
- Add LIMIT/OFFSET to queries
- Return page size + total count
- UI pagination controls

**Benefit**:
- Handle 1M+ record campaigns
- Faster initial load
- Better memory usage

**Effort**: 2-3 days
**Priority**: Medium
**Timeline**: If campaigns exceed 100K playouts

---

### FI5: Real-Time Data Refresh

**Current**: Views refreshed daily (24 hour lag)

**Improvement**:
- Incremental view refresh (every 1 hour)
- Or streaming from Kafka (real-time)

**Benefit**:
- Near real-time data (<1 hour old)
- Better for operational use cases

**Effort**: 2-4 weeks (pipeline team)
**Priority**: Low (not needed for econometrics)
**Timeline**: If real-time requirement emerges

---

### FI6: Historical Data Archival

**Current**: All data in MS-01 (1.28B records)

**Improvement**:
- Archive data older than 2 years
- Move to cheaper storage (S3, Glacier)
- On-demand restore for historical analysis

**Benefit**:
- Reduced MS-01 database size
- Lower storage costs
- Faster queries on recent data

**Effort**: 1-2 weeks (pipeline + POC)
**Priority**: Low
**Timeline**: When database size becomes issue

---

### FI7: Multi-User Concurrency Testing

**Current**: Tested with single user

**Improvement**:
- Load testing with 10, 50, 100+ users
- Identify bottlenecks
- Optimize connection pooling

**Benefit**:
- Confidence in production scale
- Identify issues before deployment

**Effort**: 2-3 days
**Priority**: High (before production)
**Timeline**: Next month

---

## When to Use Local vs MS-01

### Use MS-01 When:

✅ **Production Analysis**
- Real campaign data needed
- Econometric modeling
- Client deliverables

✅ **Large Campaigns**
- 10K+ playouts
- Multi-brand campaigns
- Date range >1 month

✅ **Performance Testing**
- Query optimization
- Load testing
- Benchmarking

✅ **Brand Attribution**
- Multi-brand campaigns
- Proportional impact splitting
- Brand-level reporting

---

### Use Local Database When:

✅ **UI Development**
- Building new features
- Layout/design work
- Frontend development

✅ **Demos Without VPN**
- Client presentations
- Conference demos
- Offline demonstrations

✅ **Quick Testing**
- Unit tests
- Integration tests
- Feature validation

✅ **Offline Work**
- No VPN access
- Poor network connection
- Working remotely

✅ **Development Iteration**
- Rapid prototyping
- Debugging
- Experimentation

---

### Decision Matrix

| Use Case | MS-01 | Local | Rationale |
|----------|-------|-------|-----------|
| Client analysis | ✅ | ❌ | Need real data |
| UI development | ❌ | ✅ | Faster iteration |
| Performance testing | ✅ | ❌ | Production scale |
| Demo (with VPN) | ✅ | ❌ | Show real capabilities |
| Demo (no VPN) | ❌ | ✅ | Local works offline |
| Unit tests | ❌ | ✅ | Fast, no network |
| Integration tests | ✅ | ❌ | Test real queries |
| Brand attribution | ✅ | ❌ | Needs brands view |
| Small campaigns | Either | Either | Both work fine |
| Large campaigns | ✅ | ❌ | Local has limited data |

---

## Issue Reporting

### How to Report New Issues

1. **Check This Document**: Issue may be already known
2. **Search Existing Issues**: May be already reported
3. **Create New Issue**: Use template below

**Issue Template**:
```markdown
## Issue Description
Brief description of the problem

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Database: MS-01 or Local
- Python version: X.Y.Z
- OS: MacOS/Linux/Windows
- Network: VPN or Local

## Error Message
```
Paste full error message here
```

## Screenshots
Attach if relevant

## Workaround
If you found a workaround, share it
```

### Issue Severity Levels

**Critical (P0)**:
- Application crash
- Data loss
- Security vulnerability
- **Response**: Immediate

**High (P1)**:
- Feature broken
- Major performance issue
- Blocking production
- **Response**: Within 24 hours

**Medium (P2)**:
- Workaround exists
- Minor performance issue
- UI/UX problem
- **Response**: Next sprint

**Low (P3)**:
- Enhancement request
- Minor inconvenience
- Documentation issue
- **Response**: Backlog

---

## Monitoring and Alerts

### Recommended Monitors

**MS-01 Connection Health**:
```python
@app.get("/health/ms01")
async def ms01_health():
    try:
        await initialize_ms01_database()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

**Data Freshness**:
```python
@app.get("/health/data-freshness")
async def data_freshness():
    freshness = await check_data_freshness()
    status = "healthy" if freshness['hours_old'] < 48 else "degraded"
    return {
        "status": status,
        "hours_old": freshness['hours_old']
    }
```

**Query Performance**:
```python
import time

async def monitored_query(campaign_id, start, end):
    start_time = time.time()
    result = await get_campaign_for_route_api(campaign_id, start, end)
    elapsed = time.time() - start_time

    if elapsed > 5.0:
        logger.warning(f"Slow query: {campaign_id} took {elapsed:.2f}s")

    return result
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Data age | >24 hours | >48 hours |
| Query time | >5 seconds | >30 seconds |
| Connection failures | >5% | >20% |
| Pool exhaustion | >80% | >95% |

---

## Summary

### Key Takeaways

1. **POC is CSV-based by design** - database integration is Phase 2
2. **MS-01 requires VPN** - always have local fallback ready
3. **Data refreshed daily** - 24 hour lag is acceptable
4. **Connection pooling needs wiring** - 30 min task for next sprint
5. **Most issues have workarounds** - document blockers only

### Production Readiness Checklist

Before going to production:

- [ ] All known issues addressed or documented
- [ ] Workarounds tested and validated
- [ ] Monitoring and alerts configured
- [ ] Fallback to local database tested
- [ ] Performance benchmarks met
- [ ] Multi-user concurrency tested
- [ ] Issue reporting process established

---

**Prepared By**: Claude Code Agent Team
**Date**: 2025-10-17
**Status**: Complete Issue Documentation
**Next Review**: After integration phase
