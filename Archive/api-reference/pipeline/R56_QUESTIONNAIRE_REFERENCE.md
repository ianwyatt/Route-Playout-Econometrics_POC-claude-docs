# Route R56 Questionnaire Response - Complete Reference

**Route Release**: R56 (Q3 2025)
**Retrieved**: October 26, 2025 12:40:51
**Variables**: 792 demographic and psychographic variables
**Format**: JSON

---

## Purpose

This document provides a reference for the **actual Route R56 questionnaire response** from the production Route API. Use this to discover all available demographic variables for building custom audience targets.

---

## File Location

**Full Response**: `docs/api-reference/route/Route_API_Documentation/Route_R56_Questionnaire_response.json`
**Size**: 197 KB
**Format**: JSON

---

## File Structure

```json
{
  "route_release_id": 56,
  "processed_datetime": "2025-10-26 12:40:51",
  "questionnaire": {
    "variable_name": {
      "wording": "Human-readable question text",
      "mandatory": true/false,
      "answers": {
        "code": "value",
        "code": "value",
        ...
      }
    },
    ...
  }
}
```

---

## Quick Stats

- **Total Variables**: 792
- **Route Release**: R56 (Q3 2025)
- **Categories**: Demographics, Geography, Psychographics, Lifestyle, Media Consumption
- **File Size**: 197 KB

---

## Key Demographic Variables

### Age and Gender

**Variable**: `sex`
```json
{
  "wording": "SEX OF RESPONDENT",
  "mandatory": true,
  "answers": {
    "1": "Male",
    "2": "Female"
  }
}
```

**Usage in API**:
```python
demographics = ["sex=1"]  # Male only
demographics = ["sex=2"]  # Female only
```

### Social Grade

**Variable**: `social_grade`
```json
{
  "wording": "SOCIAL GRADE",
  "mandatory": true,
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C1",
    "4": "C2",
    "5": "D",
    "6": "E"
  }
}
```

**Usage in API**:
```python
# ABC1
demographics = ["social_grade=1", "social_grade=2", "social_grade=3"]

# C2DE
demographics = ["social_grade=4", "social_grade=5", "social_grade=6"]
```

### Geographic Variables

#### Region

**Variable**: `region`
```json
{
  "wording": "Government Office Region",
  "mandatory": true,
  "answers": {
    "1": "North East",
    "2": "North West",
    "3": "Yorkshire",
    "4": "West Midlands",
    "5": "East Midlands",
    "6": "East Anglia",
    "7": "South West",
    "8": "South East",
    "9": "London",
    "10": "Wales",
    "11": "Scotland"
  }
}
```

#### TV Area

**Variable**: `tv_area`
```json
{
  "wording": "TV Area (BARB)",
  "mandatory": true,
  "answers": {
    "1": "Border",
    "2": "Central Scotland",
    "3": "East Of England",
    "4": "London",
    "5": "Midlands",
    "6": "North East",
    "7": "North Scotland",
    "8": "North West",
    "9": "South and South-East",
    "10": "South West",
    "11": "Wales",
    "12": "West",
    "13": "Yorkshire"
  }
}
```

#### Town

**Variable**: `TOWN`
- **Values**: 1,646 UK towns
- **Examples**: London, Manchester, Edinburgh, Cardiff, etc.

**Usage**:
```python
demographics = ["TOWN=9"]  # London
demographics = ["TOWN=562"]  # Manchester
```

#### Postal District

**Variable**: `pdist`
```json
{
  "wording": "Postal District",
  "mandatory": true,
  "answers": {
    "{string}": "UK Postal District"
  }
}
```

### Geodemographic Segmentation

#### ACORN 2024

**ACORN Category**: `ACORNCATEGORY_2024`
**ACORN Group**: `ACORNGROUP_2024`
**ACORN Type**: `ACORNTYPE_2024`

ACORN is a geodemographic classification system that categorizes UK postcodes.

---

## Working Status

**Variable**: `CIE_working_status`

Common codes:
- Working full-time
- Working part-time
- Unemployed
- Retired
- Student

### Employment Classification

**Variable**: `CIE_BDM_Manager_Proprietor_Supervisor`

Identifies management and supervisory roles.

---

## TGI (Target Group Index) Variables

The questionnaire includes **600+ TGI variables** covering:

### Categories

1. **Media Consumption** (TGI_Q1_* to TGI_Q10_*)
   - TV viewing habits
   - Radio listening
   - Newspaper readership
   - Magazine readership
   - Online behavior

2. **Lifestyle & Attitudes** (TGI_Q11 to TGI_Q50)
   - Shopping behavior
   - Financial products
   - Hobbies and interests
   - Health and fitness
   - Technology adoption

3. **Product Usage** (TGI_Q51 to TGI_Q100)
   - Food and drink
   - Personal care
   - Household products
   - Automotive
   - Travel

4. **Psychographics** (TGI_Q101+)
   - Values and beliefs
   - Environmental attitudes
   - Brand preferences

### Example TGI Variables

**TGI_Q2**: Main newspaper read
**TGI_Q11**: Car ownership
**TGI_Q15**: Internet usage
**TGI_Q33**: Shopping frequency
**TGI_Q100**: Brand awareness

---

## How to Use This File

### 1. View All Variables

```bash
# List all variable names
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys'

# Count variables
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys | length'
# Output: 792
```

### 2. Explore a Specific Variable

```bash
# Get social_grade details
cat Route_R56_Questionnaire_response.json | jq '.questionnaire.social_grade'

# Output:
{
  "wording": "SOCIAL GRADE",
  "mandatory": true,
  "answers": {
    "1": "A",
    "2": "B",
    "3": "C1",
    "4": "C2",
    "5": "D",
    "6": "E"
  }
}
```

### 3. Search for Variables

```bash
# Find all variables containing "age"
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys | .[] | select(contains("age"))'

# Find variables about working status
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys | .[] | select(contains("working"))'
```

### 4. Python Script to Explore

```python
#!/usr/bin/env python3
import json

# Load questionnaire
with open('Route_R56_Questionnaire_response.json', 'r') as f:
    data = json.load(f)

questionnaire = data['questionnaire']

# Print all variables with "social" in name
for var_name, var_data in questionnaire.items():
    if 'social' in var_name.lower():
        print(f"\n{var_name}:")
        print(f"  Wording: {var_data.get('wording')}")
        print(f"  Answers: {len(var_data.get('answers', {}))} options")

# Find geographic variables
geo_vars = [v for v in questionnaire.keys() if any(
    keyword in v.lower() for keyword in ['region', 'town', 'area', 'postal']
)]
print(f"\nGeographic variables: {geo_vars}")
```

---

## Common Use Cases

### Use Case 1: Build Custom Target

**Goal**: Target affluent London residents aged 35-54

**Step 1**: Find relevant variables
```bash
# Check available variables
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | {social_grade, region, age}'
```

**Step 2**: Build demographic filter
```python
demographics = [
    "social_grade=1",  # Grade A
    "social_grade=2",  # Grade B
    "region=9",        # London
    "ageband=35-54"    # Age 35-54
]
```

### Use Case 2: Regional Campaign

**Goal**: Target all demographics in North West

**Step 1**: Find region code
```bash
cat Route_R56_Questionnaire_response.json | jq '.questionnaire.region.answers'
```

**Step 2**: Use in API
```python
demographics = [
    "region=2"  # North West
]
```

### Use Case 3: Lifestyle Targeting

**Goal**: Target high internet users who own cars

**Step 1**: Find TGI variables
```bash
# Find internet usage variable
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys | .[] | select(contains("internet"))'

# Find car ownership variable
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys | .[] | select(contains("car"))'
```

**Step 2**: Build filter
```python
demographics = [
    "TGI_Q15_1=1",  # High internet usage
    "TGI_Q11=1"     # Car owner
]
```

---

## Variable Categories Reference

### Core Demographics (Always Available)
- `sex` - Gender (Male/Female)
- `social_grade` - Social grade (A, B, C1, C2, D, E)
- `region` - Government office region (11 regions)
- `tv_area` - TV area (BARB) (13 areas)

### Geographic (Always Available)
- `TOWN` - Town (1,646 towns)
- `pdist` - Postal district
- `conurbation` - Urban conurbation (if applicable)

### Geodemographic
- `ACORNCATEGORY_2024` - ACORN category
- `ACORNGROUP_2024` - ACORN group
- `ACORNTYPE_2024` - ACORN type

