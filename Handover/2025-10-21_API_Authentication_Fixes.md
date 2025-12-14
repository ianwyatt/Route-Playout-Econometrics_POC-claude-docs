# Handover: API Authentication Fixes for Pipeline Integration
**Date:** October 21, 2025
**Session:** API authentication debugging and utilities handover preparation

---

## Executive Summary

Fixed critical authentication issues in both SPACE API and Route API clients that were blocking pipeline integration. Both APIs now authenticate successfully and all endpoints are working. Pipeline team can now successfully connect using the updated utilities.

---

## Problems Identified

### 1. Route API - HTTP 401 Unauthorized

**Issue:** Route API was failing with 401 errors even with valid API key.

**Root Cause:** Route API requires **dual authentication** but our client only sent the API key:
- ✅ `X-Api-Key` header (was being sent)
- ❌ `Authorization: Basic` header (was missing!)

Route API needs BOTH headers for authentication to succeed.

### 2. SPACE API - HTTP 401 / No Data Returned

**Issues Found:**
1. Wrong environment variable names (case-sensitive!)
   - ❌ `SPACE_API_Username` (lowercase)
   - ✅ `SPACE_API_USERNAME` (uppercase)
2. Wrong endpoint format
   - ❌ `/media-owners/171`
   - ✅ `/media-owner?id=171` (query parameter)
3. Missing required header
   - ❌ No Accept header
   - ✅ `Accept: application/json` (required by SPACE API)
4. Buyer/Agency/Brand endpoints don't exist
   - Must fetch full lists and filter by ID

### 3. Route API - Invalid Request Formats

**Issues:**
1. Wrong demographics format
   - ❌ `["ageband>=1"]` (strings)
   - ✅ `[{"demographic_id": 1}]` (objects)
2. Wrong algorithm figure name
   - ❌ `"frequency"`
   - ✅ `"average_frequency"`
3. Playout endpoint doesn't accept `algorithm_figures` parameter
   - Must omit this field entirely for playout calls

---

## Fixes Implemented

### Route API Client (`utilities/route_api/client.py`)

#### 1. Added Dual Authentication
```python
def __init__(
    self,
    api_key: Optional[str] = None,
    username: Optional[str] = None,  # NEW
    password: Optional[str] = None,  # NEW
    base_url: Optional[str] = None
):
    self.api_key = api_key or os.getenv('ROUTE_API_KEY')
    self.username = username or os.getenv('ROUTE_API_User_Name')  # NEW
    self.password = password or os.getenv('ROUTE_API_Password')  # NEW
```

#### 2. Updated Request Headers
```python
def _get_headers(self) -> Dict[str, str]:
    """Route API requires BOTH API Key and Basic Auth"""
    import base64
    credentials = f"{self.username}:{self.password}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()

    return {
        "Authorization": f"Basic {b64_credentials}",  # NEW
        "X-Api-Key": self.api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
```

#### 3. Fixed Demographics Format
```python
# Before:
demographics = ["ageband>=1"]

# After:
demographics = [{"demographic_id": 1}]
```

#### 4. Fixed Algorithm Figures
```python
# Before:
"algorithm_figures": ["impacts", "reach", "frequency", "grp", "population"]

# After:
"algorithm_figures": ["impacts", "reach", "average_frequency", "grp", "population"]
```

#### 5. Implemented Playout Endpoint
Added `call_process_playout()` method for per-spot audience data:
- Returns `audience_spot_avg` for individual playouts
- Omits `algorithm_figures` parameter (not supported by playout endpoint)
- Provides per-frame breakdown with playout counts

#### 6. Fixed Response Parsing
```python
# Route API returns 'route_releases' not 'releases'
releases = data.get('route_releases', [])  # Fixed
```

### SPACE API Client (`utilities/space_api/client.py`)

#### 1. Fixed Environment Variable Names
```python
# Now reads uppercase variables
self.username = username or os.getenv('SPACE_API_USERNAME')  # Uppercase!
self.password = password or os.getenv('SPACE_API_PASSWORD')  # Uppercase!
```

#### 2. Fixed Media Owner Endpoint
```python
# Before:
response = requests.get(f"{self.base_url}/media-owners/{media_owner_id}")

# After:
response = requests.get(
    f"{self.base_url}/media-owner",
    params={'id': media_owner_id}  # Query parameter
)
```

#### 3. Added Required Accept Header
```python
headers = {
    'User-Agent': 'Route-Playout-Pipeline/1.0',
    'Accept': 'application/json'  # Required by SPACE API
}
```

#### 4. Implemented List-Based Lookups
Since individual endpoints don't exist for buyers/agencies/brands:

```python
def _get_all_agencies(self) -> Dict[str, Any]:
    """Fetch full agency list and cache for 1 hour"""
    # Fetch from /agency endpoint
    # Cache results with TTL
    # Return full list

def get_buyer(self, buyer_id: str) -> Optional[SpaceEntity]:
    """Fetch agency list and filter by ID"""
    agencies = self._get_all_agencies()
    # Filter by agency_id and return match
```

Same pattern for `get_agency()` and `get_brand()` methods.

---

