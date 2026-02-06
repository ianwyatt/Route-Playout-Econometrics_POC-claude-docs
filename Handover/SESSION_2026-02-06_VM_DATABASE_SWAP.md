# Session Handover: VM Database Swap (114 GB → 57 GB)

**Date**: 6 February 2026
**Session Focus**: Replace the full 114 GB database on the Ubuntu VM with the reduced 57 GB export

---

## Summary

Swapped the Ubuntu 24.04 Parallels VM database from the original 114 GB install to the
post-cleanup 57 GB export. Also pulled the latest code (6 commits behind) and confirmed
the app runs correctly on the updated database. VM disk usage dropped from 138 GB to 81 GB.

---

## Work Completed

### Database Swap

| Step | Detail |
|------|--------|
| Drop existing database | `DROP DATABASE route_poc` — freed 114 GB |
| Transfer dump | Copied `exports/route_poc_adwanted_20260205.dump` (5.7 GB) to Desktop, accessed via Parallels shared folder |
| Restore | `pg_restore --no-owner --no-privileges -d route_poc -j 4` — restored to 57 GB |
| VACUUM ANALYZE | Completed after restore |
| Verification | 18 tables + 1 view, 19 indexes, 836 campaigns, 415M+ impact rows |

### VM Disk Space

| Metric | Before | After |
|--------|--------|-------|
| Disk used | 138 GB / 251 GB (58%) | 81 GB / 251 GB (34%) |
| Free space | 103 GB | 159 GB |
| Database size | 114 GB | 57 GB |

### Code Update

Pulled 6 commits (`aaec1d5` → `76e0aca`):
- Dead code removal (7 files, 2,411 lines)
- 6 unused runtime deps removed (fastapi, uvicorn, sqlalchemy, httpx, click, rich)
- Stale MV references fixed across source and docs
- Null safety fix for campaign count query
- README updated for econometrician audience

`uv sync` removed the 6 unused deps from the VM's venv automatically.

### Infrastructure Fixes

- Installed `openssh-server` on VM (was not installed)
- Fixed git safe directory warning (root ownership from `prlctl exec`)
- Fixed file ownership after root-executed `git pull` and `uv sync`

### App Verification

- Streamlit running on `http://10.211.55.5:8504`
- HTTP 200 confirmed from Mac
- Database connection working (836 campaigns returned)
- App on latest code (`76e0aca`)

---

## VM State

**Platform:** Ubuntu 24.04.3 ARM64 on Parallels (251 GB disk)
**IP:** 10.211.55.5
**PostgreSQL:** 17
**Python:** 3.12.3
**uv:** 0.9.30
**SSH:** Installed and running (openssh-server)
**User:** parallels (app runs as this user)
**Code:** `/home/parallels/Route-Playout-Econometrics_POC` at `76e0aca`
**Database:** `route_poc` — 57 GB, 18 tables + 1 view, 19 indexes
**App:** `uv run streamlit run src/ui/app.py --server.port 8504 --server.address 0.0.0.0`

---

## Working with the VM via prlctl

`prlctl exec` runs as root but has quoting issues with complex commands. Workaround:

```bash
# Write a script locally, copy to VM, execute
cat > /tmp/myscript.sh << 'EOF'
#!/bin/bash
su -s /bin/bash postgres << 'SUEOF'
psql -d route_poc -c "SELECT count(*) FROM mv_campaign_browser"
SUEOF
EOF

prlctl exec "Ubuntu 24.04.3 ARM64" bash -c "cat > /tmp/myscript.sh" < /tmp/myscript.sh
prlctl exec "Ubuntu 24.04.3 ARM64" chmod +x /tmp/myscript.sh
prlctl exec "Ubuntu 24.04.3 ARM64" /tmp/myscript.sh
```

Alternatively, SSH is now available: `ssh parallels@10.211.55.5` (needs key or password setup).

---

## Files on Mac (Cleanup Note)

The following exports exist on the Mac and can be cleaned up if space is needed:

| File | Size | Notes |
|------|------|-------|
| `exports/route_poc_adwanted_20260205.dump` | 5.7 GB | Post-cleanup export (current, keep) |
| `exports/pharos_source_20260205.tar.gz` | 228 KB | Source code archive for Adwanted |
| `~/poc export/route_poc_export/` | 7.9 GB | Old pre-cleanup export (can delete) |
| `~/Desktop/route_poc_adwanted_20260204.dump` | 7.9 GB | Old pre-cleanup backup (can delete) |

The old exports total ~16 GB and are superseded by the 5.7 GB post-cleanup dump.

---

## Next Session: DigitalOcean Deployment

The VM swap was a stepping stone. The DigitalOcean deployment remains the next priority.
See `Claude/todo/upcoming_tasks.md` for the full task list.

### Start Prompt

```
Continue deploying Route Playout Econometrics POC to DigitalOcean.

Previous work:
- Database cleaned: 114 GB → 57 GB
- Export ready: exports/route_poc_adwanted_20260205.dump (5.7 GB compressed, 57 GB restored)
- VM tested: Ubuntu 24.04, reduced DB, app fully functional
- Repo public: https://github.com/RouteResearch/Route-Playout-Econometrics_POC

Next steps:
1. Provision DO Managed PostgreSQL (London, Basic 4 GB, 60 GB storage)
2. Transfer and restore database
3. Provision Droplet for Streamlit app
4. Deploy with PocketID auth and GB geo-blocking

See handover: Claude/Handover/SESSION_2026-02-06_VM_DATABASE_SWAP.md
See tasks: Claude/todo/upcoming_tasks.md
```

---

*Handover prepared: 6 February 2026*
