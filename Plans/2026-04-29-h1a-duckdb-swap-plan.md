# H1A — DuckDB Swap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace PostgreSQL with DuckDB as the read-only query backend for the existing Streamlit app, with zero changes to UI behaviour. Establishes the data substrate every subsequent plan depends on.

**Architecture:** A `BACKEND=postgres|duckdb` env var selects the engine in `src/db/queries/connection.py`. All `get_*_sync` query functions return `List[Dict]` regardless of backend (DuckDB results wrapped via a small `cursor.description`-based helper). Dialect differences are mechanical (`%s` → `?`, casts). A pytest parity test runs every query against both backends and asserts shape consistency, catching dialect drift before it surfaces in the UI.

**Tech Stack:** Python 3.11+, psycopg2 (existing), duckdb (new), pytest, uv. No Streamlit changes; no new dependencies in the UI layer.

**Spec:** `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `src/db/queries/connection.py` | Modify | Backend selector; opens postgres or duckdb connection per env |
| `src/db/queries/_dict_cursor.py` | Create | DuckDB cursor → list-of-dicts helper |
| `src/db/queries/campaigns.py` | Modify | Param style sweep |
| `src/db/queries/impacts.py` | Modify | Param style sweep |
| `src/db/queries/reach.py` | Modify | Param style sweep |
| `src/db/queries/geographic.py` | Modify | Param style sweep |
| `src/db/queries/demographics.py` | Modify | Param style sweep |
| `src/db/queries/frame_audience.py` | Modify | Param style sweep |
| `src/db/queries/mobile_index.py` | Modify | Param style sweep |
| `tests/db/test_query_parity.py` | Create | Parity test across backends |
| `tests/db/conftest.py` | Create | Fixtures: known campaign IDs, query fixture catalogue |
| `tests/fixtures/route_poc_test.duckdb` | Create (gitignored) | Small test DB |
| `scripts/build_test_duckdb.py` | Create | Generates fixture DB from production DuckDB |
| `.env.example` | Modify | Document `BACKEND`, `DUCKDB_PATH` |
| `pyproject.toml` | Modify | Add `duckdb` dependency |

---

## Pre-Flight

### Task 0: Branch and dependency setup

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Create feature branch**

```bash
git checkout main
git pull origin main
git checkout -b feature/duckdb-migration
```

Expected: branch created, working tree clean.

- [ ] **Step 2: Add duckdb dependency**

```bash
uv add duckdb
```

Expected: `pyproject.toml` and `uv.lock` updated. `python -c "import duckdb; print(duckdb.__version__)"` prints a version string.

- [ ] **Step 3: Verify DuckDB file is accessible**

Set `DUCKDB_PATH` in your local `.env` to the file produced by your in-flight DuckDB data work. Verify:

```bash
python -c "import duckdb, os; conn = duckdb.connect(os.environ['DUCKDB_PATH'], read_only=True); print(conn.execute('SHOW TABLES').fetchall()); conn.close()"
```

Expected: lists tables including `mv_campaign_browser`, `mv_cache_campaign_impacts_day`, `cache_mi_*`. If tables are missing, the data-side work isn't ready and this plan is blocked.

- [ ] **Step 4: Commit dependency**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add duckdb dependency"
```

---

## Tasks

### Task 1: Test DuckDB fixture script

**Files:**
- Create: `scripts/build_test_duckdb.py`
- Modify: `.gitignore`

Generates a small fixture DuckDB file from the production DuckDB by selecting 5 advertisers / ~20 campaigns. Used by tests so CI doesn't depend on the full DB.

- [ ] **Step 1: Write the fixture builder script**

