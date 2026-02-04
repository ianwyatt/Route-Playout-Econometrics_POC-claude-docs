# Database Naming Refactor: MS01 → Primary/Secondary

**Completed**: 4 February 2026
**Spans**: Two sessions (2 Feb core refactor, 4 Feb completion)

---

## Motivation

The codebase originally referred to the production database server by its hostname "MS-01" (a ZimaCube NAS). Variable names, function names, class names, and documentation all used `ms01` or `MS-01` terminology. This created several problems:

- **Tight coupling to infrastructure**: Code referenced a specific machine rather than a logical role
- **Confusing for new contributors**: "MS01" is meaningless without knowing the hardware setup
- **Inflexible for deployment**: Moving to cloud hosting (DigitalOcean, Google Cloud SQL) would leave misleading names everywhere

The refactor renames everything to use generic `primary`/`secondary` terminology that describes the database's _role_ rather than its _location_.

---

## Scope of Changes

### Session 1 (2 February 2026) — Core Refactor

| Area | Files | Status |
|------|-------|--------|
| `src/config.py` | Environment variable fallback chains | Complete |
| `src/db/db_helpers.py` | Canonical implementation + legacy aliases | Complete |
| `src/db/queries/connection.py` | Fallback chains | Complete |
| `src/db/__init__.py` | Exports legacy aliases | Complete |
| All `src/ui/` files | `use_primary` params, env var fallbacks | Complete |
| All `src/api/`, `src/services/` | Updated references | Complete |
| All `docs/` (code repo) | Documentation updates | Complete |
| `migrations/README.md` | Updated references | Complete |
| `.env.example` | New variable names with comments | Complete |

### Session 2 (4 February 2026) — Completion

| Area | Files | Status |
|------|-------|--------|
| `src/db/ms01_helpers.py` | Converted to re-export shim | Complete |
| `skills/` Python scripts | Renamed + updated imports | Complete |
| `skills/` documentation | ~75 references updated | Complete |
| `scripts/` | Updated imports + fallback chains | Complete |
| `src/paths.py` | Path constant rename | Complete |
| `tests/test_db_selector.py` | Comment update | Complete |
| Docs repo `CLAUDE.md` | Updated examples and labels | Complete |
| Docs repo `SKILL.md` | Updated script paths | Complete |

---

## Backwards Compatibility Design

The refactor is designed so that **nothing breaks**. All old code, scripts, `.env` files, and import paths continue to work.

### Layer 1: Environment Variable Fallback Chains

In `src/config.py`, the `_env_with_fallback()` helper tries the new name first, then falls back to the old:

```python
def _env_with_fallback(primary_key: str, fallback_key: str, default: str = '') -> str:
    """Read env var with fallback to legacy name."""
    return os.getenv(primary_key) or os.getenv(fallback_key) or default
```

Usage throughout config:
```python
host = _env_with_fallback('POSTGRES_HOST_PRIMARY', 'POSTGRES_HOST_MS01')
port = int(_env_with_fallback('POSTGRES_PORT_PRIMARY', 'POSTGRES_PORT_MS01', '5432'))
use_primary = _env_with_fallback('USE_PRIMARY_DATABASE', 'USE_MS01_DATABASE', 'true')
```

**Effect**: `.env` files with either naming convention work. No migration required.

### Layer 2: Module Re-export Shim

`src/db/ms01_helpers.py` was a 742-line standalone module that duplicated all logic from `db_helpers.py`. It's now a thin shim:

```python
from src.db.db_helpers import (
    DatabaseConnection as MS01DatabaseConnection,
    initialize_database as initialize_ms01_database,
    close_database as close_ms01_database,
    # ... all query functions
)
```

**Effect**: `from src.db.ms01_helpers import MS01DatabaseConnection` still works.

### Layer 3: In-module Aliases

At the bottom of `src/db/db_helpers.py`:

```python
MS01DatabaseConnection = DatabaseConnection
initialize_ms01_database = initialize_database
close_ms01_database = close_database
```

These are also exported from `src/db/__init__.py`.

**Effect**: `from src.db import MS01DatabaseConnection` still works.

### Deprecation Strategy

No hard deprecation timeline is set. The backwards-compatible layers add minimal overhead (just Python name bindings). They can be removed when:

1. All `.env` files across all environments have been updated to new names
2. The `~/.zshrc` shell function has been updated
3. Any external scripts or tools referencing old names have been updated

---

## Environment Variable Mapping

| New Name | Legacy Name | Default |
|----------|-------------|---------|
| `USE_PRIMARY_DATABASE` | `USE_MS01_DATABASE` | `true` |
| `POSTGRES_HOST_PRIMARY` | `POSTGRES_HOST_MS01` | — |
| `POSTGRES_PORT_PRIMARY` | `POSTGRES_PORT_MS01` | `5432` |
| `POSTGRES_DATABASE_PRIMARY` | `POSTGRES_DATABASE_MS01` | `route_poc` |
| `POSTGRES_USER_PRIMARY` | `POSTGRES_USER_MS01` | `postgres` |
| `POSTGRES_PASSWORD_PRIMARY` | `POSTGRES_PASSWORD_MS01` | — |

Secondary database variables follow the same pattern with `_SECONDARY`/`_LOCAL` suffixes.

---

## Symbol Mapping

| New Name | Legacy Name | Location |
|----------|-------------|----------|
| `DatabaseConnection` | `MS01DatabaseConnection` | `src/db/db_helpers.py` |
| `initialize_database` | `initialize_ms01_database` | `src/db/db_helpers.py` |
| `close_database` | `close_ms01_database` | `src/db/db_helpers.py` |
| `DatabaseQueryTool` | `MS01QueryTool` | `skills/database/query_database.py` |
| `query_database.py` | `query_ms01.py` | `skills/database/` |
| `db_helpers_example.py` | `ms01_helpers_example.py` | `scripts/examples/` |
| `CLAUDE_MIGRATION_DIR` | (pointed to `MS01_Migration_Plan`) | `src/paths.py` → now `Database_Migration_Plan` |

---

## Known Remaining Legacy References

These are intentional and serve backwards compatibility:

| Location | Reference | Purpose |
|----------|-----------|---------|
| `src/config.py` | `POSTGRES_HOST_MS01` etc. | Fallback chain targets |
| `src/db/db_helpers.py` | `MS01DatabaseConnection` etc. | Legacy aliases |
| `src/db/ms01_helpers.py` | Entire file | Re-export shim |
| `src/db/__init__.py` | `MS01DatabaseConnection` etc. | Legacy exports |
| `scripts/export_demo_database.sh` | `--host ms01.local` | Actual hostname in CLI example |
| `~/.zshrc` `startstream` | `USE_MS01_DATABASE` | User's shell function (works via fallback) |
| `docs/MS01_Migration_Plan/` | Directory name | Docs repo historical content |

---

## Verification

### Automated
- Unit tests: 112 passed (2 pre-existing failures unrelated to refactor)
- `grep -ri "ms01\|MS-01" src/ skills/ scripts/ tests/ docs/` — all hits are in backwards-compat code

### Manual (recommended before removing compat layers)
- Start app with old `.env` variables → should work
- Start app with new `.env` variables → should work
- Run `startstream` shell function → should work (uses old env var via fallback)
