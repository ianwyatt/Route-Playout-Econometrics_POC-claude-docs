# Upcoming Tasks

## Next Priority: DigitalOcean Deployment

**Status**: Database cleaned up (76 GB), consider re-exporting before deployment

### Background

- Database export prepared (14 January 2026): `~/poc export/route_poc_export/` (7.9 GB)
- MVs converted to regular tables (pg_dump workaround)
- Excludes `playout_data` (not needed by UI)
- **5 Feb 2026**: Index cleanup removed 38 GB of unused indexes (114 GB → 76 GB)
- Re-exporting after cleanup would produce a smaller transfer (~5-6 GB estimated)

### Pre-Deployment Decision

- [ ] **Decide**: Re-export database post-cleanup OR use existing export + run cleanup SQL on DO

### Tasks

**Database (~$61/month)**
- [ ] Provision DO Managed PostgreSQL (London, Basic 4 GB, 60 GB storage)
- [ ] Transfer and restore database
- [ ] If using old export: run index cleanup SQL from handover
- [ ] Create read-only app user
- [ ] Verify data integrity

**App Droplet (~$6/month)**
- [ ] Provision Droplet (London, Basic 1 GB)
- [ ] SSH hardening (key-only, non-standard port, Fail2ban)
- [ ] Install Python 3.11+, UV, git
- [ ] Clone repo and install dependencies
- [ ] Configure .env for cloud database

**Security**
- [ ] Install Caddy reverse proxy
- [ ] HTTPS with Let's Encrypt
- [ ] PocketID authentication (passkey-only)
- [ ] GB geo-blocking
- [ ] Security headers, rate limiting

### Reference Files

| File | Purpose |
|------|---------|
| `handover/SESSION_2026-02-05_INDEX_CLEANUP.md` | Index cleanup SQL + deployment path |
| `handover/2026-01-14-digitalocean-database-export.md` | Export details, restore commands |
| `docs/Documentation/DATABASE_INDEX_CLEANUP.md` | Full index analysis |
| `docs/Documentation/SELF_HOSTED_DEPLOYMENT_GUIDE.md` | Pangolin/PocketID guide |
| `docs/Documentation/GITHUB_PRIVATE_REPO_ACCESS.md` | Fine-grained token auth |

---

## Completed: Database Index Cleanup (5 February 2026)

- Audited all 101 indexes against every SQL query in `src/db/`
- Dropped 64 unused indexes across 4 phases
- Database: 114 GB → 76 GB (38 GB freed, 33% reduction)
- Kept `idx_impacts_demo_campaign` (2.8 GB) as fallback safety net
- Documentation: `docs/Documentation/DATABASE_INDEX_CLEANUP.md`
- Handover: `handover/SESSION_2026-02-05_INDEX_CLEANUP.md`

---

## Completed: Adwanted Handover (5 February 2026)

- All dead code removed from codebase and documentation
- VM installation tested successfully (Ubuntu 24.04)
- GitHub fine-grained token auth documented
- Tag `v2.0-adwanted-handover` at commit `eb5a7c8`
- Database backup: `~/Desktop/route_poc_adwanted_20260204.dump` (7.9 GB)

---

## Completed: Codex Code Review Fixes (4 February 2026)

All 12 actionable findings addressed across 6 rounds. Score: 6.4 → 7.8/10.

---

## Pre-Existing Test Failures (Local DB)

Two test failures when running against local database:

1. `test_empty_demographic_segments_list` — returns all data instead of empty
2. `test_query_performance_under_100ms` — 214ms on local DB

Not blocking; investigate separately.

---

## Future Enhancements

- Cumulative build with daily data (smoother charts)
- Cost and financial tracking
- Natural language query interface
- AI-powered insights
- Classic frame support
- Multi-user support with role-based access
- Demographic filtering for Weekly Reach/GRP tab
- User areas with saved campaigns

---

*Last Updated: 5 February 2026*
