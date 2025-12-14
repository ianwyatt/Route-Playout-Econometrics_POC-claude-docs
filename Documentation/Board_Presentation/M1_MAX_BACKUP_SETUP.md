# M1 Max Backup Setup for Board Demo

**Purpose**: Backup device in case primary Mac has issues during Dec 4th board demo

---

## Constraints

- **Disk Space**: 1TB only - cannot run local PostgreSQL database
- **Role**: UI and terminal only, connects to remote databases
- **Primary Database**: MS-01 (192.168.1.34)
- **Secondary Database**: Framework desktop (192.168.1.76) - CONFIGURED

---

## Database Failover

| Priority | Database Host | IP Address | Status |
|----------|---------------|------------|--------|
| Primary | MS-01 | 192.168.1.34 | Default in .env |
| Failover | Framework | 192.168.1.76 | Ready if MS-01 down |

**To switch to Framework**: Edit `.env`, change `DB_HOST=192.168.1.34` to `DB_HOST=192.168.1.76`

See `FRAMEWORK_DATABASE_SETUP.md` for Framework server details.

---

## Setup Checklist

### 1. Clone Repository
```bash
cd ~/PycharmProjects
git clone <repo-url> Route-Playout-Econometrics_POC
cd Route-Playout-Econometrics_POC
```

### 2. Install UV (if not installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create Virtual Environment & Install Dependencies
```bash
uv sync
```

### 4. Configure Environment Variables
Create `.env` file with MS-01 database connection:
```bash
# Copy from primary Mac or create manually
cp /path/to/primary/.env .env
```

Required variables:
```env
# Database - MS-01 (primary)
DB_HOST=192.168.1.34
DB_PORT=5432
DB_NAME=route_poc
DB_USER=postgres
DB_PASSWORD=<password>

# Route API
ROUTE_API_URL=https://route.mediatelapi.co.uk/
ROUTE_API_KEY=<key>

# SPACE API
SPACE_API_URL=https://oohspace.co.uk/api
SPACE_API_KEY=<key>
```

### 5. Set Up Terminal Aliases
Add to `~/.zshrc`:
```bash
# Streamlit management aliases
alias stopstream='pkill -f "streamlit run"'
alias startstream='USE_MS01_DATABASE=true streamlit run src/ui/app.py --server.port 8504 &'
```

Then:
```bash
source ~/.zshrc
```

### 6. Test Connection
```bash
# Start the app
startstream

# Wait a few seconds, then test
curl http://localhost:8504/_stcore/health

# Open in browser
open http://localhost:8504
```

### 7. Test Demo Campaigns
Verify these campaigns load correctly:
- [ ] Campaign 16699 (feature walkthrough)
- [ ] Campaign 16879 (data quality issue)
- [ ] Campaign "16879 & 16882" (overlap demo)

---

## Framework Desktop (Secondary Backup)

**Status**: ✅ CONFIGURED (2025-12-01)

| Item | Value |
|------|-------|
| IP Address | 192.168.1.76 |
| OS | Fedora |
| Hardware | Ryzen AI Max+ 395, 128GB RAM, 8TB NVMe |
| PostgreSQL Data | `/data/postgresql` on dedicated NVMe |
| Password | Same as MS-01 (only IP change needed for failover) |

**Full setup guide**: `FRAMEWORK_DATABASE_SETUP.md`

### Failover Procedure
1. Edit `.env` on M1 Max
2. Change `DB_HOST=192.168.1.34` to `DB_HOST=192.168.1.76`
3. Run `stopstream && startstream demo`
4. Test: load campaign 16699

### Demo Day Redundancy
| Priority | Demo Machine | Database |
|----------|--------------|----------|
| Primary | M4 Max | Local PostgreSQL |
| Backup | M1 Max | MS-01 (192.168.1.34) |
| Failover | M1 Max | Framework (192.168.1.76) |

---

## Pre-Demo Day Checklist

### Night Before (Dec 3rd)
- [ ] Ensure M1 Max is charged
- [ ] Pull latest code: `git pull`
- [ ] Test MS-01 connection from M1 Max
- [ ] Verify all three demo campaigns load
- [ ] Check all tabs render correctly
- [ ] Test CSV export works

### Morning Of (Dec 4th)
- [ ] Bring M1 Max to meeting room
- [ ] Have it powered on and ready (lid closed is fine)
- [ ] Know the WiFi credentials for meeting room
- [ ] Have this document accessible

---

## Troubleshooting

### Cannot Connect to MS-01
1. Check VPN/network connection
2. Verify MS-01 is running: `ping 192.168.1.34`
3. Test PostgreSQL port: `nc -zv 192.168.1.34 5432`
4. Check firewall rules on MS-01

### Streamlit Won't Start
1. Check port not in use: `lsof -ti:8504`
2. Kill existing: `stopstream`
3. Check logs: Look at terminal output
4. Verify dependencies: `uv sync`

### Campaign Won't Load
1. Check database connection in Streamlit logs
2. Verify MV exists: Check `mv_campaign_browser` is populated
3. Try refreshing browser
4. Restart Streamlit: `stopstream && startstream`

---

*Last Updated: 2025-12-01*
