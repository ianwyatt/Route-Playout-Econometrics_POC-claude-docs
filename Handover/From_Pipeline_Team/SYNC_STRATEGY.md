# Pipeline ↔ POC Synchronization Strategy

**Created**: 2025-10-17
**Purpose**: Keep POC project informed of pipeline changes
**Status**: ACTIVE

---

## 🎯 The Challenge

We have **two separate repositories**:

1. **route-playout-pipeline** (this repo)
   - Backend data processing
   - Database management
   - API integrations (future)
   - Infrastructure

2. **Route-Playout-Econometrics-POC** (separate repo)
   - User-facing application
   - UI/UX
   - Route API integration
   - Reports and analytics

**Problem**: How do we keep POC aware of pipeline changes that affect them?

---

## 📋 What Needs Syncing

### High Priority (Breaking Changes)

These **must** be communicated immediately:

1. **Database schema changes**
   - New tables/views
   - Column additions/removals
   - Index changes affecting queries
   - Constraint changes

2. **View definition changes**
   - `mv_playout_15min` structure
   - `mv_playout_15min_brands` structure
   - Aggregation formula changes

3. **Data refresh schedule changes**
   - Timing changes (currently 2am daily)
   - Refresh duration changes
   - Maintenance windows

4. **Breaking API changes** (future)
   - Cache table schema changes
   - Query pattern changes

### Medium Priority (New Features)

Should be communicated **within 1 week**:

1. **New materialized views**
2. **New cache tables** (when implemented)
3. **Performance improvements**
4. **New indexes** (can improve POC queries)
5. **Data quality improvements**

### Low Priority (FYI)

Can be communicated **monthly**:

1. **Import process improvements**
2. **Internal scripts**
3. **Backup strategy changes**
4. **Documentation updates**

---

## 🔄 Sync Methods

### Method 1: Shared Documentation Folder ⭐ RECOMMENDED

**What**: Maintain a shared `POC_Handover` folder in pipeline repo

**How**:
```
route-playout-pipeline/
├── Claude/
│   └── POC_Handover/          # ← Shared with POC team
│       ├── DATABASE_HANDOVER_FOR_POC.md    # Core reference
│       ├── QUICK_REFERENCE.md              # Quick lookups
│       ├── PYTHON_EXAMPLES.py              # Code samples
│       ├── FUTURE_ROADMAP.md               # What's coming
│       ├── SYNC_STRATEGY.md                # This document
│       └── CHANGELOG_FOR_POC.md            # Change log ← NEW
```

**POC team**:
- Bookmarks `DATABASE_HANDOVER_FOR_POC.md`
- Checks `CHANGELOG_FOR_POC.md` weekly
- Subscribes to notifications (see Method 2)

**Pipeline team**:
- Updates docs when changes happen
- Adds entry to `CHANGELOG_FOR_POC.md`
- Notifies POC team of critical changes

**Pros**:
- ✅ Single source of truth
- ✅ Version controlled
- ✅ Always up to date

**Cons**:
- ⚠️ POC needs to remember to check
- ⚠️ Requires manual updates

---

### Method 2: Change Log + Notifications

**What**: Maintain a `CHANGELOG_FOR_POC.md` in POC_Handover folder

**Format**:
```markdown
# Pipeline Changes Affecting POC

## [Unreleased]
- Feature X planned for next month

## [2025-10-17] - API Caching Roadmap
### Added
- FUTURE_ROADMAP.md documenting planned API caching
- SYNC_STRATEGY.md for coordination

### Changed
- Nothing

### Breaking
- None

## [2025-10-15] - 15-Minute Aggregation
### Added
- mv_playout_15min materialized view (PRIMARY for Route API)
- mv_playout_15min_brands for brand tracking

### Changed
- Database size now 596GB (was 480GB)

### Breaking
- None (new views, existing tables unchanged)
```

**Notification methods**:
1. **Email** - Send to POC team lead
2. **Slack** - Post in shared channel
3. **GitHub** - Tag POC repo in commit message
4. **Meeting** - Monthly sync call

**Frequency**:
- **Breaking changes**: Immediate
- **New features**: Weekly digest
- **FYI updates**: Monthly summary

---

### Method 3: API Version Headers (Future)

**What**: When cache tables exist, include version in responses

**How**:
```python
# POC queries cache table
response = db.query("""
    SELECT *, 'v2.1' as schema_version
    FROM route_audience_cache
    WHERE ...
""")

# POC checks version
if response['schema_version'] != POC_EXPECTED_VERSION:
    log_warning("Pipeline schema version mismatch")
    # Fallback or alert
```

**Pros**:
- ✅ Automatic detection
- ✅ Runtime validation

**Cons**:
- ⚠️ Requires implementation
- ⚠️ Only works for cache tables

---

### Method 4: Shared Database Views

**What**: Create POC-specific views with stable interfaces

