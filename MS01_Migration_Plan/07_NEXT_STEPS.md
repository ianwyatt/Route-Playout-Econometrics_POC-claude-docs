# Next Steps - MS-01 Migration Action Plan

**Date**: 2025-10-17
**Purpose**: Prioritized action items for completing MS-01 integration
**Status**: Ready for Execution

---

## Table of Contents

1. [Immediate Actions (This Week)](#immediate-actions-this-week)
2. [Short-Term Tasks (Next Sprint)](#short-term-tasks-next-sprint)
3. [Medium-Term Goals (Next Month)](#medium-term-goals-next-month)
4. [Long-Term Roadmap](#long-term-roadmap)
5. [Task Assignment Recommendations](#task-assignment-recommendations)

---

## Immediate Actions (This Week)

### Priority 1: Verify MS-01 Access

**Owner**: System Administrator / DevOps
**Estimated Time**: 30 minutes
**Blocking**: All other tasks

#### Tasks:
1. **Verify VPN/Network Access**
   ```bash
   # Test from development machine
   ping -c 3 192.168.1.34
   nc -zv 192.168.1.34 5432
   ```

   **If successful**:
   - ✅ Document VPN setup procedure
   - ✅ Share VPN credentials with team

   **If unsuccessful**:
   - 📞 Contact network team for firewall rules
   - 📞 Request VPN access if not available
   - 📋 Document fallback to local database

2. **Test Database Connection**
   ```bash
   # Test with credentials from .env
   PGPASSWORD='<password>' psql -h 192.168.1.34 -U postgres -d route_poc -c "SELECT version();"
   ```

   **If successful**:
   - ✅ Verify credentials in `.env` file
   - ✅ Document successful connection

   **If unsuccessful**:
   - 📞 Contact pipeline team for correct credentials
   - 📞 Verify user permissions (SELECT on views, ALL on route_releases)

3. **Check Required Database Objects**
   ```sql
   -- Check materialized views
   SELECT matviewname FROM pg_matviews
   WHERE matviewname IN ('mv_playout_15min', 'mv_playout_15min_brands');

   -- Should return 2 rows
   ```

   **If views missing**:
   - 📞 Contact pipeline team urgently
   - 📋 Request view creation using pipeline SQL scripts
   - ⏰ Estimate: 1-2 hours for pipeline team

**Deliverable**: Document with VPN setup, credentials, and connection test results

---

### Priority 2: Run Validation Scripts

**Owner**: Developer
**Estimated Time**: 15 minutes
**Dependency**: MS-01 access verified

#### Tasks:
1. **Setup Route Releases**
   ```bash
   python scripts/setup_route_releases.py
   ```

   **Success Criteria**: 8 releases (R54-R61) inserted

2. **Test MS-01 Helpers**
   ```bash
   python examples/ms01_helpers_example.py
   ```

   **Success Criteria**: All 17 functions execute without errors

3. **Test Brand Split Service**
   ```bash
   python src/services/test_brand_split.py
   ```

   **Success Criteria**: All brand splits sum to 100%

4. **Test Route Releases**
   ```bash
   python scripts/test_route_releases.py
   ```

   **Success Criteria**: All date lookups return correct releases

**Deliverable**: Test results report (screenshots or log output)

---

### Priority 3: Review Documentation

**Owner**: Tech Lead / Project Manager
**Estimated Time**: 1-2 hours
**Dependency**: None (can be done in parallel)

#### Documents to Review:
1. **Executive Summary** (`01_EXECUTIVE_SUMMARY.md`)
   - Verify business value aligns with goals
   - Confirm timeline is acceptable
   - Review success criteria

2. **Integration Guide** (`04_INTEGRATION_GUIDE.md`)
   - Understand integration approach
   - Identify any missing use cases
   - Note questions for developer

3. **Known Issues** (`08_KNOWN_ISSUES.md`)
   - Review limitations
   - Understand workarounds
   - Assess impact on project

**Deliverable**: Approval or feedback on documentation

---

## Short-Term Tasks (Next Sprint)

### Priority 4: Complete Integration (2-4 hours)

**Owner**: Lead Developer
**Estimated Time**: 2-4 hours
**Dependency**: MS-01 access verified, validation passed

#### Task 1: Wire Connection Pooling (30 minutes)

**Current State**: Pool infrastructure exists but not used by main app

**Steps**:
1. **Initialize Pool at App Startup**

   Edit main application entry point (e.g., `main.py`, `app.py`, or `__init__.py`):

   ```python
   # Add to startup function
   from src.db.ms01_helpers import initialize_ms01_database, close_ms01_database

   async def startup():
       """Initialize application resources."""
       # Existing startup code...

       # Add MS-01 initialization
       await initialize_ms01_database()
       logger.info("✅ MS-01 database pool initialized")

   async def shutdown():
       """Cleanup application resources."""
       # Add MS-01 cleanup
       await close_ms01_database()
       logger.info("MS-01 database pool closed")

       # Existing shutdown code...
   ```

2. **Wire to FastAPI/Flask** (if applicable)

   **FastAPI**:
   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.on_event("startup")
   async def startup_event():
       await initialize_ms01_database()

   @app.on_event("shutdown")
   async def shutdown_event():
       await close_ms01_database()
   ```

   **Flask**:
   ```python
   from flask import Flask
   import asyncio

   app = Flask(__name__)

   @app.before_first_request
   def initialize():
       asyncio.run(initialize_ms01_database())

   # Note: Flask cleanup is manual or use flask-async
   ```

3. **Test Pool is Active**
   ```python
   from src.db.ms01_helpers import _ms01_db

   async def test_pool():
       if _ms01_db.connection_pool:
           print(f"✅ Pool active with {_ms01_db.connection_pool.get_size()} connections")
       else:
           print("❌ Pool not initialized")
   ```

**Deliverable**: Connection pool initialized at app startup

#### Task 2: Add Database Switcher to UI (1-2 hours)

**Current State**: Database switched via .env only (requires restart)

**Options**:

**Option A: Settings Page** (Recommended for UI apps)
```python
# Add to settings page/route

from src.config.database import DatabaseConfig

async def get_database_status():
    """Get current database info for display."""
    config = DatabaseConfig()
    return config.get_active_database_info()

async def switch_database(use_ms01: bool):
    """Switch database (requires app restart)."""
    import os
    os.environ['USE_MS01_DATABASE'] = str(use_ms01).lower()

    # Update .env file
    # (code to update .env file)

    return {
        'status': 'success',
        'message': 'Database switched. Please restart application.',
        'new_database': 'MS-01' if use_ms01 else 'Local'
    }
```

**UI Component**:
```html
<div class="database-settings">
  <h3>Database Settings</h3>
  <p>Current: <strong id="current-db"></strong></p>

  <button onclick="switchDatabase(true)">Use MS-01 (Production)</button>
  <button onclick="switchDatabase(false)">Use Local (Dev/Demo)</button>

  <p class="warning">⚠️ Switching database requires application restart</p>
</div>
```

**Option B: CLI Command** (For development)
```bash
# Add CLI command
python manage.py switch-database --ms01
python manage.py switch-database --local

# Show current database
python manage.py database-info
```

**Option C: Runtime Switching** (Advanced, not needed for POC)
- Dynamically reconnect without restart
- More complex implementation
- Defer to production phase

**Deliverable**: UI control or CLI command for database switching

#### Task 3: Integrate Helper Functions into Services (1-2 hours)

**Current State**: Helper functions exist but not called by UI services

**Steps**:
1. **Identify UI Services Using CSV**

   Find code like:
   ```python
   # Old CSV-based code
   df = pd.read_csv('playout_sample.csv')
   campaign_data = df[df['campaignid'] == campaign_id]
   ```

2. **Replace with Database Queries**

   ```python
   # New database-based code
   from src.db.ms01_helpers import get_campaign_for_route_api

   campaign_data = await get_campaign_for_route_api(
       campaign_id,
       start_date,
       end_date
   )
   df = pd.DataFrame(campaign_data)
   ```

3. **Add Brand Split (if multi-brand)**

   ```python
   from src.services.brand_split_service import BrandSplitService

   # After Route API call
   brand_service = BrandSplitService()
   await brand_service.initialize()

   try:
       brand_results = await brand_service.aggregate_brand_impacts(route_response)
   finally:
       await brand_service.cleanup()
   ```

4. **Update Service Constructors**

   Pass database config to services:
   ```python
   from src.config.database import DatabaseConfig

   config = DatabaseConfig()
   brand_service = BrandSplitService(db_config=config)
   ```

**Deliverable**: At least one UI workflow uses MS-01 queries

---

### Priority 5: Testing Phase (2-3 hours)

**Owner**: QA / Developer
**Estimated Time**: 2-3 hours
**Dependency**: Integration complete

#### Task 1: End-to-End Workflow Testing

**Test Scenario 1**: Single-brand campaign
1. User enters campaign ID: `18295`
2. Date range: `2025-08-01` to `2025-09-01`
3. System queries MS-01 → builds Route API payload → calls Route API
4. Results displayed with correct impacts

**Test Scenario 2**: Multi-brand campaign
1. User enters campaign ID: `18699`
2. Date range: `2025-08-20` to `2025-08-25`
3. System queries MS-01 → builds Route API payload → calls Route API
4. Brand split service distributes impacts proportionally
5. Results show per-brand breakdown

**Test Scenario 3**: Database switching
1. Switch to Local database
2. Verify CSV data loaded
3. Switch back to MS-01
4. Verify production data accessible

#### Task 2: Error Handling Testing

**Test Error 1**: MS-01 connection failure
1. Disconnect from VPN
2. Attempt query
3. Verify graceful error message
4. Verify fallback to local or clear error

**Test Error 2**: Campaign not found
1. Query non-existent campaign ID: `99999`
2. Verify user-friendly error message
3. Verify no system crash

**Test Error 3**: Date outside release coverage
1. Query date before Q1 2025 (e.g., `2024-01-01`)
2. Verify error message explains release coverage
3. Verify suggests available date ranges

#### Task 3: Performance Testing

Run performance benchmarks (see `05_TESTING_VALIDATION.md`):
```bash
# Run benchmark suite
python tests/benchmark_ms01.py

# Expected: All queries < 5 seconds
```

**Deliverable**: Test report with pass/fail for each scenario

---

### Priority 6: User Acceptance Testing

**Owner**: Product Manager / End User
**Estimated Time**: 2-4 hours
**Dependency**: Testing phase complete

#### Activities:
1. **Demo MS-01 Capabilities**
   - Show query speed improvement
   - Demonstrate brand split feature
   - Show database switching

2. **Validate Business Requirements**
   - Verify outputs match econometric modeling needs
   - Confirm audience data accuracy
   - Check export formats are correct

3. **Gather Feedback**
   - UI/UX improvements needed?
   - Missing features?
   - Performance acceptable?

**Deliverable**: User acceptance sign-off or feedback for iteration

---

## Medium-Term Goals (Next Month)

### Priority 7: Production Preparation (1-2 days)

**Owner**: DevOps / Lead Developer
**Estimated Time**: 1-2 days
**Dependency**: UAT passed

#### Task 1: Optimize Connection Pool

**Current**: max_pool_size=10
**Production**: max_pool_size=30

```bash
# Update .env
POSTGRES_MAX_POOL=30

# Restart application
```

**Test**: Monitor connection pool utilization

#### Task 2: Add Monitoring and Alerting

```python
# Add health check endpoint
@app.get("/health/database")
async def database_health():
    from src.db.ms01_helpers import check_data_freshness

    freshness = await check_data_freshness()

    return {
        'status': 'healthy' if freshness['hours_old'] < 48 else 'degraded',
        'data_age_hours': freshness['hours_old'],
        'last_refresh': freshness['latest_playout'].isoformat()
    }
```

**Setup Alerts**:
- Alert if data >48 hours old
- Alert if connection pool exhausted
- Alert if query times >10 seconds

#### Task 3: Documentation Updates

**User Guides**:
- How to switch databases
- How to interpret brand split results
- Troubleshooting common errors

**Admin Guides**:
- Database maintenance procedures
- Connection pool tuning
- Performance optimization

**Deliverable**: Production-ready deployment

---

### Priority 8: Replace CSV Loading (2-3 days)

**Owner**: Developer
**Estimated Time**: 2-3 days
**Dependency**: Production stable

#### Current Architecture:
```
User Query → Load CSV → Process → Display
```

#### Target Architecture:
```
User Query → MS-01 Database → Process → Display
```

#### Tasks:
1. **Identify All CSV Loading Points**
   ```bash
   grep -r "read_csv" src/
   ```

2. **Replace with Database Queries**

   One file at a time:
   ```python
   # Before
   df = pd.read_csv('playout_sample.csv')

   # After
   from src.db.ms01_helpers import get_campaign_for_route_api
   data = await get_campaign_for_route_api(campaign_id, start, end)
   df = pd.DataFrame(data)
   ```

3. **Remove CSV Dependencies**

   Once all replaced:
   - Remove CSV sample files (or move to `/archive/`)
   - Update docs to reference database
   - Remove pandas CSV-specific code

4. **Add Caching Layer** (optional)

   Cache frequent queries:
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=100)
   async def cached_campaign_query(campaign_id, start, end):
       return await get_campaign_for_route_api(campaign_id, start, end)
   ```

**Deliverable**: POC fully database-backed (no CSV dependencies)

---

## Long-Term Roadmap

### Phase 1: Current (Complete)
- ✅ MS-01 helper functions
- ✅ Brand split service
- ✅ Route release lookups
- ✅ Database switching
- ✅ Documentation

### Phase 2: Integration (This Sprint)
- ⏳ Wire connection pooling
- ⏳ Add UI database switcher
- ⏳ Integrate helper functions into UI
- ⏳ End-to-end testing

### Phase 3: Production (Next Month)
- 📋 Optimize connection pool (30 connections)
- 📋 Add monitoring and alerting
- 📋 Replace all CSV loading with database queries
- 📋 Performance tuning

### Phase 4: Enhancements (Future)
- 📋 Advanced caching strategies
- 📋 Query optimization for large campaigns
- 📋 Real-time data refresh notifications
- 📋 Historical data archival
- 📋 Multi-user concurrency testing

### Phase 5: Scale Out (Future)
- 📋 Read replicas for MS-01
- 📋 Load balancing
- 📋 Horizontal scaling
- 📋 Geographic distribution (if needed)

---

## Task Assignment Recommendations

### By Role

#### System Administrator / DevOps
1. Verify MS-01 network access
2. Setup VPN for team
3. Configure firewall rules
4. Monitor connection pool in production
5. Setup alerting

**Estimated Effort**: 4-6 hours

#### Lead Developer
1. Wire connection pooling
2. Integrate helper functions into UI
3. Add database switcher
4. Performance optimization
5. Code reviews

**Estimated Effort**: 1-2 days

#### Developer
1. Replace CSV loading with database queries
2. Add error handling
3. Write tests
4. Update documentation
5. Bug fixes

**Estimated Effort**: 2-3 days

#### QA Engineer
1. Run validation scripts
2. End-to-end testing
3. Error handling testing
4. Performance testing
5. Create test reports

**Estimated Effort**: 1 day

#### Product Manager
1. Review documentation
2. User acceptance testing
3. Gather feedback
4. Prioritize enhancements
5. Stakeholder communication

**Estimated Effort**: 4-6 hours

### By Priority

#### Critical (Must have for launch)
1. ✅ MS-01 access verification
2. ✅ Validation scripts pass
3. ⏳ Wire connection pooling
4. ⏳ End-to-end testing
5. ⏳ User acceptance

**Timeline**: This week + next sprint (2 weeks)

#### Important (Should have soon)
1. 📋 UI database switcher
2. 📋 Monitoring/alerting
3. 📋 Performance optimization
4. 📋 Replace CSV loading

**Timeline**: Next month (4 weeks)

#### Nice to Have (Can wait)
1. 📋 Advanced caching
2. 📋 Read replicas
3. 📋 Real-time refresh
4. 📋 Historical archival

**Timeline**: Future phases (3+ months)

---

## Success Metrics

### This Week
- [ ] MS-01 connection verified
- [ ] All validation scripts pass
- [ ] Documentation reviewed

**Target**: 100% completion

### Next Sprint
- [ ] Connection pool wired to main app
- [ ] Database switcher in UI
- [ ] At least one workflow uses MS-01 queries
- [ ] End-to-end tests pass
- [ ] UAT sign-off

**Target**: 80% completion (acceptable to defer UI switcher)

### Next Month
- [ ] All CSV loading replaced
- [ ] Monitoring/alerting live
- [ ] Connection pool optimized
- [ ] Performance targets met
- [ ] Production deployment

**Target**: 90% completion

---

## Communication Plan

### Daily Standups
- Report progress on current task
- Blockers (especially MS-01 access issues)
- Coordination with pipeline team

### Weekly Status
- % completion of sprint goals
- Performance metrics
- Risks and mitigation

### Sprint Demo
- Show MS-01 integration working
- Demonstrate brand split feature
- Compare performance: CSV vs MS-01

---

## Risk Mitigation

### Risk 1: MS-01 Access Delayed
**Impact**: Blocks all work
**Mitigation**:
- Escalate to management if >48 hours
- Use local database for development
- Continue with documentation and UI work

### Risk 2: Views Don't Exist
**Impact**: Brand split won't work
**Mitigation**:
- Contact pipeline team immediately
- Use pipeline SQL scripts to create views
- Test with sample data if needed

### Risk 3: Performance Issues
**Impact**: Slow user experience
**Mitigation**:
- Add connection pooling (increases concurrency)
- Optimize queries (add indexes)
- Implement caching layer
- Consider read replicas

### Risk 4: Integration Complexity
**Impact**: Takes longer than estimated
**Mitigation**:
- Start with one simple workflow
- Iterate and expand coverage
- Keep CSV fallback available
- Pair programming for complex integrations

---

## Getting Help

### Documentation References
- **Integration Guide**: `04_INTEGRATION_GUIDE.md`
- **Testing Guide**: `05_TESTING_VALIDATION.md`
- **Prerequisites**: `06_PREREQUISITES_DEPENDENCIES.md`
- **Known Issues**: `08_KNOWN_ISSUES.md`

### Contacts
- **MS-01 Database Issues**: Pipeline team
- **VPN/Network Issues**: IT/Network team
- **Code Questions**: Lead developer
- **Business Requirements**: Product manager

### Support Channels
- **Slack**: #route-poc-dev (example)
- **Email**: ian@route.org.uk
- **Issues**: GitHub Issues (if using)

---

## Summary

### This Week (Critical)
1. ✅ Verify MS-01 access (30 min)
2. ✅ Run validation scripts (15 min)
3. ✅ Review documentation (1-2 hours)

**Total**: 2-3 hours

### Next Sprint (Important)
1. ⏳ Wire connection pooling (30 min)
2. ⏳ Add database switcher (1-2 hours)
3. ⏳ Integrate into UI (1-2 hours)
4. ⏳ Testing phase (2-3 hours)
5. ⏳ User acceptance (2-4 hours)

**Total**: 1-2 days

### Next Month (Enhancement)
1. 📋 Production preparation (1-2 days)
2. 📋 Replace CSV loading (2-3 days)

**Total**: 3-5 days

---

**Prepared By**: Claude Code Agent Team
**Date**: 2025-10-17
**Status**: Ready for Execution
**Next Review**: After this week's critical tasks
