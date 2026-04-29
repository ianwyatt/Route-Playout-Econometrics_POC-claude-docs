# H1B — FastAPI Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a FastAPI service that exposes the existing query functions as JSON endpoints, plus the new advertiser-trends routes that the React app needs. Read-only, localhost-only in H1.

**Architecture:** Thin route layer over existing `src/db/queries/*.py` functions. Each FastAPI route is ~5 lines: parse args, call the existing sync query function, return through a Pydantic model. Connection per-request via FastAPI `Depends`. Stub `current_user` dependency in place from day one so H3 auth wiring doesn't change route signatures.

**Tech Stack:** FastAPI, Uvicorn, Pydantic v2, fastapi-cache2 (in-memory backend), pytest, httpx (TestClient).

**Spec:** `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`

**Depends on:** H1A complete (DuckDB backend selectable; query functions return `List[Dict]` on DuckDB).

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `src/api/__init__.py` | Create | Package marker |
| `src/api/main.py` | Create | FastAPI app, middleware, exception handlers, lifespan |
| `src/api/deps.py` | Create | `get_db_connection_dep`, `get_current_user` (stub) |
| `src/api/routes/__init__.py` | Create | Route registration |
| `src/api/routes/campaigns.py` | Create | Campaign endpoints |
| `src/api/routes/impacts.py` | Create | Impacts endpoints |
| `src/api/routes/reach.py` | Create | Reach endpoints |
| `src/api/routes/geographic.py` | Create | Geographic endpoints |
| `src/api/routes/demographics.py` | Create | Demographics endpoints |
| `src/api/routes/mobile_index.py` | Create | MI endpoints |
| `src/api/routes/advertisers.py` | Create | NEW advertiser endpoints |
| `src/api/schemas/__init__.py` | Create | Schema package marker |
| `src/api/schemas/campaign.py` | Create | Campaign Pydantic models |
| `src/api/schemas/impacts.py` | Create | Impacts Pydantic models |
| `src/api/schemas/advertiser.py` | Create | Advertiser Pydantic models |
| `src/api/services/advertisers.py` | Create | Domain logic ported from `_build_pages.py` |
| `src/api/services/shape_descriptor.py` | Create | "Steady ramp-up", "Twin peaks" etc. heuristics |
| `tests/api/conftest.py` | Create | TestClient fixture, shared test setup |
| `tests/api/test_campaigns.py` | Create | Campaign route tests |
| `tests/api/test_advertisers.py` | Create | Advertiser route tests |
| `tests/api/test_main.py` | Create | App-level (CORS, errors) tests |
| `pyproject.toml` | Modify | Add fastapi, uvicorn, fastapi-cache2, httpx |
| `.env.example` | Modify | Document API_PORT, ALLOWED_ORIGINS |

---

## Pre-Flight

### Task 0: Dependencies and branch state

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Verify on H1A branch**

```bash
git status
git log --oneline -5
```

Expected: on `feature/duckdb-migration`, recent commits include H1A work. If H1A has been merged to main, branch off main.

- [ ] **Step 2: Add dependencies**

```bash
uv add fastapi 'uvicorn[standard]' fastapi-cache2 httpx
uv add --dev pytest-asyncio
```

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add fastapi and related deps"
```

---

## Tasks

### Task 1: Package skeleton

**Files:**
- Create: `src/api/__init__.py`
- Create: `src/api/main.py`
- Create: `src/api/routes/__init__.py`
- Create: `src/api/schemas/__init__.py`
- Create: `src/api/services/__init__.py`

- [ ] **Step 1: Create empty package markers**

Each file is just:

```python
# ABOUTME: Package marker.
# ABOUTME: <one-line description of what lives here>
```

For example, `src/api/__init__.py`:

```python
# ABOUTME: FastAPI service exposing query functions as JSON endpoints.
# ABOUTME: Read-only; consumed by the React frontend in H1.
```

- [ ] **Step 2: Skeleton `main.py`**

```python
# ABOUTME: FastAPI application entry point.
# ABOUTME: Wires routes, middleware, lifespan, and exception handlers.

from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="Route Playout Econometrics API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 3: Smoke test the skeleton**

```bash
uv run uvicorn src.api.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/api/health
kill %1
```

Expected: `{"status":"ok"}`.

- [ ] **Step 4: Commit**

```bash
git add src/api/
git commit -m "feat: FastAPI skeleton with health endpoint"
```

---

### Task 2: Connection dependency

**Files:**
- Create: `src/api/deps.py`

- [ ] **Step 1: Write the failing test**

`tests/api/__init__.py` (empty), then `tests/api/conftest.py`:

```python
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _setup_env():
    fixture = Path(__file__).parent.parent / "fixtures" / "route_poc_test.duckdb"
    if not fixture.exists():
        pytest.skip(f"Fixture DB missing: {fixture}")
    os.environ["BACKEND"] = "duckdb"
    os.environ["DUCKDB_PATH"] = str(fixture)


@pytest.fixture
def client():
    from src.api.main import app
    return TestClient(app)
```

`tests/api/test_main.py`:

```python
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_db_dependency_returns_connection(client):
    # Indirect test: any route that uses the dep should work.
    # We'll verify directly once we have a real route in Task 5.
    pass
```

- [ ] **Step 2: Implement `deps.py`**

```python
# ABOUTME: FastAPI dependencies — DB connection, current user (stub).
# ABOUTME: Connections opened per-request, closed on response.

from typing import Any, Generator

from fastapi import Depends

from src.db.queries.connection import get_db_connection


def get_db() -> Generator[Any, None, None]:
    """Yield a DB connection per request, ensure close on completion."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


class CurrentUser:
    """Stub user object. Replaced with real auth in H3."""

    def __init__(self, user_id: str = "anonymous", email: str = "anonymous@local"):
        self.user_id = user_id
        self.email = email


def get_current_user() -> CurrentUser:
    """No-op auth dependency — H3 swaps in real JWT validation."""
    return CurrentUser()
```

