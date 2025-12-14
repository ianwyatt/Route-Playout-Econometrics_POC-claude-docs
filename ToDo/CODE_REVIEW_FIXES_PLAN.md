# Code Review Fixes Plan

**Date:** 9 December 2025
**Status:** Ready for implementation

---

## Issue 1: f-string Table Names in cache_service.py (SQL Safety)

### Problem

Three methods in `src/services/cache_service.py` use f-string interpolation for table names:

| Method | Line | Query |
|--------|------|-------|
| `get_space_entity()` | 721 | `FROM {table_name}` |
| `upsert_space_entity()` | 770 | `INSERT INTO {table_name}` |
| `batch_get_space_entities()` | 824 | `FROM {table_name}` |

While currently safe (callers use `SPACE_TABLE_*` constants), this pattern is risky. If someone later passes user input, it becomes SQL injection.

### Current State

```python
# Lines 15-18 define valid tables
SPACE_TABLE_MEDIA_OWNERS = 'cache_space_media_owners'
SPACE_TABLE_BUYERS = 'cache_space_buyers'
SPACE_TABLE_AGENCIES = 'cache_space_agencies'
SPACE_TABLE_BRANDS = 'cache_space_brands'
```

### Solution

Add a validation function that checks table names against an allowlist before query execution.

### Implementation Steps

1. **Add allowlist constant** (after line 18):
   ```python
   VALID_SPACE_TABLES = frozenset({
       SPACE_TABLE_MEDIA_OWNERS,
       SPACE_TABLE_BUYERS,
       SPACE_TABLE_AGENCIES,
       SPACE_TABLE_BRANDS,
   })
   ```

2. **Add validation method** to CacheService class:
   ```python
   @staticmethod
   def _validate_table_name(table_name: str) -> str:
       """
       Validate table name against allowlist to prevent SQL injection.

       Args:
           table_name: Table name to validate

       Returns:
           Validated table name

       Raises:
           ValueError: If table name is not in allowlist
       """
       if table_name not in VALID_SPACE_TABLES:
           raise ValueError(
               f"Invalid table name '{table_name}'. "
               f"Must be one of: {', '.join(sorted(VALID_SPACE_TABLES))}"
           )
       return table_name
   ```

3. **Update each method** to validate at entry:
   - `get_space_entity()` - add `table_name = self._validate_table_name(table_name)` at start
   - `upsert_space_entity()` - add validation at start
   - `batch_get_space_entities()` - add validation at start

### Files Modified

- `src/services/cache_service.py`

### Risk Assessment

- **Low risk** - Adding validation cannot break existing functionality
- **Defence in depth** - Even if callers are correct, validation adds safety layer

---

## Issue 2: Archive export_legacy.py (Dead Code)

### Problem

`src/ui/utils/export_legacy.py` (926 lines) appears to be unused.

### Verification

```bash
# Search result: NO imports found
grep -r "export_legacy" src/ --include="*.py"
```

### Solution

Move to archive folder.

### Implementation Steps

1. Move file:
   - From: `src/ui/utils/export_legacy.py`
   - To: `src/ui/archive/export_legacy.py`

2. Verify app still runs after move

### Files Modified

- `src/ui/utils/export_legacy.py` → `src/ui/archive/export_legacy.py`

### Risk Assessment

- **Very low risk** - No imports found, file is unused

---

## Issue 3: Dead Imports from Archive (Already Clean)

### Finding

**No action needed.** Search confirmed no active code imports from archive folders:

```bash
# Search result: NO matches
grep -r "from src.archive\|from ..archive\|import.*archive" src/ --include="*.py"
```

The archive folders are properly isolated.

---

## Implementation Order

1. **Issue 1** - Table name validation (highest value, prevents future bugs)
2. **Issue 2** - Archive export_legacy.py (quick cleanup)
3. **Issue 3** - Already clean, document only

---

## Testing Plan

After implementation:

1. Run Streamlit app: `startstream`
2. Select a campaign from browser
3. Verify all tabs load without errors
4. Check logs for any validation errors

---

## Estimated Effort

| Task | Time |
|------|------|
| Issue 1: Table validation | 15 min |
| Issue 2: Archive file | 5 min |
| Testing | 10 min |
| Documentation | 10 min |
| **Total** | **40 min** |

---

*Plan created: 9 December 2025*
