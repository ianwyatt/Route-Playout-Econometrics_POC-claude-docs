# Code Review – Round 6 (Active Codebase)

Date: 2026-02-04

## Summary
- Overall score: 7.8/10
- Top 3 critical findings: None
- Top 3 strengths: Consistent `use_primary` threading; centralized formatting utilities; parameterized SQL with a clean query facade

## Detailed Findings

**[MEDIUM] Code Quality > Broad exception swallows rendering errors**
- File: `src/ui/tabs/overview.py:286-287`
- Issue: `_render_campaign_shape()` catches `Exception` and silently passes, which hides data or plotting errors and makes debugging harder.
- Fix: Log the exception and show a non-blocking warning in the UI.

**[LOW] Code Quality > Unused runtime dependencies**
- File: `pyproject.toml:7-12`
- Issue: `fastapi`, `uvicorn`, and `sqlalchemy` are listed as runtime dependencies but are not referenced in `src/`.
- Fix: Remove unused deps or document why they are required.

**[MEDIUM] Documentation > `analyze_campaign()` referenced but not present**
- File: `docs/01-architecture.md:86`
- Issue: Data flow references `analyze_campaign()` which does not exist in the codebase.
- Fix: Update the flow to reflect the current campaign selection + session_state path.

**[MEDIUM] Documentation > UI guide references non-existent `analyze_campaign()`**
- File: `docs/02-ui-guide.md:17`
- Issue: The UI guide states `analyze_campaign()` drives DB queries, but this function is not in the codebase.
- Fix: Replace with the actual control flow in `app.py` / campaign selector.

**[MEDIUM] Documentation > “No tab re-queries the database” is inaccurate**
- File: `docs/02-ui-guide.md:80`
- Issue: Multiple tabs call `streamlit_queries` on demand; they do re-query (with caching), not exclusively via session state.
- Fix: Clarify that tabs query via cached loaders when needed.

**[LOW] Documentation > README dev instructions mention Ruff but config is absent**
- File: `README.md:110-113`
- Issue: README recommends `ruff`, but there is no Ruff config in `pyproject.toml`.
- Fix: Remove Ruff from README or add Ruff config.

**[MEDIUM] Tests > Coverage limited to validators + formatters**
- File: `tests/README.md:10-26`
- Issue: No tests cover `db/queries`, UI components/tabs, or export pipelines.
- Fix: Add at least smoke tests for query modules and a small export integration test.

**[MEDIUM] Linting & Style > mypy strict but many defs are untyped**
- File: `src/ui/tabs/overview.py:14`
- Issue: `tool.mypy` sets `disallow_untyped_defs=true`, but many UI functions omit return types.
- Fix: Add return type annotations or relax the mypy setting for UI modules.

**[MEDIUM] Security > No in-app authorization for exports**
- File: `src/ui/utils/export_dialog.py:9-28`
- Issue: Any user with app access can export full campaign datasets. Access control is external only.
- Fix: Document the deployment expectation or add a simple auth gate if needed.

**[MEDIUM] Performance > No connection pooling for sync queries**
- File: `src/db/queries/connection.py:11-45`
- Issue: Each query opens a new psycopg2 connection; repeated queries can be slow under load.
- Fix: Introduce a connection pool or cache a connection per Streamlit session.

**[LOW] Performance > Time-series queries not cached**
- File: `src/ui/tabs/time_series.py:82-90`
- Issue: Daily/hourly queries run on every rerun; can be expensive for larger campaigns.
- Fix: Wrap data fetches in `@st.cache_data` keyed by `(campaign_id, demographic, use_primary)`.

## Recommendations

**Quick wins**
1. Update docs to remove `analyze_campaign()` references and clarify DB access patterns.
2. Add `use_primary` caching for time-series queries.
3. Add logging (or UI warning) in `_render_campaign_shape` exception handler.

**Larger refactors**
1. Introduce pooled DB connections for sync queries.
2. Add a minimal integration test suite for db queries and exports.
3. Decide whether to enforce strict typing in UI modules or relax mypy for UI.