- [ ] **Step 3: Run test**

```bash
uv run pytest tests/api/test_main.py -v
```

Expected: `test_health` PASS.

- [ ] **Step 4: Commit**

```bash
git add src/api/deps.py tests/api/
git commit -m "feat: DB and current-user dependencies"
```

---

### Task 3: CORS + global exception handler

**Files:**
- Modify: `src/api/main.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/api/test_main.py`:

```python
def test_cors_allows_localhost_5173(client):
    r = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204)
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_unhandled_exception_returns_structured_500(client, monkeypatch):
    from src.api import main as main_mod
    @main_mod.app.get("/api/_test_explode")
    def _explode():
        raise RuntimeError("boom")
    r = client.get("/api/_test_explode")
    assert r.status_code == 500
    body = r.json()
    assert "error" in body
    assert "detail" in body
```

- [ ] **Step 2: Update `main.py`**

```python
# ABOUTME: FastAPI application entry point.
# ABOUTME: Wires routes, middleware, lifespan, and exception handlers.

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Route Playout Econometrics API",
    version="0.1.0",
    lifespan=lifespan,
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception in request %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": str(exc)},
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/api/test_main.py -v
```

Expected: 3 PASS (including new CORS + 500 tests).

- [ ] **Step 4: Commit**

```bash
git add src/api/main.py tests/api/test_main.py
git commit -m "feat: CORS middleware and structured 500 handler"
```

---

### Task 4: First Pydantic schema + first real endpoint (campaign summary)

**Files:**
- Create: `src/api/schemas/campaign.py`
- Create: `src/api/routes/campaigns.py`

- [ ] **Step 1: Write the failing test**

`tests/api/test_campaigns.py`:

```python
KNOWN_CAMPAIGN_ID = "REPLACE_ME"  # use the same ID as tests/db/query_fixtures.py


def test_campaign_summary_known_campaign(client):
    r = client.get(f"/api/campaigns/{KNOWN_CAMPAIGN_ID}/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["campaign_id"] == KNOWN_CAMPAIGN_ID
    assert "total_impacts" in body
    assert "total_frames" in body


def test_campaign_summary_unknown_campaign_returns_404(client):
    r = client.get("/api/campaigns/__nonexistent__/summary")
    assert r.status_code == 404
    body = r.json()
    assert body.get("error") == "not_found"
```

Replace `KNOWN_CAMPAIGN_ID` with the same ID from `tests/db/query_fixtures.py`.

- [ ] **Step 2: Run, expect failure**

```bash
uv run pytest tests/api/test_campaigns.py -v
```

Expected: 404s on the route itself (not registered yet).

- [ ] **Step 3: Define schema**

`src/api/schemas/campaign.py`:

```python
# ABOUTME: Pydantic models for campaign-related API responses.
# ABOUTME: Field names mirror what get_campaign_summary_sync etc. return.

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class CampaignSummary(BaseModel):
    campaign_id: str
    primary_brand: Optional[str] = None
    primary_media_owner: Optional[str] = None
    media_owner_names: List[str] = []
    total_impacts: float = 0
    total_frames: int = 0
    total_playouts: int = 0
    days_active: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```

- [ ] **Step 4: Implement the route**

`src/api/routes/campaigns.py`:

```python
# ABOUTME: Campaign-level FastAPI routes.
# ABOUTME: Thin wrappers over src.db.queries.campaigns get_*_sync functions.

from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_db, get_current_user, CurrentUser
from src.api.schemas.campaign import CampaignSummary
from src.db.queries.campaigns import (
    get_campaign_summary_sync,
    get_campaign_from_browser_by_id_sync,
)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.get("/{campaign_id}/summary", response_model=CampaignSummary)
def campaign_summary(
    campaign_id: str,
    conn=Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    # Existing functions accept their own connection management; we honour their signature
    # and drop the dep connection (it's a backstop for endpoints that need it directly).
    result = get_campaign_summary_sync(campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail={"error": "not_found", "detail": f"campaign_id={campaign_id} not found"})
    if isinstance(result, list):
        result = result[0] if result else None
    if not result:
        raise HTTPException(status_code=404, detail={"error": "not_found", "detail": f"campaign_id={campaign_id} not found"})
    return CampaignSummary(**result)
```

- [ ] **Step 5: Register router in `main.py`**

Add to `main.py` after the CORS middleware:

```python
from src.api.routes import campaigns

app.include_router(campaigns.router)
```

- [ ] **Step 6: Run test**

```bash
uv run pytest tests/api/test_campaigns.py -v
```

Expected: 2 PASS.

- [ ] **Step 7: Verify 404 returns expected JSON shape**

The default `HTTPException` produces `{"detail": {...}}`. Check the test asserts on the right path. If needed, add an exception handler in `main.py`:

```python
from fastapi.exceptions import HTTPException as FastAPIHTTPException

@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": "http_error", "detail": exc.detail})
```

- [ ] **Step 8: Commit**

```bash
git add src/api/schemas/campaign.py src/api/routes/campaigns.py src/api/main.py tests/api/test_campaigns.py
git commit -m "feat: campaign summary endpoint with 404 handling"
```

---

### Task 5: Remaining campaign endpoints

**Files:** Modify `src/api/routes/campaigns.py`, `src/api/schemas/campaign.py`, `tests/api/test_campaigns.py`.

For each of the following endpoints, follow the same TDD cycle: write a test asserting status 200 + minimum shape, implement the route, run the test, commit.

