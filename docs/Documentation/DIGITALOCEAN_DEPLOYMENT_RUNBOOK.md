# DigitalOcean Deployment Runbook

**Created:** 10 February 2026
**Status:** Ready to execute
**Author:** Claude + Doctor Biz
**Estimated Time:** ~4 hours (DB restore overlaps with app setup)
**Monthly Cost:** ~$67 ($61 database + $6 droplet)

---

## Decision Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| SSL support | Option A: zero code changes | `PGSSLMODE=require` in DO `.env`, libpq reads it natively via python-dotenv → os.environ. No risk to public GitHub repo or Adwanted's local setup. |
| Auth approach | PocketID via Pangolin | Passkey-only, no passwords. If it blocks, deploy without auth first. |
| Initial HTTPS | Self-signed (IP only) | No domain yet. Swap to Let's Encrypt when domain added. |
| Geo-blocking | UFW + GeoIP initially | Switch to Cloudflare when domain added. |

---

## Prerequisites

Before starting, ensure you have:

- [ ] DigitalOcean account with payment method
- [ ] SSH key pair (if not already generated: `ssh-keygen -t ed25519`)
- [ ] Fresh Dropbox link for the database dump (5.7 GB)
- [ ] This runbook open on your local machine

---

## Phase 1: Provision Infrastructure (~10 min)

### 1.1 Managed PostgreSQL Database

**DO Dashboard → Databases → Create Database Cluster**

| Setting | Value |
|---------|-------|
| Engine | PostgreSQL 17 |
| Region | London (LON1) |
| Plan | Basic |
| Size | 4 GB RAM / 2 vCPUs / 60 GB storage |
| Database name | `route_poc` |
| Cluster name | `route-poc-db` |

After creation, note down:
- **Host**: `route-poc-db-do-user-XXXXX-0.x.db.ondigitalocean.com`
- **Port**: `25060`
- **Username**: `doadmin`
- **Password**: (shown once, save it)
- **SSL**: Required (this is enforced by DO)

### 1.2 App Droplet

**DO Dashboard → Droplets → Create Droplet**

| Setting | Value |
|---------|-------|
| Region | London (LON1) |
| Image | Ubuntu 24.04 (LTS) x64 |
| Size | Basic, Regular, $6/mo (1 GB / 1 vCPU / 25 GB SSD) |
| Auth | SSH key (select your key) |
| Hostname | `pharos` |

After creation, note down the **Droplet IP address**.

### 1.3 Add Droplet to Database Trusted Sources

**DO Dashboard → Databases → route-poc-db → Settings → Trusted Sources**

Add the droplet (`pharos`) to trusted sources so it can connect to the database.

---

## Phase 2: Harden Droplet (~15 min)

SSH in as root:

```bash
ssh root@<DROPLET_IP>
```

### 2.1 Create deploy user

```bash
adduser deploy
# Set a strong password when prompted

usermod -aG sudo deploy

# Copy SSH keys to new user
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

### 2.2 SSH hardening

```bash
nano /etc/ssh/sshd_config
```

Set these values:

```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Restart SSH:

```bash
systemctl restart sshd
```

**IMPORTANT:** Before closing your root session, open a NEW terminal and verify you can SSH as `deploy`:

```bash
ssh deploy@<DROPLET_IP>
```

If that works, you can close the root session. If not, fix the config before logging out.

---

## Phase 3: Database Setup (~90 min)

SSH in as deploy:

```bash
ssh deploy@<DROPLET_IP>
```

### 3.1 Download database dump from Dropbox

```bash
curl -L -o /tmp/route_poc.dump "<DROPBOX_LINK>"
```

This is 5.7 GB — takes a few minutes depending on connection speed. Verify the size:

```bash
ls -lh /tmp/route_poc.dump
# Should be approximately 5.7 GB
```

### 3.2 Install PostgreSQL client

```bash
sudo apt update
sudo apt install -y postgresql-client
```

### 3.3 Test database connection

```bash
psql "host=<DB_HOST> port=25060 dbname=route_poc user=doadmin password=<DOADMIN_PASSWORD> sslmode=require" -c "SELECT 1;"
```

If this returns `1`, the connection is working.

### 3.4 Restore database

```bash
PGPASSWORD="$DOADMIN_PASSWORD" pg_restore \
  -h <DB_HOST> \
  -p 25060 \
  -U doadmin \
  -d route_poc \
  --no-owner \
  --no-privileges \
  -j 4 \
  /tmp/route_poc.dump
```

