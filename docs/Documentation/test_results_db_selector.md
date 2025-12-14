# Database Selector Test Results

**Date:** October 21, 2025
**Test:** Database switching functionality

---

## Test Summary: ✅ PASSED

The database selector successfully switches between MS-01 (Production) and Local Mac (Development) databases, retrieving different data from each.

---

## Database Comparison

### Campaign Count
- **MS-01 (Production)**: 1,019 campaigns
- **Local Mac (Development)**: 470 campaigns

### Date Range
- **MS-01 (Production)**: Aug 6 - Oct 13, 2025 (10 weeks)
- **Local Mac (Development)**: Oct 6 - Oct 13, 2025 (1 week)

---

## Test Campaign: 15285

### Local Mac Database
```
Playouts:    2,852,812
Frames:      190
Date Range:  Oct 6 - Oct 13, 2025
```

### MS-01 Database
```
Playouts:    2,872,120 (+19,308 vs Local)
Frames:      190
Date Range:  Oct 3 - Oct 13, 2025
```

**Explanation:** MS-01 has 19,308 additional playouts because it includes Oct 3-5 data that Local Mac doesn't have.

---

## Functional Tests

### ✅ Test 1: Query Local Mac Database
- Successfully retrieved 5 campaigns
- Most recent campaign: 15782 (721,914 playouts)
- Connection: localhost:5432, user=ianwyatt

### ✅ Test 2: Query MS-01 Database
- Successfully retrieved 5 campaigns
- Most recent campaign: 15884 (1,447,732 playouts)
- Connection: 192.168.1.34:5432, user=postgres

### ✅ Test 3: Campaign Summary Switching
- Successfully retrieved campaign 15285 from both databases
- Data correctly differs between databases
- Date ranges match expected data availability

### ✅ Test 4: Streamlit UI Integration
- Database selector radio buttons working
- Session state properly maintained
- Cache clearing on database switch
- Auto-reload after database change

---

## UI Features Verified

1. **Database Selector in Sidebar**
   - Radio button: "MS-01 (Production)" vs "Local Mac (Development)"
   - Shows connection status with ✅
   - Displays database statistics

2. **Smart Cache Management**
   - `st.cache_data.clear()` called on database switch
   - Fresh data loaded from selected database
   - No stale data issues

3. **Session State**
   - `use_ms01_database` tracks current selection
   - `previous_db_selection` detects changes
   - Triggers rerun only when database actually changes

---

## Code Changes

### Modified Files
1. `src/db/streamlit_queries.py`
   - `get_db_connection(use_ms01)` - accepts database parameter
   - `get_all_campaigns_sync(limit, use_ms01)` - passes selection
   - `get_campaign_summary_sync(campaign_id, use_ms01)` - passes selection

2. `src/ui/app_campaign_selector.py`
   - Added session state for database selection
   - Added database selector UI in sidebar
   - Updated all function calls to pass database selection
   - Removed duplicate sidebar section

3. `test_db_selector.py` - NEW
   - Programmatic test of database switching
   - Verifies both databases are accessible
   - Compares data between databases

---

## Performance Notes

- Database connections are synchronous (psycopg2)
- New connection created for each query (no pooling)
- Cache TTL: 5 minutes for campaign list
- Database switch clears all cached data

---

## Next Steps

1. Wait for cached audiences to be populated by pipeline team
2. Use cached data where available before resorting to live API
3. Implement Route API integration for campaigns without cached data
4. Add export functionality (CSV, Excel, Parquet)

---

**Status:** Database selector fully functional and tested ✅