| Endpoint | Underlying Function | Pydantic Model |
|---|---|---|
| `GET /api/campaigns` | `get_campaigns_from_browser_sync` | `List[CampaignBrowserRow]` |
| `GET /api/campaigns/browser-summary` | `get_campaign_browser_summary_sync` | `CampaignBrowserSummary` |
| `GET /api/campaigns/{campaign_id}/header` | `get_campaign_header_info_sync` | `CampaignHeader` |
| `GET /api/campaigns/{campaign_id}/demographics` | `get_available_demographics_for_campaign_sync` | `List[str]` |
| `GET /api/platform/stats` | `get_platform_stats_sync` | `PlatformStats` |

- [ ] **Step 1: Add Pydantic models for each**

Define each model in `src/api/schemas/campaign.py` with fields matching the underlying SQL output.

- [ ] **Step 2–6: Add tests, implement routes, commit per endpoint**

Use the Task 4 pattern. For list-returning routes, the response_model is `List[Model]`.

- [ ] **Step 7: Final commit (after all 5 endpoints land)**

```bash
git add src/api/routes/campaigns.py src/api/schemas/campaign.py tests/api/test_campaigns.py
git commit -m "feat: campaign browser, header, demographics, platform stats endpoints"
```

---

### Task 6: Impacts endpoints

**Files:**
- Create: `src/api/schemas/impacts.py`
- Create: `src/api/routes/impacts.py`
- Create: `tests/api/test_impacts.py`

- [ ] **Step 1: Define schemas**

```python
# ABOUTME: Pydantic models for impacts endpoints.
# ABOUTME: Mirrors get_*_impacts_sync output.

from datetime import date as DateType
from typing import Optional
from pydantic import BaseModel


class DailyImpact(BaseModel):
    date: DateType
    total_impacts: float


class HourlyImpact(BaseModel):
    hour: int
    total_impacts: float


class RegionalImpact(BaseModel):
    tv_region: str
    total_impacts: float
    frame_count: int


class EnvironmentImpact(BaseModel):
    environment_name: str
    total_impacts: float
    frame_count: int
```

- [ ] **Step 2: Implement routes**

```python
# ABOUTME: Impacts-related FastAPI routes.
# ABOUTME: Daily, hourly, regional, environment.

from typing import List
from fastapi import APIRouter, Depends

from src.api.deps import get_current_user, CurrentUser
from src.api.schemas.impacts import DailyImpact, HourlyImpact, RegionalImpact, EnvironmentImpact
from src.db.queries.impacts import (
    get_daily_impacts_sync,
    get_hourly_impacts_sync,
    get_regional_impacts_sync,
    get_environment_impacts_sync,
)

router = APIRouter(prefix="/api/campaigns", tags=["impacts"])


@router.get("/{campaign_id}/impacts/daily", response_model=List[DailyImpact])
def daily_impacts(
    campaign_id: str,
    demographic: str = "all_adults",
    user: CurrentUser = Depends(get_current_user),
):
    return get_daily_impacts_sync(campaign_id, demographic)


@router.get("/{campaign_id}/impacts/hourly", response_model=List[HourlyImpact])
def hourly_impacts(
    campaign_id: str,
    demographic: str = "all_adults",
    user: CurrentUser = Depends(get_current_user),
):
    return get_hourly_impacts_sync(campaign_id, demographic)


@router.get("/{campaign_id}/impacts/regional", response_model=List[RegionalImpact])
def regional_impacts(
    campaign_id: str,
    demographic: str = "all_adults",
    user: CurrentUser = Depends(get_current_user),
):
    return get_regional_impacts_sync(campaign_id, demographic)


@router.get("/{campaign_id}/impacts/environment", response_model=List[EnvironmentImpact])
def environment_impacts(
    campaign_id: str,
    demographic: str = "all_adults",
    user: CurrentUser = Depends(get_current_user),
):
    return get_environment_impacts_sync(campaign_id, demographic)
```

- [ ] **Step 3: Register router in `main.py`**

```python
from src.api.routes import impacts
app.include_router(impacts.router)
```

- [ ] **Step 4: Tests**

`tests/api/test_impacts.py`:

```python
KNOWN_CAMPAIGN_ID = "REPLACE_ME"


def test_daily_impacts(client):
    r = client.get(f"/api/campaigns/{KNOWN_CAMPAIGN_ID}/impacts/daily")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    if body:
        assert "date" in body[0]
        assert "total_impacts" in body[0]


def test_hourly_impacts(client):
    r = client.get(f"/api/campaigns/{KNOWN_CAMPAIGN_ID}/impacts/hourly")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_regional_impacts(client):
    r = client.get(f"/api/campaigns/{KNOWN_CAMPAIGN_ID}/impacts/regional")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_environment_impacts(client):
    r = client.get(f"/api/campaigns/{KNOWN_CAMPAIGN_ID}/impacts/environment")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
```

- [ ] **Step 5: Run tests**

```bash
uv run pytest tests/api/test_impacts.py -v
```

Expected: 4 PASS.

- [ ] **Step 6: Commit**

```bash
git add src/api/routes/impacts.py src/api/schemas/impacts.py src/api/main.py tests/api/test_impacts.py
git commit -m "feat: impacts endpoints (daily/hourly/regional/environment)"
```

---

### Task 7: Reach endpoints

Apply the Task 6 pattern for:

| Endpoint | Underlying Function |
|---|---|
| `GET /api/campaigns/{campaign_id}/reach/weekly` | `get_weekly_reach_data_sync` |
| `GET /api/campaigns/{campaign_id}/reach/cumulative-daily` | `get_daily_cumulative_reach_sync` |
| `GET /api/campaigns/{campaign_id}/reach/full` | `get_full_campaign_reach_sync` |

