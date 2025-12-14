---
name: check-cache
description: Check PostgreSQL cache status, coverage, and statistics. Use when asked about cache health, whether campaigns are cached, cache hit rates, or debugging slow queries.
---

# Check Cache Status

Inspect Route API and SPACE API cache state in PostgreSQL.

## Commands

```bash
# Basic status
python skills/cache/check_cache_status.py

# Detailed breakdown
python skills/cache/check_cache_status.py --detailed
```

## When to Use

- "Is campaign X cached?"
- "What's the cache coverage?"
- "Show cache statistics"
- Debugging slow queries (check for cache miss)
- Verifying cache after pipeline runs

## Output

Shows:
- Total cached records
- Campaigns with cache data
- Cache freshness (oldest/newest dates)
- Hit rates if available
