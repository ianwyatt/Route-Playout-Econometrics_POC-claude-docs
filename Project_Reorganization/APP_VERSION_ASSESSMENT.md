# Application Version Assessment Guide

**Date**: 2025-10-17
**Purpose**: Evaluate each application version for keep/archive/delete decisions
**Status**: Awaiting Doctor Biz Review

---

## 🎯 Assessment Criteria

For each application, evaluate:
- **Usage Frequency**: When was it last used?
- **Unique Features**: Does it have features not in other apps?
- **Deployment Status**: Is it deployed anywhere?
- **Documentation**: Is it referenced in docs/handovers?
- **Performance**: Does it work well?
- **Maintenance Burden**: Is it worth maintaining?

**Decision Options**:
- ✅ **KEEP** - Active, needed, maintain
- 📦 **ARCHIVE** - Not active but keep for reference
- 🗑️ **DELETE** - Obsolete, can safely remove

---

## 📊 Application Assessment Matrix

### Version 1: Mock Data Applications

#### App 1: `app_mock_full.py` (1,207 lines, Port 8503)

**Current Status**: ✅ Production Demo App

**Unique Features**:
- Complete feature set with all visualizations
- <3 second response time
- Board demo ready
- Executive summary
- Cost upload integration
- 3D business charts
- Geographic visualizations

**Usage**:
- ✅ Primary demo application
- ✅ Board presentations
- ✅ Fast demos for stakeholders

**Referenced In**:
- `APP_VERSIONS_COMPLETE_GUIDE.md`
- `HANDOVER_2025_09_10_SESSION_COMPLETE.md`
- `README_START_HERE.md`

**Git History**:
- Recent commits (last 7 days)
- Active development
- Multiple feature additions

**Dependencies**:
- Uses: mock_data_factory, campaign_service, all UI components
- Depends on: Entire shared infrastructure

**Performance**:
- ⚡ Excellent (<3 seconds)
- No known issues

**Recommendation**: ✅ **KEEP** - This is the primary demo app
**Priority**: CRITICAL - Main demo application
**Action**: Keep as main Version 1 app

---

#### App 2: `app_mock_simple.py` (358 lines, Port 8502)

**Current Status**: ✅ Working but unclear purpose

**Unique Features**:
- Simplified interface (fewer tabs)
- Basic campaign display
- Minimal feature set
- Faster loading than full version

**Compared to `app_mock_full.py`**:
- Missing: Executive summary, 3D charts, advanced visualizations
- Has: Basic metrics, simple campaign display

**Usage**:
- ❓ Unknown - when is this used instead of full version?
- ❓ Is this for quick demos?
- ❓ Is this for low-resource environments?

**Referenced In**:
- `APP_VERSIONS_COMPLETE_GUIDE.md` - Listed but no specific use case mentioned

**Git History**:
- [ ] Check last commit date
- [ ] Check if actively maintained

**Questions to Answer**:
1. **When do you use this instead of app_mock_full?**
   - [ ] Quick demos?
   - [ ] Low-resource environments?
   - [ ] Specific use case?
   - [ ] Never used anymore?

2. **Does app_mock_full replace this entirely?**
   - If YES → Archive or delete
   - If NO → What's the specific use case?

3. **How often is this actually run?**
   - [ ] Check server logs
   - [ ] Ask team members

**Recommendation**: ❓ **ASSESS** - Need clarification on use case
**Priority**: LOW - Can be archived if not actively used
**Action**:
- [ ] Answer questions above
- [ ] If rarely used → **ARCHIVE**
- [ ] If specific need → **KEEP** with documented use case
- [ ] If obsolete → **DELETE**

---

#### App 3: `app_mock_modular.py` (360 lines, Port 8507)

**Current Status**: ✅ Working but unclear purpose

**Unique Features**:
- Modular architecture (different code organization)
- Similar features to app_mock_simple
- Demonstrates architectural pattern

