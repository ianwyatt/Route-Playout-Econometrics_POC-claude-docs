# Pipeline Team Documentation

**Purpose**: Documentation for data engineers and pipeline developers working with Route API caching and data integration for the Route Playout Econometrics POC.

**⚠️ IMPORTANT UPDATE (October 26, 2025)**: Documentation updated with Route API **custom endpoint** optimization. Use minimal payloads with `["impacts"]` only for fastest caching performance (~2x faster than requesting all metrics). See [ROUTE_API_CACHING_GUIDE.md](./ROUTE_API_CACHING_GUIDE.md) for details.

---

## 📚 Documentation Index

### 🎯 Database Integration (NEW - November 2025) ⭐
- **[database/README.md](./database/README.md)** - **START HERE for database integration**
  - Complete database handover package
  - Primary production database (252.7M cached records)
  - 5-minute quick start with working examples
  - Cache systems overview (demographic, campaign reach, brand reach)
  - Performance guide (sub-second queries vs API calls)
- **[database/API_INTEGRATION_GUIDE.md](./database/API_INTEGRATION_GUIDE.md)** - 🚨 **CRITICAL - Route API integration**
  - **Frame limits explained** (grouping vs non-grouping) - #1 pitfall!
  - Cache-first integration pattern (1,000-6,000x faster)
  - Frame validation workflow
  - Rate limiting (6 calls/sec per account, dual account strategy)
  - Error handling with exponential backoff
  - 3 complete Python examples

### Quick Start
- **[QUICK_START.md](./QUICK_START.md)** - Get caching in 5 minutes
  - Minimal working example
  - Common issues and fixes
  - Verification queries

### Complete Guide
- **[ROUTE_API_CACHING_GUIDE.md](./ROUTE_API_CACHING_GUIDE.md)** - Comprehensive implementation guide
  - Route API endpoint details
  - Custom demographics and questionnaire endpoint
  - Database schema
  - Complete workflows
  - Error handling
  - Performance optimization
  - Monitoring and maintenance

### Examples
- **[EXAMPLES_QUESTIONNAIRE.md](./EXAMPLES_QUESTIONNAIRE.md)** - Questionnaire endpoint examples
  - Query available demographic variables
  - Build custom demographic targets
  - Cache custom demographics
  - Common demographic scenarios
- **[R56_QUESTIONNAIRE_REFERENCE.md](./R56_QUESTIONNAIRE_REFERENCE.md)** - R56 complete reference ⭐
  - Actual R56 (Q3 2025) questionnaire response
  - All 792 available variables
  - Variable categories and usage
  - Search and exploration guide

### Troubleshooting
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common problems and solutions
  - Timeout errors
  - Authentication failures
  - Data quality issues
  - Performance problems

---

## 🎯 What This Documentation Covers

### Route API Integration
- Calling the Route **custom** endpoint (optimized for demographics)
- Dual authentication (Basic Auth + X-Api-Key)
- Request/response formats
- Release mapping and versioning
- **Performance optimization**: Minimal payloads for fastest processing

### Data Caching
- PostgreSQL cache table schemas
- Insert/update strategies (UPSERT)
- Cache invalidation
- Data freshness management

### Performance
- Batch processing strategies
- Parallel worker patterns
- Timeout optimization
- Connection pooling

### Monitoring
- Cache coverage metrics
- Progress tracking
- Health checks
- Logging best practices

---

## 🚀 Quick Links

### For New Developers
1. Read [QUICK_START.md](./QUICK_START.md) first
2. Run the minimal example
3. Verify cache in database
4. Move to [ROUTE_API_CACHING_GUIDE.md](./ROUTE_API_CACHING_GUIDE.md) for production

