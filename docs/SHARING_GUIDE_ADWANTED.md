# Sharing Guide: Route Playout Econometrics POC — Adwanted

This guide covers how to share the Route Playout Econometrics POC application with Adwanted, including repository access, database provisioning, environment setup, and running the application.

---

## 1. Repository Access

The source code is hosted on GitHub as a private repository.

### Adding Adwanted as a Collaborator

```bash
# Add individual user
gh api repos/RouteResearch/Route-Playout-Econometrics_POC/collaborators/USERNAME -X PUT -f permission=read

# Or via GitHub UI:
# Settings > Collaborators > Add people > search by GitHub username
```

**Recommended permission level**: `read` (view and clone only). Elevate to `write` if they need to submit pull requests.

### What They'll Receive

- Full source code (Python, Streamlit UI, SQL queries)
- Tests and configuration templates
- Documentation within the repo (`docs/` directory)

### What's NOT Included

- `.env` files (credentials — provided separately)
- Claude Code documentation (separate private repo)
- Pipeline code (`route-playout-pipeline` is a separate repository)

---

## 2. Database Sharing

The application queries a PostgreSQL database populated by the pipeline. Adwanted needs a copy of this database (or access to it).

### Option A: Full Database Dump

```bash
# Create compressed custom-format dump
pg_dump -Fc -h <host> -U <user> -d <dbname> -f route_playout_full.dump

# Restore on target server
pg_restore -h <target-host> -U <target-user> -d <target-db> route_playout_full.dump
```

### Option B: Cache-Only Subset (Smaller)

If Adwanted only needs the materialised views and cache tables (no raw playout data):

```bash
# Dump only materialised views and cache tables
pg_dump -Fc -h <host> -U <user> -d <dbname> \
  -t 'mv_*' \
  -t 'cache_*' \
  -t 'space_*' \
  -f route_playout_cache_only.dump

# Restore
pg_restore -h <target-host> -U <target-user> -d <target-db> route_playout_cache_only.dump
```

### Option C: Remote Database Access

If granting direct access to the existing database:

1. Create a read-only PostgreSQL role
2. Grant `SELECT` on all relevant tables/views
3. Provide connection string for their `.env` file

```sql
CREATE ROLE adwanted_reader WITH LOGIN PASSWORD '<secure-password>';
GRANT CONNECT ON DATABASE <dbname> TO adwanted_reader;
GRANT USAGE ON SCHEMA public TO adwanted_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO adwanted_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO adwanted_reader;
```

---

## 3. Environment Setup

### Prerequisites

- Python 3.11+
- PostgreSQL client libraries (`libpq-dev` on Linux, `postgresql` via Homebrew on macOS)
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/RouteResearch/Route-Playout-Econometrics_POC.git
cd Route-Playout-Econometrics_POC

# Install dependencies
uv sync

# Or with pip (alternative)
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root (see `.env.example` for template):

```env
# Primary database connection
POSTGRES_HOST=<hostname>
POSTGRES_PORT=5432
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<password>
POSTGRES_DATABASE=<database>

# Secondary database (optional — for local/development use)
POSTGRES_HOST_SECONDARY=<hostname>
POSTGRES_PORT_SECONDARY=5432
POSTGRES_USER_SECONDARY=<username>
POSTGRES_PASSWORD_SECONDARY=<password>
POSTGRES_DATABASE_SECONDARY=<database>
```

If only one database is available, set `USE_PRIMARY_DATABASE=true` and only configure the primary credentials.

---

## 4. Running the Application

```bash
# Start the Streamlit app (primary database)
USE_PRIMARY_DATABASE=true streamlit run src/ui/app.py --server.port 8504

# Start in demo mode (anonymises brand names for presentations)
USE_PRIMARY_DATABASE=true DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504

# Health check
curl http://localhost:8504/_stcore/health
```

The application will be available at `http://localhost:8504`.

### Key Workflows

1. **Campaign Browser**: Landing page shows all cached campaigns with search/filter
2. **Campaign Analysis**: Click a campaign to see 6 analysis tabs (Overview, Executive Summary, Geographic, Detailed Analysis, Daily & Hourly Patterns, Weekly Reach)
3. **Export**: Use the export button on any tab to download data as Excel

---

## 5. Scope and Limitations

### What This Application Does

- **Read-only cache viewer** — queries pre-computed PostgreSQL materialised views
- Displays audience metrics (impacts, reach, GRP, frequency, cover) by campaign
- Geographic analysis with interactive maps
- Demographic breakdowns (ABC1, C2DE, age bands)
- Data export (Excel format)

### What This Application Does NOT Do

- **No data ingestion** — the pipeline (`route-playout-pipeline`) populates the database
- **No live API calls** — all data comes from cached tables
- **No data modification** — strictly read-only queries
- **No authentication** — anyone with access can view all campaigns

### Data Freshness

Data freshness depends on how recently the pipeline ran. The materialised views show:
- The date range of cached data in the campaign browser
- Route release versions used for audience calculations

---

## 6. Support and Contact

For questions about:
- **This application**: Contact the Route Research team
- **Database/pipeline**: Contact the Pipeline team
- **Route API methodology**: Refer to `docs/api-reference/route/` in the repository

---

*Created: 4 February 2026*
