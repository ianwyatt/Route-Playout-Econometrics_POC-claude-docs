# Failover Test Checklist
**Date**: 2025-12-01
**Purpose**: Verify Framework database failover works before board demo

---

## Pre-Test Status

- [ ] M4 Max local database working
- [ ] MS-01 currently accessible
- [ ] Framework (192.168.1.76) currently accessible

---

## Step 1: Shut Down MS-01

On MS-01 or via SSH:
```bash
# Graceful shutdown
sudo shutdown now
```

**Verify**: MS-01 is no longer pingable
```bash
ping 192.168.1.34
# Should timeout/fail
```

- [ ] MS-01 shut down successfully

---

## Step 2: Test M4 Max with Local Database

On M4 Max:
```bash
# Start app with local database in demo mode
startstream local demo
```

**Test**:
- [ ] App starts on http://localhost:8504
- [ ] Load campaign 16699
- [ ] Verify all 6 tabs load correctly
- [ ] Brands are anonymised (demo mode)

```bash
# Health check
curl http://localhost:8504/_stcore/health
```

- [ ] M4 Max local demo working perfectly

---

## Step 3: Pull Latest Code on M1 Max

On M1 Max:
```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC

# Check current status
git status

# Pull latest changes
git pull origin main

# Verify dependencies are up to date
uv sync
```

- [ ] Git pull successful
- [ ] Dependencies synced

---

## Step 4: Edit .env to Point to Framework

On M1 Max:
```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC

# Backup current .env (just in case)
cp .env .env.backup

# Edit .env file
nano .env
```

**Find this line**:
```
POSTGRES_HOST_MS01=192.168.1.34
```

**Change to**:
```
POSTGRES_HOST_MS01=192.168.1.76
```

**Save and exit** (Ctrl+X, Y, Enter)

- [ ] .env edited to point to Framework (192.168.1.76)

---

## Step 5: Test M1 Max with Framework Database

On M1 Max:
```bash
# Stop any running Streamlit
stopstream

# Start with MS01 database setting (now pointing to Framework)
startstream demo
```

**Test**:
- [ ] App starts on http://localhost:8504
- [ ] Load campaign 16699
- [ ] Executive Summary tab loads
- [ ] Campaign Overview tab loads
- [ ] Weekly Reach & GRPs tab loads
- [ ] Geographic Distribution tab loads
- [ ] Frame Audiences tab loads (tests mv_frame_brand_* MVs)
- [ ] Data Quality tab loads
- [ ] Brands are anonymised (demo mode)

**Verify Framework connection** (optional):
```bash
# Check which database you're connected to
# Use: psql -h 192.168.1.76 -U postgres -d route_poc
# Password: see POSTGRES_PASSWORD_MS01 in .env
# Query: SELECT COUNT(*) FROM mv_campaign_browser;
# Should return 836
```

- [ ] M1 Max successfully running on Framework database

---

## Step 6: Restore .env to MS-01

On M1 Max:
```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC

# Option A: Edit .env back
nano .env
# Change POSTGRES_HOST_MS01=192.168.1.76 back to POSTGRES_HOST_MS01=192.168.1.34

# Option B: Restore from backup
cp .env.backup .env

# Clean up backup
rm .env.backup
```

- [ ] .env restored to point to MS-01 (192.168.1.34)

---

## Step 7: Restart MS-01

Power on MS-01 (physically or via management interface).

**Verify**: MS-01 is accessible again
```bash
ping 192.168.1.34
# Should succeed

# Test database connection
# Use: psql -h 192.168.1.34 -U postgres -d route_poc -c "SELECT 1;"
# Password: see POSTGRES_PASSWORD_MS01 in .env
```

- [ ] MS-01 back online and accessible

---

## Test Results Summary

| Test | Result | Notes |
|------|--------|-------|
| M4 Max + Local DB | [x] Pass | Tested 16699, 16882, export |
| M1 Max + Framework DB | [x] Pass | All tabs loaded correctly |
| All 6 tabs working | [x] Pass | Including Frame Audiences |
| Frame Audiences (MVs) | [x] Pass | MVs created on Framework |
| Demo mode (anonymised) | [x] Pass | Brands anonymised |

---

## Issues Encountered

_(Problems found and fixed during test)_

1. **Database dropdown defaulting to MS-01** - Fixed in commit `685a1e2`. Session state now initialises from `USE_MS01_DATABASE` env var.
2. **Weekly reach queries ignoring Local setting** - Fixed by passing `use_ms01` parameter through all data loaders.
3. **Export functions hardcoded to MS-01** - Fixed in `src/ui/utils/export.py`.

---

## Post-Test Actions

- [x] Stop Streamlit on M1 Max: `stopstream`
- [x] Verify .env is back to MS-01 settings
- [x] MS-01 restarted and accessible
- [x] Framework can remain running (no action needed)

---

**Test Completed**: [x] Yes
**Tester**: Ian Wyatt
**Time**: 2025-12-01 ~20:30

---

*Created: 2025-12-01*
