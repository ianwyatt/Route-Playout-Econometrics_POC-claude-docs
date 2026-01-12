# Next Session Prompt: DigitalOcean Full Deployment

Copy and paste this prompt to start the next session:

---

## Prompt

I want to deploy the Route Playout Econometrics POC (both database AND app) to DigitalOcean for reliable demos without depending on my Mac.

**Important context:**
- This is a **demo deployment for my personal use only**
- I'm the only person who will access it
- We should implement geo-blocking to GB for additional security
- Use PocketID for authentication (passkey-only OIDC, no passwords)

In the previous session we:
1. Analysed which tables the app actually needs (see `docs/12-database-export.md`)
2. Created an export script (`scripts/export_demo_database.sh`)
3. Confirmed `playout_data` table is NOT needed - the MVs are self-contained

**Key context:**
- Source database: MS-01 PostgreSQL server (~620GB total, but we're excluding playout_data)
- The largest table we need is `cache_route_impacts_15min_by_demo` (~416M rows)
- Demo campaigns: 16699, 16879, 16882, 18409
- App: Streamlit (Python)

---

## Part 1: Database Deployment

**Tasks:**

1. **Size estimation**: Query MS-01 to get actual sizes of required tables (excluding playout_data)

2. **DigitalOcean Managed PostgreSQL**: Recommend:
   - Database tier (Basic vs Professional)
   - Storage size needed
   - Compute size (vCPUs/RAM)
   - Estimated monthly cost

3. **Export strategy**: Decide between:
   - Full export (all campaigns, ~50-100GB estimate)
   - Demo-only export (specific campaigns, ~1-5GB estimate)

4. **Export and import**: Execute the migration

---

## Part 2: App Deployment

**Tasks:**

5. **DigitalOcean Droplet (VPS)**: Recommend:
   - Droplet size for Streamlit app
   - Region (London for GB geo-blocking)
   - Estimated monthly cost

6. **Security setup** (see detailed recommendations below):
   - VPC: Database on private IP only (not public)
   - Read-only database user (SELECT only)
   - Pangolin or Cloudflare for reverse proxy
   - Geo-blocking to GB only
   - PocketID authentication (passkey-only OIDC)
   - SSH hardening (key-only, non-standard port, Fail2ban)
   - Security headers, rate limiting
   - HTTPS with Let's Encrypt

7. **App deployment**:
   - Install Python/UV
   - Clone repo, install dependencies
   - Configure systemd service or Docker
   - Set up reverse proxy (nginx/Caddy)

8. **Configuration**:
   - Environment variables for cloud database
   - PocketID OIDC settings
   - Test end-to-end

---

## Questions to Answer

**Database:**
- Full export or demo-only for cost savings?
- What's the actual size of the data we need?
- What DigitalOcean tier gives acceptable performance?

**App:**
- What Droplet size for a single-user Streamlit app?
- Docker vs bare metal deployment?
- How to integrate PocketID with Streamlit?
- Best approach for GB geo-blocking?

**Cost:**
- Total monthly cost estimate (database + VPS)?

---

## Security Architecture (Recommended)

```
User → Pangolin (geo-block, SSL) → DO Firewall → Droplet (VPC) → PostgreSQL (private IP)
```

### Essential Security Measures

| Measure | Purpose |
|---------|---------|
| VPC private network | Database not exposed to internet |
| Read-only DB user | Even if compromised, can't modify data |
| Pangolin | Self-hosted proxy (no 100MB limit like Cloudflare) |
| PocketID | Passkey-only auth (phishing resistant) |
| Geo-blocking | GB only, reduces attack surface |
| SSH hardening | Key-only, port 2222, Fail2ban |
| Security headers | HSTS, X-Frame-Options, CSP |
| Rate limiting | Prevent abuse |
| Auto-updates | Unattended security patches |

### Why Pangolin over Cloudflare?

- Cloudflare free tier: 100MB upload/request limit
- Data exports (CSV, Excel, Parquet) could exceed this
- Pangolin: Self-hosted, no limits, still provides SSL + geo-blocking

### Database Security

```sql
-- Read-only user for app
CREATE USER demo_app WITH PASSWORD 'xxx';
GRANT CONNECT ON DATABASE route_playout TO demo_app;
GRANT USAGE ON SCHEMA public TO demo_app;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO demo_app;
```

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
