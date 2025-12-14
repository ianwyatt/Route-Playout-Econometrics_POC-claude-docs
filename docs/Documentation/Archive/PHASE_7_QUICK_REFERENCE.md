# Phase 7 Integration Tests - Quick Reference

## Test Execution

### Run All Tests
```bash
python -m pytest tests/test_phase7_integration.py -v -s
```

### Run Specific Test
```bash
python -m pytest tests/test_phase7_integration.py::TestPhase7Integration::test_1_cached_campaign_performance -v
```

### Run Without Pytest (Direct)
```bash
python tests/test_phase7_integration.py
```

---

## Test Coverage

| Test # | Name | Campaign | Purpose | Expected Result |
|--------|------|----------|---------|-----------------|
| 1 | Cached Campaign | 16932 | Cache HIT performance | <5s, 7 demographics |
| 2 | Uncached Campaign | 99999 | API fallback | No crash, graceful fallback |
| 3 | Large Campaign | 18295 | Large dataset handling | <90s, 19.3M records |
| 4 | Performance Benchmark | 16932 | Cache consistency | Avg <5s, 3 runs |

---

## Test Results Summary

**Status:** ✅ ALL TESTS PASSED (4/4)
**Execution Time:** ~90 seconds
**Date:** November 15, 2025

### Key Metrics

- **Cache HIT Time:** 1.7s - 3.6s (962K records)
- **Cache MISS Fallback:** 1.3s (50 API calls)
- **Large Campaign:** 29.2s query, 58.4s total (19.3M records)
- **Speedup vs API:** 2400x - 8500x

---

## Test Scenarios

### 1. Cached Campaign (16932)
**Expected:**
- from_cache: True
- cache_type: 'postgresql'
- response_time_ms: <5000ms
- demographics: 7 segments

**Validates:**
- Cache HIT detection
- Fast retrieval (<5s)
- All 7 demographics returned
- Impacts multiplied by 1000

### 2. Uncached Campaign (99999)
**Expected:**
- from_cache: False
- cache_type: 'none'
- No crashes/exceptions

**Validates:**
- Cache MISS detection
- Graceful API fallback
- Mixed success/failure handling

### 3. Large Campaign (18295)
**Expected:**
- Success: True
- response_time_ms: <90000ms
- Records: 19.3M+

**Validates:**
- Large dataset processing
- No grouping errors
- Acceptable performance

### 4. Performance Benchmark
**Expected:**
- avg_time_ms: <5000ms
- 3 successful runs

**Validates:**
- Cache consistency
- Performance distribution
- Speedup documentation

---

## Configuration Requirements

### Environment Variables (.env)
```bash
USE_MS01_DATABASE=true
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_DATABASE_MS01=route_poc
USE_MOCK_DATA=false
```

### Database
- **Host:** MS-01 (192.168.1.34)
- **Database:** route_poc
- **Table:** cache_route_impacts_15min_by_demo
- **Size:** 1.28B records, 596GB

---

## Troubleshooting

### Test Failures

**"Cache query took Xms, expected <5000ms"**
- Adjust threshold in test file (line 85)
- Check network latency to MS-01
- Verify database performance

**"Missing demographic segment: X"**
- Check actual demographics in cache
- Run: `python3 -c "from src.db.cache_queries import query_demographic_cache; df = query_demographic_cache('16932'); print(df['demographic_segment'].unique())"`
- Update expected_segments list (line 93)

**"psycopg2.OperationalError: could not connect"**
- Verify MS-01 database is running
- Check .env: USE_MS01_DATABASE=true
- Test connection: `psql -h 192.168.1.34 -U postgres -d route_poc`

### Performance Issues

**Slow cache queries (>10s)**
- Check network connectivity to MS-01
- Monitor database load: `SELECT * FROM pg_stat_activity;`
- Consider connection pooling

**Large campaign timeout (>90s)**
- Increase timeout in test (line 205)
- Check if pagination needed for UI
- Monitor memory usage

---

## Test File Structure

```
tests/test_phase7_integration.py
├── TestPhase7Integration (class)
│   ├── test_1_cached_campaign_performance()
│   ├── test_2_uncached_campaign_fallback()
│   ├── test_3_large_campaign_grouping()
│   └── test_4_performance_benchmark()
├── print_test_summary()
└── run_all_tests() (for direct execution)
```

---

## Dependencies

### Python Packages
- pytest
- pytest-asyncio
- pandas
- psycopg2-binary
- asyncio

### Services Required
- PostgreSQL (MS-01)
- Route API (live)
- SPACE API (live)

---

## Success Criteria Checklist

- [x] Cache HIT occurs for campaign 16932
- [x] Response time <5s for 962K records
- [x] All 7 demographics returned
- [x] Impacts multiplied by 1000
- [x] Cache MISS graceful fallback works
- [x] No crashes on uncached campaign
- [x] Large campaign (19.3M records) processes <90s
- [x] Performance benchmark shows cache speedup
- [x] No API error 221 (grouping limit)
- [x] All tests pass (4/4)

---

## Next Steps After Testing

1. **Review Test Results**
   - See `PHASE_7_TEST_RESULTS.md` for detailed analysis
   - Check performance metrics against requirements
   - Document any anomalies or issues

2. **Production Optimizations**
   - Implement connection pooling
   - Add pagination for large campaigns
   - Setup monitoring and alerting
   - Optimize slow queries

3. **UI Integration**
   - Display "from cache" indicator
   - Show loading progress for large campaigns
   - Implement demographic selector
   - Add export functionality

4. **Documentation Updates**
   - Update API documentation
   - Create deployment guide
   - Write operational runbook
   - Document cache refresh process

---

**Last Updated:** November 15, 2025
**Test File:** `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/tests/test_phase7_integration.py`
**Results Document:** `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/PHASE_7_TEST_RESULTS.md`
