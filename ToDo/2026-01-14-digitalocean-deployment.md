# DigitalOcean Deployment - Task List

**Last Updated**: 14 January 2026

---

## Part 1: Database Export (COMPLETED ✅)

- [x] Analyse database table sizes on MS-01
- [x] Truncate playout_data on LOCAL Mac (freed 533 GB)
- [x] Run VACUUM ANALYZE
- [x] Discover pg_dump MV limitation (doesn't export MV row data)
- [x] Create MV-to-table conversion script
- [x] Convert 21 MVs to regular tables
- [x] Export database with pg_dump (7.9 GB compressed)
- [x] Document export location and restore commands

**Export Location**: `~/poc export/route_poc_export/`

---

## Part 2: DigitalOcean Deployment (PENDING)

### Database
- [ ] Create DigitalOcean account / login
- [ ] Provision Managed PostgreSQL (London, Basic 4 GB, ~$61/month)
- [ ] Transfer export file to DO (via Droplet or direct)
- [ ] Restore database with pg_restore
- [ ] Create read-only app user
- [ ] Verify data integrity (check campaign counts, etc.)

### App Droplet
- [ ] Provision Droplet (London, Basic 1 GB, ~$6/month)
- [ ] SSH hardening (key-only, port 2222, Fail2ban)
- [ ] Install Python 3.11+, UV, git
- [ ] Clone repo
- [ ] Install dependencies
- [ ] Configure .env for cloud database

### Reverse Proxy & Security
- [ ] Install Caddy (or nginx)
- [ ] Configure HTTPS with Let's Encrypt
- [ ] Set up PocketID authentication
- [ ] Configure GB geo-blocking
- [ ] Add security headers (HSTS, X-Frame-Options, CSP)
- [ ] Set up rate limiting

### Final Testing
- [ ] Test all tabs in the app
- [ ] Test data export functionality
- [ ] Verify demo mode works
- [ ] Performance test queries

---

## Cost Estimate

| Component | Plan | Monthly Cost |
|-----------|------|--------------|
| Managed PostgreSQL | Basic 4 GB | $60.90 |
| Droplet (App) | Basic 1 GB | $6.00 |
| **Total** | | **~$67/month** |

---

## Reference Files

- Handover: `handover/2026-01-14-digitalocean-database-export.md`
- Export: `~/poc export/route_poc_export/`
- Conversion script: `~/poc export/convert_mvs_to_tables.sql`
- Previous prompt: `todo/2026-01-12-digitalocean-deployment-prompt.md`

---

*Updated: 14 January 2026*