This restores 57 GB of data and takes 60–90 minutes. The `-j 4` flag uses 4 parallel jobs to speed things up.

**While this runs, proceed to Phase 4 in another terminal.**

### 3.5 Create read-only application user

After restore completes:

```bash
psql "host=<DB_HOST> port=25060 dbname=route_poc user=doadmin password=<DOADMIN_PASSWORD> sslmode=require"
```

Run these SQL commands:

```sql
CREATE USER app_readonly WITH PASSWORD '<GENERATE_A_STRONG_PASSWORD>';
GRANT CONNECT ON DATABASE route_poc TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;
\q
```

### 3.6 Verify data integrity

```bash
psql "host=<DB_HOST> port=25060 dbname=route_poc user=app_readonly password=<APP_PASSWORD> sslmode=require"
```

```sql
SELECT COUNT(*) FROM mv_campaign_browser;
-- Expect: 836

SELECT COUNT(DISTINCT campaign_id) FROM cache_route_impacts_15min_by_demo;
-- Should return a number (this is the main data table)

\dt
-- Should show 18 tables + 1 view

\q
```

### 3.7 Clean up dump file

```bash
rm /tmp/route_poc.dump
```

---

## Phase 4: App Deployment (~25 min)

**Run this in a second terminal while the database restores.**

```bash
ssh deploy@<DROPLET_IP>
```

### 4.1 System updates and dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv git curl
```

### 4.2 Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

Verify:

```bash
uv --version
```

### 4.3 Clone repository

```bash
cd /home/deploy
git clone https://github.com/RouteResearch/Route-Playout-Econometrics_POC.git
cd Route-Playout-Econometrics_POC
```

### 4.4 Install Python dependencies

```bash
uv sync
```

### 4.5 Create .env file

```bash
nano .env
```

Paste this content, replacing the placeholders:

```bash
# DigitalOcean Managed PostgreSQL
POSTGRES_HOST_PRIMARY=<DB_HOST>.ondigitalocean.com
POSTGRES_PORT_PRIMARY=25060
POSTGRES_USER_PRIMARY=app_readonly
POSTGRES_PASSWORD_PRIMARY=<APP_READONLY_PASSWORD>
POSTGRES_DATABASE_PRIMARY=route_poc

# libpq SSL mode — required for DO Managed PostgreSQL
# This is read natively by psycopg2 via libpq, no code changes needed
PGSSLMODE=require

# Application settings
USE_PRIMARY_DATABASE=true
ENVIRONMENT=production
LOG_LEVEL=INFO

# Demo mode — set to true for presentations
DEMO_MODE=false

# Selective anonymisation — set media owner name to protect their brands
# Only active when DEMO_MODE=true
# DEMO_PROTECT_MEDIA_OWNER=Global
```

Lock down permissions:

```bash
chmod 600 .env
```

### 4.6 Test the application (after DB restore completes)

```bash
uv run streamlit run src/ui/app.py --server.port 8504 --server.address 0.0.0.0
```

Open `http://<DROPLET_IP>:8504` in your browser. Verify:

- [ ] App loads
- [ ] Campaign browser shows campaigns
- [ ] Campaign 16699 loads with all 6 tabs
- [ ] Data appears in charts and tables

Then kill the test process with `Ctrl+C`.

---

## Phase 5: Process Management (~10 min)

### 5.1 Create systemd service

```bash
sudo nano /etc/systemd/system/pharos.service
```

Paste:

```ini
[Unit]
Description=Pharos Route Playout Streamlit App
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/deploy/Route-Playout-Econometrics_POC
EnvironmentFile=/home/deploy/Route-Playout-Econometrics_POC/.env
ExecStart=/home/deploy/.local/bin/uv run streamlit run src/ui/app.py --server.port 8504 --server.address 127.0.0.1
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/log/pharos.log
StandardError=append:/var/log/pharos.log

[Install]
WantedBy=multi-user.target
```

**Note:** `--server.address 127.0.0.1` binds to localhost only. Caddy will proxy external traffic.

### 5.2 Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable pharos
sudo systemctl start pharos
```

### 5.3 Verify

```bash
sudo systemctl status pharos
# Should show "active (running)"