```python
# ABOUTME: Builds a small test DuckDB fixture from the production DuckDB.
# ABOUTME: Selects 5 advertisers and ~20 campaigns for fast test runs.

"""Build tests/fixtures/route_poc_test.duckdb from production DuckDB."""

import os
import shutil
import duckdb
from pathlib import Path

SRC_PATH = os.environ["DUCKDB_PATH"]
DST_PATH = Path(__file__).parent.parent / "tests" / "fixtures" / "route_poc_test.duckdb"
DST_PATH.parent.mkdir(parents=True, exist_ok=True)

# Pick 5 advertisers known to be in the data
TEST_BRANDS = ["Lidl", "McDonald's Restaurants", "Sainsbury's", "British Gas", "Argos"]

src = duckdb.connect(SRC_PATH, read_only=True)
campaign_ids = src.execute(
    """
    SELECT campaign_id FROM mv_campaign_browser
    WHERE EXISTS (
        SELECT 1 FROM UNNEST(brand_names) AS bn(name)
        WHERE name = ANY(?)
    )
    LIMIT 20
    """,
    [TEST_BRANDS],
).fetchall()
campaign_ids = [c[0] for c in campaign_ids]
print(f"Selected {len(campaign_ids)} campaigns")

if DST_PATH.exists():
    DST_PATH.unlink()

dst = duckdb.connect(str(DST_PATH))
dst.execute(f"ATTACH '{SRC_PATH}' AS src (READ_ONLY)")

# Tables to copy with campaign filtering
campaign_filtered_tables = [
    "mv_campaign_browser",
    "mv_cache_campaign_impacts_day",
    "mv_cache_campaign_impacts_hour",
    "cache_route_impacts_15min_by_demo",
    "cache_mi_daily",
    "cache_mi_weekly",
    "cache_mi_hourly",
    "cache_mi_frame_daily",
    "cache_mi_frame_hourly",
    "cache_mi_frame_totals",
    "cache_mi_coverage",
]

for table in campaign_filtered_tables:
    print(f"Copying {table}…")
    dst.execute(
        f"CREATE TABLE {table} AS SELECT * FROM src.{table} WHERE campaign_id = ANY(?)",
        [campaign_ids],
    )

# Tables that don't have campaign_id — copy fully
full_copy_tables = ["mobile_volume_index"]
for table in full_copy_tables:
    print(f"Copying {table} (full)…")
    dst.execute(f"CREATE TABLE {table} AS SELECT * FROM src.{table}")

dst.close()
src.close()
print(f"Fixture written to {DST_PATH}")
```

- [ ] **Step 2: Add fixture path to .gitignore**

Append to `.gitignore`:

```
# Test fixture binary (generated from production DuckDB)
tests/fixtures/*.duckdb
```

- [ ] **Step 3: Run the script**

```bash
uv run python scripts/build_test_duckdb.py
```

Expected: prints "Selected N campaigns" and "Copying ...", produces a file at `tests/fixtures/route_poc_test.duckdb` of ~30–80 MB.

- [ ] **Step 4: Commit script + gitignore**

```bash
git add scripts/build_test_duckdb.py .gitignore
git commit -m "feat: add test DuckDB fixture builder"
```

---

### Task 2: Dict-row helper

**Files:**
- Create: `src/db/queries/_dict_cursor.py`

DuckDB's cursor returns tuples; psycopg2's `RealDictCursor` returns dicts. A small helper produces dicts using `cursor.description`.

- [ ] **Step 1: Write the failing test**

Create `tests/db/__init__.py` (empty) and `tests/db/test_dict_cursor.py`:

```python
import duckdb
from src.db.queries._dict_cursor import fetchall_as_dicts


def test_fetchall_as_dicts_returns_list_of_dicts():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE t (a INT, b VARCHAR)")
    conn.execute("INSERT INTO t VALUES (1, 'one'), (2, 'two')")
    cursor = conn.execute("SELECT a, b FROM t ORDER BY a")
    result = fetchall_as_dicts(cursor)
    assert result == [{"a": 1, "b": "one"}, {"a": 2, "b": "two"}]


def test_fetchall_as_dicts_returns_empty_list_for_no_rows():
    conn = duckdb.connect(":memory:")
    conn.execute("CREATE TABLE t (a INT)")
    cursor = conn.execute("SELECT a FROM t")
    assert fetchall_as_dicts(cursor) == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/db/test_dict_cursor.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'src.db.queries._dict_cursor'`.

- [ ] **Step 3: Write minimal implementation**

```python
# ABOUTME: Helper to convert DuckDB cursor results into list-of-dicts.
# ABOUTME: Mirrors the shape psycopg2.extras.RealDictCursor produces.

"""DuckDB result-to-dict adapter."""

from typing import Any, Dict, List


def fetchall_as_dicts(cursor: Any) -> List[Dict[str, Any]]:
    """Fetch all rows from a DuckDB cursor as a list of dicts.

    DuckDB's cursor.fetchall() returns tuples; this wrapper uses
    cursor.description to produce the same shape as psycopg2's RealDictCursor.
    """
    rows = cursor.fetchall()
    if not rows:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/db/test_dict_cursor.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/db/queries/_dict_cursor.py tests/db/test_dict_cursor.py tests/db/__init__.py
git commit -m "feat: add DuckDB dict-row helper"
```

