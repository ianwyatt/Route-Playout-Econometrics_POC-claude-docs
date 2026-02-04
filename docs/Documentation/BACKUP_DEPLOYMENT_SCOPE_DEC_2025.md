# Backup Deployment Scope - Board Demo Dec 4, 2025

**Created**: November 29, 2025
**Deadline**: December 4, 2025 (5 days)
**Status**: Planning

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKUP DEPLOYMENT                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   UI DEVICES                           DATABASES                     │
│   ──────────                           ─────────                     │
│                                                                      │
│   ┌─────────────┐                     ┌─────────────┐               │
│   │  M4 Max     │ ───────────────────▶│   MS01      │               │
│   │  (Primary)  │                     │ 192.168.1.34│               │
│   └─────────────┘                     └─────────────┘               │
│         │                                   ▲                        │
│         │                                   │                        │
│   ┌─────────────┐                           │                        │
│   │  M1 Max     │ ──────────────────────────┘                        │
│   │  (Backup)   │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─▶┌─────────────┐               │
│   └─────────────┘     (failover)      │  Framework  │               │
│                                       │  (Postgres) │               │
│   ┌─────────────┐                     └─────────────┘               │
│   │  Framework  │ ───────────────────▶      │                        │
│   │  (Last     │                     localhost                      │
│   │   Resort)   │                                                    │
│   └─────────────┘                                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Priority Order (Demo Day)

| Priority | UI Device | Database | When to Use |
|----------|-----------|----------|-------------|
| 1 | M4 Max | MS01 | Primary - everything working |
| 2 | M1 Max | MS01 | M4 hardware failure |
| 3 | M4/M1 Max | Framework PG | MS01 down, network OK |
| 4 | Framework | Local PG | Complete network failure |

---

## Part 1: M1 Max MacBook Pro Setup

**Time Estimate**: 30-45 minutes
**Prerequisites**: Git, Python 3.11+, UV installed

### Step 1: Clone Repository

```bash
cd ~/PycharmProjects
git clone git@github.com:route/Route-Playout-Econometrics_POC.git
cd Route-Playout-Econometrics_POC
```

### Step 2: Copy Environment File

```bash
# Copy from M4 Max (via AirDrop, USB, or scp)
scp ianwyatt@<m4-ip>:~/PycharmProjects/Route-Playout-Econometrics_POC/.env .

# Or manually create with these values:
cat > .env << 'EOF'
# MS01 Database (Primary)
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
POSTGRES_PASSWORD_MS01="$POSTGRES_PASSWORD"

# Local Database (not used on M1)
POSTGRES_HOST_LOCAL=localhost
POSTGRES_PORT_LOCAL=5432
POSTGRES_DATABASE_LOCAL=route_poc
POSTGRES_USER_LOCAL=ianwyatt
POSTGRES_PASSWORD_LOCAL=

# API Configuration
MEDIATEL_ENVIRONMENT=uat
LOG_LEVEL=INFO
EOF
chmod 600 .env
```

### Step 3: Install Dependencies

```bash
# Using UV (recommended)
uv sync

# Or pip
pip install -r requirements.txt
```

### Step 4: Add Shell Aliases

```bash
# Add to ~/.zshrc
cat >> ~/.zshrc << 'EOF'

# Streamlit management aliases
alias stopstream='pkill -f "streamlit run"'
alias startstream='USE_MS01_DATABASE=true streamlit run src/ui/app_api_real.py --server.port 8504 &'
alias startstream-framework='USE_MS01_DATABASE=false POSTGRES_HOST_LOCAL=<framework-tailscale-ip> streamlit run src/ui/app_api_real.py --server.port 8504 &'
EOF

source ~/.zshrc
```

### Step 5: Test

```bash
# Start app connecting to MS01
startstream

# Open browser
open http://localhost:8504

# Test a campaign (e.g., 16699)
# Verify data loads correctly
```

---

## Part 2: Framework Desktop Setup (Postgres + UI)

**Time Estimate**: 2-4 hours
**Prerequisites**:
- Framework OS: Linux (Fedora/Ubuntu) or Windows
- Tailscale installed and connected
- At least 100GB free disk space

### Step 1: Install PostgreSQL

