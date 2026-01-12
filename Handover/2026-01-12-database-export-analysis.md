# Session Handover: Database Export Analysis & Split Repo Refinements

**Date**: 12 January 2026
**Session Focus**: Database table analysis for DigitalOcean deployment, split repo guide updates, claude-mem plugin setup

---

## Summary of Work Completed

### 1. Database Table Analysis

Analysed all database queries in the codebase to determine which tables/views are actually used by the POC UI application.

**Key Finding**: The `playout_data` table (~500GB+) is **NOT needed** by the UI. All queries use materialised views which are self-contained.

**Tables Required by App:**

| Category | Tables/Views |
|----------|--------------|
| Campaign Browser | `mv_campaign_browser`, `mv_campaign_browser_summary`, `mv_platform_stats` |
| Playout Aggregations | `mv_playout_15min`, `mv_playout_15min_brands` |
| Audience Cache | `cache_route_impacts_15min_by_demo` (~416M rows), `mv_cache_campaign_impacts_*` |
| Reach Cache | `cache_campaign_reach_week`, `cache_campaign_reach_full`, `cache_campaign_reach_day_cumulative`, `cache_campaign_brand_reach` |
| Frame Audiences | `mv_frame_audience_daily`, `mv_frame_audience_hourly`, `mv_frame_brand_daily`, `mv_frame_brand_hourly` |
| Frame Reference | `route_frames`, `route_frame_details`, `route_releases` |
| Entity Lookups | `cache_space_brands`, `cache_space_media_owners`, `cache_space_buyers`, `cache_space_agencies` |

**NOT Needed:**
- `playout_data` - Raw playouts, only used by pipeline
- `frame_playouts` - Legacy/archive code
- `frame_demographics` - Legacy/archive code

### 2. Created Database Export Documentation

**File**: `docs/12-database-export.md`

Documents:
- All tables/views used by the app
- Which tables can be excluded
- Demo campaign IDs (16699, 16879, 16882, 18409)
- Size estimates
- Import instructions

### 3. Created Database Export Script

**File**: `scripts/export_demo_database.sh`

Features:
```bash
# Full export (schema + data, excludes playout_data)
./scripts/export_demo_database.sh --host ms01.local --db route_playout

# Schema only
./scripts/export_demo_database.sh --schema-only

# Filtered to specific demo campaigns (smaller export)
./scripts/export_demo_database.sh --campaigns "16699,16879,18409"

# Data only (for incremental updates)
./scripts/export_demo_database.sh --data-only
```

### 4. Split Repo Guide Updates

The user updated `reference/SPLIT_REPO_SETUP_GUIDE.md` with:
- RouteInvoiceProcessor as reference implementation
- CLAUDE.md symlink (third symlink for root-level access)
- Beads stays in code repo (separate sync mechanism)
- Clearer "Key Insight" about docs repo being the Claude folder

### 5. claude-mem Plugin Setup

- Installed claude-mem plugin with `scope: "user"` (works across all projects)
- Plugin version: 7.2.3
- Key learning: `"project"` scope didn't work for multi-project use; `"user"` scope is correct

### 6. Beads Issue Tracking

- Enabled `sync-branch: "beads-sync"` in `.beads/config.yaml`
- Committed beads setup to code repo
- Pushed to both GitHub and Gitea

---

## Code Commits This Session

### Code Repo (`Route-Playout-Econometrics_POC`)

| Hash | Description |
|------|-------------|
| `f538ab7` | feat: add beads issue tracking setup |
| `c15a4cc` | feat: add database export documentation and script |

### Docs Repo (`Route-Playout-Econometrics_POC-claude-docs`)

| Hash | Description |
|------|-------------|
| `5090e35` | docs: add post-commit hook and updated install.sh to setup guide |
| (user commits) | Split repo guide updates, CLAUDE.md refinements |

---

## Important Files

### Code Repo

| File | Purpose |
|------|---------|
| `docs/12-database-export.md` | Database export documentation |
| `scripts/export_demo_database.sh` | Export script for demo deployments |
| `.beads/config.yaml` | Beads config with sync-branch enabled |

### Docs Repo

| File | Purpose |
|------|---------|
| `reference/SPLIT_REPO_SETUP_GUIDE.md` | Updated guide for other projects |
| `CLAUDE.md` | Main instructions with split repo banner |

---

## Campaign Date Logic (Researched)

User asked about campaign start/end dates:

**Flow:**
```
Media Owner CSV (startdate field)
    ↓
Pipeline truncates to 15-minute windows
    ↓
mv_playout_15min.time_window_start
    ↓
MIN(time_window_start) = campaign start_date
MAX(time_window_start) = campaign end_date
```

Campaign dates reflect **actual playouts**, not declared schedules.

---

## Next Session: DigitalOcean Deployment

**Prepared prompt saved to**: `todo/2026-01-12-digitalocean-deployment-prompt.md`

### Database Deployment
1. Estimate database size without playout_data
2. Determine DigitalOcean Managed PostgreSQL requirements
3. Export data from MS-01
4. Import and verify

### App Deployment (NEW)
5. Deploy Streamlit app to DigitalOcean VPS (Droplet)
6. Set up PocketID authentication (passkey-only OIDC)
7. Implement geo-blocking to GB only
8. Configure HTTPS and security best practices

### Context
- This is a **demo deployment for personal use only**
- User is the only person who will access it
- Geo-blocking to GB provides additional security layer
- PocketID = passkey-only authentication (no passwords)

---

## Technical Notes

### Export Size Estimates

| Component | Approximate Size |
|-----------|------------------|
| Full export (without playout_data) | ~50-100GB |
| Demo export (3-5 campaigns) | ~1-5GB |
| Entity lookups + frame data only | ~500MB |

### Demo Campaigns

| Campaign ID | Purpose |
|-------------|---------|
| 16699 | Standard demo campaign |
| 16879 | Overlap demo (with 16882) |
| 16882 | Overlap demo (with 16879) |
| 18409 | Board demo |

---

## Remotes Reference

### Code Repo
```
origin   → https://github.com/ianwyatt/Route-Playout-Econometrics_POC.git
zimacube → https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC.git
```

### Docs Repo
```
origin → https://zimacube-gitea.eagle-pythagorean.ts.net/IanW/Route-Playout-Econometrics_POC-claude-docs.git
```

---

*Handover prepared: 12 January 2026*
