# API Archive

Archived API code from the Route Playout Econometrics POC, removed during the handover cleanup (February 2026). This code was part of the API fallback path that allowed the app to call Route and SPACE APIs directly. In practice, the app operates cache-only — all data is served from PostgreSQL materialised views populated by the `route-playout-pipeline` repo.

## Files

### `api/` — Route and SPACE API Clients

| File | Purpose |
|------|---------|
| `__init__.py` | Package init (empty) |
| `base_client.py` | Abstract base class for API clients with retry logic and TTL caching |
| `route_client.py` | Route API client — playout audience endpoint, frame validation, batch requests |
| `space_client.py` | SPACE API client — entity lookups (media owners, buyers, agencies, brands, frames) |
| `campaign_service.py` | Campaign service — orchestrates Route + SPACE APIs for full campaign queries |
| `playout_processor.py` | Playout processor — groups frames into 15-minute windows, calls Route API in batches |
| `route_release_service.py` | Route release service — determines which Route release applies for a given date |
| `api_fallback_handler.py` | Placeholder circuit breaker/fallback handler (never integrated) |
| `archive/campaign_service_optimized.py` | Earlier performance-focused implementation (superseded by campaign_service.py) |

### Dependency Chain

```
campaign_service.py
├── route_client.py → base_client.py
├── space_client.py → base_client.py
└── playout_processor.py → route_client.py
```

### Service Layer

| File | Purpose |
|------|---------|
| `reach_service.py` | Async reach calculation service — cached reach/GRP/frequency via Route API |

### Data Processing

| File | Purpose |
|------|---------|
| `data_processor.py` | Playout data processing and transformation utilities |
| `econometric_processor.py` | Econometric calculations (imports data_processor) |

## Why Archived

The POC evolved to a cache-first architecture where the `route-playout-pipeline` (separate repo) handles all API calls, data processing, and cache population. The Pharos UI reads exclusively from PostgreSQL. These API modules were retained for potential future use but had become dead code in the UI application.