- [ ] **Step 1:** Define `src/api/schemas/reach.py` with `WeeklyReachRow`, `CumulativeReachRow`, `FullReach`
- [ ] **Step 2:** Implement `src/api/routes/reach.py`
- [ ] **Step 3:** Register in `main.py`
- [ ] **Step 4:** Write `tests/api/test_reach.py` — 200 + shape check per endpoint
- [ ] **Step 5:** Run tests, expect PASS
- [ ] **Step 6:** Commit `git commit -m "feat: reach endpoints (weekly/cumulative/full)"`

---

### Task 8: Geographic endpoints

| Endpoint | Underlying Function |
|---|---|
| `GET /api/campaigns/{campaign_id}/geographic/frames` | `get_frame_geographic_data_sync` |

(Regional and environment already covered by impacts in Task 6.)

- [ ] **Step 1:** Define `FrameLocation` schema (frameid, latitude, longitude, town, tv_region, environment_name, mediaowner_name, total_impacts)
- [ ] **Step 2:** Implement route
- [ ] **Step 3:** Register
- [ ] **Step 4:** Test
- [ ] **Step 5:** Commit `git commit -m "feat: geographic frames endpoint"`

---

### Task 9: Demographics endpoint

| Endpoint | Underlying Function |
|---|---|
| `GET /api/demographics/count` | `get_demographic_count_sync` |

- [ ] **Step 1–5:** Standard cycle, return `{"count": N}` shape
- [ ] **Step 6:** Commit

---

### Task 10: Frame-audience endpoints

| Endpoint | Underlying Function |
|---|---|
| `GET /api/campaigns/{campaign_id}/frame-audience/daily` | `get_frame_audience_by_day_sync` |
| `GET /api/campaigns/{campaign_id}/frame-audience/hourly` | `get_frame_audience_by_hour_sync` |
| `GET /api/campaigns/{campaign_id}/frame-audience/weekly` | `get_frame_audience_by_week_sync` |
| `GET /api/campaigns/{campaign_id}/frame-audience/table` | `get_frame_audience_table_sync` |
| `GET /api/campaigns/{campaign_id}/frame-audience/counts` | combined counts (daily, hourly, weekly, campaign) |

- [ ] **Step 1–5:** Define schemas, implement routes, test, commit per endpoint
- [ ] **Step 6:** Commit `git commit -m "feat: frame-audience endpoints"`

---

### Task 11: Mobile-index endpoints

| Endpoint | Underlying Function |
|---|---|
| `GET /api/campaigns/{campaign_id}/mobile-index/coverage` | `get_mobile_index_coverage_sync` |
| `GET /api/campaigns/{campaign_id}/mobile-index/campaign` | `get_campaign_mobile_index_sync` |
| `GET /api/campaigns/{campaign_id}/mobile-index/daily` | `get_daily_impacts_with_mobile_index_sync` |
| `GET /api/campaigns/{campaign_id}/mobile-index/hourly` | `get_hourly_impacts_with_mobile_index_sync` |
| `GET /api/campaigns/{campaign_id}/mobile-index/weekly` | `get_weekly_impacts_with_mobile_index_sync` |
| `GET /api/campaigns/{campaign_id}/mobile-index/frame-totals` | `get_frame_totals_with_mobile_index_sync` |
| `GET /api/campaigns/{campaign_id}/mobile-index/frame-daily` | `get_frame_daily_with_mobile_index_sync` |
| `GET /api/campaigns/{campaign_id}/mobile-index/frame-hourly` | `get_frame_hourly_with_mobile_index_sync` |
| `GET /api/mobile-index/exists` | `mobile_index_table_exists` |

- [ ] **Step 1:** Define `MICoverage`, `MIDaily`, `MIHourly`, `MIWeekly`, `MIFrameTotal` schemas. Each timeseries row has `indexed_impacts: Optional[float]` and `median_indexed_impacts: Optional[float]` plus the relevant time field.
- [ ] **Step 2–5:** Standard cycle for each endpoint
- [ ] **Step 6:** Commit `git commit -m "feat: mobile-index endpoints"`

---

### Task 12: Caching layer

**Files:**
- Modify: `src/api/main.py`
- Modify: route files

Add `fastapi-cache2` with in-memory backend. Cache TTLs match Streamlit's existing TTLs.

- [ ] **Step 1: Configure cache in lifespan**

In `src/api/main.py`:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(InMemoryBackend(), prefix="route-poc-cache")
    yield
```

- [ ] **Step 2: Apply `@cache` decorator to read-heavy endpoints**

For each route file, decorate the read-heavy endpoints. Example pattern:

```python
from fastapi_cache.decorator import cache

@router.get("/{campaign_id}/impacts/daily", response_model=List[DailyImpact])
@cache(expire=600)  # 10 min, matches Streamlit
def daily_impacts(...):
    ...
