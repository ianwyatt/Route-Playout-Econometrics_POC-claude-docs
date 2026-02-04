# Route API Questionnaire Endpoint - Examples

**Purpose**: Examples for querying available demographic variables and building custom targets

**📋 R56 Reference**: For the complete R56 (Q3 2025) questionnaire with all 792 variables, see **[R56_QUESTIONNAIRE_REFERENCE.md](./R56_QUESTIONNAIRE_REFERENCE.md)**

---

## Quick Test: Get Available Demographics

### Command Line (curl)

```bash
# Query questionnaire endpoint
curl -X POST https://route.mediatelapi.co.uk/rest/codebook/questionnaire \
  -H "Authorization: ${ROUTE_API_AUTH}" \
  -H "API-Key: ${ROUTE_API_KEY}" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### Python Script

```python
#!/usr/bin/env python3
"""
Query Route API questionnaire endpoint to discover available demographic variables.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def get_questionnaire_variables():
    """Get all available demographic variables from Route API."""
    url = f"{os.getenv('ROUTE_API_URL')}/rest/codebook/questionnaire"

    headers = {
        'Authorization': os.getenv('ROUTE_API_AUTH'),
        'Content-Type': 'application/json',
        'API-Key': os.getenv('ROUTE_API_KEY')
    }

    try:
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def print_variables_summary(data):
    """Print a summary of available variables."""
    print("=" * 80)
    print("ROUTE API QUESTIONNAIRE VARIABLES")
    print("=" * 80)

    for category in data.get('variables', []):
        print(f"\n📊 Category: {category.get('name', 'Unknown')}")
        print("-" * 80)

        for item in category.get('items', []):
            code = item.get('code', 'N/A')
            description = item.get('description', 'No description')
            values = item.get('values', [])

            print(f"\n  Variable: {code}")
            print(f"  Description: {description}")

            if values:
                if len(values) <= 10:
                    print(f"  Values: {', '.join(map(str, values))}")
                else:
                    print(f"  Values: {', '.join(map(str, values[:10]))} ... ({len(values)} total)")

    print("\n" + "=" * 80)

def save_to_file(data, filename='questionnaire_variables.json'):
    """Save questionnaire data to JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ Saved to {filename}")

if __name__ == "__main__":
    # Get variables
    print("Querying Route API questionnaire endpoint...")
    data = get_questionnaire_variables()

    if data:
        # Print summary
        print_variables_summary(data)

        # Save to file
        save_to_file(data)

        # Print usage examples
        print("\n" + "=" * 80)
        print("USAGE EXAMPLES")
        print("=" * 80)
        print("\n# All ages (default)")
        print('demographics = ["ageband>=1"]')

        print("\n# Young adults (15-34)")
        print('demographics = ["ageband=15-34"]')

        print("\n# ABC1 social grade")
        print('demographics = ["social_grade=ABC1"]')

        print("\n# Males only")
        print('demographics = ["gender=male"]')

        print("\n# Complex: Young working ABC1 males")
        print('demographics = ["ageband=15-34", "social_grade=ABC1", "gender=male", "working_status=working"]')

        print("\n" + "=" * 80)
    else:
        print("❌ Failed to retrieve questionnaire variables")
```

---

## Example Output

When you run the script, you'll see output like:

```
================================================================================
ROUTE API QUESTIONNAIRE VARIABLES
================================================================================

📊 Category: Age
--------------------------------------------------------------------------------

  Variable: ageband
  Description: Age bands
  Values: 15-34, 35-54, 55+

  Variable: age
  Description: Specific age
  Values: 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 ... (70 total)

📊 Category: Demographics
--------------------------------------------------------------------------------

  Variable: social_grade
  Description: Social grade classification
  Values: ABC1, C2DE

  Variable: gender
  Description: Gender
  Values: male, female

  Variable: working_status
  Description: Employment status
  Values: working, not_working

  Variable: household_composition
  Description: Household type
  Values: with_children, without_children, single

📊 Category: Geography
--------------------------------------------------------------------------------

  Variable: tv_region
  Description: ITV television region
  Values: London, Yorkshire, Central, ...

  Variable: conurbation
  Description: Urban conurbation
  Values: Greater London, Greater Manchester, West Midlands, ...

  Variable: postal_sector
  Description: Postal sector
  Values: E1 0, E1 1, E1 2, E1 3, E1 4, E1 5, E1 6, E1 7, E1 8, E1 9 ... (9000+ total)

================================================================================
USAGE EXAMPLES
================================================================================

# All ages (default)
demographics = ["ageband>=1"]

# Young adults (15-34)
demographics = ["ageband=15-34"]

# ABC1 social grade
demographics = ["social_grade=ABC1"]

# Males only
demographics = ["gender=male"]

# Complex: Young working ABC1 males
demographics = ["ageband=15-34", "social_grade=ABC1", "gender=male", "working_status=working"]