# Check it's listening on localhost only
curl -s http://127.0.0.1:8504 | head -5
# Should return HTML
```

### 5.4 Create log rotation

```bash
sudo nano /etc/logrotate.d/pharos
```

Paste:

```
/var/log/pharos.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 644 deploy deploy
    postrotate
        systemctl restart pharos
    endscript
}
```

Create the log file with correct ownership:

```bash
sudo touch /var/log/pharos.log
sudo chown deploy:deploy /var/log/pharos.log
```

---

## Phase 6: Reverse Proxy + HTTPS (~15 min)

### 6.1 Install Caddy

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

### 6.2 Configure Caddyfile

```bash
sudo nano /etc/caddy/Caddyfile
```

Paste:

```
:443 {
    tls internal

    reverse_proxy 127.0.0.1:8504 {
        # WebSocket support for Streamlit
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }

    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }
}

:80 {
    redir https://{host}{uri} permanent
}
```

**Note:** `tls internal` generates a self-signed certificate. Your browser will show a warning — this is expected for IP-only access. When you add a domain, replace `tls internal` with nothing (Caddy auto-provisions Let's Encrypt).

### 6.3 Restart Caddy

```bash
sudo systemctl restart caddy
sudo systemctl status caddy
```

### 6.4 Test HTTPS access

Open `https://<DROPLET_IP>` in your browser. Accept the self-signed certificate warning. The app should load.

---

## Phase 7: Firewall (~5 min)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP redirect'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw enable
```

Confirm with `y` when prompted.

### 7.1 Verify port 8504 is NOT accessible externally

From your local machine:

```bash
curl -s http://<DROPLET_IP>:8504
# Should timeout or connection refused
```

### 7.2 Verify HTTPS still works

```bash
curl -sk https://<DROPLET_IP>
# Should return HTML (the -k flag accepts self-signed cert)
```

---

## Phase 8: PocketID Authentication (~45 min)

> **This is the least predictable phase.** If it blocks progress, skip it and come back later. The app is already secured by HTTPS + firewall at this point.

### 8.1 Install Docker

```bash
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable docker
sudo usermod -aG docker deploy
```

Log out and back in for the docker group to take effect:

```bash
exit
ssh deploy@<DROPLET_IP>
```

### 8.2 Create Pangolin + PocketID directory

```bash
mkdir -p ~/pangolin && cd ~/pangolin
```

### 8.3 Deploy with Docker Compose

Create `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Paste:

```yaml
services:
  pocket-id:
    image: stonith404/pocket-id
    container_name: pocket-id
    restart: unless-stopped
    ports:
      - "127.0.0.1:8081:80"
    environment:
      - PUBLIC_APP_URL=https://<DROPLET_IP>:8444
      - TRUST_PROXY=true
    volumes:
      - ./pocketid-data:/app/data
```

Start it:

```bash
docker compose up -d
```

### 8.4 Configure Caddy for PocketID

Update the Caddyfile to add PocketID and forward auth:

```bash
sudo nano /etc/caddy/Caddyfile
```

```
# Main app — requires PocketID authentication
:443 {
    tls internal

    # Forward auth to PocketID
    # (This section needs working through interactively —
    #  Pangolin/PocketID forward auth configuration varies by version)

    reverse_proxy 127.0.0.1:8504 {
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }

    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }
}

# PocketID auth UI
:8444 {
    tls internal
    reverse_proxy 127.0.0.1:8081
}

:80 {
    redir https://{host}{uri} permanent
}
```

```bash
sudo systemctl restart caddy
```

> **Note:** The PocketID forward auth integration will likely need interactive debugging. The exact configuration depends on the PocketID version and how it exposes its OIDC endpoints. We'll work through this on the live droplet.

### 8.5 Allow PocketID port through firewall

```bash
sudo ufw allow 8444/tcp comment 'PocketID auth UI'
```

---

## Phase 9: GB Geo-Blocking (~15 min)

### 9.1 Install GeoIP tools

```bash
sudo apt install -y xtables-addons-common libtext-csv-xs-perl
```

### 9.2 Download MaxMind GeoLite2 database

```bash
sudo mkdir -p /usr/share/xt_geoip
cd /tmp
sudo /usr/lib/xtables-addons/xt_geoip_dl
sudo /usr/lib/xtables-addons/xt_geoip_build -D /usr/share/xt_geoip *.csv
```