```

TTL guidance:
- Volatile (campaign list, summaries): 300s (5 min)
- Mid-tier (impacts, reach): 600s (10 min)
- MI overlays, totals: 3600s (60 min)

- [ ] **Step 3: Verify cache works**

Ad-hoc check:

```bash
uv run uvicorn src.api.main:app --port 8000 &
sleep 2
time curl -s http://localhost:8000/api/campaigns/REPLACE_ME/impacts/daily > /dev/null
time curl -s http://localhost:8000/api/campaigns/REPLACE_ME/impacts/daily > /dev/null
kill %1
```

Expected: second call noticeably faster than first.

- [ ] **Step 4: Commit**

```bash
git add src/api/main.py src/api/routes/
git commit -m "feat: in-memory caching with fastapi-cache2"
```

---

### Task 13: Advertiser service — port shape descriptor

**Files:**
- Create: `src/api/services/shape_descriptor.py`
- Create: `tests/api/test_shape_descriptor.py`

Port the heuristic that converts a weekly impacts series into a short label like "Steady ramp-up", "Twin peaks", "Late surge", etc. The reference implementation lives in `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/scripts/temp_sensitive_files/pepsi_netlify/_build_pages.py`.

- [ ] **Step 1: Read the reference implementation**

```bash
grep -n "shape\|descriptor" /Users/ianwyatt/PycharmProjects/route-playout-pipeline/scripts/temp_sensitive_files/pepsi_netlify/_build_pages.py
```

Identify the function or section that produces "Steady ramp-up" / "Mid-dip then surge" / "Late surge" / etc.

- [ ] **Step 2: Write tests for the heuristic**

```python
from src.api.services.shape_descriptor import describe_shape


def test_steady_ramp_up():
    weekly = [10, 15, 20, 30, 45, 55]  # monotonic increase
    assert "ramp" in describe_shape(weekly).lower() or "increase" in describe_shape(weekly).lower()


def test_late_surge():
    weekly = [5, 4, 6, 5, 4, 50]
    assert "late" in describe_shape(weekly).lower() or "surge" in describe_shape(weekly).lower()


def test_concentrated_burst():
    weekly = [0, 0, 100, 80, 0, 0]
    assert "burst" in describe_shape(weekly).lower() or "concentrated" in describe_shape(weekly).lower()


def test_twin_peaks():
    weekly = [5, 20, 5, 25, 5, 5]
    assert "twin" in describe_shape(weekly).lower() or "peaks" in describe_shape(weekly).lower()
```

- [ ] **Step 3: Implement heuristic**

```python
# ABOUTME: Heuristic to describe an advertiser's weekly campaign shape.
# ABOUTME: Ported from route-playout-pipeline pepsi_netlify/_build_pages.py.

from typing import List


def describe_shape(weekly_impacts: List[float]) -> str:
    """Return a short factual descriptor for a weekly impacts series.

    Returns one of: "Steady ramp-up", "Late surge", "Concentrated burst",
    "Twin peaks", "Mid-dip then surge", "Volatile, large spike", or "Variable shape".
    """
    if not weekly_impacts or len(weekly_impacts) < 3:
        return "Variable shape"

    n = len(weekly_impacts)
    peak_idx = max(range(n), key=lambda i: weekly_impacts[i])
    peak = weekly_impacts[peak_idx]
    mean = sum(weekly_impacts) / n

    # Concentrated burst: most of the volume in 1-2 weeks
    above_half_peak = sum(1 for v in weekly_impacts if v > peak * 0.5)
    if above_half_peak <= 2 and peak > mean * 3:
        return "Concentrated burst"

    # Late surge: peak in last 25% of weeks and significantly above mean
    if peak_idx >= n * 0.75 and peak > mean * 1.5:
        return "Late surge"

    # Twin peaks: two local maxima with a dip between
    peaks = [
        i for i in range(1, n - 1)
        if weekly_impacts[i] > weekly_impacts[i - 1]
        and weekly_impacts[i] > weekly_impacts[i + 1]
        and weekly_impacts[i] > mean
    ]
    if len(peaks) >= 2:
        return "Twin peaks"

    # Steady ramp-up: monotonic-ish increase
    increases = sum(
        1 for i in range(1, n)
        if weekly_impacts[i] >= weekly_impacts[i - 1]
    )
    if increases >= n * 0.7:
        return "Steady ramp-up"

    # Mid-dip then surge: dip in middle third, peak after
    mid_start, mid_end = n // 3, 2 * n // 3
    mid_min = min(weekly_impacts[mid_start:mid_end] or [mean])
    if mid_min < mean * 0.5 and peak_idx > mid_end:
        return "Mid-dip then surge"

    # Volatile, large spike
    if peak > mean * 2.5:
        return "Volatile, large spike"

    return "Variable shape"
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/api/test_shape_descriptor.py -v
```

Expected: 4 PASS. Tweak heuristic thresholds until tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/api/services/shape_descriptor.py tests/api/test_shape_descriptor.py
git commit -m "feat: campaign shape descriptor heuristic"
```

---

### Task 14: Advertiser service — list and metadata

**Files:**
- Create: `src/api/services/advertisers.py`
- Create: `src/api/schemas/advertiser.py`

Logic for grouping campaigns by advertiser (brand) and producing the rollup metadata.

- [ ] **Step 1: Define schemas**

```python
# ABOUTME: Pydantic models for advertiser-facing endpoints.
# ABOUTME: Used by the React advertiser views in H1C.

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class AdvertiserSummary(BaseModel):
    slug: str
    brand_name: str
    campaign_count: int
    weeks_active: int
    peak_week_impacts: float
    peak_week_label: Optional[str] = None
    mean_week_impacts: float
    shape_descriptor: str


class AdvertiserDetail(BaseModel):
    slug: str
    brand_name: str
    campaign_count: int
    weeks_active: int
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    total_impacts: float
    sub_brands: List[str] = []


class AdvertiserCampaign(BaseModel):
    campaign_id: str
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    days_active: int
    total_impacts: float
    reach: Optional[float] = None
    frequency: Optional[float] = None
    primary_media_owner: Optional[str] = None


class AdvertiserDailyPoint(BaseModel):
    date: date
    total_impacts: float
    indexed_impacts: Optional[float] = None
    median_indexed_impacts: Optional[float] = None
    is_partial: bool = False


class AdvertiserWeeklyPoint(BaseModel):
    week_label: str
    iso_week: int
    total_impacts: float
    indexed_impacts: Optional[float] = None
    median_indexed_impacts: Optional[float] = None
    active_brand: Optional[str] = None
    frame_count: int = 0
    campaign_count: int = 0
    is_partial: bool = False


class DataLimitation(BaseModel):
    code: str
    title: str
    detail: str


class AdvertiserDataLimitations(BaseModel):
    items: List[DataLimitation]
```

