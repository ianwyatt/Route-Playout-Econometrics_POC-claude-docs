# Framework Desktop Database Setup

**Purpose**: Backup PostgreSQL server for M1 Max if MS-01 is unavailable during Dec 4th board demo

---

## System Specifications

| Item | Value |
|------|-------|
| Device | Framework Desktop |
| OS | Fedora |
| CPU | Ryzen AI Max+ 395 |
| RAM | 128GB |
| Storage | 2x Samsung 990 PRO 4TB NVMe |
| Network IP | 192.168.1.76 |

---

## Storage Layout

| Drive | Device | Purpose |
|-------|--------|---------|
| OS Drive | `/dev/nvme1n1` | Fedora (Btrfs with LUKS) |
| Data Drive | `/dev/nvme0n1` | PostgreSQL data |

---

## Setup Instructions

### Step 1: Partition & Format the Data Drive

```bash
# Check the drive is correct (should show 4TB unformatted)
sudo fdisk -l /dev/nvme0n1

# Create a single partition
sudo fdisk /dev/nvme0n1
# Press: n (new), p (primary), 1 (partition 1), Enter (default start), Enter (default end), w (write)

# Format as ext4
sudo mkfs.ext4 -L pgdata /dev/nvme0n1p1

# Create mount point
sudo mkdir -p /data

# Get UUID for fstab
sudo blkid /dev/nvme0n1p1
# Note the UUID (e.g., UUID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")

# Add to fstab (replace YOUR-UUID with actual UUID)
echo 'UUID=YOUR-UUID /data ext4 defaults 0 2' | sudo tee -a /etc/fstab

# Mount it
sudo mount /data

# Verify
df -h /data
```

---

### Step 2: Install PostgreSQL

```bash
# Install PostgreSQL
sudo dnf install -y postgresql-server postgresql-contrib

# Create data directory on the NVMe
sudo mkdir -p /data/postgresql
sudo chown postgres:postgres /data/postgresql
sudo chmod 700 /data/postgresql

# Initialise database in custom location
sudo -u postgres initdb -D /data/postgresql

# Configure PostgreSQL to use custom data directory
sudo systemctl edit postgresql
```

Add this content in the editor:
```ini
[Service]
Environment=PGDATA=/data/postgresql
```

Save and exit.

---

### Step 3: Configure PostgreSQL for Network Access

#### Edit postgresql.conf
```bash
sudo nano /data/postgresql/postgresql.conf
```

Find and change these settings:
```
listen_addresses = '*'
port = 5432
```

#### Edit pg_hba.conf
```bash
sudo nano /data/postgresql/pg_hba.conf
```

The file should contain (add the first line if missing):
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

host    all             all             192.168.1.0/24          scram-sha-256
# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
```

---

### Step 4: Set PostgreSQL Password

```bash
# Start PostgreSQL
sudo systemctl enable --now postgresql

# Set postgres user password (same as MS-01 for easy failover)
# Use password from POSTGRES_PASSWORD_MS01 in .env
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '<password-from-env>';"

# Create the database
sudo -u postgres createdb route_poc

# Verify PostgreSQL is running
sudo systemctl status postgresql
```

---

### Step 5: Open Firewall

```bash
# Open PostgreSQL port
sudo firewall-cmd --permanent --add-service=postgresql
sudo firewall-cmd --reload

# Verify
sudo firewall-cmd --list-services
```

---

### Step 6: Create Database Dump (on M4 Max)

On your M4 Max, create a dump of the local database:

```bash
# Navigate to a directory with space
cd ~

# Create dump (custom format, compressed)
pg_dump -h localhost -U postgres -d route_poc -F c -f route_poc_backup.dump

# Check the size
ls -lh route_poc_backup.dump
```

**Note**: This may take a while depending on database size (~658GB).

---

### Step 7: Transfer Dump to Framework

From M4 Max:

```bash
# Using rsync (recommended - shows progress, can resume)
rsync -avh --progress ~/route_poc_backup.dump user@192.168.1.76:/data/

# Or using scp
scp ~/route_poc_backup.dump user@192.168.1.76:/data/
```

Replace `user` with your Framework username.

---

### Step 8: Restore Database (on Framework)

```bash
# Restore the dump (use -j for parallel jobs, adjust based on CPU)
sudo -u postgres pg_restore -d route_poc -j 8 /data/route_poc_backup.dump

# For verbose output
sudo -u postgres pg_restore -v -d route_poc -j 8 /data/route_poc_backup.dump
```

**Note**: With the Ryzen AI Max+ 395 and NVMe storage, restore should be fast. Using `-j 8` for parallel restore.

---

### Step 9: Verify Installation

On Framework:
```bash
# Check database exists
sudo -u postgres psql -d route_poc -c "SELECT COUNT(*) FROM playout_raw;"