**How**:
```sql
-- Pipeline creates POC-friendly view
CREATE VIEW vw_poc_campaign_data AS
SELECT
    frameid,
    buyercampaignref as campaign_id,
    time_window_start as datetime_from,
    time_window_start + INTERVAL '15 minutes' as datetime_to,
    spot_count,
    playout_length_seconds as spot_length,
    break_length_seconds as break_length
FROM mv_playout_15min;

-- POC always queries vw_poc_campaign_data
-- Pipeline can change mv_playout_15min without breaking POC
```

**Pros**:
- ✅ Decouples POC from internal changes
- ✅ Stable interface
- ✅ Pipeline can refactor freely

**Cons**:
- ⚠️ Additional maintenance
- ⚠️ May hide new features

---

## 📅 Recommended Workflow

### Weekly

**Pipeline team** (5 minutes):
1. Review changes made this week
2. Update `CHANGELOG_FOR_POC.md` if needed
3. Update core docs if schemas changed
4. Post in Slack if critical changes

**POC team** (5 minutes):
1. Check `CHANGELOG_FOR_POC.md` for updates
2. Review any breaking changes
3. Plan integration if needed

### Monthly

**Joint sync call** (30 minutes):
1. Review upcoming pipeline features
2. Discuss POC needs/requests
3. Align on priorities
4. Update roadmaps

**Pipeline team**:
1. Update future roadmap
2. Share performance metrics
3. Get POC feedback

**POC team**:
1. Share usage patterns
2. Request new features
3. Report issues

---

## 📊 Sync Checklist

### When Pipeline Makes Database Changes

- [ ] Update `DATABASE_HANDOVER_FOR_POC.md` (if schema changed)
- [ ] Update `QUICK_REFERENCE.md` (if query patterns changed)
- [ ] Update `PYTHON_EXAMPLES.py` (if API changed)
- [ ] Add entry to `CHANGELOG_FOR_POC.md`
- [ ] Tag severity: [BREAKING], [FEATURE], [FYI]
- [ ] If [BREAKING]: Email POC team immediately
- [ ] If [FEATURE]: Post in Slack within 1 week
- [ ] If [FYI]: Include in monthly digest

### When POC Encounters Issues

- [ ] Check `CHANGELOG_FOR_POC.md` for recent changes
- [ ] Check `DATABASE_HANDOVER_FOR_POC.md` for documentation
- [ ] Test with example queries from `PYTHON_EXAMPLES.py`
- [ ] If still broken: Contact pipeline team
- [ ] Document issue for future reference

---

## 🚨 Emergency Communication

### Critical Breaking Changes

**Examples**:
- Database down for > 1 hour
- Schema change breaks existing queries
- Data corruption/loss
- Security issue

**Process**:
1. **Immediate**: Email + Slack ping
2. **Within 15 min**: Describe issue and ETA
3. **Hourly updates**: Until resolved
4. **Post-mortem**: After resolution

**Contact**:
- **Pipeline team**: ian@route.org.uk
- **Slack**: #route-playout-pipeline (shared channel)
- **Emergency**: [Phone number]

---

## 📂 File Structure

### In Pipeline Repo (route-playout-pipeline)

```
Claude/
├── POC_Handover/                # ← POC team bookmarks this folder
│   ├── README.md                # Start here
│   ├── DATABASE_HANDOVER_FOR_POC.md   # ⭐ Main reference
│   ├── QUICK_REFERENCE.md       # Quick lookups
│   ├── PYTHON_EXAMPLES.py       # Code examples
│   ├── FUTURE_ROADMAP.md        # Planned features
│   ├── SYNC_STRATEGY.md         # This document
│   └── CHANGELOG_FOR_POC.md     # ⭐ Check weekly (TO BE CREATED)
│
├── Future_Plans/                # Detailed planning
│   └── API_CACHING_ROADMAP_2025.md
│
└── Documentation/               # Internal docs (POC can ignore)
```

### POC Team Bookmarks

**Must read**:
1. `POC_Handover/DATABASE_HANDOVER_FOR_POC.md`
2. `POC_Handover/CHANGELOG_FOR_POC.md`

**Reference as needed**:
3. `POC_Handover/QUICK_REFERENCE.md`
4. `POC_Handover/PYTHON_EXAMPLES.py`

**Future planning**:
5. `POC_Handover/FUTURE_ROADMAP.md`

---

## 🔗 Cross-Project Links

### From Pipeline → POC

**In git commits**:
```bash
# Tag POC repo in commit message
git commit -m "feat: add mv_playout_15min view

This adds the 15-minute aggregation view for Route API.

Affects: Route-Playout-Econometrics-POC
See: Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md
```

**In documentation**:
```markdown
<!-- Link to POC repo -->
For POC integration examples, see:
https://github.com/[org]/Route-Playout-Econometrics-POC/docs/pipeline-integration.md
```

### From POC → Pipeline

**In POC docs**:
```markdown
<!-- Link to pipeline docs -->
For database schema details, see:
https://github.com/[org]/route-playout-pipeline/Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md
```

**In POC code**:
```python
# Reference pipeline docs in comments
# See: route-playout-pipeline/Claude/POC_Handover/PYTHON_EXAMPLES.py
# For more query examples
```