---

### Task 3: Backend selector in connection.py

**Files:**
- Modify: `src/db/queries/connection.py`

- [ ] **Step 1: Write the failing test**

Create `tests/db/test_connection.py`:

```python
import os
import pytest
from src.db.queries.connection import get_db_connection


def test_postgres_backend_returns_psycopg2_connection(monkeypatch):
    monkeypatch.setenv("BACKEND", "postgres")
    monkeypatch.setenv("USE_PRIMARY_DATABASE", "false")
    monkeypatch.setenv("POSTGRES_HOST_SECONDARY", "localhost")
    conn = get_db_connection()
    assert type(conn).__module__.startswith("psycopg2")
    conn.close()


def test_duckdb_backend_returns_duckdb_connection(monkeypatch, tmp_path):
    import duckdb
    db_path = tmp_path / "smoke.duckdb"
    duckdb.connect(str(db_path)).close()  # create empty
    monkeypatch.setenv("BACKEND", "duckdb")
    monkeypatch.setenv("DUCKDB_PATH", str(db_path))
    conn = get_db_connection()
    assert type(conn).__module__.startswith("duckdb")
    conn.close()


def test_unknown_backend_raises(monkeypatch):
    monkeypatch.setenv("BACKEND", "sqlite")
    with pytest.raises(ValueError, match="Unknown BACKEND"):
        get_db_connection()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/db/test_connection.py -v
```

Expected: tests fail (BACKEND not yet honoured).

- [ ] **Step 3: Modify `connection.py` to add backend selector**

Replace `src/db/queries/connection.py` content with:

```python
# ABOUTME: Database connection management for synchronous queries.
# ABOUTME: Selects PostgreSQL or DuckDB backend via BACKEND env var.

import os
from typing import Any

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_db_connection(use_primary: bool = None) -> Any:
    """Return a database connection based on BACKEND env var.

    BACKEND=postgres (default) → psycopg2 connection (primary or secondary).
    BACKEND=duckdb → DuckDB read-only connection on DUCKDB_PATH.
    """
    backend = os.getenv("BACKEND", "postgres").lower()

    if backend == "postgres":
        return _get_postgres_connection(use_primary)
    if backend == "duckdb":
        return _get_duckdb_connection()
    raise ValueError(f"Unknown BACKEND: {backend!r} (expected 'postgres' or 'duckdb')")


def _get_postgres_connection(use_primary: bool = None) -> Any:
    if use_primary is None:
        use_primary = os.getenv("USE_PRIMARY_DATABASE", "true").lower() == "true"

    if use_primary:
        host = os.getenv("POSTGRES_HOST_PRIMARY", "")
        if not host:
            raise ValueError(
                "POSTGRES_HOST_PRIMARY environment variable "
                "must be set for primary database connection"
            )
        return psycopg2.connect(
            host=host,
            port=int(os.getenv("POSTGRES_PORT_PRIMARY", "5432")),
            database=os.getenv("POSTGRES_DATABASE_PRIMARY", "route_poc"),
            user=os.getenv("POSTGRES_USER_PRIMARY", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD_PRIMARY", ""),
        )
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST_SECONDARY", "localhost"),
        port=int(os.getenv("POSTGRES_PORT_SECONDARY", "5432")),
        database=os.getenv("POSTGRES_DATABASE_SECONDARY", "route_poc"),
        user=os.getenv("POSTGRES_USER_SECONDARY", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD_SECONDARY", ""),
    )


def _get_duckdb_connection() -> Any:
    import duckdb

    path = os.getenv("DUCKDB_PATH", "")
    if not path:
        raise ValueError("DUCKDB_PATH must be set when BACKEND=duckdb")
    return duckdb.connect(path, read_only=True)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run pytest tests/db/test_connection.py -v
```

