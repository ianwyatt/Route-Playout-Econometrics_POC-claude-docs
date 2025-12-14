# Project Reorganization Documentation

**Created**: 2025-10-17
**Purpose**: Document analysis and plan for cleaning up project structure
**Status**: Assessment Phase

---

## 📁 What's in This Folder

This folder contains complete documentation for reorganizing the Route Playout Econometrics POC project structure.

### Documents

1. **PROJECT_STRUCTURE_ANALYSIS.md** (Complete)
   - Comprehensive analysis of current project state
   - All 7 application files documented
   - Critical infrastructure issues identified
   - Code volume metrics
   - Dependency analysis

2. **APP_VERSION_ASSESSMENT.md** (Awaiting Review)
   - Detailed assessment guide for each of 7 apps
   - Questions to answer for keep/archive/delete decisions
   - Critical: Check if app.py is in production!
   - Test procedures and comparison tools

3. **Coming Next** (After Assessment):
   - KEEP_LIST.md - Apps to maintain
   - ARCHIVE_CANDIDATES.md - Apps to archive
   - REORGANIZATION_PLAN.md - Step-by-step restructuring
   - FOUNDATION_FIXES.md - Fix brittle infrastructure

---

## 🎯 Current Status

### Discovered
- ✅ 7 application files (expected 2!)
- ✅ 45+ files with sys.path hacks
- ✅ 22 files with brittle config loading
- ✅ 10+ files with hardcoded data paths
- ✅ Multiple legacy/testing versions

### Critical Finding
⚠️ **Deployment scripts reference `app.py`** - Must verify if this is in production before any changes!

---

## 📋 Next Steps

### Immediate (Doctor Biz Actions)
1. **Read PROJECT_STRUCTURE_ANALYSIS.md** - Understand current state
2. **Read APP_VERSION_ASSESSMENT.md** - Assessment guide
3. **Answer assessment questions** - For each app
4. **Check app.py production status** - URGENT
5. **Make decisions** - Keep/Archive/Delete

### After Assessment (Implementation)
6. Archive unnecessary files
7. Fix foundation issues
8. Reorganize remaining files
9. Test everything

---

## ⚠️ CRITICAL: app.py Production Check

**MUST DO BEFORE ANY CHANGES**:

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC

# Check deployment references
cat deployment/deploy-app.sh | grep "app.py"
cat deployment/supervisor.conf | grep "app.py"

# If references found, IS THIS IN PRODUCTION?
# If YES → MUST KEEP until migration planned
# If NO → Can proceed with archival
```

---

## 📊 Summary Statistics

**Current State**:
- 7 application files (4,509 lines)
- 150+ Python files total (~35,000 lines)
- 50+ documentation files (~500 KB)
- 35+ scripts (many random/one-time)

**Decision Needed**:
- 3 apps: ✅ Definitely keep
- 4 apps: ❓ Need assessment

**Impact of Changes**:
- 80+ files will need import updates
- 22 files have brittle config loading
- 45+ files have sys.path hacks
- All must be fixed before reorganization

---

## 🎓 Key Lessons

### Why Structure Matters
- **Clarity**: Easy to find and understand code
- **Maintainability**: Easy to update and fix
- **Safety**: Hard to break things accidentally
- **Onboarding**: New developers can navigate

### Why We Need Assessment First
- **Avoid Breaking Production**: Must know what's deployed
- **Avoid Wasting Time**: Don't organize obsolete files
- **Preserve History**: Archive, don't delete learning
- **Plan Properly**: Know scope before starting

---

## 📞 Questions?

Contact Doctor Biz with any questions or concerns before proceeding.

**This is pre-surgery analysis** - we don't touch anything until you approve the plan!

---

**Status**: ✅ Analysis Complete, ⏳ Awaiting Assessment Decisions