**Compared to Other Apps**:
- Features: Similar to app_mock_simple
- Code: Different organization (more modular)
- Purpose: Architectural demonstration?

**Usage**:
- ❓ Was this an architectural experiment?
- ❓ Is this a template for future development?
- ❓ Is anyone using this?

**Referenced In**:
- `APP_VERSIONS_COMPLETE_GUIDE.md` - Listed with "modular architecture" note

**Git History**:
- [ ] Check last commit date
- [ ] Check if experimental branch

**Questions to Answer**:
1. **What was the original purpose of this?**
   - [ ] Experiment with modular architecture?
   - [ ] Alternative approach to app structure?
   - [ ] Template for Version 2?
   - [ ] Just testing?

2. **Was the modular approach successful?**
   - [ ] Did it get adopted in other apps?
   - [ ] Is it the preferred pattern now?
   - [ ] Or was it abandoned?

3. **Is there any reason to keep this?**
   - [ ] Active development?
   - [ ] Specific use case?
   - [ ] Or just historical artifact?

**Recommendation**: ❓ **ASSESS** - Likely archive candidate
**Priority**: LOW - Appears to be experimental
**Action**:
- [ ] Answer questions above
- [ ] If experiment completed → **ARCHIVE** with notes
- [ ] If pattern adopted → Merge learnings, **DELETE** this
- [ ] If still developing → **KEEP** with clear purpose

---

### Version 2: Live API Applications

#### App 4: `app_api_real.py` (585 lines, Port 8504)

**Current Status**: 🔄 In Development

**Unique Features**:
- Direct Route API integration
- Real playout CSV loading
- Live audience calculations
- Production target architecture

**Usage**:
- ✅ Primary Version 2 application
- 🔄 In active development
- 🎯 Production deployment target

**Referenced In**:
- `APP_VERSIONS_COMPLETE_GUIDE.md` - Listed as "Version 2 Main"
- MS-01 migration docs reference this
- Marked as production target

**Git History**:
- Recent commits
- Active development
- Performance optimization ongoing

**Performance**:
- ⚠️ Slow (>10 seconds currently)
- 🔄 Needs optimization
- 🎯 Target: Match Version 1 speed

**Dependencies**:
- Uses: route_client, route_service, playout_processor
- Target: Will use MS-01 helpers

**Recommendation**: ✅ **KEEP** - Critical production target
**Priority**: CRITICAL - This is the future production app
**Action**: Keep as main Version 2 app, continue optimization

---

#### App 5: `app_hybrid_demo.py` (644 lines, Port 8505)

**Current Status**: 🧪 Testing/Development

**Unique Features**:
- Real API with mock fallback
- Good for development when API unavailable
- Hybrid approach for resilience

**Usage**:
- ✅ Development testing
- ✅ Demo when API credentials missing
- ✅ Fallback for API failures

**Compared to `app_api_real.py`**:
- Has: Fallback mechanism
- Purpose: Testing and resilience
- Value: Safety net during development

**Referenced In**:
- `APP_VERSIONS_COMPLETE_GUIDE.md`
- Mentioned as testing version

**Value Proposition**:
- Allows development without API access
- Good for distributed team
- Resilient to API issues

**Questions to Answer**:
1. **Is this actively used for development?**
   - [ ] Yes, regularly?
   - [ ] Sometimes?
   - [ ] Not really?

2. **Is the fallback mechanism valuable?**
   - [ ] Should this be merged into app_api_real.py?
   - [ ] Or keep separate for testing?

3. **Long-term plan?**
   - [ ] Keep as testing harness?
   - [ ] Merge fallback into production app?
   - [ ] Archive once Version 2 is stable?

**Recommendation**: ✅ **KEEP** - Valuable for development
**Priority**: MEDIUM - Useful but not critical
**Action**:
- Keep during Version 2 development
- Consider merging fallback mechanism into app_api_real.py
- Archive once Version 2 is production-stable

