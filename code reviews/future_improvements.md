# Future Improvements

Findings from Codex code review (round 6, 4 Feb 2026) and agent-based review (5 Feb 2026) that were assessed and deliberately deferred. These are acceptable for a POC but worth addressing if the project grows beyond its current scope.

---

## Acceptable for POC — Address If Scaling

### Connection Pooling
- **File**: `src/db/queries/connection.py`
- **Issue**: Each query opens a new psycopg2 connection. No pooling.
- **Why it's fine**: 1-5 concurrent users, queries complete in <100ms. Pooling matters at 100+ connections.
- **When to fix**: If deploying for multiple teams or >10 concurrent users.

### Test Coverage
- **Files**: `tests/`
- **Issue**: Tests cover only `formatters.py` and `validators.py`. No tests for query modules, UI components, or exports.
- **Why it's fine**: Query modules are thin SQL wrappers — testing them means testing PostgreSQL, not application logic. UI is Streamlit rendering.
- **When to fix**: When modifying query logic or adding business rules.

### mypy Strict Mode vs Reality
- **File**: `pyproject.toml` line 69
- **Issue**: `disallow_untyped_defs = true` but many Streamlit UI functions omit return types.
- **Why it's fine**: Aspirational config. Doesn't affect runtime. Streamlit functions mostly return None (they render UI).
- **When to fix**: Either add type annotations to UI functions or relax mypy config for `src/ui/`.

### Time-Series Query Caching
- **File**: `src/ui/tabs/time_series.py`
- **Issue**: Daily/hourly queries run on every Streamlit rerun.
- **Why it's fine**: Queries are fast (<100ms) and Streamlit has its own caching layer.
- **When to fix**: If users report slow tab switches or if campaign datasets grow significantly.

### In-App Authorisation
- **File**: `src/ui/utils/export_dialog.py`
- **Issue**: Any user with app access can export full campaign datasets.
- **Why it's fine by design**: Authentication and authorisation are handled externally via PocketID (passkey-only) and Caddy reverse proxy with GB geo-blocking. The app itself is behind network-level access control. The data (OOH audience impacts) is not sensitive personal data.
- **When to fix**: If the app needs role-based access or serves different permission levels.

---

*Last Updated: 5 February 2026*