### Employment
- `CIE_working_status` - Working status
- `CIE_BDM_Manager_Proprietor_Supervisor` - Management role

### Lifestyle (TGI)
- 600+ TGI variables covering:
  - Media consumption
  - Product usage
  - Shopping behavior
  - Attitudes and values
  - Brand preferences

---

## Important Notes

### Mandatory vs Optional

**Mandatory Variables**:
- Always present in respondent data
- Safe to use in demographic filters
- Examples: `sex`, `social_grade`, `region`, `tv_area`

**Optional Variables**:
- May not be present for all respondents
- Use with caution - may reduce sample size significantly
- Examples: Most TGI variables

### Sample Size Considerations

**Broad Targeting** (Large Sample):
```python
demographics = ["sex=1"]  # Male only
# Sample: ~50% of total
```

**Narrow Targeting** (Small Sample):
```python
demographics = [
    "sex=1",
    "social_grade=1",      # Grade A
    "region=9",            # London
    "ACORNTYPE_2024=1",   # Specific ACORN type
    "TGI_Q15_1=1"         # Specific behavior
]
# Sample: May be <1% of total
```

**Recommendation**: Start broad, add filters incrementally while checking sample size.

---

## Testing Demographics

### Test Script

```python
#!/usr/bin/env python3
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_demographic(demographic_code):
    """Test if a demographic code is valid."""

    # Small test payload
    payload = {
        "route_release_id": "56",
        "route_algorithm_version": "10.2",
        "algorithm_figures": ["impacts"],
        "grouping": "frame_ID",
        "demographics": [demographic_code],  # Test code
        "campaign": [{
            "schedule": [{
                "datetime_from": "2025-10-11 12:00",
                "datetime_until": "2025-10-11 13:00"  # 1 hour only
            }],
            "spot_length": 10,
            "spot_break_length": 50,
            "frames": [1234567890]  # Single frame
        }],
        "target_month": 1
    }

    response = requests.post(
        f"{os.getenv('ROUTE_API_URL')}/rest/process/playout",
        json=payload,
        headers={
            'Authorization': os.getenv('ROUTE_API_AUTH'),
            'API-Key': os.getenv('ROUTE_API_KEY')
        },
        timeout=30
    )

    if response.status_code == 200:
        print(f"✅ Valid: {demographic_code}")
        return True
    else:
        print(f"❌ Invalid: {demographic_code}")
        print(f"   Error: {response.text}")
        return False

# Test examples
test_demographic("sex=1")
test_demographic("social_grade=1")
test_demographic("region=9")
test_demographic("invalid_var=1")  # Should fail
```

---

## Version History

| Release | Variables | Date Retrieved | Notes |
|---------|-----------|----------------|-------|
| R56 | 792 | 2025-10-26 | Q3 2025, current release |

---

## Quick Reference

```bash
# File location
docs/api-reference/route/Route_API_Documentation/Route_R56_Questionnaire_response.json

# View entire file
cat Route_R56_Questionnaire_response.json | jq '.'

# Count variables
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys | length'

# List all variables
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys'

# Get specific variable
cat Route_R56_Questionnaire_response.json | jq '.questionnaire.social_grade'

# Search for variables
cat Route_R56_Questionnaire_response.json | jq '.questionnaire | keys | .[] | select(contains("age"))'

# Get metadata
cat Route_R56_Questionnaire_response.json | jq '.route_release_id, .processed_datetime'
```

---

## Related Documentation

- **[ROUTE_API_CACHING_GUIDE.md](./ROUTE_API_CACHING_GUIDE.md)** - Complete caching guide
- **[EXAMPLES_QUESTIONNAIRE.md](./EXAMPLES_QUESTIONNAIRE.md)** - Usage examples
- **[QUICK_START.md](./QUICK_START.md)** - Quick start guide

---

## Support

For questions about specific variables or how to use them:

1. **Explore the JSON file** directly
2. **Test demographics** with small API calls before full cache run
3. **Check Route documentation** for variable definitions
4. **Contact Route support** for clarification on TGI variables

---

**File**: `Route_R56_Questionnaire_response.json`
**Size**: 197 KB
**Variables**: 792
**Route Release**: R56 (Q3 2025)
**Last Updated**: October 26, 2025