---

## 📋 Change Classification Guide

### [BREAKING] Changes

**Require immediate notification + POC code changes**

Examples:
- Column removed from `mv_playout_15min`
- Index dropped (query performance impact)
- View renamed
- Data type changed (e.g., VARCHAR → INTEGER)
- Query syntax change required

**Template**:
```markdown
## [2025-XX-XX] - Breaking Schema Change

### [BREAKING] Changed
- Removed `old_column` from `mv_playout_15min`
- Renamed `time_window` to `time_window_start`

### Migration Required
- Update POC queries to use new column name
- See: DATABASE_HANDOVER_FOR_POC.md section X.Y

### Timeline
- Change deployed: 2025-XX-XX
- POC must update by: 2025-XX-XX (7 days)
- Support for old schema ends: 2025-XX-XX (14 days)
```

### [FEATURE] Changes

**Require notification + optional integration**

Examples:
- New materialized view added
- New cache table added
- New index improves performance
- New column added (optional to use)

**Template**:
```markdown
## [2025-XX-XX] - New Feature

### [FEATURE] Added
- `mv_playout_15min` materialized view
- Pre-aggregated 15-minute windows for Route API

### POC Integration
- Optional: Use new view for faster queries
- See: PYTHON_EXAMPLES.py for usage
- Backward compatible: Old queries still work

### Benefits
- 10,000x faster than querying raw data
- Route API ready format
```

### [FYI] Changes

**Informational only, no action needed**

Examples:
- Internal script improvements
- Documentation updates
- Performance tuning (no API changes)
- Backup strategy changes

**Template**:
```markdown
## [2025-XX-XX] - Maintenance Update

### [FYI] Changed
- Improved import script performance
- Updated backup schedule to 3am (was 2am)

### POC Impact
- None (internal changes only)
```

---

## 🎯 Success Metrics

### Pipeline Team

- [ ] CHANGELOG updated within 24h of change
- [ ] Breaking changes communicated same day
- [ ] Monthly sync call attendance
- [ ] Zero POC outages from surprise changes

### POC Team

- [ ] CHANGELOG checked weekly
- [ ] Breaking change migrations completed on time
- [ ] Feature adoption when beneficial
- [ ] Monthly sync call attendance

---

## 🔮 Future Improvements

### Automated Notifications

```bash
# Git hook to auto-notify on schema changes
#!/bin/bash
# .git/hooks/post-commit

if git diff --name-only HEAD~1 | grep -q "sql/.*\.sql"; then
    echo "Schema change detected!"
    # Auto-update CHANGELOG
    # Send Slack notification
    # Email POC team
fi
```

### Schema Diffing

```bash
# Compare database schemas
scripts/compare_schemas.sh ms01 poc_expected

# Output:
# [BREAKING] Column removed: mv_playout_15min.old_field
# [FEATURE] New table: route_audience_cache
```

### Documentation CI

```bash
# Verify POC docs are up to date
scripts/verify_poc_docs.sh

# Fails if:
# - DATABASE_HANDOVER_FOR_POC.md last updated > 30 days ago
# - CHANGELOG_FOR_POC.md empty
# - PYTHON_EXAMPLES.py has syntax errors
```

---

## 📞 Contacts

### Pipeline Team
- **Lead**: Ian Wyatt (ian@route.org.uk)
- **Slack**: #route-playout-pipeline
- **Repository**: route-playout-pipeline

### POC Team
- **Lead**: [To be filled]
- **Slack**: #route-poc-dev
- **Repository**: Route-Playout-Econometrics-POC

### Shared Channels
- **General**: #route-project
- **Technical**: #route-dev
- **Alerts**: #route-alerts

---

## 📚 Related Documents

**In this repo**:
- `Claude/POC_Handover/DATABASE_HANDOVER_FOR_POC.md` - Database reference
- `Claude/POC_Handover/FUTURE_ROADMAP.md` - Upcoming features
- `Claude/Future_Plans/API_CACHING_ROADMAP_2025.md` - Detailed roadmap

**To be created**:
- `Claude/POC_Handover/CHANGELOG_FOR_POC.md` - Change log ← **Create next**

---

## 🚀 Getting Started

### Pipeline Team Action Items

1. **Now**: Create `CHANGELOG_FOR_POC.md`
2. **Now**: Add to weekly routine (update changelog)
3. **This week**: Set up Slack channel
4. **This month**: Schedule first monthly sync call
5. **Ongoing**: Update docs when changes happen

### POC Team Action Items

1. **Now**: Bookmark `POC_Handover/` folder
2. **Now**: Subscribe to Slack channel
3. **Weekly**: Check `CHANGELOG_FOR_POC.md`
4. **This month**: Attend first sync call
5. **Ongoing**: Report issues/requests

---

**Summary**: Keep POC informed through shared docs, weekly changelog checks, and monthly sync calls. Breaking changes require immediate notification.

**Status**: ✅ ACTIVE
**Owner**: Pipeline team (primary), POC team (consumer)
**Review**: Quarterly
