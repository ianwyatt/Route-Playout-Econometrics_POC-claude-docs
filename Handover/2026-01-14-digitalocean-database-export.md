# Session Handover: DigitalOcean Database Export Preparation

**Date**: 14 January 2026
**Session Focus**: Preparing local database for DigitalOcean deployment

---

## Summary

Prepared the local Mac PostgreSQL database for export to DigitalOcean Managed PostgreSQL. The key challenge was that `pg_dump` doesn't export materialized view data as row data - it only exports definitions and expects REFRESH on restore. Since we truncated `playout_data` to save space, MVs couldn't be refreshed.

**Solution**: Converted all 21 materialized views to regular tables before export.

---

## Work Completed

### 1. Database Size Analysis

Queried MS-01 and local Mac databases to understand table sizes:

| Category | Size |
|----------|------|
| Total database | 660 GB |
| `playout_data` (raw playouts) | 533 GB |
| Without `playout_data` | 127 GB |
| `cache_route_impacts_15min_by_demo` | 92 GB |
| All MVs combined | ~35 GB |

**Key finding**: The `playout_data` table is NOT needed by the UI - all queries use materialised views.

### 2. Truncated playout_data

Freed 533 GB by truncating the raw playout table (LOCAL only, not MS-01):

```sql
TRUNCATE TABLE playout_data;
```

Database reduced from 660 GB → 127 GB.

### 3. Discovered pg_dump MV Limitation

**Problem**: `pg_dump` with `--exclude-table=playout_data` skipped MV data because MVs depend on playout_data. Even without the exclude flag, pg_dump only exports MV definitions, not row data - it relies on REFRESH MATERIALIZED VIEW during restore.

Since playout_data is empty, MVs cannot be refreshed on the destination.

### 4. Created MV-to-Table Conversion Script

**File**: `/Users/ianwyatt/poc export/convert_mvs_to_tables.sql`

The script:
1. Creates regular tables from each MV's data (`CREATE TABLE x_tbl AS SELECT * FROM x`)
2. Drops all MVs (including 3 unpopulated ones: frame_spot_distribution, frame_spot_summary, spot_length_summary)
3. Renames tables to original MV names
4. Creates key indexes for query performance

**21 MVs converted to tables** with all data preserved.

### 5. Exported Database

```bash
pg_dump -h localhost -U ianwyatt -d route_poc \
  -Fd -j 4 \
  --exclude-table=playout_data \
  -f "/Users/ianwyatt/poc export/route_poc_export"
```

**Export results**:
| Metric | Value |
|--------|-------|
| Export size (compressed) | 7.9 GB |
| Data files | 42 |
| Largest file | 4.1 GB (cache_route_impacts_15min_by_demo) |
| Location | `~/poc export/route_poc_export/` |

---

## Files Created

| File | Purpose |
|------|---------|
| `~/poc export/route_poc_export/` | pg_dump directory format export |
| `~/poc export/convert_mvs_to_tables.sql` | SQL script for MV conversion |

---

## DigitalOcean Recommendation (Revised)

Based on actual export size of 7.9 GB (uncompressed ~35-40 GB):

### Database
| Plan | vCPUs | RAM | Storage | Monthly Cost |
|------|-------|-----|---------|--------------|
| **Basic 4 GB** | 2 | 4 GB | 60 GB | **$60.90** |

**Region**: London (LON1)

### App (Droplet)
| Plan | vCPUs | RAM | Storage | Monthly Cost |
|------|-------|-----|---------|--------------|
| Basic | 1 | 1 GB | 25 GB | ~$6 |

**Estimated total**: ~$67/month

---

## What's Next (Part 2)

### Database Deployment
1. Provision DigitalOcean Managed PostgreSQL (London, Basic 4 GB plan)
2. Transfer export to a temporary Droplet (or restore directly if connection allows)
3. Restore with: `pg_restore -h <do-host> -U doadmin -d defaultdb -j 4 ~/poc export/route_poc_export`
4. Create read-only app user

### App Deployment
5. Provision Droplet for Streamlit app
6. Clone repo, install dependencies with UV
7. Configure environment variables for cloud database
8. Set up reverse proxy (Caddy or nginx)
9. Configure PocketID authentication
10. Set up geo-blocking to GB only
11. HTTPS with Let's Encrypt

### Security
- VPC: Database on private IP only
- Read-only database user for app
- SSH hardening (key-only, non-standard port, Fail2ban)
- Security headers, rate limiting

---

## Important Notes

### Local Database State
The local Mac database has been modified:
- `playout_data` is TRUNCATED (empty)
- All MVs are now regular TABLES (not materialized views)
- The database cannot refresh MVs without playout_data

**To restore local to original state**: Restore from MS-01 backup or re-sync from MS-01.

### MS-01 Database
**UNCHANGED** - MS-01 still has full playout_data and original MVs.

### Export Restore Command
```bash
# On destination (DigitalOcean)
pg_restore -h <do-host> -p 25060 -U doadmin -d defaultdb \
  -j 4 --no-owner --no-privileges \
  /path/to/route_poc_export
```

Note: Use `--no-owner --no-privileges` since DO uses different user.

---

## Quick Reference

### Export Location
```
~/poc export/route_poc_export/
```

### Conversion Script
```
~/poc export/convert_mvs_to_tables.sql
```

### Start Next Session Prompt
```
I want to continue deploying the Route Playout Econometrics POC to DigitalOcean.

In the previous session we:
1. Truncated playout_data on LOCAL Mac (freed 533 GB)
2. Converted 21 MVs to regular tables
3. Exported the database (7.9 GB compressed, 42 data files)

The export is at: ~/poc export/route_poc_export/

Next steps:
1. Provision DigitalOcean Managed PostgreSQL (London, Basic 4 GB, ~$61/month)
2. Restore the database
3. Provision Droplet for Streamlit app
4. Deploy app with PocketID auth and GB geo-blocking

See handover: handover/2026-01-14-digitalocean-database-export.md
```

---

*Handover prepared: 14 January 2026*