## Environment Variables Required

### Route API (3 variables - ALL required)
```bash
ROUTE_API_KEY=<api_key>
ROUTE_API_User_Name=<username>
ROUTE_API_Password=<password>
```

### SPACE API (3 variables - ALL required)
```bash
SPACE_API_URL=https://oohspace.co.uk/api
SPACE_API_USERNAME=<username>  # UPPERCASE!
SPACE_API_PASSWORD=<password>  # UPPERCASE!
```

**Critical:** Variable names are case-sensitive!

---

## Testing Completed

### SPACE API - All Entity Types ✅
```python
# Media Owner lookup
media_owner = client.get_media_owner('171')
# Result: "Global" (ID: 171) ✅

# Buyer lookup (via agency list)
buyer = client.get_buyer('15320')
# Result: Returns buyer from agency list ✅

# Agency lookup (via agency list)
agency = client.get_agency('15320')
# Result: Returns agency from list ✅

# Brand lookup (via client-brand list)
brand = client.get_brand('14215')
# Result: Returns brand from list ✅
```

### Route API - Both Endpoints ✅

#### /rest/process/custom Endpoint
```python
result = client.call_process_custom(
    schedules=[{'datetime_from': '2025-08-20 10:00',
                'datetime_until': '2025-08-20 10:15'}],
    frames=[1234932595, 1235074313, 1234934873],
    route_release_id=55,
    target_month=8,
    spot_length=10,
    break_length=50
)
# Result: Returns impacts, reach, frequency, GRP ✅
```

#### /rest/process/playout Endpoint
```python
result = client.call_process_playout(
    schedules=[{'datetime_from': '2025-08-20 10:00',
                'datetime_until': '2025-08-20 10:15'}],
    frames=[1234932595, 1235074313, 1234934873],
    route_release_id=55,
    target_month=8,
    spot_length=10,
    spot_break_length=0
)
# Result: Returns audience_spot_avg per frame ✅
# Per-frame breakdown with playout counts ✅
```

#### /rest/version Endpoint
```python
releases = client.get_available_releases()
# Result: Returns 4 releases (R53, R54, R55, R56) ✅
```

---

## Documentation Created for Pipeline Team

### 1. README_PIPELINE.md
- Complete setup instructions
- Required environment variables
- Common issues and troubleshooting
- Usage examples
- Verification checklist

### 2. test_utilities.py
- Diagnostic script to verify setup
- Checks all environment variables
- Tests both API connections
- Clear success/failure messages
- Helps identify old utility versions

**Note:** These files contain NO credentials and are safe to share.

---

## Files Modified (Committed to GitHub)

### Committed Changes
1. `Route_Cache_Pipeline_Handover/utilities/route_api/client.py`
   - Added dual authentication
   - Implemented playout endpoint
   - Fixed demographics and algorithm figures
   - Fixed response parsing

2. `Route_Cache_Pipeline_Handover/utilities/space_api/client.py`
   - Fixed environment variable names
   - Fixed endpoint format
   - Added Accept header
   - Implemented list-based lookups with caching

3. `src/services/reach_service.py`
   - Fixed datetime formatting for Route API

4. `tests/unit/test_reach_service.py`
   - Updated test assertions for datetime format

### Not Committed (Documentation Only)
- `Route_Cache_Pipeline_Handover/README_PIPELINE.md` - No credentials, safe
- `Route_Cache_Pipeline_Handover/test_utilities.py` - No credentials, safe

---

## Git Commits

```bash
# Commit 1: Datetime fix
feat: fix datetime formatting for Route API calls

# Commit 2: Route API playout endpoint
feat: implement Route API playout endpoint for per-spot audience data

# All commits pushed to GitHub dev branch
```

---

## Known Issues / Future Work

### 1. Route API Rate Limiting
- Current limit: 6 calls per second
- Current limit: 10,000 frames per call
- Client has built-in rate limiting
- Large campaigns need batching

### 2. SPACE API Caching
- Current: 1-hour TTL for agency and brand lists
- Consider: Database caching for production
- Lists are relatively static

### 3. Route Release Mapping
- Current: Hardcoded mapping in client
- Future: Store in database
- Only last 5 releases available from API

---

## Pipeline Team Status

✅ **Successfully Connected** - Pipeline team confirmed both APIs working after:
1. Copying latest utilities (Oct 21, 2025)
2. Setting correct environment variables
3. Running test_utilities.py diagnostic

Both SPACE API and Route API now authenticate successfully.

---

## Key Takeaways

1. **Route API requires dual authentication** - API key alone is not sufficient
2. **SPACE API variable names are case-sensitive** - Must use UPPERCASE
3. **SPACE API uses query parameters** - Not REST path parameters
4. **Route API demographics must be objects** - Not strings
5. **Playout endpoint is different from custom endpoint** - Different parameters
6. **Pipeline utilities were updated** - Team needs latest version

---

## Contact

For questions about these fixes:
- ian@route.org.uk
- See README_PIPELINE.md for troubleshooting guide
- Run test_utilities.py to diagnose issues

---

**Status:** ✅ Complete - Pipeline team successfully connected to both APIs
