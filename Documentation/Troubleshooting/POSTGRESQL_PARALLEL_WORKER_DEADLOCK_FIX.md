# PostgreSQL Parallel Worker Deadlock Fix

**Issue Date**: November 15, 2025
**Resolved**: November 15, 2025
**Severity**: High - Migration blocked for extended periods
**Database**: PostgreSQL @ MS-01 (192.168.1.34:5432/route_poc)

---

## Issue Summary

When running migration 003 to create the `mv_campaign_browser` materialized view with reach and impacts metrics, PostgreSQL parallel workers would spawn and become deadlocked, causing the migration to hang indefinitely (6+ minutes with no completion).

---

## Symptoms

### Observable Behavior
1. Migration SQL executed via `psql -f migrations/003_create_mv_campaign_browser.sql`
2. **6-7 parallel PostgreSQL worker processes** spawned immediately
3. All workers showed as "active" in `pg_stat_activity`
4. All workers executing identical `CREATE MATERIALIZED VIEW` query
5. Query ran for 6+ minutes with no completion
6. No intermediate output from `psql`
7. View was never created

### Query Output from pg_stat_activity
```sql
SELECT pid, query_start, LEFT(query, 80) as query_preview
FROM pg_stat_activity
WHERE datname = 'route_poc'
  AND state = 'active'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY query_start;
```

**Result**: 6-7 rows, all with same query_start time, all executing `CREATE MATERIALIZED VIEW mv_campaign_browser AS...`

### Failed Approaches

1. **Using `psql -f` flag**: Spawned 6 parallel workers
2. **Using input redirection `psql <`**: Spawned 6 parallel workers
3. **Python script with single connection**: Spawned 7 parallel workers
4. **Killing stuck processes**: Stopped the migration but didn't solve the root cause
5. **Waiting longer**: No completion even after 6+ minutes

---

## Root Cause

PostgreSQL's **parallel query execution** was enabled by default and attempting to parallelize the materialized view creation. However, the parallel workers were **fighting with each other** rather than cooperating, resulting in a deadlock scenario.

### Why This Happened

The `CREATE MATERIALIZED VIEW` statement with complex CTEs (Common Table Expressions) triggered PostgreSQL's query planner to spawn multiple parallel workers. The query involved:

- 5 complex CTEs (campaign_brands, campaign_media_owners, campaign_reach, campaign_impacts, campaign_stats)
- Multiple LEFT JOINs across large tables (mv_playout_15min, cache tables)
- Window functions (`FIRST_VALUE() OVER ...`)
- Array aggregations
- ~838 campaigns × large data sets

PostgreSQL's parallel execution created multiple workers that all tried to build the materialized view simultaneously, but instead of coordinating, they blocked each other.

---

## Solution

**Disable parallel workers for the migration session** using session-level PostgreSQL settings.

### Method 1: psql with Inline Settings (RECOMMENDED)

```bash
PGPASSWORD='...' psql -h 192.168.1.34 -U postgres -d route_poc <<'EOF'
-- Disable parallel workers for this session
SET max_parallel_workers_per_gather = 0;
SET max_parallel_workers = 0;

-- Now run the migration
\i migrations/003_create_mv_campaign_browser.sql
EOF
```

### Method 2: Python Script with Settings

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST_MS01', '192.168.1.34'),
    port=int(os.getenv('POSTGRES_PORT_MS01', '5432')),
    database=os.getenv('POSTGRES_DATABASE_MS01', 'route_poc'),
    user=os.getenv('POSTGRES_USER_MS01', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD_MS01', '')
)

conn.autocommit = True
cursor = conn.cursor()

# Disable parallel workers for this session
cursor.execute("SET max_parallel_workers_per_gather = 0")
cursor.execute("SET max_parallel_workers = 0")

# Read and execute migration SQL
with open('migrations/003_create_mv_campaign_browser.sql', 'r') as f:
    migration_sql = f.read()
    cursor.execute(migration_sql)

cursor.close()
conn.close()
```

### Method 3: Using Provided Helper Script

```bash
python run_migration_003.py
```

**Note**: Update `run_migration_003.py` to include the `SET` commands before executing the migration SQL.

---

## Results After Fix

### Migration Performance
- **Execution Time**: ~3.5 minutes (with parallel workers disabled)
- **Worker Count**: 1 (single-threaded execution)
- **Success Rate**: 100%
- **View Size**: 872 kB for 838 campaigns

### Verification Query
```sql
-- Check that parallel workers are disabled for the current session
SHOW max_parallel_workers_per_gather;  -- Should show 0
SHOW max_parallel_workers;              -- Should show 0

