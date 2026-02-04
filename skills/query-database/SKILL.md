---
name: query-database
description: Query PostgreSQL database for playout data. Use when asked to check campaign data, inspect playouts, or debug database queries.
---

# Query Database

Query the PostgreSQL database for playout records and campaign data.

## Commands

```bash
# Query by campaign ID
python skills/database/query_database.py --campaign-id 16699

# Limit results
python skills/database/query_database.py --campaign-id 16699 --limit 10

# Query by date range
python skills/database/query_database.py --campaign-id 16699 --start-date 2025-01-01 --end-date 2025-01-31

# Export to CSV
python skills/database/query_database.py --campaign-id 16699 --output results.csv
```

## When to Use

- "Show playouts for campaign X"
- "Check what data we have for campaign X"
- "Query the database for..."
- Debugging data issues
- Verifying playout records

## Output

Shows playout records with:
- Frame IDs
- Playout timestamps
- Media owner
- Brand
- Duration