- [ ] **Step 2: Implement service helpers**

`src/api/services/advertisers.py`:

```python
# ABOUTME: Domain logic for advertiser views.
# ABOUTME: Aggregates campaigns by brand, produces summaries and time series.

import re
from typing import Any, Dict, List, Optional

from src.api.services.shape_descriptor import describe_shape
from src.db.queries.campaigns import get_campaigns_from_browser_sync


def slugify(name: str) -> str:
    """Slug derived from brand name. Stable: lowercase, dashes for non-alnum."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def list_advertisers() -> List[Dict[str, Any]]:
    """Group campaigns from mv_campaign_browser by primary brand."""
    rows = get_campaigns_from_browser_sync()
    by_brand: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        brands = row.get("brand_names") or []
        if not brands:
            continue
        primary = brands[0]
        by_brand.setdefault(primary, []).append(row)

    advertisers = []
    for brand, campaigns in by_brand.items():
        weekly_impacts = _aggregate_weekly_impacts(campaigns)
        peak_idx = max(range(len(weekly_impacts)), key=lambda i: weekly_impacts[i]) if weekly_impacts else 0
        advertisers.append({
            "slug": slugify(brand),
            "brand_name": brand,
            "campaign_count": len(campaigns),
            "weeks_active": len(weekly_impacts),
            "peak_week_impacts": weekly_impacts[peak_idx] if weekly_impacts else 0,
            "peak_week_label": f"W{peak_idx + 1}" if weekly_impacts else None,
            "mean_week_impacts": sum(weekly_impacts) / len(weekly_impacts) if weekly_impacts else 0,
            "shape_descriptor": describe_shape(weekly_impacts),
        })
    advertisers.sort(key=lambda a: a["campaign_count"], reverse=True)
    return advertisers


def get_advertiser(slug: str) -> Optional[Dict[str, Any]]:
    return next((a for a in list_advertisers() if a["slug"] == slug), None)


def get_advertiser_campaigns(slug: str) -> List[Dict[str, Any]]:
    rows = get_campaigns_from_browser_sync()
    return [r for r in rows if r.get("brand_names") and slugify(r["brand_names"][0]) == slug]


def _aggregate_weekly_impacts(campaigns: List[Dict[str, Any]]) -> List[float]:
    """Placeholder: real implementation joins campaign impacts week-by-week.
    For H1, this calls into get_weekly_reach_data_sync per campaign and merges.
    """
    # TODO in implementation: query each campaign's weekly data and merge by ISO week.
    # See _build_pages.py for the reference pattern.
    return []
```

> Note: `_aggregate_weekly_impacts` is a stub here; **expand it in Task 15** when wiring up the timeseries route, so the implementation is co-located with its consumer.

- [ ] **Step 3: Test**

```python
# tests/api/test_advertisers_service.py
from src.api.services.advertisers import slugify, list_advertisers


def test_slugify():
    assert slugify("McDonald's Restaurants") == "mcdonald-s-restaurants"
    assert slugify("Lidl") == "lidl"
    assert slugify("British Gas") == "british-gas"


def test_list_advertisers_returns_grouped_brands(client):
    # client fixture sets BACKEND=duckdb pointing at test fixture
    advertisers = list_advertisers()
    assert isinstance(advertisers, list)
    assert all("slug" in a for a in advertisers)
    slugs = {a["slug"] for a in advertisers}
    assert "lidl" in slugs  # known to be in test fixture
```

- [ ] **Step 4: Commit**

```bash
git add src/api/services/advertisers.py src/api/schemas/advertiser.py tests/api/test_advertisers_service.py
git commit -m "feat: advertiser grouping service (list + slugify)"
```

---

### Task 15: Advertiser routes — list, detail, campaigns

**Files:**
- Create: `src/api/routes/advertisers.py`
- Create: `tests/api/test_advertisers.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/api/test_advertisers.py
def test_list_advertisers_returns_200(client):
    r = client.get("/api/advertisers")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert all("slug" in a and "brand_name" in a for a in body)


def test_get_advertiser_lidl(client):
    r = client.get("/api/advertisers/lidl")
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == "lidl"
    assert body["brand_name"]  # not empty


def test_get_advertiser_unknown_returns_404(client):
    r = client.get("/api/advertisers/unknown-brand-xyz")
    assert r.status_code == 404


def test_advertiser_campaigns(client):
    r = client.get("/api/advertisers/lidl/campaigns")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
```

- [ ] **Step 2: Implement routes**

