# Brand Split Service - Quick Reference Card

## Import

```python
from src.services.brand_split_service import BrandSplitService
```

## Basic Usage

### Initialize Service

```python
service = BrandSplitService()
await service.initialize()

# When done:
await service.cleanup()
```

### Split Single Window

```python
brand_impacts = await service.split_audience_by_brand(
    frame_id=1234860035,
    campaign_id="16012",
    window_start=datetime(2025, 6, 1, 0, 0, 0),
    total_impacts=1000000
)

# Returns: {4950: 750000.0, 4951: 250000.0}
```

### Analyze Campaign

```python
brands = await service.get_campaign_brands(
    campaign_id="16012",
    start_date=date(2025, 6, 1),
    end_date=date(2025, 6, 30)
)

# Returns list of brands with spot counts
```

### Process Route API Response

```python
route_response = {...}  # From Route API

brand_results = await service.aggregate_brand_impacts(route_response)

# Returns brand-attributed impacts
```

## Quick Commands

### Run Tests

```bash
python src/services/test_brand_split.py
```

### Run Examples

```bash
python src/services/brand_split_integration_example.py
```

### Health Check

```python
health = await service.health_check()
print(health['status'])  # 'healthy', 'degraded', or 'unhealthy'
```

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `brand_split_service.py` | Core service | 709 |
| `test_brand_split.py` | Test suite | 392 |
| `brand_split_integration_example.py` | Examples | 458 |
| `BRAND_SPLIT_SERVICE.md` | Documentation | 1000+ |

## Key Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `split_audience_by_brand()` | Split impacts for window | `Dict[int, float]` |
| `get_brand_distribution()` | Get raw brand data | `List[Dict]` |
| `get_campaign_brands()` | Get campaign summary | `List[Dict]` |
| `aggregate_brand_impacts()` | Process full response | `Dict` |
| `get_multi_brand_windows()` | Find complex windows | `List[Dict]` |

## Database

- **Host**: 192.168.1.34 (MS-01)
- **Database**: route_poc
- **View**: mv_playout_15min_brands
- **Requires**: VPN connection

## Configuration

```python
# Custom cache TTL
service = BrandSplitService(cache_ttl=1800)

# Custom database config
from src.config.database import DatabaseConfig
db_config = DatabaseConfig()
service = BrandSplitService(db_config=db_config)
```

## Performance

| Operation | Time |
|-----------|------|
| Cache hit | ~0.1ms |
| Database query | 5-20ms |
| Single window split | <25ms |
| Full campaign | <500ms |

## Error Handling

```python
# No data found
if not brand_impacts:
    print("No brands or single brand campaign")

# Health check
health = await service.health_check()
if health['status'] != 'healthy':
    print(f"Issue: {health.get('warning', health.get('error'))}")
```

## Common Patterns

### Pattern 1: Route API Integration

```python
# Get Route data
route_data = await route_service.get_playout(campaign_id)

# Add brand attribution
brand_data = await brand_service.aggregate_brand_impacts(route_data)
```

### Pattern 2: Pre-Processing Check

```python
# Check if splitting needed
brands = await service.get_campaign_brands(campaign_id)

if len(brands) > 1:
    # Multiple brands - use brand split service
    multi_brand = await service.get_multi_brand_windows(campaign_id)
    needs_splitting = len(multi_brand) > 0
```

### Pattern 3: Export with Brands

```python
# Process campaign
brand_results = await service.aggregate_brand_impacts(route_response)

# Export
export_data = {
    'total_impacts': brand_results['total_impacts'],
    'brands': brand_results['brands']
}
```

## Troubleshooting

| Issue | Check | Fix |
|-------|-------|-----|
| Empty results | `health_check()` | View may not exist |
| Connection error | `ping 192.168.1.34` | Connect VPN |
| Slow queries | Cache entries | Clear cache |

## Next Steps

1. ✅ Service created
2. ⚠️ Create mv_playout_15min_brands view
3. 🔄 Run tests
4. 🔄 Integrate with Route service
5. 🔄 Add to exports

---

**Full Documentation**: `/Claude/Documentation/BRAND_SPLIT_SERVICE.md`
**Handover**: `/Claude/Handover/BRAND_SPLIT_SERVICE_HANDOVER.md`
