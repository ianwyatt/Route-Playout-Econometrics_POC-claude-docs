# Route Playout Econometrics POC - Project Specification

---

## Repository Structure - IMPORTANT

This project uses a **split repo setup** to keep Claude working docs off GitHub:

| Content | Location | Remote |
|---------|----------|--------|
| Application code | This repo | GitHub + Gitea mirror |
| Claude docs (handovers, todos, skills) | Sibling repo | **Gitea only** |

**How it works:**
- `.claude/` and `Claude/` are symlinks to `../Route-Playout-Econometrics_POC-claude-docs/`
- The sibling directory is a separate git repo pushing only to Gitea
- Code repo `.gitignore` excludes both directories

**Committing Claude docs:**
```bash
cd ../Route-Playout-Econometrics_POC-claude-docs
git add . && git commit -m "message" && git push
```

**Never commit to the code repo:**
- `.claude/` or `Claude/` contents
- Handovers, todos, session notes
- API keys, credentials, internal business details

**New machine setup:** See `../Route-Playout-Econometrics_POC-claude-docs/SETUP.md` for:
- Symlink creation
- Git hooks installation (`hooks/install.sh`)
- `.gitignore` template

---

## Commit Rules - READ FIRST

**NEVER commit without explicit user approval.**

- Do NOT auto-commit after completing a task
- Do NOT commit "for safety" or "to preserve work"
- WAIT for the user to say "commit", "commit and push", or similar explicit instruction
- If unsure, ASK before committing

This rule exists because premature commits disrupt the user's workflow and version control strategy.

---

## Project Scope

**This POC focuses exclusively on:**
- User interface for campaign analysis
- Route API and SPACE API integration for live queries
- Data visualization and interactive mapping
- Data export capabilities (CSV, Excel, Parquet)
- Query interface for econometricians

**Pipeline work (data ingestion, processing) is handled separately:**
- Repository: `route-playout-pipeline` (separate GitHub repo)
- Populates PostgreSQL database that this POC queries

---

## Documentation Locations

- **Architecture**: `docs/01-architecture.md`
- **UI Guide**: `docs/02-ui-guide.md`
- **Demo Mode**: `docs/03-demo-mode.md`
- **Cache Integration**: `docs/04-cache-integration.md`
- **Route API**: `docs/api-reference/route/`
- **SPACE API**: `docs/api-reference/space/`
- **Playout Schema**: `docs/playout/playout-digital-file-format.md`, `playout-classic-file-format.md`

---

## Core Functionality

**Primary Use Case**: Econometrician enters Campaign ID (buyercampaignref) → System queries PostgreSQL cache for audience data → Presents metrics and allows export.

**Architecture**: Cache-first design - all data served from PostgreSQL materialized views. Route API only called as fallback for uncached campaigns (rare).

**Aggregation Levels**: By day, time period, environment, media owner

**Key Features**:
- Filter by: time period, geography, brand, buyer, agency, campaign ID, media owner, frame characteristics
- Geographic filters: GPS coordinates, TV Region, Town, Conurbation, Postal Sector
- Demographics: ABC1, C2DE, Age bands (15-34, 35-54, 55+), custom filters
- Export: CSV, Excel, Parquet, API access
- Interactive maps, dashboards, heatmaps

**Frame Coverage**: Digital frames only (classic frames are future enhancement)

---

## Data Sources

### 1. PostgreSQL Database
Primary data store for playout records and cached API responses.

### 2. Route API
- **Endpoint**: `https://route.mediatelapi.co.uk/`
- **Purpose**: Audience measurement (impacts per frame playout)
- **Important**: Only use playout audiences endpoint. Do NOT retrieve reach-only data.
- **Frames not in Route**: Assign zero audience (impacts = 0)

### 3. SPACE API
- **Endpoint**: `https://oohspace.co.uk/api`
- **Purpose**: Decode playout data IDs
- **Lookups**: `spacemediaownerid` → Media Owner, `spacebuyerid` → Buyer, `spaceagencyid` → Agency, `spacebrandid` → Brand, `frameid` → Frame Metadata
- **Caching**: Cache lookups in PostgreSQL with 30-day expiration

---

## Route API Integration

> **Note**: Route API calls are handled by the `route-playout-pipeline` (separate repo), not this POC.
> This POC queries pre-cached data from PostgreSQL. The information below is for reference only.

### Playout Endpoint
**Endpoint**: `https://route.mediatelapi.co.uk/rest/process/playout`

**Process** (handled by pipeline):
1. Group frames by 15-minute intervals
2. Call Route API with grouped frames
3. Retrieve impacts per frame
4. Cache results in PostgreSQL

**Time Conversion**: Playout `yyyy-mm-ddTHH:mm:ss.SSS` → Route API `YYYY-MM-DD HH:MM:SS`

### API Request Example
```json
{
  "route_release_id": "55",
  "route_algorithm_version": "10.2",
  "algorithm_figures": ["impacts"],
  "grouping": "frame_ID",
  "demographics": ["ageband>=1"],
  "campaign": [{
    "schedule": [{"datetime_from": "2025-07-28 00:00", "datetime_until": "2025-07-28 00:14"}],
    "spot_length": 10,
    "spot_break_length": 50,
    "frames": [1234723633, 2000032505]
  }],
  "target_month": 1
}
```

---

## Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: Streamlit
- **Database**: PostgreSQL
- **Package Manager**: UV (recommended) or pip

### Application
- `app.py`: Production app with cache-first data access
- **Demo mode**: `DEMO_MODE=true` anonymises brand names for presentations

### Performance (December 2025)

| Operation | Response Time |
|-----------|---------------|
| Campaign browser | <100ms |
| Frame Audiences (initial) | <100ms |
| Frame Audiences (full daily) | <5s |
| Tab switching | Instant |

### Security
- Pre-commit hooks prevent credential commits
- All secrets in `.env` files (gitignored)
- See `.env.example` for configuration template

---

## Coding Style Guidelines

### Modularity and Reusability

**Prefer modular, reusable code over monolithic implementations.**

#### UI Structure (`src/ui/`)
- **`components/`** - Reusable UI elements (charts, tables, maps)
- **`tabs/`** - Page-level tab implementations that compose components
- **`config/`** - Configuration and constants (colors, demographics)
- **`data/`** - Geographic reference data

#### Guidelines
1. Check `src/ui/components/` for existing chart/map functions first
2. Extract reusable chart logic to `components/` with generic parameters
3. Keep tab files focused on layout and data orchestration
4. Keep SQL in query functions (`src/db/`), not scattered in UI code
5. Use `src/ui/config/` for shared colors, constants, settings

#### Refactor When
- Same chart pattern appears in 2+ tabs
- Inline Plotly code exceeds 30 lines
- Color values hardcoded in multiple places

---

## Route Releases Reference

**Query Available Releases**: `POST https://route.mediatelapi.co.uk/rest/version` (last 5 releases only)

| Name    | Release | Trading Period Start | Trading Period End |
|---------|---------|---------------------|-------------------|
| Q1 2025 | R54     | 07/04/2025          | 29/06/2025        |
| Q2 2025 | R55     | 30/06/2025          | 28/09/2025        |
| Q3 2025 | R56     | 29/09/2025          | 04/01/2026        |
| Q4 2025 | R57     | 05/01/2026          | 29/03/2026        |
| Q1 2026 | R58     | 30/03/2026          | 28/06/2026        |
| Q2 2026 | R59     | 29/06/2026          | 27/09/2026        |
| Q3 2026 | R60     | 28/09/2026          | 03/01/2027        |
| Q4 2026 | R61     | 04/01/2027          | 04/04/2027        |

---

## Quick Reference

### Run Application
```bash
# Normal mode
startstream

# Demo mode (brands anonymised for presentations)
startstream demo

# Or manually:
USE_MS01_DATABASE=true DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504
```

### Environment
See `.env.example` for required variables (Route API, SPACE API, Database credentials).

### Manual Streamlit App Management

**IMPORTANT**: The Streamlit app is now managed manually by the user in their terminal (not via Claude Code background processes). This prevents context pollution from background process tracking.

**Recommended workflow** (using shell function in `~/.zshrc`):

```bash
# Start app (MS01 database, normal mode) - auto-stops any running instance
startstream

# Start in demo mode (brands anonymised for presentations)
startstream demo

# Start with local database
startstream local

# Start local database in demo mode
startstream local demo

# Stop all Streamlit processes (if needed separately)
stopstream
```

| Command | Database | Demo Mode |
|---------|----------|-----------|
| `startstream` | MS01 | Off |
| `startstream demo` | MS01 | On |
| `startstream local` | Local | Off |
| `startstream local demo` | Local | On |

**Shell function defined** (in `~/.zshrc`):
```bash
alias stopstream='pkill -f "streamlit run"'

startstream() {
    pkill -f "streamlit run" 2>/dev/null
    sleep 1  # Give port time to be released

    local use_ms01="true"
    local demo_mode="false"
    local db_name="MS01"

    for arg in "$@"; do
        case "$arg" in
            demo)  demo_mode="true" ;;
            local) use_ms01="false"; db_name="Local" ;;
            ms01)  use_ms01="true"; db_name="MS01" ;;
        esac
    done

    USE_MS01_DATABASE=$use_ms01 DEMO_MODE=$demo_mode streamlit run src/ui/app.py --server.port 8504 &

    local msg="Started on $db_name database"
    [[ "$demo_mode" == "true" ]] && msg="$msg (DEMO MODE - brands anonymised)"
    echo "$msg"
}
```

**Manual command** (if not using shell function):
```bash
# Normal mode
USE_MS01_DATABASE=true streamlit run src/ui/app.py --server.port 8504 &

# Demo mode (brands anonymised)
USE_MS01_DATABASE=true DEMO_MODE=true streamlit run src/ui/app.py --server.port 8504 &

# Health check
curl http://localhost:8504/_stcore/health
```

**Why manual management?**: Running Streamlit via Claude Code's background bash processes creates 90+ context-consuming reminders that exhaust the conversation token budget quickly. Running in the user's terminal avoids this issue.

---

## Future Enhancements

- Cost and financial tracking (rate cards, CPM, cost per GRP)
- Natural language query interface
- AI-powered insights (OpenAI/Claude integration)
- Classic frame support (static/scroller)
- Multi-user support with role-based access
- Demographic filtering for Weekly Reach/GRP tab (requires Route API backfill for demographic-specific reach calculations)
- User authentication (Pocket ID - passkey-only OIDC)
- User areas with saved campaigns and history

---

*Last Updated: December 14, 2025*
