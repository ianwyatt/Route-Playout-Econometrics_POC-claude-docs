# Next Session Prompt: DigitalOcean Database Deployment

Copy and paste this prompt to start the next session:

---

## Prompt

I want to deploy the Route Playout Econometrics POC database to DigitalOcean for reliable demos without depending on my Mac's local database.

In the previous session we:
1. Analysed which tables the app actually needs (see `docs/12-database-export.md`)
2. Created an export script (`scripts/export_demo_database.sh`)
3. Confirmed `playout_data` table is NOT needed - the MVs are self-contained

**Key context:**
- Source database: MS-01 PostgreSQL server (~620GB total, but we're excluding playout_data)
- The largest table we need is `cache_route_impacts_15min_by_demo` (~416M rows)
- Demo campaigns: 16699, 16879, 16882, 18409

**Tasks for this session:**

1. **Size estimation**: Query MS-01 to get actual sizes of required tables (excluding playout_data)

2. **DigitalOcean requirements**: Based on the size, recommend:
   - Database tier (Basic vs Professional)
   - Storage size needed
   - Compute size (vCPUs/RAM)
   - Estimated monthly cost

3. **Export strategy**: Decide between:
   - Full export (all campaigns, ~50-100GB estimate)
   - Demo-only export (specific campaigns, ~1-5GB estimate)

4. **Export execution**: Run the export from MS-01

5. **DigitalOcean setup**:
   - Create managed PostgreSQL database
   - Configure connection settings
   - Import the data

6. **App configuration**:
   - Add DigitalOcean database credentials to `.env`
   - Test the app connects correctly
   - Verify demo campaigns load properly

**Questions to answer:**
- Should we do a full export or demo-only for cost savings?
- What's the actual size of the data we need?
- What DigitalOcean tier gives us acceptable performance for demos?

---

## Reference Files

- `docs/12-database-export.md` - Table documentation
- `scripts/export_demo_database.sh` - Export script
- `docs/11-database-schema.md` - Full schema reference
- `handover/2026-01-12-database-export-analysis.md` - Previous session handover

---

## Quick Commands

```bash
# Check export script help
./scripts/export_demo_database.sh --help

# Demo export (smaller)
./scripts/export_demo_database.sh --campaigns "16699,16879,16882,18409" --host ms01.local

# Full export
./scripts/export_demo_database.sh --host ms01.local --db route_playout
```

---

*Prepared: 12 January 2026*