---

### Legacy Applications

#### App 6: `app.py` (673 lines, Port 8501)

**Current Status**: 📦 Legacy - **HIGH PRIORITY ASSESSMENT**

**Critical Concern**: ⚠️ **Deployment scripts reference this file**
```bash
deployment/deploy-app.sh:150: exec streamlit run src/ui/app.py
deployment/supervisor.conf:5: command=/opt/route-ui/venv/bin/python -m streamlit run src/ui/app.py
```

**Features**:
- Mix of mock and semi-real data
- Original application architecture
- Complete feature set (at time of creation)

**Usage Questions** (CRITICAL):
1. **Is this deployed in production somewhere?**
   - [ ] Yes, where? → **MUST KEEP** until migrated
   - [ ] No, deployment is outdated → Can consider archiving

2. **Are deployment files up to date?**
   - [ ] Check if deployment/ is current or historical
   - [ ] Is there a production deployment using this?

3. **What's the migration path?**
   - [ ] If in production, plan migration to app_mock_full or app_api_real
   - [ ] If not in production, safe to archive

**Git History**:
- [ ] Check last commit date
- [ ] Check if referenced in recent work
- [ ] Look for production deployment notes

**Dependencies**:
- Uses: Mix of services and components
- May have unique config patterns

**Recommendation**: ❓ **URGENT ASSESSMENT NEEDED**
**Priority**: HIGH - Could be production app
**Action**:
- [ ] **IMMEDIATELY** check if this is in production
- [ ] If YES → Document migration plan, **KEEP** until migrated
- [ ] If NO → **ARCHIVE** with clear notes on what it was
- [ ] Update deployment files to point to correct app

---

#### App 7: `app_enhanced.py` (682 lines, Port 8506)

**Current Status**: 📦 Legacy

**Unique Features**:
- "Enhanced" UI features
- Unknown what enhancements are

**Questions to Answer**:
1. **What enhancements does this have?**
   - [ ] Review code to identify unique features
   - [ ] Compare with app_mock_full.py

2. **Were enhancements merged into other apps?**
   - [ ] Check if app_mock_full has these features
   - [ ] Or if they were abandoned

3. **When was this last actively used?**
   - [ ] Check git logs
   - [ ] Check references in docs

**Potential Scenarios**:
- **Scenario A**: Enhancements merged into app_mock_full
  - Action: **ARCHIVE** or **DELETE**

- **Scenario B**: Has unique valuable features
  - Action: Merge into app_mock_full, then **DELETE**

- **Scenario C**: Experimental, features not adopted
  - Action: **ARCHIVE** with notes on lessons learned

**Recommendation**: ❓ **ASSESS** - Likely archive/delete
**Priority**: LOW - Appears superseded
**Action**:
- [ ] Code review to identify unique features
- [ ] If nothing unique → **DELETE**
- [ ] If has unique features → Merge, then **DELETE**
- [ ] If historical value → **ARCHIVE** with notes

---

## 📋 Assessment Checklist

### For Each App, Complete:

- [ ] Review code and features
- [ ] Check git history (last commit, activity)
- [ ] Check deployment references
- [ ] Check documentation references
- [ ] Test if it still runs
- [ ] Compare with other apps
- [ ] Identify unique features
- [ ] Determine use case
- [ ] Make decision: KEEP / ARCHIVE / DELETE

---

## 🎯 Decision Summary Template

Once assessed, fill in:

```
Application: [app_name.py]
Decision: [KEEP / ARCHIVE / DELETE]
Reason: [1-2 sentences]
Action Items:
  - [ ] [Specific action 1]
  - [ ] [Specific action 2]
Priority: [HIGH / MEDIUM / LOW]
Timeline: [Immediate / Next Sprint / Later]
```

---

## 📊 Preliminary Recommendations (Subject to Assessment)