> **Note:** MaxMind now requires a free licence key. If this step fails, register at https://www.maxmind.com/en/geolite2/signup and use the licence key with the download.

### 9.3 Configure iptables geo-blocking

```bash
# Allow GB IPs on HTTPS
sudo iptables -I INPUT -p tcp --dport 443 -m geoip --src-cc GB -j ACCEPT

# Allow GB IPs on HTTP (redirect)
sudo iptables -I INPUT -p tcp --dport 80 -m geoip --src-cc GB -j ACCEPT

# Drop non-GB traffic on web ports (after the ACCEPT rules)
sudo iptables -A INPUT -p tcp --dport 443 -j DROP
sudo iptables -A INPUT -p tcp --dport 80 -j DROP
```

### 9.4 Make persistent

```bash
sudo apt install -y iptables-persistent
sudo netfilter-persistent save
```

> **When domain is added later:** Switch to Cloudflare for geo-blocking + DDoS protection (much simpler and more reliable than iptables GeoIP).

---

## Verification Checklist

Run through this list after all phases are complete:

```bash
# 1. Service is running
sudo systemctl status pharos
# Expected: active (running)

# 2. Auto-restart works
sudo systemctl kill pharos
sleep 15
sudo systemctl status pharos
# Expected: active (running) — systemd restarted it

# 3. Logs are working
sudo tail -20 /var/log/pharos.log
# Expected: Streamlit startup messages

# 4. Port 8504 NOT accessible externally (run from local machine)
curl -s --connect-timeout 5 http://<DROPLET_IP>:8504
# Expected: timeout/connection refused

# 5. HTTPS works (run from local machine)
curl -sk https://<DROPLET_IP> | head -5
# Expected: HTML content

# 6. SSH hardened (run from local machine)
ssh root@<DROPLET_IP>
# Expected: Permission denied

# 7. Firewall status
sudo ufw status verbose
# Expected: 22, 80, 443 allowed; default deny incoming
```

Browser checks:

- [ ] `https://<DROPLET_IP>` loads (accept self-signed cert warning)
- [ ] Campaign browser shows ~836 campaigns
- [ ] Campaign 16699 loads with all 6 tabs and data
- [ ] Charts render correctly
- [ ] CSV export downloads
- [ ] Excel export downloads
- [ ] PocketID login required (if Phase 8 completed)
- [ ] Non-GB IP blocked (if Phase 9 completed)

---

## Updating the App

When you push changes to GitHub:

```bash
ssh deploy@<DROPLET_IP>
cd ~/Route-Playout-Econometrics_POC
git pull
uv sync
sudo systemctl restart pharos
```

---

## Monitoring

```bash
# Service status
sudo systemctl status pharos

# Live logs
sudo tail -f /var/log/pharos.log

# Resource usage
htop

# Disk usage
df -h

# Database connection test
psql "host=<DB_HOST> port=25060 dbname=route_poc user=app_readonly password=<PASSWORD> sslmode=require" -c "SELECT COUNT(*) FROM mv_campaign_browser;"
```

---

## Rollback Plan

If anything goes wrong:

1. **App won't start:** Check logs (`/var/log/pharos.log`), verify `.env` credentials
2. **Database connection fails:** Verify droplet is in trusted sources, check `PGSSLMODE=require`
3. **Can't SSH in:** Use DO console (Dashboard → Droplets → pharos → Console)
4. **Need to start over:** Destroy droplet and database, re-provision (infrastructure is stateless except for DB data)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| 60 GB storage tight for 57 GB DB | Monitor during restore. Upgrade to 115 GB ($31/mo) if needed. |
| 1 GB RAM too small for Streamlit | Monitor with `htop`. Upgrade to 2 GB ($12/mo) if needed. |
| PocketID config unclear | Deploy without auth first (Phases 1–7), add auth as follow-up. |
| Dropbox link expires | Generate fresh link immediately before starting Phase 3. |
| Geo-blocking breaks access | Test from a GB IP first. If GeoIP module fails, skip and use Cloudflare later. |

---

## Future: Adding a Domain

When you have a domain name:

1. Point DNS A record to droplet IP
2. Update Caddyfile — replace `:443` with `yourdomain.com` and remove `tls internal`
3. Caddy will auto-provision Let's Encrypt certificates
4. Switch geo-blocking from iptables to Cloudflare
5. Update PocketID `PUBLIC_APP_URL`

---

*Last Updated: 10 February 2026*
