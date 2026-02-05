# Session Handover: Adwanted Handover Complete + VM Installation Test

**Date**: 5 February 2026
**Session Focus**: Final codebase cleanup, documentation fixes, VM installation testing

---

## Summary

Completed Adwanted developer handover preparation:
1. Removed all dead code references from documentation
2. Fixed environment variable naming inconsistencies
3. Successfully tested fresh installation on Ubuntu 24.04 VM
4. Documented GitHub fine-grained token authentication
5. Updated tag `v2.0-adwanted-handover` to include all fixes

---

## Work Completed

### Documentation Fixes

| File | Fix |
|------|-----|
| `README.md` | Removed `src/services/` from structure, fixed pg_restore command, added Linux PostgreSQL note |
| `docs/01-architecture.md` | Removed `cache_queries.py`, `db_helpers.py`, `services/` references |
| `docs/04-cache-integration.md` | Complete rewrite for MV-based architecture (removed deleted functions) |
| `docs/05-cache-troubleshooting.md` | Replaced Python health check with SQL commands |
| `docs/09-credentials.md` | Fixed `POSTGRES_HOST_LOCAL` → `POSTGRES_HOST_SECONDARY` |
| `docs/11-database-export.md` | Removed `cache_campaign_brand_reach` (dropped table) |
| `.env.example` | Removed pipeline repo URL reference |

### Database Cleanup

- Dropped `cache_campaign_brand_reach` table (unused after removing `query_brand_reach_cache`)
- Ran `VACUUM ANALYZE`
- Created new backup: `~/Desktop/route_poc_adwanted_20260204.dump` (7.9 GB)

### VM Installation Test (Ubuntu 24.04)

Successfully tested full installation from scratch:

| Step | Status |
|------|--------|
| Clone from GitHub (fine-grained token) | ✓ |
| Install uv | ✓ |
| `uv sync` with Python 3.12 | ✓ |
| Database restore (114 GB) | ✓ |
| Configure .env | ✓ |
| Run app | ✓ |

**Key findings:**
- Fine-grained tokens require `x-access-token` as username (not GitHub username)
- Ubuntu PostgreSQL requires password for TCP connections (unlike macOS Homebrew)
- Python 3.12 (Ubuntu 24.04 default) works fine

### New Documentation

- `docs/Documentation/GITHUB_PRIVATE_REPO_ACCESS.md` — Fine-grained token authentication guide

---

## Commits (Code Repo)

| Hash | Message |
|------|---------|
| `aaec1d5` | docs: fix dead code references and env var naming |
| `32b31c8` | docs: remove pipeline repo URL from .env.example |
| `eb5a7c8` | docs: add Linux PostgreSQL password setup note |

### Tag

`v2.0-adwanted-handover` updated to `eb5a7c8`

---

## Commits (Docs Repo)

| Hash | Message |
|------|---------|
| `c5eb82e` | docs: add GitHub fine-grained token authentication guide |

---

## Database State

**Local Mac:**
- `cache_campaign_brand_reach` table DROPPED
- Database size: 114 GB
- Backup at: `~/Desktop/route_poc_adwanted_20260204.dump` (7.9 GB)

**MS-01 (Primary):** Unchanged

---

## For Next Session: DigitalOcean Deployment

### Context

Previous session (14 January 2026) prepared database export for DigitalOcean:
- Truncated `playout_data` on local Mac (freed 533 GB)
- Converted 21 MVs to regular tables (pg_dump limitation workaround)
- Exported database: `~/poc export/route_poc_export/` (7.9 GB)

### Task List

See `todo/archive/2026-01-14-digitalocean-deployment.md` for full details.

**Part 2: DigitalOcean Deployment (PENDING)**

Database:
- [ ] Create DigitalOcean account / login
- [ ] Provision Managed PostgreSQL (London, Basic 4 GB, ~$61/month)
- [ ] Transfer export file to DO
- [ ] Restore database with pg_restore
- [ ] Create read-only app user
- [ ] Verify data integrity

App Droplet:
- [ ] Provision Droplet (London, Basic 1 GB, ~$6/month)
- [ ] SSH hardening
- [ ] Install Python 3.11+, UV, git
- [ ] Clone repo, install dependencies
- [ ] Configure .env for cloud database

Reverse Proxy & Security:
- [ ] Install Caddy (or nginx)
- [ ] HTTPS with Let's Encrypt
- [ ] PocketID authentication
- [ ] GB geo-blocking
- [ ] Security headers, rate limiting

**Estimated cost:** ~$67/month

### Key Files

| File | Purpose |
|------|---------|
| `handover/2026-01-14-digitalocean-database-export.md` | Full handover with export details |
| `todo/archive/2026-01-14-digitalocean-deployment.md` | Task checklist |
| `docs/Documentation/SELF_HOSTED_DEPLOYMENT_GUIDE.md` | Pangolin/PocketID guide (alternative) |
| `~/poc export/route_poc_export/` | Database export for DO |

### Start Prompt

```
I want to continue deploying the Route Playout Econometrics POC to DigitalOcean.

Previous work:
- Database export ready at ~/poc export/route_poc_export/ (7.9 GB)
- MVs converted to tables for pg_dump compatibility
- Export excludes playout_data (not needed by UI)

Next steps:
1. Provision DigitalOcean Managed PostgreSQL (London, Basic 4 GB)
2. Restore database
3. Provision Droplet for Streamlit app
4. Deploy with PocketID auth and GB geo-blocking

See handover: handover/2026-01-14-digitalocean-database-export.md
```

---

## VM Test Summary

**Platform:** Ubuntu 24.04 on Parallels (160 GB disk)
**PostgreSQL:** 17 (from official repo)
**Python:** 3.12 (system default)

### Installation Steps Verified

1. Add PostgreSQL 17 repo and install
2. Clone repo with fine-grained GitHub token (`x-access-token:TOKEN@github.com/...`)
3. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. `uv sync` (creates venv, installs all deps)
5. Copy database dump, restore with `sudo -u postgres pg_restore`
6. Set postgres password: `ALTER USER postgres PASSWORD 'xxx'`
7. Configure `.env` with `USE_PRIMARY_DATABASE=false` and password
8. Run: `uv run streamlit run src/ui/app.py --server.port 8504`

All tabs functional, data displays correctly.

---

*Handover prepared: 5 February 2026*