### For Experienced Developers
1. Check [Database Schema](#database-schema) section
2. Review [Error Handling](#error-handling)
3. Implement [Performance Optimization](#performance-optimization)
4. Setup [Monitoring](#monitoring)

### For Troubleshooting
1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Review error logs
3. Query cache health metrics
4. Contact POC team if unresolved

---

## 📊 Key Concepts

### Cache Tables

#### Primary: `cache_campaign_reach_day`
Daily audience metrics per campaign:
- Reach (000s people)
- GRP (Gross Rating Points)
- Frequency (average views per person)
- Total impacts (000s impressions)
- Frame count

#### Detailed: `cache_route_impacts_15min`
15-minute interval impacts:
- Frame-level granularity
- Time window specific
- Used for detailed analysis

### Data Flow

```
PostgreSQL (mv_playout_15min)
    ↓ Query playouts
Python Script
    ↓ Build request
Route API
    ↓ Get audience data
Python Script
    ↓ Calculate metrics
PostgreSQL (cache_campaign_reach_day)
    ↓ Query cache
POC Application (Streamlit)
```

### Route Releases

Route audience data is quarterly:
- **R56** (Q3 2025): Sep 29, 2025 - Jan 4, 2026
- **R55** (Q2 2025): Jun 30, 2025 - Sep 28, 2025
- **R54** (Q1 2025): Apr 7, 2025 - Jun 29, 2025

Only last 5 releases available via API.

---

## 🛠️ Tools and Scripts

### Backfill Script
Located in `route-playout-pipeline` repository:
```bash
python scripts/tools/backfill_route_cache.py --granularity campaign-full
```

### Progress Tracking
```sql
SELECT
    COUNT(DISTINCT campaign_id) as cached,
    (SELECT COUNT(DISTINCT buyercampaignref) FROM mv_playout_15min) as total,
    ROUND(100.0 * COUNT(DISTINCT campaign_id) /
          (SELECT COUNT(DISTINCT buyercampaignref) FROM mv_playout_15min), 1) as percent
FROM cache_campaign_reach_day;
```

### Cache Verification
```sql
SELECT
    campaign_id,
    COUNT(*) as days_cached,
    MIN(date) as first_date,
    MAX(date) as last_date,
    MAX(cached_at) as last_update
FROM cache_campaign_reach_day
WHERE campaign_id = '15884'
GROUP BY campaign_id;
```

---

## 📈 Performance Expectations

### API Response Times
- **Small campaigns** (<50 frames, <100k playouts): 5-15 seconds
- **Medium campaigns** (50-150 frames, 100k-1M playouts): 15-60 seconds
- **Large campaigns** (150+ frames, 1M+ playouts): 60-180 seconds

### Processing Speed
- **Serial processing**: ~48 campaigns/hour
- **3 parallel workers**: ~144 campaigns/hour
- **With 120s timeout**: 80-90% success rate

### Database Performance
- **Cache query**: <10ms (indexed)
- **Playout query** (mv_playout_15min): <100ms
- **Insert/upsert**: <5ms

---

## 🔒 Security Notes

### Credentials
- ✅ Store in `.env` file (gitignored)
- ✅ Use environment variables only
- ❌ Never hardcode credentials
- ❌ Never commit `.env` to git

### Pre-commit Hooks
The project has hooks that block commits containing:
- API keys
- Passwords
- Tokens
- Secret patterns

### Database Access
- Use read-only user for POC queries
- Use write user only for caching scripts
- Implement connection pooling
- Close connections properly

---

## 📞 Support

### Documentation
- **Route API**: `docs/api-reference/route/`
- **SPACE API**: `docs/api-reference/space/`
- **Playout Schema**: `docs/playout/`
- **POC Architecture**: `docs/01-architecture.md`

### Issues
- Pipeline issues: `route-playout-pipeline` repository
- POC issues: This repository
- API issues: Route support team

### Contact
- POC Team: See `CLAUDE.md` for team info
- Pipeline Team: See `route-playout-pipeline` README

---

## 🎓 Learning Path

### Beginner
1. ✅ Read Quick Start
2. ✅ Run minimal example
3. ✅ Understand cache schema
4. ✅ Verify cached data

### Intermediate
1. ✅ Implement error handling
2. ✅ Add retry logic
3. ✅ Setup logging
4. ✅ Monitor progress

### Advanced
1. ✅ Parallel processing
2. ✅ Performance optimization
3. ✅ Cache invalidation
4. ✅ Production deployment

---

## 📝 Recent Updates

**October 22, 2025**
- Created pipeline documentation
- Added quick start guide
- Documented cache schema
- Added troubleshooting guide

---

## 🔗 Related Documentation

- [Project Specification](../../../CLAUDE.md)
- [Route API Documentation](../route/)
- [SPACE API Documentation](../space/)
- [Database Schema](../../playout/)
- [UI Guide](../../02-ui-guide.md)

---

**Version**: 1.1
**Last Updated**: November 14, 2025
**Maintained By**: Route POC Team

---

## 🆕 Recent Updates (November 14, 2025)

### Database Integration Documentation
- ✅ Created `database/` subdirectory with complete handover package
- ✅ Added Primary production database integration guide
- ✅ Complete cache usage documentation (252.7M records, 66.8 GB)
- ✅ Critical Route API integration patterns
- ✅ Frame limits guide (grouping vs non-grouping)
- ✅ Cache-first pattern (1,000-6,000x performance improvement)
- ✅ Rate limiting and error handling examples

**New Files**:
- `database/README.md` - Database handover index
- `database/API_INTEGRATION_GUIDE.md` - Route API integration guide
