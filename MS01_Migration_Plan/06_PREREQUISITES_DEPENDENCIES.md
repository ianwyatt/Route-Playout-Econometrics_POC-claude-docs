# Prerequisites & Dependencies - MS-01 Migration

**Date**: 2025-10-17
**Audience**: Developers and system administrators
**Purpose**: Complete list of requirements for MS-01 integration

---

## Table of Contents

1. [Network Requirements](#network-requirements)
2. [Database Requirements](#database-requirements)
3. [Python Dependencies](#python-dependencies)
4. [Environment Variables](#environment-variables)
5. [Configuration Steps](#configuration-steps)
6. [Optional Components](#optional-components)

---

## Network Requirements

### MS-01 Server Access

**Required for Production Mode**:
- **VPN Access**: Must be connected to internal network OR
- **Direct Network Access**: Local network access to 192.168.1.0/24 subnet

**Server Details**:
- **Host**: `192.168.1.34`
- **Port**: `5432` (PostgreSQL)
- **Protocol**: TCP
- **SSL**: Not required (internal network)

### Firewall Rules

**Outbound Rules** (from your machine):
```
Allow TCP to 192.168.1.34:5432
```

**Testing Connectivity**:
```bash
# Test ping
ping -c 3 192.168.1.34

# Test port access
nc -zv 192.168.1.34 5432
# Or with telnet
telnet 192.168.1.34 5432

# Expected: Connection successful
```

### VPN Configuration

If using VPN:
1. Connect to company VPN
2. Verify routing to 192.168.1.0/24 subnet
3. Test connectivity with ping/nc

**Troubleshooting VPN**:
```bash
# Check routing
route -n get 192.168.1.34

# Check if VPN is connected
ifconfig | grep -A 5 tun0  # Or your VPN interface

# Test DNS resolution (if using hostname)
nslookup ms-01.internal.domain
```

### Fallback: Local Database

If MS-01 access is not available:
- Set `USE_MS01_DATABASE=false` in `.env`
- Use local PostgreSQL on `localhost:5432`
- Limited functionality (no production data)

---

## Database Requirements

### MS-01 Production Database

**Database Server**: PostgreSQL 14+
**Location**: Proxmox server at 192.168.1.34

#### Required Database Objects

##### 1. Database
```
Name: route_poc
Owner: postgres
Size: ~596 GB
Records: ~1.28 billion playout records
```

##### 2. Materialized Views

**mv_playout_15min** (PRIMARY VIEW):
```sql
-- Must exist and be refreshed daily
-- Used by: get_campaign_for_route_api() and other helper functions

SELECT table_name, schemaname
FROM pg_matviews
WHERE matviewname = 'mv_playout_15min';

-- Expected: 1 row returned
```

**Columns Required**:
- `frameid` (text or bigint)
- `buyercampaignref` (text)
- `time_window_start` (timestamp)
- `time_window_end` (timestamp) - computed as time_window_start + 15 minutes
- `spot_count` (integer)
- `playout_length_seconds` (integer)
- `break_length_seconds` (integer)
- `latest_playout` (timestamp)

**mv_playout_15min_brands** (BRAND SPLIT VIEW):
```sql
-- Must exist for brand split functionality
-- Used by: BrandSplitService

SELECT table_name, schemaname
FROM pg_matviews
WHERE matviewname = 'mv_playout_15min_brands';

-- Expected: 1 row returned
```

**Columns Required**:
- `frameid` (text or bigint)
- `buyercampaignref` (text)
- `spacebrandid` (integer)
- `window_start` (timestamp)
- `window_end` (timestamp)
- `spot_count` (integer) - spots for THIS brand

**Refresh Schedule**:
- Both views refreshed daily at 2am UTC
- Managed by pipeline repository
- Data may be up to 24 hours old (acceptable for econometric analysis)

##### 3. Tables

**route_releases** (CREATED BY POC):
```sql
-- Created automatically by setup_route_releases.py
-- No manual creation needed

-- Verify it exists:
SELECT tablename FROM pg_tables
WHERE tablename = 'route_releases';
```

**playout** (RAW DATA TABLE):
- Managed by pipeline
- Not directly accessed by POC
- Source for materialized views

#### Database User Permissions

**User**: `postgres` (or custom user)

**Required Permissions**:
```sql
-- Read access to views
GRANT SELECT ON mv_playout_15min TO postgres;
GRANT SELECT ON mv_playout_15min_brands TO postgres;

-- Full access to route_releases table
GRANT SELECT, INSERT, UPDATE, DELETE ON route_releases TO postgres;
GRANT USAGE, SELECT ON SEQUENCE route_releases_id_seq TO postgres;

-- Schema access
GRANT USAGE ON SCHEMA public TO postgres;
```

**Test Permissions**:
```sql
-- Test read access
SELECT COUNT(*) FROM mv_playout_15min LIMIT 1;
SELECT COUNT(*) FROM mv_playout_15min_brands LIMIT 1;

-- Test write access
INSERT INTO route_releases (name, release_number, data_publication, trading_period_start, trading_period_end)
VALUES ('TEST', 'R99', '2025-01-01', '2025-01-01', '2025-12-31')
RETURNING id;

-- Cleanup test
DELETE FROM route_releases WHERE release_number = 'R99';
```

### Local Development Database

**Alternative to MS-01 for development/demos**

**Requirements**:
- PostgreSQL 12+ installed locally
- Database name: `route_poc`
- User: `ianwyatt` (or your MacOS username)
- No password required (trust authentication)

**Setup Local Database**:
```bash
# Install PostgreSQL (if not installed)
brew install postgresql@14

# Start PostgreSQL
brew services start postgresql@14

# Create database
createdb route_poc

# Test connection
psql -d route_poc -c "SELECT version();"
```

**Limitations of Local Database**:
- No production playout data (use sample CSV files)
- Smaller dataset for testing
- No materialized views (create route_releases table only)
- Good for: UI development, demos, testing when MS-01 offline

---

## Python Dependencies

### Required Packages

**Core Dependencies**:
```
asyncpg>=0.29.0      # PostgreSQL async driver
asyncio              # Async/await support (stdlib)
pandas>=2.0.0        # Data manipulation
numpy>=1.24.0        # Numerical operations
```

**Configuration**:
```
python-dotenv>=1.0.0  # Environment variable loading
pydantic>=2.0.0       # Data validation
```

**Utilities**:
```
logging              # Logging (stdlib)
dataclasses          # Data structures (stdlib)
datetime             # Date/time handling (stdlib)
typing               # Type hints (stdlib)
functools            # Caching decorators (stdlib)
```

### Installation

**Using pip**:
```bash
pip install asyncpg>=0.29.0 pandas>=2.0.0 numpy>=1.24.0 python-dotenv>=1.0.0 pydantic>=2.0.0
```

**Using requirements.txt** (if available):
```bash
pip install -r requirements.txt
```

**Using uv** (if available):
```bash
uv pip install asyncpg pandas numpy python-dotenv pydantic
```

### Python Version

**Minimum**: Python 3.9
**Recommended**: Python 3.11+
**Tested**: Python 3.11.5

**Check Version**:
```bash
python --version
# Should be >= 3.9
```

### Virtual Environment

**Recommended Setup**:
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # On MacOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Variables

### Required Variables

**Database Selection**:
```bash
# Master switch: true=MS-01, false=Local
USE_MS01_DATABASE=true
```

### MS-01 Database Configuration

```bash
# MS-01 Proxmox PostgreSQL (Production)
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
POSTGRES_PASSWORD_MS01=YOUR_MS01_PASSWORD_HERE
```

**Security Note**: Never commit `.env` file to git. Use `.env.example` as template.

### Local Database Configuration

```bash
# Local MacOS Database (Development/Demo)
POSTGRES_HOST_LOCAL=localhost
POSTGRES_PORT_LOCAL=5432
POSTGRES_DATABASE_LOCAL=route_poc
POSTGRES_USER_LOCAL=ianwyatt
POSTGRES_PASSWORD_LOCAL=
```

### Optional Performance Tuning

```bash
# Connection Pooling (optional, has defaults)
POSTGRES_MIN_POOL=2           # Min connections (default: 2)
POSTGRES_MAX_POOL=10          # Max connections (default: 10, recommend 30 for prod)
POSTGRES_POOL_TIMEOUT=30      # Timeout in seconds (default: 30)

# Query Caching (optional, has defaults)
DB_QUERY_CACHE_ENABLED=true   # Enable query caching (default: true)
DB_QUERY_CACHE_TTL=300        # Cache TTL in seconds (default: 300 = 5 min)
DB_QUERY_CACHE_SIZE=100       # Max cached queries (default: 100)

# Database Timeouts (optional)
DB_CONNECTION_TIMEOUT=10      # Connection timeout (default: 10s)
DB_COMMAND_TIMEOUT=60         # Query timeout (default: 60s)
DB_MAX_RETRIES=3              # Max retry attempts (default: 3)
```

### Backward Compatibility Variables

```bash
# Generic variables (fallback if MS01/LOCAL not set)
POSTGRES_HOST=${POSTGRES_HOST_MS01}
POSTGRES_PORT=${POSTGRES_PORT_MS01}
POSTGRES_DATABASE=${POSTGRES_DATABASE_MS01}
POSTGRES_USER=${POSTGRES_USER_MS01}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_MS01}

# Legacy variables (for older code)
DATABASE_HOST=${POSTGRES_HOST}
DATABASE_PORT=${POSTGRES_PORT}
DATABASE_NAME=${POSTGRES_DATABASE}
DATABASE_USER=${POSTGRES_USER}
DATABASE_PASSWORD=${POSTGRES_PASSWORD}
```

### .env File Example

**Create** `/Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC/.env`:

```bash
# Database Configuration
# Set USE_MS01_DATABASE=true to use MS-01, false for local Mac database
USE_MS01_DATABASE=true

# Local MacOS Database (for quick dev testing and demos when MS-01 is down)
POSTGRES_HOST_LOCAL=localhost
POSTGRES_PORT_LOCAL=5432
POSTGRES_DATABASE_LOCAL=route_poc
POSTGRES_USER_LOCAL=ianwyatt
POSTGRES_PASSWORD_LOCAL=

# MS-01 Proxmox PostgreSQL (Primary Production Database)
# 1.28B records, 596GB, Aug 6 - Oct 13 2025 data
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT_MS01=5432
POSTGRES_DATABASE_MS01=route_poc
POSTGRES_USER_MS01=postgres
POSTGRES_PASSWORD_MS01=YOUR_MS01_PASSWORD_HERE
```

**Loading Environment Variables**:
```python
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Access variables
use_ms01 = os.getenv('USE_MS01_DATABASE', 'true').lower() == 'true'
```

---

## Configuration Steps

### Step 1: Clone or Update Repository

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
git pull origin main
```

### Step 2: Install Python Dependencies

```bash
# Activate virtual environment (if using)
source venv/bin/activate

# Install packages
pip install asyncpg pandas numpy python-dotenv pydantic
```

### Step 3: Configure Environment Variables

```bash
# Copy example (if exists)
cp .env.example .env

# Edit .env
nano .env  # or your preferred editor

# Set USE_MS01_DATABASE=true
# Verify MS-01 credentials are correct
```

### Step 4: Test Database Connection

```bash
# Quick connection test
python -c "
import asyncio
import os
os.environ['USE_MS01_DATABASE'] = 'true'
from src.db.ms01_helpers import initialize_ms01_database
asyncio.run(initialize_ms01_database())
print('✅ Connection successful')
"
```

**Expected Output**:
```
✅ MS-01 database connection pool initialized (192.168.1.34/route_poc)
✅ Connection successful
```

### Step 5: Setup Route Releases

```bash
# Populate route_releases table
python scripts/setup_route_releases.py
```

**Expected Output**:
```
✅ Database connection pool initialized
✅ Route releases table created successfully
✅ Inserted/updated release R54 with ID 1
✅ Inserted/updated release R55 with ID 2
...
📊 Successfully loaded 8 releases
```

### Step 6: Validate Installation

```bash
# Run comprehensive tests
python examples/ms01_helpers_example.py
python src/services/test_brand_split.py
python scripts/test_route_releases.py
```

**If all tests pass**:
```
✅ All validation tests passed
✅ MS-01 integration ready to use
```

---

## Optional Components

### Pipeline Repository (Separate)

**Location**: `/Users/ianwyatt/PycharmProjects/route-playout-pipeline`

**Purpose**:
- Creates and refreshes materialized views
- Manages playout data ingestion
- Maintains MS-01 database

**Not Required for POC**:
- POC uses existing views (read-only)
- Pipeline team manages view refresh
- POC does not modify playout data

### SPACE API (For Lookups)

**Purpose**: Lookup brand names, media owners, agencies

**Configuration** (in .env):
```bash
SPACE_API_BASE_URL=https://oohspace.co.uk/api
SPACE_API_Username=106
SPACE_API_Password=7p2Ce2fN
```

**Usage**: Optional enrichment of brand IDs
**Not Required**: MS-01 integration works with brand IDs only

### Route API (For Audience Data)

**Purpose**: Get audience impacts for playouts

**Configuration** (in .env):
```bash
ROUTE_API_LIVE_URL=https://route.mediatelapi.co.uk
ROUTE_API_KEY=5a08fc4d-34f6-4686-9228-b5a5b059b97d
ROUTE_API_AUTH=Basic aWFud0Byb3V0ZS5vcmcudWs6YTlDZ25nd1g=
```

**Usage**: POC prepares Route API payloads, then calls Route API
**Integration**: `build_route_api_payload()` creates payload for Route API POST

---

## Troubleshooting Prerequisites

### Issue: Cannot Connect to MS-01

**Symptoms**:
```
❌ Connection Timeout
❌ Connection refused
```

**Checklist**:
1. ✅ Connected to VPN?
2. ✅ Firewall allows port 5432?
3. ✅ MS-01 server online? (ping 192.168.1.34)
4. ✅ Credentials correct in .env?
5. ✅ Port 5432 accessible? (nc -zv 192.168.1.34 5432)

**Solution**:
- Connect to VPN
- Or set `USE_MS01_DATABASE=false` to use local database

### Issue: Views Not Found

**Symptoms**:
```
❌ relation "mv_playout_15min" does not exist
```

**Solution**:
- Contact pipeline team to create views
- Views should be created by pipeline setup scripts
- SQL for views should be in pipeline repository

### Issue: Permission Denied

**Symptoms**:
```
❌ permission denied for table mv_playout_15min
```

**Solution**:
```sql
-- Run as postgres superuser
GRANT SELECT ON mv_playout_15min TO postgres;
GRANT SELECT ON mv_playout_15min_brands TO postgres;
GRANT ALL ON route_releases TO postgres;
```

### Issue: Python Package Missing

**Symptoms**:
```
ModuleNotFoundError: No module named 'asyncpg'
```

**Solution**:
```bash
pip install asyncpg
# Or install all dependencies
pip install asyncpg pandas numpy python-dotenv pydantic
```

---

## Verification Checklist

Before declaring prerequisites complete:

- [ ] Network access to MS-01 (192.168.1.34:5432) verified
- [ ] Database credentials tested and working
- [ ] Materialized views exist and contain data
- [ ] Python 3.9+ installed
- [ ] All required Python packages installed
- [ ] .env file configured with correct credentials
- [ ] Route releases table populated (R54-R61)
- [ ] Basic connection test passes
- [ ] Example scripts execute successfully

**Run Full Checklist**:
```bash
# Network
ping -c 3 192.168.1.34 && echo "✅ Network" || echo "❌ Network"

# Port
nc -zv 192.168.1.34 5432 2>&1 | grep -q succeeded && echo "✅ Port" || echo "❌ Port"

# Python version
python --version | grep -q "3\.[9-9]\|3\.1[0-9]" && echo "✅ Python" || echo "❌ Python"

# Packages
python -c "import asyncpg; import pandas; print('✅ Packages')" 2>/dev/null || echo "❌ Packages"

# .env file
test -f .env && echo "✅ .env file" || echo "❌ .env file"

# Connection
python -c "import asyncio, os; os.environ['USE_MS01_DATABASE']='true'; from src.db.ms01_helpers import initialize_ms01_database; asyncio.run(initialize_ms01_database()); print('✅ Connection')" 2>/dev/null || echo "❌ Connection"
```

---

## Production vs Development

### Production (MS-01)

**Requirements**:
- VPN or network access
- MS-01 credentials
- All views exist and refreshed
- High-speed network connection

**Advantages**:
- 1.28B records
- Real playout data
- Pre-aggregated views (fast queries)
- Production-scale testing

### Development (Local)

**Requirements**:
- Local PostgreSQL installed
- Sample CSV files
- route_releases table only

**Advantages**:
- No VPN needed
- Works offline
- Fast restart/reset
- Good for UI development

**Recommendation**: Develop locally, test on MS-01 before production

---

**Prepared By**: Claude Code Agent Team
**Date**: 2025-10-17
**Status**: Complete Prerequisites Guide
