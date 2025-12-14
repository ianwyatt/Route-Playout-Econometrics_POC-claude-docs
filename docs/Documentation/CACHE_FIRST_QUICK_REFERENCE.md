# Cache-First Pattern - Quick Reference Card

**One-Page Guide for Developers** | Last Updated: 2025-11-14

---

## 🎯 What Was Implemented?

PostgreSQL cache-first pattern for **1000-6000x speedup** on cached campaigns.

**Files Modified**:
- `/src/api/campaign_service.py` - Added cache check at start of `query_campaign()`
- `/src/db/cache_queries.py` - Made date parameters optional

---

## 🔄 How It Works

```
User Requests Campaign
         ↓
   Mock Mode? ──Yes──→ Use Mock Data (skip cache)
         ↓ No
   Check PostgreSQL Cache
         ↓
    Cached? ──Yes──→ Return in <5ms ⚡
         ↓ No
   Call Route API (5-30s)
         ↓
   Return API Data
```

---

## 📊 Response Metadata

**Every response includes**:
```python
{
    'from_cache': True/False,      # Was data from cache?
    'cache_type': 'postgresql'/'none',  # Cache type
    'response_time_ms': 4.2,       # Query time in ms
    'total_time': 4.2              # Total processing time
}
```

---

## 🧪 Quick Test

```python
from src.api.campaign_service import CampaignService
import asyncio

service = CampaignService()

# Test cached campaign (should be <5ms)
result = asyncio.run(service.query_campaign('16932'))
print(f"Cache: {result['from_cache']}, Time: {result['response_time_ms']}ms")

# Test uncached campaign (should fallback to API)
result = asyncio.run(service.query_campaign('99999'))
print(f"Cache: {result['from_cache']}, Time: {result['response_time_ms']}ms")
```

**Or run full test suite**:
```bash
python tests/test_cache_first_pattern.py
```

---

## 📝 Key Code Locations

### Cache Check (campaign_service.py, lines 70-117)
```python
if not use_mock:
    cached_data = query_demographic_cache(
        campaign_id=campaign_id,
        start_date=None,  # Get all dates
        end_date=None,
        demographic_segments=None,  # All 7 demographics
        use_ms01=True
    )

    if cached_data is not None and not cached_data.empty:
        # ✅ CACHE HIT - Format and return
        result = self._format_cached_data_for_ui(...)
        result['from_cache'] = True
        return result
```

### Cache Query (cache_queries.py, lines 14-82)
```python
def query_demographic_cache(
    campaign_id: str,
    start_date: Optional[str] = None,  # Now optional!
    end_date: Optional[str] = None,
    demographic_segments: Optional[List[str]] = None,
    use_ms01: bool = True
) -> Optional[pd.DataFrame]:
    # Returns DataFrame with all dates if start/end are None
```

### Data Formatter (campaign_service.py, lines 403-503)
```python
def _format_cached_data_for_ui(
    self,
    cached_df: pd.DataFrame,
    campaign_id: str,
    aggregate_by: str
) -> Dict[str, Any]:
    # Transforms cache DataFrame to UI-compatible dict
```

---

## ⚠️ Critical Requirements Met

- ✅ Impacts already multiplied by 1000 (in cache_queries.py)
- ✅ Frame validation handled elsewhere (don't duplicate)
- ✅ USE_MS01_DATABASE = True
- ✅ Skip cache if use_mock = True
- ✅ All 7 demographics returned
- ✅ Date range extracted from data (MIN/MAX)
- ✅ Backward compatible

---

## 🔍 Logging Examples

```
INFO: ✅ PostgreSQL Cache HIT for campaign 16932 (4704 records, 4.2ms)
INFO: ⚠️ PostgreSQL Cache MISS for campaign 99999 (3.1ms) - calling Route API
WARNING: ❌ PostgreSQL Cache ERROR for campaign 16932: timeout - falling back to Route API
```

---

## 📈 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Cache HIT | <5ms | PostgreSQL query time |
| Cache MISS | 5-30s | Route API fallback (normal) |
| Cache Hit Rate | >80% | Monitor in production |

---

## 🐛 Troubleshooting

**Cache not being used?**
1. Check if `USE_MOCK_DATA=true` (skip cache in mock mode)
2. Verify campaign is in cache: `check_campaign_cached('16932')`
3. Check logs for ERROR messages

**Slow cache queries?**
1. Ensure date filters are included (if range is small)
2. Check PostgreSQL connection (MS-01: 192.168.1.34)
3. Verify `use_ms01=True`

**Wrong impacts values?**
1. Impacts should be multiplied by 1000 automatically
2. Check you're not multiplying again (already done in cache_queries.py)
3. Verify `all_adults` demographic is being used (avoid double-counting)

---

## 📚 Documentation

**Full Details**: `/Claude/Documentation/CACHE_FIRST_IMPLEMENTATION_SUMMARY.md`
**Critical Facts**: `/Claude/Documentation/CRITICAL_CACHE_FACTS.md`
**Database Schema**: `/docs/pipeline-handover/DATABASE_HANDOVER_FOR_POC.md`

---

## ✅ Next Steps

1. **Test**: Run `python tests/test_cache_first_pattern.py`
2. **Measure**: Record actual cache hit times
3. **Monitor**: Add cache metrics to dashboard
4. **Optimize**: Fine-tune based on performance data
5. **UI**: Update UI to show cache status badge

---

**Implementation Status**: ✅ COMPLETE
**Testing Required**: YES
**Production Ready**: After testing