### Highly Confident Recommendations:

| App | Recommendation | Reason |
|-----|----------------|--------|
| `app_mock_full.py` | ✅ **KEEP** | Primary demo app, actively used |
| `app_api_real.py` | ✅ **KEEP** | Production target, in development |
| `app_hybrid_demo.py` | ✅ **KEEP** | Valuable for testing |

### Need Assessment:

| App | Likely Decision | Must Verify |
|-----|-----------------|-------------|
| `app_mock_simple.py` | 📦 Archive? | When is this used? |
| `app_mock_modular.py` | 📦 Archive? | Experimental or active? |
| `app.py` | ❓ **CRITICAL** | Is this in production? |
| `app_enhanced.py` | 📦 Archive/Delete? | Unique features? |

---

## 🚨 High Priority Actions

### Action 1: Check Production Status of app.py
```bash
# Check deployment status
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
cat deployment/deploy-app.sh | grep "app.py"
cat deployment/supervisor.conf | grep "app.py"

# Check git history
git log --oneline src/ui/app.py | head -20

# Check recent references
grep -r "app.py" Claude/Handover/ --include="*.md"
```

**If in production**:
- Plan migration to app_mock_full.py or app_api_real.py
- Keep app.py until migration complete
- Update deployment scripts

**If not in production**:
- Archive immediately
- Update deployment scripts to point to correct app

---

### Action 2: Test Each App
```bash
# Test each app to verify it works
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC

# Version 1 apps
streamlit run src/ui/app_mock_full.py --server.port 8503 &
streamlit run src/ui/app_mock_simple.py --server.port 8502 &
streamlit run src/ui/app_mock_modular.py --server.port 8507 &

# Version 2 apps
streamlit run src/ui/app_api_real.py --server.port 8504 &
streamlit run src/ui/app_hybrid_demo.py --server.port 8505 &

# Legacy apps
streamlit run src/ui/app.py --server.port 8501 &
streamlit run src/ui/app_enhanced.py --server.port 8506 &

# Visit each at http://localhost:PORT
# Document which work, which don't
```

---

### Action 3: Code Feature Comparison
For questionable apps, compare features:

```bash
# Compare line by line what's different
diff src/ui/app_mock_simple.py src/ui/app_mock_full.py > mock_comparison.txt
diff src/ui/app_enhanced.py src/ui/app.py > legacy_comparison.txt
diff src/ui/app_enhanced.py src/ui/app_mock_full.py > enhanced_vs_current.txt

# Review differences to identify unique features
```

---

## 📝 Assessment Workflow

### Step 1: Information Gathering (1 hour)
- Run tests for all apps
- Check git logs
- Review deployment files
- Check documentation

### Step 2: Feature Analysis (1 hour)
- Code comparison
- Identify unique features
- Determine value of each

### Step 3: Decision Making (30 minutes)
- Apply criteria
- Make keep/archive/delete decisions
- Document reasoning

### Step 4: Documentation (30 minutes)
- Update this document with decisions
- Create ARCHIVE_CANDIDATES.md
- Create KEEP_LIST.md

---

## 📄 Next Documents to Create

After assessment:

1. **KEEP_LIST.md** - Apps to keep and maintain
   - List active apps
   - Document use cases
   - Assign owners

2. **ARCHIVE_CANDIDATES.md** - Apps to archive
   - List apps for archival
   - Document what they were
   - Note lessons learned

3. **REORGANIZATION_PLAN.md** - How to reorganize
   - Folder structure
   - Naming conventions
   - Migration steps

---

## ⏰ Timeline

- **Immediate** (Today): Assess app.py production status
- **This Week**: Complete assessment of all apps
- **Next Week**: Execute archival and reorganization
- **Following Week**: Test and validate

---

**Status**: Awaiting Doctor Biz Assessment
**Next Step**: Answer questions in this document
**Priority**: High - Blocks reorganization work