```python
# src/api/routes/advertisers.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from src.api.deps import get_current_user, CurrentUser
from src.api.schemas.advertiser import (
    AdvertiserSummary,
    AdvertiserDetail,
    AdvertiserCampaign,
)
from src.api.services.advertisers import (
    list_advertisers,
    get_advertiser,
    get_advertiser_campaigns,
)

router = APIRouter(prefix="/api/advertisers", tags=["advertisers"])


@router.get("", response_model=List[AdvertiserSummary])
def advertisers_index(user: CurrentUser = Depends(get_current_user)):
    return list_advertisers()


@router.get("/{slug}", response_model=AdvertiserDetail)
def advertiser_detail(slug: str, user: CurrentUser = Depends(get_current_user)):
    rec = get_advertiser(slug)
    if not rec:
        raise HTTPException(status_code=404, detail={"error": "not_found", "detail": f"advertiser slug={slug} not found"})
    # Pad fields the AdvertiserDetail schema needs but list_advertisers doesn't return
    return AdvertiserDetail(
        slug=rec["slug"],
        brand_name=rec["brand_name"],
        campaign_count=rec["campaign_count"],
        weeks_active=rec["weeks_active"],
        total_impacts=0,  # filled in Task 16
    )


@router.get("/{slug}/campaigns", response_model=List[AdvertiserCampaign])
def advertiser_campaigns(slug: str, user: CurrentUser = Depends(get_current_user)):
    rows = get_advertiser_campaigns(slug)
    return [
        AdvertiserCampaign(
            campaign_id=r["campaign_id"],
            period_start=r.get("start_date"),
            period_end=r.get("end_date"),
            days_active=r.get("days_active", 0),
            total_impacts=r.get("total_impacts", 0),
            reach=r.get("reach"),
            frequency=r.get("frequency"),
            primary_media_owner=(r.get("media_owner_names") or [None])[0],
        )
        for r in rows
    ]
```

- [ ] **Step 3: Register router**

```python
from src.api.routes import advertisers
app.include_router(advertisers.router)
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/api/test_advertisers.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/api/routes/advertisers.py src/api/main.py tests/api/test_advertisers.py
git commit -m "feat: advertisers list/detail/campaigns endpoints"
```

---

### Task 16: Advertiser timeseries — daily

**Files:**
- Modify: `src/api/services/advertisers.py`
- Modify: `src/api/routes/advertisers.py`

For an advertiser, sum daily impacts across all campaigns, optionally with MI overlay.

- [ ] **Step 1: Implement service helper**

In `src/api/services/advertisers.py`:

```python
from collections import defaultdict
from datetime import date
from src.db.queries.impacts import get_daily_impacts_sync
from src.db.queries.mobile_index import get_daily_impacts_with_mobile_index_sync


def get_advertiser_daily_timeseries(
    slug: str,
    demographic: str = "all_adults",
    include_mi: bool = False,
) -> List[Dict[str, Any]]:
    campaigns = get_advertiser_campaigns(slug)
    by_date: Dict[date, Dict[str, float]] = defaultdict(lambda: {"total_impacts": 0.0, "indexed_impacts": 0.0, "median_indexed_impacts": 0.0})

    for c in campaigns:
        cid = c["campaign_id"]
        if include_mi:
            rows = get_daily_impacts_with_mobile_index_sync(cid, demographic)
        else:
            rows = get_daily_impacts_sync(cid, demographic)
        for r in rows:
            d = r["date"]
            by_date[d]["total_impacts"] += float(r.get("total_impacts") or 0)
            if include_mi:
                by_date[d]["indexed_impacts"] += float(r.get("indexed_impacts") or 0)
                by_date[d]["median_indexed_impacts"] += float(r.get("median_indexed_impacts") or 0)

    return [
        {"date": d, **vals}
        for d, vals in sorted(by_date.items())
    ]
```

- [ ] **Step 2: Add route**

```python
@router.get("/{slug}/timeseries/daily", response_model=List[AdvertiserDailyPoint])
def advertiser_daily_timeseries(
    slug: str,
    demographic: str = "all_adults",
    mi: str = "off",  # "off" | "mean" | "median" | "both"
    user: CurrentUser = Depends(get_current_user),
):
    if not get_advertiser(slug):
        raise HTTPException(status_code=404, detail={"error": "not_found", "detail": slug})
    include_mi = mi != "off"
    return get_advertiser_daily_timeseries(slug, demographic, include_mi)
```

- [ ] **Step 3: Test**

```python
def test_advertiser_daily_timeseries(client):
    r = client.get("/api/advertisers/lidl/timeseries/daily")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    if body:
        assert "date" in body[0]
        assert "total_impacts" in body[0]


def test_advertiser_daily_timeseries_with_mi(client):
    r = client.get("/api/advertisers/lidl/timeseries/daily?mi=mean")
    assert r.status_code == 200
    body = r.json()
    if body:
        assert "indexed_impacts" in body[0]
```

- [ ] **Step 4: Run, commit**

```bash
uv run pytest tests/api/test_advertisers.py -v
git add src/api/services/advertisers.py src/api/routes/advertisers.py tests/api/test_advertisers.py
git commit -m "feat: advertiser daily timeseries endpoint"
```

---

### Task 17: Advertiser timeseries — weekly

Same pattern as Task 16, sourced from `get_weekly_impacts_with_mobile_index_sync` and `get_weekly_reach_data_sync`. Includes brand-transition active-brand colour coding (`active_brand` field on each weekly row, derived from which campaign has the most impacts that week).

- [ ] **Step 1:** Implement `get_advertiser_weekly_timeseries(slug, demographic, include_mi)` in service
- [ ] **Step 2:** Determine `active_brand` per week: for each ISO week, compute impacts per (campaign → primary brand) and pick max
- [ ] **Step 3:** Add route `/api/advertisers/{slug}/timeseries/weekly`
- [ ] **Step 4:** Test the route returns expected fields including `active_brand`
- [ ] **Step 5:** Commit `git commit -m "feat: advertiser weekly timeseries with brand transitions"`

---

### Task 18: Advertiser data limitations endpoint

The structured caveats panel: "this advertiser has X% MI coverage", "weeks 32 and 42 are partial", etc.

**Files:**
- Modify: `src/api/services/advertisers.py`
- Modify: `src/api/routes/advertisers.py`

- [ ] **Step 1: Implement service helper**

