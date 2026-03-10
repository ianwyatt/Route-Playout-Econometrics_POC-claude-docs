# Session Handover: DigitalOcean Deployment Preparation

**Date:** 10 February 2026
**Session Focus:** Deployment planning and runbook creation for DigitalOcean

---

## What Was Done

### 1. Deployment Plan Review and Approval

Reviewed the comprehensive DigitalOcean deployment plan covering 9 phases:
- Infrastructure provisioning (Managed PostgreSQL + Droplet)
- Droplet hardening
- Database restore (5.7 GB dump → 57 GB)
- App deployment with UV
- systemd process management
- Caddy reverse proxy with self-signed cert (IP only)
- UFW firewall
- PocketID authentication
- GB geo-blocking

### 2. Key Decision: Zero Code Changes (Option A)

**Problem:** The plan originally called for adding `sslmode` to `connection.py`. However, the codebase is public on GitHub and used by Adwanted for local deployment. Any code change risks breaking their setup.

**Options considered:**
- **Option A (chosen):** Set `PGSSLMODE=require` in DO `.env` file. libpq reads this natively — python-dotenv loads it into `os.environ`, psycopg2/libpq picks it up automatically. Zero code changes.
- **Option B:** Add `sslmode` parameter to `psycopg2.connect()` with `prefer` default. Safe but unnecessary.
- **Option C:** Maintain a deployment branch. Too much overhead.

**Result:** No files in `src/` are modified. The entire deployment is server configuration only.

### 3. Deployment Runbook Created

Created `Claude/docs/Documentation/DIGITALOCEAN_DEPLOYMENT_RUNBOOK.md` with:
- Complete step-by-step commands for all 9 phases
- systemd service configuration (`pharos.service`)
- Caddy reverse proxy config with WebSocket support
- Log rotation config
- DO-specific `.env` template (including `PGSSLMODE=require`)
- PocketID Docker Compose template
- Verification checklist
- Rollback plan
- Monitoring commands

### 4. Updated Task Tracking

Updated `Claude/todo/upcoming_tasks.md` with:
- Option A decision documented
- Reorganised tasks into deployment phases
- Added runbook to reference files table

---

## Files Created/Modified

| File | Action |
|------|--------|
| `Claude/docs/Documentation/DIGITALOCEAN_DEPLOYMENT_RUNBOOK.md` | Created — full deployment runbook |
| `Claude/todo/upcoming_tasks.md` | Updated — deployment phases and Option A decision |
| `Claude/handover/SESSION_2026-02-10_DIGITALOCEAN_DEPLOYMENT_PREP.md` | Created — this file |

**No source code files were modified.**

---

## What's Next

Execute the runbook on DigitalOcean infrastructure:

1. **Provision** DB + Droplet via DO dashboard (~10 min)
2. **Harden** droplet — deploy user, SSH lockdown (~15 min)
3. **Restore** database — download dump, pg_restore (~90 min, runs in background)
4. **Deploy** app — clone, uv sync, configure .env, test (~25 min, concurrent with #3)
5. **systemd** service for auto-restart (~10 min)
6. **Caddy** reverse proxy with self-signed cert (~15 min)
7. **Firewall** — UFW allow 22/80/443 only (~5 min)
8. **PocketID** — Docker + forward auth (~45 min, skip if it blocks)
9. **Geo-blocking** — iptables GeoIP for GB only (~15 min)

**Total estimated: ~4 hours** (DB restore overlaps with app setup)

---

## Key Technical Details for Next Session

- **DO PostgreSQL port**: 25060 (not standard 5432)
- **SSL trick**: `PGSSLMODE=require` in `.env`, read by libpq natively
- **Streamlit binding**: `127.0.0.1:8504` (localhost only, Caddy proxies)
- **Self-signed cert**: Expected browser warning for IP-only; swap to Let's Encrypt with domain
- **PocketID**: Most uncertain phase — deploy without auth if it blocks

---

*Last Updated: 10 February 2026*