# Check MVs exist
sudo -u postgres psql -d route_poc -c "\dv mv_*"
```

From M1 Max:
```bash
# Test remote connection
psql -h 192.168.1.76 -U postgres -d route_poc -c "SELECT COUNT(*) FROM playout_raw;"
```

---

## M1 Max Failover Configuration

### Normal Operation (MS-01)

M1 Max `.env`:
```env
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
POSTGRES_PASSWORD_MS01=<see .env.example>
USE_MS01_DATABASE=true
```

### Failover (Framework)

If MS-01 is unavailable, edit M1 Max `.env`:
```env
POSTGRES_HOST_MS01=192.168.1.76
```

**Only the IP address changes** - same password, same database name, same variable.

Then restart Streamlit:
```bash
stopstream && startstream demo
```

---

## Demo Day Quick Reference

| Scenario | Demo Machine | Database Host |
|----------|--------------|---------------|
| Primary | M4 Max | Local (localhost) |
| Backup (normal) | M1 Max | MS-01 (192.168.1.34) |
| Backup (failover) | M1 Max | Framework (192.168.1.76) |

### Wake-on-LAN (if Framework is sleeping/off)

From any machine on the local network:
```bash
wakeonlan 9c:bf:0d:00:f8:e3
```

Install wakeonlan if needed:
- macOS: `brew install wakeonlan`
- Linux: `sudo dnf install wakeonlan` or `sudo apt install wakeonlan`

**Note**: Framework must have Wake-on-LAN enabled in BIOS and the network interface must support it.

### Failover Steps
1. Wake Framework if needed: `wakeonlan 9c:bf:0d:00:f8:e3`
2. Edit `.env` on M1 Max: change `POSTGRES_HOST_MS01=192.168.1.34` to `POSTGRES_HOST_MS01=192.168.1.76`
3. Run `stopstream && startstream demo`
4. Test: load campaign 16699

---

## Storage Move - COMPLETED ✅ (2025-12-01)

**Issue**: During initial setup, pg_restore ran to the OS drive (LUKS-encrypted Btrfs) instead of the dedicated NVMe.

**Resolution**: Successfully moved ~660GB of PostgreSQL data to dedicated NVMe.

### Final Configuration
- **Data Drive**: `/dev/nvme0n1p1` mounted at `/data`
- **fstab UUID**: `e914d13c-cd2d-41f4-93e6-4a8f5bd00a03`
- **PostgreSQL Data**: `/data/postgresql` (~660GB)
- **SELinux Context**: `postgresql_db_t` on both `/data` and `/data/postgresql`

### Key Fixes Applied
1. Fixed `/data` mount point permissions (`chmod 755`, `chown root:root`)
2. Fixed SELinux context on `/data` itself (was `unlabeled_t`)
3. Fixed SELinux context on `/data/postgresql` (`postgresql_db_t`)
4. Updated fstab with correct UUID for persistent mount

---

## Materialized Views - CREATED ✅ (2025-12-01)

**Note**: The pg_dump was taken before we created the `mv_frame_brand_*` MVs, so they needed to be recreated on Framework.

### MVs Created
```sql
-- mv_frame_brand_daily (1.1M rows on local, similar on Framework)
CREATE MATERIALIZED VIEW mv_frame_brand_daily AS
SELECT pb.buyercampaignref AS campaign_id,
    pb.frameid,
    date(pb.time_window_start) AS date,
    string_agg(DISTINCT sb.name::text, ', '::text ORDER BY (sb.name::text)) AS brand_names,
    count(DISTINCT pb.spacebrandid) AS brand_count,
    sum(pb.spots_for_brand) AS total_spots
FROM mv_playout_15min_brands pb
LEFT JOIN cache_space_brands sb ON pb.spacebrandid::text = sb.entity_id::text
GROUP BY pb.buyercampaignref, pb.frameid, (date(pb.time_window_start));

CREATE INDEX idx_mv_frame_brand_daily_campaign ON mv_frame_brand_daily(campaign_id);

-- mv_frame_brand_hourly (16.8M rows on local, similar on Framework)
CREATE MATERIALIZED VIEW mv_frame_brand_hourly AS
SELECT pb.buyercampaignref AS campaign_id,
    pb.frameid,
    date_trunc('hour'::text, pb.time_window_start) AS hour_start,
    string_agg(DISTINCT sb.name::text, ', '::text ORDER BY (sb.name::text)) AS brand_names,
    count(DISTINCT pb.spacebrandid) AS brand_count,
    sum(pb.spots_for_brand) AS total_spots
FROM mv_playout_15min_brands pb
LEFT JOIN cache_space_brands sb ON pb.spacebrandid::text = sb.entity_id::text
GROUP BY pb.buyercampaignref, pb.frameid, (date_trunc('hour'::text, pb.time_window_start));

CREATE INDEX idx_mv_frame_brand_hourly_campaign ON mv_frame_brand_hourly(campaign_id);
```

### Verify Storage Is Correct

```bash
# Check /data is on the dedicated NVMe
df -h /data
# Should show /dev/nvme0n1p1 with ~3.7TB total

# Check PostgreSQL data size
sudo du -sh /data/postgresql
# Should be ~660GB
```

---

## Troubleshooting

### Cannot Connect from M1 Max

```bash
# Check Framework PostgreSQL is running
sudo systemctl status postgresql

# Check firewall
sudo firewall-cmd --list-services

# Check PostgreSQL is listening
sudo ss -tlnp | grep 5432

# Check pg_hba.conf allows connections
sudo cat /data/postgresql/pg_hba.conf | grep 192.168
```

### Connection Refused

```bash
# Check listen_addresses in postgresql.conf
sudo grep listen_addresses /data/postgresql/postgresql.conf

# Should show: listen_addresses = '*'
# If not, edit and restart:
sudo systemctl restart postgresql
```

### Authentication Failed

```bash
# Reset postgres password (use password from POSTGRES_PASSWORD_MS01 in .env)
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '<password-from-env>';"
```

---

*Last Updated: 2025-12-01*
