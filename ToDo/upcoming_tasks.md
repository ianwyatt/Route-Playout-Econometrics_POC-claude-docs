# Upcoming Tasks

## Next Priority: DigitalOcean Deployment

**Status**: Database fully cleaned (57 GB), re-export recommended before deployment

### Background

- Database export prepared (14 January 2026): `~/poc export/route_poc_export/` (7.9 GB, pre-cleanup)
- MVs converted to regular tables (pg_dump workaround)
- **5 Feb 2026**: Full cleanup — dropped 64 indexes + 24 tables (114 GB → 57 GB, 50% reduction)
- Re-exporting after cleanup would produce a much smaller transfer (~3-4 GB estimated)

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

## Completed: Code Quality Review (5 February 2026)

- Agent-based review of all documentation and source code (4 rounds)
- Fixed 17 documentation inaccuracies across 10 files
- Updated 15 stale MV references across 9 source files
- Deleted 7 dead code files (2,411 lines removed)
- Fixed runtime bug: frame count query referenced dropped table
- Fixed null safety issue in campaign count query
- 4 commits: `183766c`, `4b9b7bd`, `cc34147`, `bdf4ed0`
- Handover: `handover/SESSION_2026-02-05_CODE_QUALITY_REVIEW.md`

---

## Completed: Database Cleanup (5 February 2026)

- Audited all 101 indexes and 42 tables against every SQL query in `src/db/`
- Dropped 64 unused indexes (38 GB) + 24 unused tables (19 GB)
- Database: 114 GB → 57 GB (57 GB freed, 50% reduction)
- 18 tables + 1 view + 14 indexes remaining — all used by app
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
