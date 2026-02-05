# External Code Review Prompt

Use this prompt with an external AI reviewer (Codex, Claude, etc.) for a comprehensive codebase review.

---

## The Prompt

```
You are reviewing a production Python codebase called "Pharos" — a read-only Streamlit application that queries pre-built PostgreSQL tables to display Out-of-Home (OOH) advertising campaign data for econometricians. The app has no write operations, no live API calls at runtime, and serves purely as a query and export interface.

## Codebase Facts

- **Language**: Python 3.11+
- **Framework**: Streamlit
- **Database**: PostgreSQL (psycopg2, raw SQL queries — no ORM for queries)
- **Package manager**: UV (pyproject.toml + uv.lock)
- **Linting config**: Black (88 char), isort (black profile), mypy (strict), flake8
- **Source**: ~11,200 lines across 53 Python files in src/
- **Tests**: 5 test files (tests/conftest.py, tests/test_validators.py, tests/unit/test_formatters.py)
- **Documentation**: 11 markdown files in docs/, README.md, migrations/README.md, scripts/README.md

## Architecture

```
src/
├── ui/                    # Streamlit application
│   ├── app.py                      # Entry point — campaign selection + analysis rendering
│   ├── components/                 # Reusable UI components
│   │   ├── campaign_browser/       # Campaign selection table (8 modules)
│   │   ├── key_metrics.py          # 5-column KPI row
│   │   └── demographic_analysis.py # Demographic charts + export
│   ├── tabs/                       # One module per analysis tab
│   │   ├── overview.py             # Campaign summary, frame performance
│   │   ├── reach_grp.py            # Weekly reach, impacts, GRPs
│   │   ├── time_series.py          # Daily & hourly patterns
│   │   ├── geographic.py           # UK map, regional breakdown
│   │   ├── detailed_analysis.py    # Frame-level data (econometric export)
│   │   └── executive_summary.py    # One-page KPI overview
│   ├── utils/export/               # CSV, Excel export (5 modules)
│   ├── config/                     # Demographics mappings, anonymisation
│   └── styles/css.py               # Centralised CSS
├── db/                    # Database layer
│   ├── queries/                    # Query modules (8 files)
│   │   ├── connection.py           # Database connection management
│   │   ├── campaigns.py            # Campaign listing + browser
│   │   ├── reach.py                # Reach, GRP, frequency
│   │   ├── impacts.py              # Audience impacts
│   │   ├── demographics.py         # Demographic breakdowns
│   │   ├── geographic.py           # Geographic/frame location data
│   │   └── frame_audience.py       # Frame-level audience export
│   └── streamlit_queries.py        # Facade — main entry point for UI queries
├── config.py              # DatabaseConfig, env var loading
└── utils/
    ├── formatters.py              # Number formatting, display helpers
    ├── validators.py              # Frame validation (Route API)
    └── ttl_cache.py               # TTL cache implementation
```

**Layer responsibilities:**
- `ui/` — Rendering only. Tabs read from `st.session_state`, no direct DB queries.
- `db/` — All PostgreSQL queries. `streamlit_queries.py` is the facade the UI calls.
- `config.py` — Single source for database connection settings and feature flags.

## Key Database Details

- Tables use `mv_` prefix (historical — were materialised views, now regular tables)
- 18 tables + 1 view in production
- `cache_route_impacts_15min_by_demo` (252M rows) is the fallback table used when pre-aggregated tables lack data
- Impacts stored in thousands in the raw cache table (must multiply by 1000)
- Frame data joins: `route_frames` → `route_releases` → `route_frame_details`
- `mv_campaign_browser` has pre-computed metrics per campaign (~830 rows)

## Review Instructions

Please conduct a comprehensive review covering ALL of the following areas. For each area, provide:
1. A severity rating (Critical / High / Medium / Low / Info)
2. File path and line number(s) where applicable
3. A clear description of the issue
4. A suggested fix

### 1. CODE QUALITY

- Function and variable naming (should be snake_case, descriptive, no "new_", "improved_", "fixed_")
- Code duplication — are there patterns repeated across files that should be extracted?
- Function length — any functions that are too long and should be broken up?
- Single Responsibility Principle — do functions/modules do too many things?
- Dead code — unreachable branches, unused variables, unused imports
- Type hints — are they present and correct on all function signatures?
- Error handling — appropriate use of try/except, not too broad, not swallowing errors?
- Resource management — are database connections always closed? (check for missing finally blocks)

### 2. DOCUMENTATION

Review all docs/*.md files, README.md, migrations/README.md, scripts/README.md:
- Accuracy — do descriptions match the actual code?
- Completeness — are key features, gotchas, and patterns documented?
- Consistency — is terminology consistent across all docs?
- Code examples — do they use correct function names, table names, column names?
- Cross-references — do links between docs work? Do referenced files exist?
- Freshness — any references to features, files, or tables that no longer exist?

### 3. TESTS

Review tests/conftest.py, tests/test_validators.py, tests/unit/test_formatters.py:
- Coverage — what percentage of src/ functionality has test coverage?
- Missing tests — which modules have ZERO test coverage? Prioritise what should be tested.
- Test quality — are existing tests meaningful? Do they test edge cases?
- Test organisation — is the test structure logical?
- Fixtures — are conftest.py fixtures well-designed and reusable?
- Note: this project connects to a real PostgreSQL database. No mocking is used.

### 4. CODE COMMENTS

Review all Python files in src/ for:
- ABOUTME headers — every .py file should start with two lines: `# ABOUTME: ...`
- Comment accuracy — do comments match what the code actually does?
- Stale comments — references to removed features, old table names, old architecture?
- Comment quality — are they useful or just restating the code?
- Docstrings — are they present on public functions? Do they follow Google style with Args/Returns?
- Temporal language — comments should NOT reference "recently changed", "was refactored", etc.

### 5. LINTING & STYLE

The project uses Black (88 char), isort (black profile), mypy (strict), flake8.
- Run or simulate a lint check — flag any obvious violations
- Import ordering — are imports grouped correctly (stdlib, third-party, local)?
- Line length — any lines exceeding 88 characters?
- Type annotation completeness — are all function parameters and return types annotated?
- f-string usage — any unsafe string formatting for SQL? (should use parameterised queries)
- Consistent patterns — does the codebase follow consistent patterns throughout?

### 6. SECURITY

- SQL injection — are all queries parameterised? Any string interpolation in SQL?
- Environment variables — are secrets handled properly?
- Database connections — are credentials exposed anywhere in code?
- Input validation — is user input from Streamlit sanitised before database queries?
- Export security — can users export data they shouldn't have access to?

### 7. PERFORMANCE

- Database queries — any obvious N+1 patterns, missing WHERE clauses, or full table scans?
- Connection management — are connections pooled or opened/closed per query?
- Streamlit caching — is `@st.cache_data` or session_state used effectively?
- Large dataset handling — how does the app handle tables with millions of rows?
- Any unnecessary computation in hot paths?

## Output Format

Please structure your review as:

### Summary
- Overall score: X/10
- Top 3 critical findings
- Top 3 strengths

### Detailed Findings
For each area (1-7), list findings sorted by severity. Use this format:

**[SEVERITY] Area > Finding Title**
- File: `path/to/file.py:line`
- Issue: Description
- Fix: Suggested resolution

### Recommendations
Prioritised list of changes, grouped by effort (quick wins vs larger refactors).
```

---

*Last Updated: 5 February 2026*