**Linux (Fedora):**
```bash
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Install with default options
- Note the password you set for postgres user

### Step 2: Configure PostgreSQL for Remote Access

```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/*/main/postgresql.conf
# Add/modify:
listen_addresses = '*'

# Edit pg_hba.conf
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add line for Tailscale network:
host    all    all    100.64.0.0/10    md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Step 3: Create Database and User

```bash
sudo -u postgres psql << 'EOF'
CREATE DATABASE route_poc;
CREATE USER route_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE route_poc TO route_user;
\q
EOF
```

### Step 4: Restore Database from M4 Mac Backup

**On M4 Max (create backup):**
```bash
# Full database dump (schema + data)
pg_dump -h localhost -U ianwyatt -d route_poc -F c -f ~/route_poc_backup.dump

# Transfer to Framework
scp ~/route_poc_backup.dump framework@<framework-ip>:~/
```

**On Framework (restore):**
```bash
# Restore database
pg_restore -h localhost -U postgres -d route_poc -c ~/route_poc_backup.dump

# Verify
psql -h localhost -U postgres -d route_poc -c "SELECT COUNT(*) FROM cache_route_impacts_15min_by_demo;"
```

### Step 5: Install Python and Clone Repo

**Linux:**
```bash
# Install Python
sudo dnf install python3.11 python3.11-pip git  # Fedora
# or
sudo apt install python3.11 python3.11-pip git  # Ubuntu

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repo
cd ~
git clone git@github.com:route/Route-Playout-Econometrics_POC.git
cd Route-Playout-Econometrics_POC

# Install dependencies
uv sync
```

### Step 6: Configure Environment

```bash
cat > .env << 'EOF'
# Local Database on Framework
POSTGRES_HOST_LOCAL=localhost
POSTGRES_PORT_LOCAL=5432
POSTGRES_DATABASE_LOCAL=route_poc
POSTGRES_USER_LOCAL=postgres
POSTGRES_PASSWORD_LOCAL=your-secure-password

# MS01 (for fallback if needed)
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
POSTGRES_PASSWORD_MS01="$POSTGRES_PASSWORD"

# API Configuration
MEDIATEL_ENVIRONMENT=uat
LOG_LEVEL=INFO
EOF
chmod 600 .env
```

### Step 7: Get Framework Tailscale IP

```bash
tailscale ip -4
# Note this IP (e.g., 100.x.x.x) for connecting from Macs
```

### Step 8: Test Local Postgres

```bash
# Start with local database
USE_MS01_DATABASE=false streamlit run src/ui/app_api_real.py --server.port 8504

# Open browser
open http://localhost:8504
```

---

## Part 3: Database Switching Commands

### From M4 Max or M1 Max

```bash
# Connect to MS01 (default)
USE_MS01_DATABASE=true streamlit run src/ui/app_api_real.py --server.port 8504

# Connect to Framework Postgres (via Tailscale)
USE_MS01_DATABASE=false POSTGRES_HOST_LOCAL=<framework-tailscale-ip> streamlit run src/ui/app_api_real.py --server.port 8504
```

### Quick Aliases (add to ~/.zshrc)

```bash
# M4/M1 Mac aliases
alias startstream='USE_MS01_DATABASE=true streamlit run src/ui/app_api_real.py --server.port 8504 &'
alias startstream-framework='USE_MS01_DATABASE=false POSTGRES_HOST_LOCAL=100.x.x.x streamlit run src/ui/app_api_real.py --server.port 8504 &'
alias stopstream='pkill -f "streamlit run"'
```

---

## Part 4: Pre-Demo Checklist

### Day Before Demo (Dec 3)

- [ ] Test M4 Max → MS01 connection
- [ ] Test M1 Max → MS01 connection
- [ ] Test M4 Max → Framework Postgres connection
- [ ] Test Framework local UI
- [ ] Identify 3 "hero campaigns" with good data
- [ ] Practice demo flow on primary setup
- [ ] Charge all devices
- [ ] Verify Tailscale connections

### Morning of Demo (Dec 4)

- [ ] Start M4 Max Streamlit
- [ ] Have M1 Max ready (app closed, repo up to date)
- [ ] Verify Framework is online and Postgres running
- [ ] Test quick connection to each database
- [ ] Have campaign IDs written down (not just in clipboard)

---

## Part 5: Emergency Procedures

### Scenario 1: M4 Max Dies

1. Open M1 Max
2. `cd ~/PycharmProjects/Route-Playout-Econometrics_POC`
3. `startstream`
4. Continue demo at http://localhost:8504

### Scenario 2: MS01 Unreachable

1. Check Tailscale: `tailscale status`
2. If MS01 down, switch to Framework:
   ```bash
   stopstream
   startstream-framework
   ```
3. Continue demo

### Scenario 3: Complete Network Failure

1. Remote desktop to Framework (via screen sharing)
2. On Framework:
   ```bash
   cd ~/Route-Playout-Econometrics_POC
   USE_MS01_DATABASE=false streamlit run src/ui/app_api_real.py --server.port 8504
   ```
3. Demo from Framework screen

---

## Database Sizes (Estimated)

| Table/MV | Rows | Disk Size |
|----------|------|-----------|
| cache_route_impacts_15min_by_demo | 252.7M | ~66GB |
| mv_frame_audience_daily | 3.2M | ~500MB |
| mv_frame_audience_hourly | 46M | ~8GB |
| Other tables/MVs | Various | ~5GB |
| **Total** | | **~80GB** |

**Framework needs**: 100GB+ free for Postgres data + indexes

---

## Network Requirements

| Connection | From | To | Port | Protocol |
|------------|------|-----|------|----------|
| Tailscale | All devices | Tailscale mesh | 41641 | UDP |
| Postgres | M4/M1 Mac | MS01 | 5432 | TCP |
| Postgres | M4/M1 Mac | Framework | 5432 | TCP |
| Streamlit | Browser | Local | 8504 | HTTP |

---

## Support Contacts

- **Ian Wyatt**: ian@route.org.uk
- **Tailscale Docs**: https://tailscale.com/kb/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

---

## Part 6: Hero Campaigns for Demo

**Note**: Brands are anonymized in demo mode (shown as "Brand 1", "Brand 2", etc.)

### Final Campaign Selection

| Phase | Campaign ID | Purpose | Key Stats |
|-------|-------------|---------|-----------|
| **Tour** | 16699 | Feature walkthrough | 9.2M playouts, 452 frames, 13M reach, 13 days |
| **Insight** | 16879 | Data quality story | 5.4M playouts, 918 frames, 10.9M reach, 28 days |

### Why These Two?

**16699** - Your proven standard test campaign. You know every tab works.

**16879** - The **demo gold**:
- Shows multi-owner campaign (Bauer, JCDecaux, Ocean Outdoor)
- Campaign Shape reveals dramatic cliff drop on Sep 28
- Searching "16879" in browser shows duplicate entry "16879 & 16882"
- Perfect data quality story with financial implications

### Campaign Quick Reference (Print This)

```
┌─────────────────────────────────────────────────────┐
│              DEMO CAMPAIGN IDS                       │
├─────────────────────────────────────────────────────┤
│  PHASE 1 - TOUR:     16699  (feature walkthrough)   │
│  PHASE 2 - INSIGHT:  16879  (data quality story)    │
├─────────────────────────────────────────────────────┤
│  Backups: 17652 (117k impacts), 18098 (JCDecaux)    │
└─────────────────────────────────────────────────────┘
```

---

## Part 7: Demo Flow Script (~13 minutes)

### PHASE 1: THE TOUR - Campaign 16699 (8 min)

**Opening (1 min)**
1. "This is Route's Campaign Analytics POC - built for econometricians"
2. Show campaign browser
3. "We have 836 campaigns with reach and impact data"
4. Select campaign 16699

**Overview Tab (2 min)**
1. Show Audience Metrics: 52M impacts, 13M reach, 7.2% cover
2. Show Delivery: 9.2M playouts, 452 frames
3. Campaign Shape chart: "Here's the daily delivery pattern"
4. "13 days, weekday average 432k impacts"

**Reach & GRP Tab (2 min)**
1. Show cumulative reach build
2. "13 million adults reached - that's 23% of the UK adult population"
3. Highlight GRP progression
4. "This is the data econometricians need for modeling"

**Geographic Tab (1.5 min)**
1. Show UK map with frame locations
2. "National campaign - we can see every frame location"
3. Hover over regions for breakdown
4. "Filter by TV region, town, whatever you need"

**Executive Summary (1.5 min)**
1. "For quick board-level reporting"
2. Show Daily Impacts trend
3. Show Impacts by Region table
4. "Export to Excel with one click"

---

### PHASE 2: THE INSIGHT - Campaign 16879 (5 min)

**Transition (30 sec)**
1. "So that's what the tool does. Now let me show you something interesting..."
2. Select campaign 16879

**The Setup (1 min)**
1. Show Overview: "28-day campaign, 918 frames, 3 media owners"
2. "10.9 million reach - solid campaign"
3. "But look at this Campaign Shape..."

**The Discovery (2 min)**
1. Point at chart: "See this cliff drop on September 28th?"
2. "The campaign was running strong - 2.5 million impacts per day"
3. "Then it flatlines. What happened?"
4. Go back to campaign browser
5. Search "16879"
6. "There it is - two entries: 16879 AND '16879 & 16882'"
7. "The campaign ID changed mid-flight"

**The Business Impact (1.5 min)**
1. "This is a data quality issue with real financial consequences"
2. "If you're an econometrician trying to assign £500k of media spend to this campaign..."
3. "You're working with half the data"
4. "How do you calculate cost-per-impact when your impacts are in two places?"
5. "How do you build an ROI model when spend and outcomes are disconnected?"
6. **"The POC surfaces this so you can fix it BEFORE you build the model."**

---

### CLOSE (30 sec)

1. "This is why we need this tool"
2. "It's not just reporting - it's insight"
3. "Data quality drives model accuracy, which drives business decisions"
4. "Any questions?"

---

### Total Demo Time: ~13 minutes

---

## Part 8: Pre-Test Each Campaign

Before demo day, verify each hero campaign loads correctly:

```bash
# Start app
startstream

# Test each campaign - verify:
# [ ] Campaign loads without errors
# [ ] All tabs render correctly
# [ ] Charts display properly
# [ ] No "Unknown, Unknown" in location data
# [ ] Reach data shows (not "-")
# [ ] Geographic map renders
```

**Test Checklist:**

| Campaign | Overview | Reach | Charts | Geo | Exec Summary | Frame Audiences |
|----------|----------|-------|--------|-----|--------------|-----------------|
| 16699 (Tour) | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 16879 (Insight) | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

**Special Tests for 16879:**
- [ ] Campaign Shape shows cliff drop on Sep 28
- [ ] Searching "16879" in browser shows both entries
- [ ] "16879 & 16882" entry is visible

---

*Document Version: 1.0*
*Created: November 29, 2025*
