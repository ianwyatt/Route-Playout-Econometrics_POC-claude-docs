# Upcoming Tasks

## Next Priority: DigitalOcean Deployment

**Status**: Ready to deploy. Fresh database export done, repo public, Adwanted handover package shared.

### Background

- **5 Feb 2026**: Database cleanup — 114 GB → 57 GB (dropped 64 indexes + 24 tables)
- **5 Feb 2026**: Fresh export: `exports/route_poc_adwanted_20260205.dump` (5.7 GB compressed, 57 GB restored)
- **5 Feb 2026**: Repo made public: `https://github.com/RouteResearch/Route-Playout-Econometrics_POC`
- Adwanted handover package shared via Dropbox (database + source + README)

### Tasks

**Database (~$61/month)**
- [ ] Provision DO Managed PostgreSQL (London, Basic 4 GB, 60 GB storage)
- [ ] Transfer `exports/route_poc_adwanted_20260205.dump` (5.7 GB) to DO
- [ ] Restore: `pg_restore -h host -U user -d route_poc --no-owner --no-privileges route_poc_adwanted_20260205.dump`
- [ ] Create read-only app user
- [ ] Verify data integrity (expect 836 rows in mv_campaign_browser)

**App Droplet (~$6/month)**
- [ ] Provision Droplet (London, Basic 1 GB)
- [ ] SSH hardening (key-only, non-standard port, Fail2ban)
- [ ] Install Python 3.11+, UV, git
- [ ] Clone from public repo: `git clone https://github.com/RouteResearch/Route-Playout-Econometrics_POC.git`
- [ ] `uv sync` and configure .env for cloud database

**Security**
- [ ] Install Caddy reverse proxy
- [ ] HTTPS with Let's Encrypt
- [ ] PocketID authentication (passkey-only)
- [ ] GB geo-blocking
- [ ] Security headers, rate limiting

### Reference Files

| File | Purpose |
|------|---------|
| `exports/README.md` | Adwanted handover README with restore instructions |
| `exports/route_poc_adwanted_20260205.dump` | Fresh database export (5.7 GB) |
| `handover/SESSION_2026-02-05_CODE_QUALITY_REVIEW.md` | Code quality review session |
| `handover/SESSION_2026-02-05_INDEX_CLEANUP.md` | Index cleanup SQL + deployment path |
| `docs/Documentation/SELF_HOSTED_DEPLOYMENT_GUIDE.md` | Pangolin/PocketID guide |

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
- Tag `v2.0-adwanted-handover` updated to commit `76e0aca` (was `eb5a7c8`)
- Fresh database export: `exports/route_poc_adwanted_20260205.dump` (5.7 GB)
- GitHub repo made public (issues/wiki/discussions disabled)
- Handover package shared with Adwanted via Dropbox

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