================================================================================
✅ Saved to questionnaire_variables.json
```

---

## Building Custom Playout Requests

### Example 1: Basic Age Targeting

```python
# Target young adults (15-34)
demographics = ["ageband=15-34"]

payload = {
    "route_release_id": "56",
    "route_algorithm_version": "10.2",
    "algorithm_figures": ["impacts"],
    "grouping": "frame_ID",
    "demographics": demographics,
    "campaign": [{
        "schedule": [{
            "datetime_from": "2025-10-11 00:00",
            "datetime_until": "2025-10-11 23:59"
        }],
        "spot_length": 10,
        "spot_break_length": 50,
        "frames": [1234567890, 2345678901]
    }],
    "target_month": 1
}
```

### Example 2: Social Grade Targeting

```python
# Target ABC1 audience
demographics = ["social_grade=ABC1"]

payload = {
    "route_release_id": "56",
    "route_algorithm_version": "10.2",
    "algorithm_figures": ["impacts"],
    "grouping": "frame_ID",
    "demographics": demographics,
    "campaign": [{
        "schedule": [{
            "datetime_from": "2025-10-11 00:00",
            "datetime_until": "2025-10-11 23:59"
        }],
        "spot_length": 10,
        "spot_break_length": 50,
        "frames": [1234567890, 2345678901]
    }],
    "target_month": 1
}
```

### Example 3: Complex Multi-Demographic Targeting

```python
# Target: Working ABC1 males aged 25-44 in London
demographics = [
    "ageband=25-44",
    "social_grade=ABC1",
    "gender=male",
    "working_status=working",
    "tv_region=London"
]

payload = {
    "route_release_id": "56",
    "route_algorithm_version": "10.2",
    "algorithm_figures": ["impacts"],
    "grouping": "frame_ID",
    "demographics": demographics,
    "campaign": [{
        "schedule": [{
            "datetime_from": "2025-10-11 00:00",
            "datetime_until": "2025-10-11 23:59"
        }],
        "spot_length": 10,
        "spot_break_length": 50,
        "frames": [1234567890, 2345678901]
    }],
    "target_month": 1
}
```

### Example 4: Multiple Age Bands (OR Logic)

```python
# Target both young adults AND middle-aged adults (OR logic)
demographics = [
    "ageband=15-34",
    "ageband=35-54"
]

payload = {
    "route_release_id": "56",
    "route_algorithm_version": "10.2",
    "algorithm_figures": ["impacts"],
    "grouping": "frame_ID",
    "demographics": demographics,
    "campaign": [{
        "schedule": [{
            "datetime_from": "2025-10-11 00:00",
            "datetime_until": "2025-10-11 23:59"
        }],
        "spot_length": 10,
        "spot_break_length": 50,
        "frames": [1234567890, 2345678901]
    }],
    "target_month": 1
}
```

---

## Caching Custom Demographics

### Create Extended Cache Table

```sql
CREATE TABLE cache_campaign_reach_day_custom (
    campaign_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    demographic_filter TEXT NOT NULL,         -- JSON array of demographics
    reach NUMERIC,
    grp NUMERIC,
    frequency NUMERIC,
    total_impacts NUMERIC,
    frame_count INTEGER,
    route_release_id INTEGER,
    cached_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (campaign_id, date, demographic_filter)
);

CREATE INDEX idx_cache_custom_campaign ON cache_campaign_reach_day_custom(campaign_id);
CREATE INDEX idx_cache_custom_date ON cache_campaign_reach_day_custom(date);
CREATE INDEX idx_cache_custom_filter ON cache_campaign_reach_day_custom(demographic_filter);
```

### Cache with Demographics

```python
import json
import psycopg2

def cache_with_demographics(campaign_id, date, demographics, reach, grp, frequency, impacts, frames, release_id):
    """Cache campaign data with custom demographic filter."""

    # Convert demographics list to JSON string
    demographic_filter = json.dumps(sorted(demographics))  # Sort for consistency

    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

    query = """
        INSERT INTO cache_campaign_reach_day_custom (
            campaign_id, date, demographic_filter,
            reach, grp, frequency, total_impacts,
            frame_count, route_release_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (campaign_id, date, demographic_filter)
        DO UPDATE SET
            reach = EXCLUDED.reach,
            grp = EXCLUDED.grp,
            frequency = EXCLUDED.frequency,
            total_impacts = EXCLUDED.total_impacts,
            frame_count = EXCLUDED.frame_count,
            cached_at = CURRENT_TIMESTAMP
    """

    cursor = conn.cursor()
    cursor.execute(query, (
        campaign_id,
        date,
        demographic_filter,
        reach,
        grp,
        frequency,
        impacts,
        frames,
        release_id
    ))
    conn.commit()
    conn.close()

# Example usage
demographics = ["ageband=15-34", "social_grade=ABC1"]
cache_with_demographics(
    campaign_id="15884",
    date="2025-10-11",
    demographics=demographics,
    reach=394,
    grp=1.53,
    frequency=2.16,
    impacts=852,
    frames=114,
    release_id=56
)
```

### Query Cached Demographics

```sql
-- Find all demographic variations cached for a campaign
SELECT
    demographic_filter,
    COUNT(*) as days_cached,
    AVG(reach) as avg_reach,
    AVG(grp) as avg_grp
