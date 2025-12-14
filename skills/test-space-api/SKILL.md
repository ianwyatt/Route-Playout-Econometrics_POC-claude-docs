---
name: test-space-api
description: Test SPACE API entity lookups. Use when looking up media owners, buyers, agencies, or brands by ID, or debugging SPACE API integration.
---

# Test SPACE API

Test SPACE API endpoint for entity lookups (media owners, buyers, agencies, brands).

## Commands

```bash
# Basic connectivity test
python skills/space_api/test_entity_lookup.py

# Lookup specific entities
python skills/space_api/test_entity_lookup.py --media-owner-id 100
python skills/space_api/test_entity_lookup.py --buyer-id 200
python skills/space_api/test_entity_lookup.py --brand-id 300

# Batch lookup
python skills/space_api/test_entity_lookup.py --media-owner-id 100,101,102
```

## When to Use

- "Lookup media owner ID X"
- "What brand is ID X?"
- "Test SPACE API"
- "Check entity mapping"
- Debugging entity resolution issues

## Output

Shows:
- Entity details (name, type)
- API response status
- Cache status for entity