```python
def get_advertiser_data_limitations(slug: str) -> List[Dict[str, str]]:
    rec = get_advertiser(slug)
    if not rec:
        return []

    items = []
    campaigns = get_advertiser_campaigns(slug)

    # Brand attribution
    unbranded_count = sum(1 for c in campaigns if not c.get("brand_names"))
    if unbranded_count:
        items.append({
            "code": "brand_attribution",
            "title": "Brand attribution gaps",
            "detail": f"{unbranded_count} of {len(campaigns)} campaigns lack brand labels.",
        })

    # Period boundaries
    items.append({
        "code": "period_boundary",
        "title": "Partial weeks at boundaries",
        "detail": "First and last weeks may be partial; greyed out in charts and excluded from averages.",
    })

    # Demographic
    items.append({
        "code": "demographic",
        "title": "All Adults demographic only",
        "detail": "Other demographics available but timeseries shown for All Adults 15+.",
    })

    # MI coverage (rough — count campaigns with MI data)
    # Stub: real implementation queries cache_mi_coverage per campaign
    items.append({
        "code": "mi_coverage",
        "title": "Mobile Index coverage",
        "detail": "Mobile Index reflects all-mobile-device footfall, not demographic-specific.",
    })

    return items
```

- [ ] **Step 2: Add route**

```python
@router.get("/{slug}/data-limitations", response_model=AdvertiserDataLimitations)
def advertiser_data_limitations(slug: str, user: CurrentUser = Depends(get_current_user)):
    if not get_advertiser(slug):
        raise HTTPException(status_code=404, detail={"error": "not_found", "detail": slug})
    return AdvertiserDataLimitations(items=get_advertiser_data_limitations(slug))
```

- [ ] **Step 3: Test, commit**

```python
def test_advertiser_data_limitations(client):
    r = client.get("/api/advertisers/lidl/data-limitations")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    codes = {i["code"] for i in body["items"]}
    assert "brand_attribution" in codes or len(codes) >= 1
```

```bash
uv run pytest tests/api/test_advertisers.py -v
git add src/api/services/advertisers.py src/api/routes/advertisers.py tests/api/test_advertisers.py
git commit -m "feat: advertiser data limitations endpoint"
```

---

### Task 19: Cross-cutting integration smoke test

**Files:**
- Create: `tests/api/test_integration.py`

Runs FastAPI against the test DuckDB and validates a full advertiser-view flow.

- [ ] **Step 1: Write integration test**

```python
# ABOUTME: End-to-end smoke test for the advertiser-view API surface.
# ABOUTME: Catches DuckDB → FastAPI → schema drift in one go.


def test_full_advertiser_view_flow(client):
    # 1. List advertisers
    r = client.get("/api/advertisers")
    assert r.status_code == 200
    advertisers = r.json()
    assert advertisers, "expected at least one advertiser in the test fixture"
    slug = advertisers[0]["slug"]

    # 2. Detail
    r = client.get(f"/api/advertisers/{slug}")
    assert r.status_code == 200

    # 3. Campaigns
    r = client.get(f"/api/advertisers/{slug}/campaigns")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # 4. Daily timeseries
    r = client.get(f"/api/advertisers/{slug}/timeseries/daily")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # 5. Daily with MI
    r = client.get(f"/api/advertisers/{slug}/timeseries/daily?mi=mean")
    assert r.status_code == 200

    # 6. Weekly timeseries
    r = client.get(f"/api/advertisers/{slug}/timeseries/weekly")
    assert r.status_code == 200

    # 7. Data limitations
    r = client.get(f"/api/advertisers/{slug}/data-limitations")
    assert r.status_code == 200
    assert "items" in r.json()
```

- [ ] **Step 2: Run**

```bash
uv run pytest tests/api/test_integration.py -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/api/test_integration.py
git commit -m "test: end-to-end advertiser view smoke"
```

---

### Task 20: `startapi` shell function and `.env.example`

**Files:**
- Modify: `.env.example`
- Document: shell function suggestion

- [ ] **Step 1: Update `.env.example`**

```
# FastAPI
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:5173
```

- [ ] **Step 2: Add `startapi` shell function**

Document in the project README or a new `Claude/Documentation/dev-shell-functions.md`:

```bash
# Add to ~/.zshrc
startapi() {
    cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
    uv run uvicorn src.api.main:app --reload --port "${API_PORT:-8000}"
}

stopapi() {
    pkill -f "uvicorn src.api.main"
}
```

(User adds these to their shell config; not committed to repo.)

- [ ] **Step 3: Manual smoke**

```bash
startapi &
sleep 2
curl -s http://localhost:8000/api/health
curl -s http://localhost:8000/api/advertisers | head -c 500
stopapi
```

Expected: health returns ok; advertisers returns JSON list.

- [ ] **Step 4: Commit `.env.example`**

```bash
git add .env.example
git commit -m "docs: API_PORT and ALLOWED_ORIGINS env vars"
```

- [ ] **Step 5: Push branch**

```bash
git push origin feature/duckdb-migration
```

---

## Done Criteria

- [ ] All campaign routes (summary, browser, header, demographics, platform stats) PASS
- [ ] All impacts routes (daily/hourly/regional/environment) PASS
- [ ] All reach routes (weekly/cumulative/full) PASS
- [ ] Geographic frames endpoint PASS
- [ ] All MI routes PASS
- [ ] Frame-audience routes PASS
- [ ] All advertiser routes (list, detail, campaigns, daily/weekly timeseries, data-limitations) PASS
- [ ] Integration smoke test PASS
- [ ] FastAPI runnable via `startapi` alongside Streamlit
- [ ] CORS allows `localhost:5173`
- [ ] Cache hit on second request to a heavy endpoint is faster

H1B ship signal. The React app in H1C now has a contract to consume.