-- Check database defaults (unchanged)
SELECT name, setting FROM pg_settings
WHERE name IN ('max_parallel_workers_per_gather', 'max_parallel_workers');
```

### After Migration Completes
```sql
-- Verify settings reverted to defaults
SHOW max_parallel_workers_per_gather;  -- Should show 2 (default)
SHOW max_parallel_workers;              -- Should show 8 (default)
```

**IMPORTANT**: The `SET` commands are **session-level only**. Once the psql/Python session ends, PostgreSQL automatically reverts to database defaults. No manual reset required.

---

## When to Use This Fix

### Apply This Fix When:
1. Running migrations that create materialized views with complex CTEs
2. Creating views that join multiple large tables (>1M rows)
3. Migrations involving window functions or array aggregations
4. Any DDL operation that spawns multiple parallel workers and hangs

### Safe to Use Normal Execution When:
1. Simple SELECT queries
2. Small data sets (<100K rows)
3. Straightforward INSERT/UPDATE operations
4. Migrations without complex joins or aggregations

---

## PostgreSQL Settings Explained

### max_parallel_workers_per_gather
- **Default**: 2
- **Purpose**: Maximum number of parallel workers that can be started by a single Gather or Gather Merge node
- **Setting to 0**: Disables parallel execution for queries in this session

### max_parallel_workers
- **Default**: 8 (typically based on CPU cores)
- **Purpose**: Maximum number of parallel workers that can exist system-wide
- **Setting to 0**: Prevents any new parallel workers from being created

### Session vs. Database Level

**Session-level** (`SET` command):
```sql
SET max_parallel_workers_per_gather = 0;  -- Only affects current session
```

**Database-level** (`ALTER DATABASE` - NOT RECOMMENDED):
```sql
ALTER DATABASE route_poc SET max_parallel_workers_per_gather = 0;  -- Affects all sessions
```

**Global-level** (`postgresql.conf` - NOT RECOMMENDED for this issue):
```
max_parallel_workers_per_gather = 0  # Requires PostgreSQL restart
```

---

## Monitoring and Debugging Commands

### Check for Stuck Parallel Workers
```sql
SELECT
    pid,
    query_start,
    NOW() - query_start as runtime,
    state,
    LEFT(query, 80) as query_preview
FROM pg_stat_activity
WHERE datname = 'route_poc'
  AND state = 'active'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY query_start;
```

### Kill Stuck Workers (if needed)
```sql
-- Kill all workers executing the stuck migration
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'route_poc'
  AND state = 'active'
  AND query LIKE '%CREATE MATERIALIZED VIEW mv_campaign_browser%'
  AND query NOT LIKE '%pg_stat_activity%';
```

### Check Materialized View Status
```sql
-- List all materialized views
SELECT schemaname, matviewname, ispopulated
FROM pg_matviews
WHERE matviewname = 'mv_campaign_browser';

-- Check if view exists
\d mv_campaign_browser
```

---

## Lessons Learned

### Critical Takeaways

1. **PostgreSQL parallel workers can deadlock on complex materialized view creation**
   - Not all parallelizable queries benefit from parallel execution
   - Complex CTEs with window functions are prone to worker conflicts

2. **Session-level settings are safe and temporary**
   - `SET` commands only affect the current session
   - No risk of permanently degrading database performance
   - Settings automatically revert when session ends

3. **Single-threaded execution can be faster for complex DDL**
   - Migration completed in ~3.5 minutes with parallel workers disabled
   - Previous attempts with parallel workers: 6+ minutes with no completion
   - Sometimes sequential is more efficient than parallel

4. **Monitoring is critical during migrations**
   - Always monitor `pg_stat_activity` during long-running migrations
   - Check for duplicate worker processes as early warning sign
   - Kill stuck processes before they consume excessive resources

5. **Different execution methods can have different behavior**
   - `psql -f` vs `psql <` vs Python connection all spawned workers
   - Heredoc approach (`psql <<'EOF'`) worked best with inline `SET` commands
   - Consider execution context when troubleshooting

---

## Related Issues

### Previous Session (Nov 14, 2025)
- Encountered similar parallel worker issue with same migration
- Documented in `Claude/Handover/SESSION_HANDOVER_2025-11-15_MULTI_ENTITY_SUPPORT_COMPLETE.md`
- Resolved by killing duplicate processes (not optimal solution)
- Root cause not addressed until current session

### Performance Notes
- Original O(n×m) correlated subquery issue (solved with window functions): 1000x+ speedup
- Parallel worker deadlock issue (solved with disabled parallel execution): infinite speedup (from stuck to 3.5min)
- Both issues required careful PostgreSQL query optimization

---

## References

### PostgreSQL Documentation
- [Parallel Query](https://www.postgresql.org/docs/current/parallel-query.html)
- [Parallel Plans](https://www.postgresql.org/docs/current/when-can-parallel-query-be-used.html)
- [Runtime Config - Resource Consumption](https://www.postgresql.org/docs/current/runtime-config-resource.html)

### Related Project Documentation
- `Claude/Documentation/MATERIALIZED_VIEW_PERFORMANCE_ISSUE.md` - Window function optimization
- `migrations/003_create_mv_campaign_browser.sql` - The migration that triggered this issue
- `run_migration_003.py` - Helper script for running migrations safely

---

**Last Updated**: November 15, 2025
**Author**: Claude Code & Ian Wyatt
**Status**: Resolved ✅