FROM cache_campaign_reach_day_custom
WHERE campaign_id = '15884'
GROUP BY demographic_filter;

-- Get specific demographic data
SELECT *
FROM cache_campaign_reach_day_custom
WHERE campaign_id = '15884'
    AND date = '2025-10-11'
    AND demographic_filter = '["ageband=15-34", "social_grade=ABC1"]';
```

---

## Common Demographic Scenarios

### Scenario 1: Luxury Brand Campaign

**Target**: Affluent adults 35+

```python
demographics = [
    "ageband=35-54",
    "ageband=55+",
    "social_grade=ABC1"
]
```

### Scenario 2: Youth-Oriented Product

**Target**: Young adults, any social grade

```python
demographics = [
    "ageband=15-34"
]
```

### Scenario 3: Family Product

**Target**: Adults with children

```python
demographics = [
    "ageband=35-54",
    "household_composition=with_children"
]
```

### Scenario 4: Regional Campaign

**Target**: All adults in London

```python
demographics = [
    "ageband>=1",
    "tv_region=London"
]
```

### Scenario 5: Premium Service (Multi-Target)

**Target**: Young professionals OR affluent seniors

```python
# Note: This creates OR logic between age bands
demographics = [
    "ageband=25-44",
    "ageband=55+",
    "social_grade=ABC1",
    "working_status=working"
]
```

---

## Testing Demographic Filters

### Validate Before Full Cache Run

```python
def test_demographic_filter(demographics, campaign_id="15884", date="2025-10-11"):
    """Test a demographic filter on a single campaign-day."""

    print(f"Testing demographics: {demographics}")

    # Get small sample of playouts
    playouts = get_campaign_playouts(campaign_id, date, limit=10)

    # Build request
    payload = build_custom_demographic_request(
        frames=[p['frameid'] for p in playouts[:5]],  # Just 5 frames
        schedule=[{
            "datetime_from": f"{date} 12:00",
            "datetime_until": f"{date} 13:00"  # Just 1 hour
        }],
        demographics=demographics
    )

    # Call API
    response = call_route_api(payload, timeout=60)

    if response and response.get('data'):
        print(f"✅ Filter valid - got {len(response['data'].get('frames', []))} frame results")
        return True
    else:
        print(f"❌ Filter failed or returned no data")
        return False

# Test before full run
test_demographics = [
    "ageband=25-44",
    "social_grade=ABC1",
    "working_status=working"
]

if test_demographic_filter(test_demographics):
    print("Proceeding with full cache run...")
    # Run full cache
else:
    print("Fix demographic filter before proceeding")
```

---

## Tips and Best Practices

### 1. Start Simple

Begin with basic demographics before complex combinations:
- ✅ `["ageband=15-34"]`
- ⚠️ `["ageband=15-34", "social_grade=ABC1", "working_status=working", "tv_region=London"]`

### 2. Check Sample Size

Complex filters may have insufficient sample:
```python
# Good: Broad targeting
demographics = ["ageband=15-34"]

# Risky: Very narrow targeting (may have small sample)
demographics = ["ageband=18-24", "gender=female", "working_status=working", "postal_sector=SW1A 1"]
```

### 3. Cache Strategy

- Cache all-ages (`ageband>=1`) first (most general)
- Then cache age bands separately
- Finally cache complex combinations if needed

### 4. Naming Conventions

Use consistent naming for demographic filters:
```python
# Good: Sorted, consistent
demographics = sorted(["ageband=15-34", "social_grade=ABC1"])

# Bad: Random order (creates duplicate cache entries)
demographics = ["social_grade=ABC1", "ageband=15-34"]
```

### 5. Document Your Filters

```python
DEMOGRAPHIC_PRESETS = {
    "all_ages": ["ageband>=1"],
    "young_adults": ["ageband=15-34"],
    "abc1": ["social_grade=ABC1"],
    "c2de": ["social_grade=C2DE"],
    "young_professionals": ["ageband=25-44", "social_grade=ABC1", "working_status=working"],
    "families": ["ageband=35-54", "household_composition=with_children"]
}

# Use presets
demographics = DEMOGRAPHIC_PRESETS["young_professionals"]
```

---

## Running the Example Script

```bash
# 1. Save the script
cat > query_questionnaire.py << 'EOF'
[paste the Python script from above]
EOF

# 2. Make executable
chmod +x query_questionnaire.py

# 3. Run it
python query_questionnaire.py

# 4. View saved data
cat questionnaire_variables.json | jq '.variables[0]'
```

---

**Reference**: [ROUTE_API_CACHING_GUIDE.md](./ROUTE_API_CACHING_GUIDE.md#custom-demographics-and-questionnaire-endpoint)
