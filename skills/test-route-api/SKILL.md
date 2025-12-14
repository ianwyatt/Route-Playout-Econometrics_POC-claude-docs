---
name: test-route-api
description: Test Route API connectivity and reach calculations. Use when debugging Route API integration, verifying API authentication, or testing audience calculations.
---

# Test Route API

Test Route API endpoint connectivity and verify audience calculations.

## Commands

```bash
# Basic connectivity test
python skills/route_api/test_reach_calculation.py

# Test with specific frames
python skills/route_api/test_reach_calculation.py --frame-ids 1234567,7654321 --date 2025-07-28

# Verbose output
python skills/route_api/test_reach_calculation.py --verbose
```

## When to Use

- "Test the Route API"
- "Is Route API working?"
- "Check API connection"
- Debugging audience calculation issues
- Verifying API credentials

## Output

Shows:
- API connectivity status
- Authentication result
- Sample audience calculation
- Response times