Expected: 3 passing tests. (Postgres test may be skipped if no local DB; that's acceptable — note it.)

- [ ] **Step 5: Commit**

```bash
git add src/db/queries/connection.py tests/db/test_connection.py
git commit -m "feat: BACKEND env var selects postgres or duckdb"
```

---

### Task 4: Query fixture catalogue

**Files:**
- Create: `tests/db/conftest.py`
- Create: `tests/db/query_fixtures.py`

The catalogue lists every `get_*_sync` function with a known-good argument set. Used by the parity test in Task 5.

- [ ] **Step 1: Identify a known-good campaign ID from the fixture**

```bash
DUCKDB_PATH=tests/fixtures/route_poc_test.duckdb uv run python -c "
import duckdb, os
conn = duckdb.connect(os.environ['DUCKDB_PATH'], read_only=True)
rows = conn.execute('SELECT campaign_id FROM mv_campaign_browser ORDER BY total_impacts DESC LIMIT 3').fetchall()
print(rows)
"
```

Expected: prints 3 campaign IDs. Pick one (e.g. the highest-impact campaign) — record the ID, you'll use it as `KNOWN_CAMPAIGN_ID` below.

- [ ] **Step 2: Write the fixture catalogue**

`tests/db/query_fixtures.py`:

```python
# ABOUTME: Catalogue of every sync query function with a known-good argument set.
# ABOUTME: Drives the cross-backend parity test.

"""Query fixture catalogue for backend parity testing.

KNOWN_CAMPAIGN_ID must exist in tests/fixtures/route_poc_test.duckdb.
Update if the fixture is rebuilt with different campaigns.
"""

from src.db.queries import (
    get_campaign_summary_sync,
    get_campaigns_from_browser_sync,
    get_campaign_from_browser_by_id_sync,
    get_campaign_header_info_sync,
    get_campaign_browser_summary_sync,
    get_platform_stats_sync,
    get_demographic_count_sync,
    get_available_demographics_for_campaign_sync,
    get_weekly_reach_data_sync,
    get_daily_cumulative_reach_sync,
    get_full_campaign_reach_sync,
    get_daily_impacts_sync,
    get_hourly_impacts_sync,
    get_regional_impacts_sync,
    get_environment_impacts_sync,
    get_frame_geographic_data_sync,
    get_frame_audience_by_day_sync,
    get_frame_audience_by_hour_sync,
    get_frame_audience_by_week_sync,
    get_frame_audience_daily_count_sync,
    get_frame_audience_hourly_count_sync,
    get_frame_audience_weekly_count_sync,
    get_frame_audience_campaign_count_sync,
    get_frame_audience_table_sync,
    mobile_index_table_exists,
    get_mobile_index_coverage_sync,
    get_campaign_mobile_index_sync,
    get_daily_impacts_with_mobile_index_sync,
    get_hourly_impacts_with_mobile_index_sync,
    get_weekly_impacts_with_mobile_index_sync,
    get_frame_daily_with_mobile_index_sync,
    get_frame_hourly_with_mobile_index_sync,
    get_frame_totals_with_mobile_index_sync,
)

# REPLACE with a real campaign_id present in tests/fixtures/route_poc_test.duckdb
KNOWN_CAMPAIGN_ID = "REPLACE_ME"
KNOWN_DEMOGRAPHIC = "all_adults"

QUERY_FIXTURES = [
    # (label, callable, kwargs)
    ("campaign_summary", get_campaign_summary_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("campaigns_browser", get_campaigns_from_browser_sync, {}),
    ("campaign_browser_by_id", get_campaign_from_browser_by_id_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("campaign_header", get_campaign_header_info_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("campaign_browser_summary", get_campaign_browser_summary_sync, {}),
    ("platform_stats", get_platform_stats_sync, {}),
    ("demographic_count", get_demographic_count_sync, {}),
    ("available_demographics", get_available_demographics_for_campaign_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("weekly_reach", get_weekly_reach_data_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("daily_cumulative_reach", get_daily_cumulative_reach_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("full_reach", get_full_campaign_reach_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("daily_impacts", get_daily_impacts_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("hourly_impacts", get_hourly_impacts_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("regional_impacts", get_regional_impacts_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("environment_impacts", get_environment_impacts_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("frame_geographic", get_frame_geographic_data_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("frame_audience_day", get_frame_audience_by_day_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("frame_audience_hour", get_frame_audience_by_hour_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("frame_audience_week", get_frame_audience_by_week_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("frame_audience_daily_count", get_frame_audience_daily_count_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("frame_audience_hourly_count", get_frame_audience_hourly_count_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("frame_audience_weekly_count", get_frame_audience_weekly_count_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("frame_audience_campaign_count", get_frame_audience_campaign_count_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("frame_audience_table", get_frame_audience_table_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("mi_table_exists", mobile_index_table_exists, {}),
    ("mi_coverage", get_mobile_index_coverage_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("mi_campaign", get_campaign_mobile_index_sync, {"campaign_id": KNOWN_CAMPAIGN_ID}),
    ("mi_daily", get_daily_impacts_with_mobile_index_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("mi_hourly", get_hourly_impacts_with_mobile_index_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("mi_weekly", get_weekly_impacts_with_mobile_index_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("mi_frame_daily", get_frame_daily_with_mobile_index_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("mi_frame_hourly", get_frame_hourly_with_mobile_index_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
    ("mi_frame_totals", get_frame_totals_with_mobile_index_sync, {"campaign_id": KNOWN_CAMPAIGN_ID, "demographic": KNOWN_DEMOGRAPHIC}),
]
```

- [ ] **Step 3: Replace `KNOWN_CAMPAIGN_ID = "REPLACE_ME"` with the real ID from Step 1**

- [ ] **Step 4: Write conftest**

`tests/db/conftest.py`:

```python
import os
from pathlib import Path
import pytest


@pytest.fixture
def duckdb_env(monkeypatch):
    """Configure environment for the test DuckDB fixture."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "route_poc_test.duckdb"
    monkeypatch.setenv("BACKEND", "duckdb")
    monkeypatch.setenv("DUCKDB_PATH", str(fixture_path))
    if not fixture_path.exists():
        pytest.skip(f"Fixture DB not found at {fixture_path}. Run scripts/build_test_duckdb.py.")
```

- [ ] **Step 5: Commit**

```bash
git add tests/db/query_fixtures.py tests/db/conftest.py
git commit -m "test: add query fixture catalogue and DuckDB env fixture"
```

---

### Task 5: Parity test (the linchpin)

**Files:**
- Create: `tests/db/test_query_parity.py`

- [ ] **Step 1: Write the parity test**

```python
# ABOUTME: Cross-backend parity test for every sync query function.
# ABOUTME: Asserts each function returns the expected shape on DuckDB.

"""Parity test: every get_*_sync function returns valid shape on DuckDB."""

import pytest
from .query_fixtures import QUERY_FIXTURES


@pytest.mark.parametrize(
    "label,query_fn,kwargs",
    QUERY_FIXTURES,
    ids=[f[0] for f in QUERY_FIXTURES],
)
def test_query_returns_valid_shape_on_duckdb(label, query_fn, kwargs, duckdb_env):
    """Each query function should return either a list of dicts or a tuple/scalar
    appropriate to its signature, on the DuckDB backend."""
    result = query_fn(**kwargs)

    # Some functions return tuples (e.g. mi_coverage), some return ints
    # (demographic_count), most return list-of-dicts.
    if isinstance(result, list):
        if result:
            assert isinstance(result[0], dict), (
                f"{label}: list element is {type(result[0])}, expected dict"
            )
    elif isinstance(result, (tuple, int, bool, float, type(None))):
        pass  # acceptable for scalar/tuple-returning functions
    else:
        pytest.fail(f"{label}: unexpected result type {type(result)}")
```

- [ ] **Step 2: Run the test, expect failures**

```bash
uv run pytest tests/db/test_query_parity.py -v
```

Expected: many failures with errors like `syntax error at or near "%"` or similar — these are dialect issues to fix in subsequent tasks.

- [ ] **Step 3: Capture the failure list**

```bash
uv run pytest tests/db/test_query_parity.py -v 2>&1 | tee /tmp/parity_failures.log
```

Use this log as the worklist for Tasks 6–13. Don't commit anything yet — the parity test is the failing "spec" that the next tasks resolve.

---

### Task 6: Fix dialect issues in `campaigns.py`

**Files:**
- Modify: `src/db/queries/campaigns.py`

- [ ] **Step 1: Read the current file** to understand its structure

```bash
uv run pytest "tests/db/test_query_parity.py::test_query_returns_valid_shape_on_duckdb[campaign_summary]" -v
```

Note the exact error.

- [ ] **Step 2: Sweep `%s` → `?` across the file**

In `src/db/queries/campaigns.py`, replace every parameter placeholder:
- Find: `%s`
- Replace with: `?`

Care: only inside SQL strings, not inside Python f-strings or format strings used for non-SQL purposes. Visual review every change.

- [ ] **Step 3: Replace `RealDictCursor` with the dict helper**

For each function that uses `cursor_factory=psycopg2.extras.RealDictCursor`, replace the cursor handling. Pattern to apply:

Before:
```python
with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
    cursor.execute(query, (campaign_id,))
    results = cursor.fetchall()
    return [dict(row) for row in results]
```

After:
```python
from ._dict_cursor import fetchall_as_dicts

cursor = conn.execute(query, (campaign_id,))  # DuckDB style
# OR, for postgres compatibility:
if hasattr(conn, "execute"):  # DuckDB
    cursor = conn.execute(query, (campaign_id,))
else:  # psycopg2
    cursor = conn.cursor()
    cursor.execute(query, (campaign_id,))

return fetchall_as_dicts(cursor) if hasattr(cursor, "description") else []
```

A cleaner approach: write a small `execute_query(conn, query, params)` helper in `_dict_cursor.py` that handles both backends:

```python
def execute_query(conn, query, params=None):
    """Execute a query on either psycopg2 or DuckDB connection, returning list-of-dicts."""
    if hasattr(conn, "cursor") and not hasattr(conn, "fetchall"):
        # psycopg2 connection
        import psycopg2.extras
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, params or ())
            return [dict(r) for r in cursor.fetchall()]
    # duckdb connection
    cursor = conn.execute(query, params or [])
    return fetchall_as_dicts(cursor)
```

Add this helper to `_dict_cursor.py`, then use `execute_query(conn, query, (campaign_id,))` throughout `campaigns.py`.

- [ ] **Step 4: Run the campaign parity tests**

```bash
uv run pytest tests/db/test_query_parity.py -v -k "campaign"
```

Expected: PASS for `campaign_summary`, `campaigns_browser`, `campaign_browser_by_id`, `campaign_header`, `campaign_browser_summary`, `platform_stats`.

- [ ] **Step 5: Commit**

```bash
git add src/db/queries/campaigns.py src/db/queries/_dict_cursor.py
git commit -m "feat: campaigns.py supports duckdb backend"
```

---

### Task 7: Fix dialect issues in `impacts.py`

**Files:**
- Modify: `src/db/queries/impacts.py`

The fallback pattern in this file (try `mv_*`, fall back to raw cache) is preserved unchanged — both queries use the same dialect.

- [ ] **Step 1: Sweep `%s` → `?`**

- [ ] **Step 2: Replace `RealDictCursor` blocks with `execute_query` helper from Task 6**

- [ ] **Step 3: Run impacts parity tests**

```bash
uv run pytest tests/db/test_query_parity.py -v -k "impacts"
```

Expected: PASS for `daily_impacts`, `hourly_impacts`, `regional_impacts`, `environment_impacts`.

- [ ] **Step 4: Commit**

```bash
git add src/db/queries/impacts.py
git commit -m "feat: impacts.py supports duckdb backend"
```

---

### Task 8: Fix dialect issues in `reach.py`

**Files:** `src/db/queries/reach.py`

- [ ] **Step 1: `%s` → `?` sweep**
- [ ] **Step 2: Apply `execute_query` helper**
- [ ] **Step 3:** `uv run pytest tests/db/test_query_parity.py -v -k "reach"` — expected PASS for `weekly_reach`, `daily_cumulative_reach`, `full_reach`
- [ ] **Step 4:** `git add src/db/queries/reach.py && git commit -m "feat: reach.py supports duckdb backend"`

---

### Task 9: Fix dialect issues in `geographic.py`

**Files:** `src/db/queries/geographic.py`

- [ ] **Step 1: `%s` → `?` sweep**
- [ ] **Step 2: Apply `execute_query` helper**
- [ ] **Step 3:** `uv run pytest tests/db/test_query_parity.py -v -k "geographic or regional or environment"` — expected PASS
- [ ] **Step 4:** `git add src/db/queries/geographic.py && git commit -m "feat: geographic.py supports duckdb backend"`

---

### Task 10: Fix dialect issues in `demographics.py`

**Files:** `src/db/queries/demographics.py`

- [ ] **Step 1: `%s` → `?` sweep**
- [ ] **Step 2: Apply `execute_query` helper**
- [ ] **Step 3:** `uv run pytest tests/db/test_query_parity.py -v -k "demographic"` — expected PASS
- [ ] **Step 4:** `git add src/db/queries/demographics.py && git commit -m "feat: demographics.py supports duckdb backend"`

---

### Task 11: Fix dialect issues in `frame_audience.py`

**Files:** `src/db/queries/frame_audience.py`

- [ ] **Step 1: `%s` → `?` sweep**
- [ ] **Step 2: Apply `execute_query` helper**
- [ ] **Step 3:** `uv run pytest tests/db/test_query_parity.py -v -k "frame_audience"` — expected PASS for all `frame_audience_*` cases
- [ ] **Step 4:** `git add src/db/queries/frame_audience.py && git commit -m "feat: frame_audience.py supports duckdb backend"`

---

### Task 12: Fix dialect issues in `mobile_index.py`

**Files:** `src/db/queries/mobile_index.py`

- [ ] **Step 1: `%s` → `?` sweep**
- [ ] **Step 2: Apply `execute_query` helper, including the `mobile_index_table_exists` query**
- [ ] **Step 3:** `uv run pytest tests/db/test_query_parity.py -v -k "mi_"` — expected PASS for all `mi_*` cases
- [ ] **Step 4:** `git add src/db/queries/mobile_index.py && git commit -m "feat: mobile_index.py supports duckdb backend"`

---

### Task 13: Full parity test run

- [ ] **Step 1: Run the full parity suite**

```bash
uv run pytest tests/db/test_query_parity.py -v
```

Expected: all ~32 tests PASS on DuckDB. If any fail, return to the relevant module task and fix.

- [ ] **Step 2: Run on the postgres backend too (optional, slower)**

```bash
USE_PRIMARY_DATABASE=false BACKEND=postgres uv run pytest tests/db/test_query_parity.py -v
```

Expected: same tests PASS on Postgres. Confirms no regressions.

---

### Task 14: Streamlit smoke test on DuckDB

**Files:** none modified — manual verification.

- [ ] **Step 1: Start Streamlit pointed at DuckDB**

```bash
BACKEND=duckdb DUCKDB_PATH=/path/to/full/route_poc.duckdb uv run streamlit run src/ui/app.py --server.port 8504
```

- [ ] **Step 2: Click through every tab for one campaign**

For a representative campaign, visit:
- Overview — verify hero metrics, daily chart, MI overlay toggle
- Reach/GRP — verify weekly table, cumulative build chart
- Geographic — verify UK map, regional chart, towns table
- Time Series — verify hourly/daily patterns, day-of-week
- Detailed Analysis — verify each sub-tab loads
- Executive Summary — verify all sections render

Expected: every tab loads, no Streamlit error banners. MI toggle (mean and median) works on every chart that supports it. Visual output matches Postgres-backed version (eyeball comparison).

- [ ] **Step 3: Spot-check numerical values**

For one campaign, capture a key metric (e.g. total impacts, frame count) from the DuckDB-backed app and compare to the Postgres-backed app on `main`. Should be identical (same underlying data) or within tolerance if the data sources differ.

- [ ] **Step 4: If smoke fails**

Identify the failing tab, find the underlying query function, and confirm whether it's missing from the parity test catalogue or has a deeper dialect issue. Fix and add to the catalogue.

---

### Task 15: Update `.env.example` and finalise

**Files:**
- Modify: `.env.example`

- [ ] **Step 1: Document the new env vars**

Add to `.env.example`:

```
# Database backend selection
# Options: postgres (default), duckdb
BACKEND=duckdb

# DuckDB path (required when BACKEND=duckdb)
DUCKDB_PATH=/path/to/route_poc.duckdb
```

- [ ] **Step 2: Verify CI is green**

```bash
uv run pytest tests/db/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Final commit**

```bash
git add .env.example
git commit -m "docs: document BACKEND and DUCKDB_PATH env vars"
```

- [ ] **Step 4: Push branch**

```bash
git push -u origin feature/duckdb-migration
```

---

## Done Criteria

- [ ] All ~32 parity tests pass on DuckDB
- [ ] All ~32 parity tests pass on Postgres (no regression)
- [ ] Streamlit smoke test passes for one full campaign across every tab on DuckDB
- [ ] `.env.example` documents `BACKEND` and `DUCKDB_PATH`
- [ ] Branch pushed to private origin
- [ ] No new dependencies beyond `duckdb`

This is the H1A ship signal. Streamlit-on-DuckDB works end-to-end. Plan H1B (FastAPI) can begin.
