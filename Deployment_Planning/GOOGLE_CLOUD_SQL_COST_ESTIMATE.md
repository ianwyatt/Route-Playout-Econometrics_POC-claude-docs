# Google Cloud SQL PostgreSQL Cost Estimate

**Created**: 10 December 2025
**Updated**: 10 December 2025 - Revised to exclude raw playout_data table (Adwanted batch model)
**Purpose**: Cost analysis for hosting Route Playout database on Google Cloud
**Status**: Research/Planning

---

## Key Insight: Adwanted Batch Model

With the Adwanted batch extract approach (Option B), we **don't need to store raw playout_data**. Adwanted produces pre-aggregated audience data directly. This dramatically reduces storage requirements.

See: `/Users/ianwyatt/PycharmProjects/route-playout-pipeline/Claude/Documentation/Adwanted_Batch_Request/Option_B/`

---

## Current Database Size Breakdown

| Table/Category | Size | Include in Cloud? |
|----------------|------|-------------------|
| `playout_data` (raw) | **603 GB** | ❌ NO - Adwanted provides aggregated data |
| `cache_route_impacts_15min_by_demo` | 92 GB | ✅ Yes |
| `mv_playout_15min` | 14 GB | ✅ Yes |
| `mv_playout_15min_brands` | 11 GB | ✅ Yes |
| `mv_cache_campaign_impacts_frame_1hr` | 10 GB | ✅ Yes |
| All other MVs and cache tables | ~15 GB | ✅ Yes |
| **Total Database** | **745 GB** | - |
| **Excluding playout_data** | **~142 GB** | ✅ Cloud target |

### Storage Required for Cloud (Adwanted Model)

**69-Day Dataset**: ~142 GB (current MVs + cache tables)
**15-Month Dataset**: ~920 GB (extrapolated: 142 GB × 450/69 days)

---

## Adwanted Batch Deliverables (16 Tables)

From the spec, Adwanted will provide:

| Category | Tables | Description |
|----------|--------|-------------|
| Core Audience | 5 | Impacts, reach (day/week/cumulative/full) |
| Route Frame Data | 1 | Frame metadata per release |
| Playout Aggregations | 3 | 15-min windows, daily/hourly counts |
| Reference Tables | 7 | Buyers, brands, agencies, media owners, etc. |

This replaces the need for raw playout storage entirely.

---

## Current Database Specifications

### 69-Day Dataset (Current POC) - Cloud Target
- **Storage (excluding raw playouts)**: ~142 GB
- **Date Range**: Aug 6 - Oct 13, 2025 (69 days)
- **Campaigns**: 826 campaigns

### 15-Month Dataset (Full Production Estimate)
- **Estimated Storage**: ~920 GB (extrapolated)
- **Date Range**: ~450 days (Sep 2024 onwards)

---

## Google Cloud SQL Pricing Components (2025)

Sources: [Google Cloud SQL Pricing](https://cloud.google.com/sql/docs/postgres/pricing), [NetApp Cheat Sheet](https://www.netapp.com/blog/gcp-cvo-blg-google-cloud-sql-pricing-and-limits-a-cheat-sheet/), [Pump.co Guide](https://www.pump.co/blog/google-cloud-sql-pricing)

### Storage Costs

| Storage Type | Price/GB/Month | Notes |
|--------------|----------------|-------|
| SSD (recommended) | $0.17 - $0.22 | Varies by region |
| HDD | ~$0.12 | Lower performance |
| Backup | ~$0.11 | Per GB/month |

### Compute Costs (Enterprise Edition)

| vCPUs | Memory | On-Demand/Hour | On-Demand/Month |
|-------|--------|----------------|-----------------|
| 2 | 8 GB | ~$0.19 | ~$139 |
| 4 | 15 GB | ~$0.39 | ~$282 |
| 8 | 32 GB | ~$0.78 | ~$565 |
| 16 | 64 GB | ~$1.56 | ~$1,130 |

**Committed Use Discounts**:
- 1-year commitment: **25% off** compute
- 3-year commitment: **52% off** compute
- Note: Discounts do NOT apply to storage

### Network Costs

| Type | Price |
|------|-------|
| Same region (to GCP services) | Free |
| Cross-region/continent | $0.19/GB |
| Idle IPv4 address | $0.0131/hour (~$9.55/month) |

---

## Cost Estimates: 69-Day Dataset (~142 GB) - Adwanted Model

### Option A: Minimum Viable (Development/Demo)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 2 vCPU, 8 GB RAM | $139 |
| Storage (SSD) | 150 GB @ $0.20/GB | $30 |
| Backups | 150 GB @ $0.11/GB | $17 |
| **Total** | | **~$186/month** |

### Option B: Production Ready
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 4 vCPU, 16 GB RAM | $282 |
| Storage (SSD) | 150 GB @ $0.20/GB | $30 |
| Backups | 150 GB @ $0.11/GB | $17 |
| High Availability | +100% compute | $282 |
| **Total** | | **~$611/month** |

### Option C: Production + 1-Year Commitment
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute (25% off) | 4 vCPU, 16 GB RAM | $212 |
| Storage (SSD) | 150 GB @ $0.20/GB | $30 |
| Backups | 150 GB @ $0.11/GB | $17 |
| High Availability | +100% compute (discounted) | $212 |
| **Total** | | **~$471/month** |

---

## Cost Estimates: 15-Month Dataset (~920 GB) - Adwanted Model

### Option A: Minimum Viable
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 4 vCPU, 16 GB RAM | $282 |
| Storage (SSD) | 1,000 GB @ $0.20/GB | $200 |
| Backups | 1,000 GB @ $0.11/GB | $110 |
| **Total** | | **~$592/month** |

### Option B: Production Ready (HA)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 8 vCPU, 32 GB RAM | $565 |
| Storage (SSD) | 1,000 GB @ $0.20/GB | $200 |
| Backups | 1,000 GB @ $0.11/GB | $110 |
| High Availability | +100% compute | $565 |
| **Total** | | **~$1,440/month** |

### Option C: Production + 1-Year Commitment (25% off compute)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute (25% off) | 8 vCPU, 32 GB RAM | $424 |
| Storage (SSD) | 1,000 GB @ $0.20/GB | $200 |
| Backups | 1,000 GB @ $0.11/GB | $110 |
| High Availability | +100% compute (discounted) | $424 |
| **Total** | | **~$1,158/month** |

---

## Comparison: Cloud vs Self-Hosted

### Current Self-Hosted (MS-01 Proxmox)

| Item | Cost |
|------|------|
| Hardware | Already owned |
| Electricity | ~$20-40/month |
| Maintenance | Staff time |
| **Total** | **~$40/month** + staff time |

**Pros**: Cheap, fast LAN access, no egress costs
**Cons**: No external access, single point of failure, manual backups

### Google Cloud SQL (Adwanted Model - No Raw Playouts)

| Dataset | Min Cost | Production (HA) | With 1yr Commit |
|---------|----------|-----------------|-----------------|
| 69-day (~142 GB) | **$186/month** | $611/month | $471/month |
| 15-month (~920 GB) | **$592/month** | $1,440/month | $1,158/month |

**Pros**: Managed service, automatic backups, HA available, external access
**Cons**: Ongoing cost, egress charges, latency vs LAN

---

## Recommendations

### For Demo/POC Phase
**Stay with MS-01** - Use Pangolin for external access
- Cost: ~$0 (existing infrastructure)
- Use Pangolin tunnel for external demos

### For Production (External Users)
**Google Cloud SQL is now viable** with Adwanted model:

| Scenario | Storage | Monthly Cost |
|----------|---------|--------------|
| 69-day, minimal | 142 GB | ~$186 |
| 69-day, production HA | 142 GB | ~$471 (1yr commit) |
| 15-month, minimal | 920 GB | ~$592 |
| 15-month, production HA | 920 GB | ~$1,158 (1yr commit) |

### Cost Comparison Summary

| Approach | 69-Day | 15-Month |
|----------|--------|----------|
| MS-01 + Pangolin | ~$40/month | ~$40/month |
| Cloud SQL (minimal) | ~$186/month | ~$592/month |
| Cloud SQL (prod + commit) | ~$471/month | ~$1,158/month |

### Key Savings from Adwanted Model

By excluding raw `playout_data` (603 GB):
- **69-day storage**: 596 GB → 142 GB (76% reduction)
- **15-month storage**: ~3.9 TB → ~920 GB (76% reduction)
- **Monthly cost savings**: ~$500-2,000/month depending on tier

---

## Alternative: AlloyDB (Google's PostgreSQL-compatible)

AlloyDB is Google's high-performance PostgreSQL-compatible database with a disaggregated architecture (separate compute and storage).

### AlloyDB vs Cloud SQL Comparison

| Feature | Cloud SQL | AlloyDB |
|---------|-----------|---------|
| Transactional performance | Baseline | **4x faster** |
| Analytical queries | Baseline | **100x faster** |
| Uptime SLA | 99.95% | **99.99%** |
| Recovery time | Minutes | **<60 seconds** |
| Columnar engine (HTAP) | No | **Yes** |
| Storage auto-scaling | Manual | **Automatic** |
| I/O charges | None | **None** |
| PostgreSQL compatibility | Full | Full |

### AlloyDB Pricing (us-central1 region)

| Component | Price |
|-----------|-------|
| vCPU | $0.0661/hour (~$48/month) |
| Memory | $0.0112/GB/hour (~$8/GB/month) |
| Storage | $0.339/GB/month |
| Backups | $0.113/GB/month |

**Committed Use Discounts**: 25% off (1-year), 52% off (3-year) - applies to compute only

### AlloyDB Cost Estimates: 69-Day Dataset (~142 GB)

#### Option A: Minimal (2 vCPU, 16 GB RAM)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 2 vCPU @ $48/vCPU | $96 |
| Memory | 16 GB @ $8/GB | $128 |
| Storage | 150 GB @ $0.34/GB | $51 |
| Backups | 150 GB @ $0.11/GB | $17 |
| **Total** | | **~$292/month** |

#### Option B: Production HA (4 vCPU, 32 GB RAM, 2 nodes)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 4 vCPU × 2 nodes @ $48/vCPU | $384 |
| Memory | 32 GB × 2 nodes @ $8/GB | $512 |
| Storage | 150 GB @ $0.34/GB | $51 |
| Backups | 150 GB @ $0.11/GB | $17 |
| **Total** | | **~$964/month** |

#### Option C: Production HA + 1-Year Commitment (25% off compute)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute (25% off) | 4 vCPU × 2 nodes | $288 |
| Memory (25% off) | 32 GB × 2 nodes | $384 |
| Storage | 150 GB @ $0.34/GB | $51 |
| Backups | 150 GB @ $0.11/GB | $17 |
| **Total** | | **~$740/month** |

### AlloyDB Cost Estimates: 15-Month Dataset (~920 GB)

#### Option A: Minimal (4 vCPU, 32 GB RAM)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 4 vCPU @ $48/vCPU | $192 |
| Memory | 32 GB @ $8/GB | $256 |
| Storage | 1,000 GB @ $0.34/GB | $340 |
| Backups | 1,000 GB @ $0.11/GB | $113 |
| **Total** | | **~$901/month** |

#### Option B: Production HA (8 vCPU, 64 GB RAM, 2 nodes)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute | 8 vCPU × 2 nodes @ $48/vCPU | $768 |
| Memory | 64 GB × 2 nodes @ $8/GB | $1,024 |
| Storage | 1,000 GB @ $0.34/GB | $340 |
| Backups | 1,000 GB @ $0.11/GB | $113 |
| **Total** | | **~$2,245/month** |

#### Option C: Production HA + 1-Year Commitment (25% off compute)
| Component | Specification | Monthly Cost |
|-----------|---------------|--------------|
| Compute (25% off) | 8 vCPU × 2 nodes | $576 |
| Memory (25% off) | 64 GB × 2 nodes | $768 |
| Storage | 1,000 GB @ $0.34/GB | $340 |
| Backups | 1,000 GB @ $0.11/GB | $113 |
| **Total** | | **~$1,797/month** |

---

## Full Comparison: Cloud SQL vs AlloyDB

### 69-Day Dataset (~142 GB)

| Option | Cloud SQL | AlloyDB | Difference |
|--------|-----------|---------|------------|
| Minimal | $186/month | $292/month | +57% |
| Production HA | $611/month | $964/month | +58% |
| Prod HA + 1yr | $471/month | $740/month | +57% |

### 15-Month Dataset (~920 GB)

| Option | Cloud SQL | AlloyDB | Difference |
|--------|-----------|---------|------------|
| Minimal | $592/month | $901/month | +52% |
| Production HA | $1,440/month | $2,245/month | +56% |
| Prod HA + 1yr | $1,158/month | $1,797/month | +55% |

### When to Choose AlloyDB Over Cloud SQL

**Choose AlloyDB if:**
- Analytical queries are slow on Cloud SQL (AlloyDB is 100x faster)
- You need sub-minute failover recovery
- Running HTAP workloads (transactional + analytical)
- Query performance is more important than cost

**Stick with Cloud SQL if:**
- Budget is the primary concern
- Current query performance is acceptable
- Workload is primarily transactional (not heavy analytics)
- Starting out and want to keep costs low

### Recommendation for Route

**Start with Cloud SQL** (~$186-592/month minimal) and monitor query performance. If analytical queries become slow with the 15-month dataset, evaluate AlloyDB migration. The 100x analytical speedup could justify the ~55% cost increase.

**AlloyDB Free Trial**: 30 days free with up to 1TB storage and 8 vCPU instances - worth testing before committing

---

## Other Hosting Alternatives

### Quick Comparison: All Options

| Provider | 69-Day (~150GB) | 15-Month (~1TB) | Notes |
|----------|-----------------|-----------------|-------|
| **Route Office Proxmox** | **~$0-40** | **~$0-40** | Self-hosted, Pangolin for access |
| **DigitalOcean Storage Opt** | N/A (min 1TB) | **$367** (single) / $734 (HA) | Best value for 1TB |
| **DigitalOcean Basic** | **$162** / $325 (HA) | $393 / $786 (HA) | Best for <200GB |
| **Google Cloud SQL** | $186-471 | $592-1,158 | Managed, standard choice |
| **AWS RDS PostgreSQL** | ~$150-300 | ~$400-800 | Complex pricing, mature |
| **Neon** | ~$150-350 | ~$500-900 | Serverless, scale-to-zero |
| **Google AlloyDB** | $292-740 | $901-1,797 | 100x faster analytics |
| **Supabase** | ~$100-200 | Not ideal >100GB | Great for small apps |

### Best Cloud Options by Dataset Size

| Dataset | Best Option | Monthly Cost |
|---------|-------------|--------------|
| 69-day (~150GB) | DigitalOcean Basic (8GB/4vCPU/160GB) | **$162** |
| 15-month (~1TB) | DigitalOcean Storage Optimized (16GB/2vCPU/1TB) | **$367** |

### Detailed Alternatives

#### AWS RDS PostgreSQL
- **Storage**: $0.115/GB/month (gp3 SSD)
- **Compute**: Varies by instance (db.t3.medium ~$50/month, db.r5.large ~$180/month)
- **150GB estimate**: ~$150-300/month (single-AZ)
- **1TB estimate**: ~$400-800/month (single-AZ)
- **Pros**: Mature, lots of tooling, Multi-AZ HA
- **Cons**: Complex pricing, hidden costs (IOPS, transfer)
- [AWS RDS Pricing](https://aws.amazon.com/rds/postgresql/pricing/)

#### DigitalOcean Managed PostgreSQL (Actual Pricing)

**Single Node (Basic Premium Intel):**

| Memory | vCPUs | Disk | $/month |
|--------|-------|------|---------|
| 1 GiB | 1 | 20 GiB | $20.30 |
| 2 GiB | 1 | 50 GiB | $40.75 |
| 4 GiB | 2 | 80 GiB | $81.20 |
| 8 GiB | 2 | 100 GiB | $110.50 |
| 8 GiB | 4 | 160 GiB | **$162.40** ← 69-day dataset |
| 16 GiB | 4 | 1,000 GiB | $393.00 |
| 32 GiB | 8 | 1,010 GiB | $573.15 |

**Storage Optimized (Best for 1TB+ datasets):**

| Memory | vCPUs | Disk | $/month |
|--------|-------|------|---------|
| 16 GiB | 2 | 1,000 GiB | **$367.00** ← 15-month dataset (BEST VALUE) |
| 32 GiB | 4 | 600 GiB | $431.00 |
| 64 GiB | 8 | 1,200 GiB | $868.00 |
| 128 GiB | 16 | 2,400 GiB | $1,734.00 |

**With 1 Additional Node (HA):**

| Tier | Config | $/month |
|------|--------|---------|
| Basic | 8 GiB, 4 vCPU, 160 GiB | **$324.80** ← 69-day HA |
| Storage Opt | 16 GiB, 2 vCPU, 1 TB | **~$734** ← 15-month HA |

**Route Dataset Estimates:**
- **69-day (~150GB)**: $162/month single, $325/month HA (Basic tier)
- **15-month (~1TB)**: **$367/month** single, ~$734/month HA (Storage Optimized)

**RAM Requirements for 50-100 Users:**
- PostgreSQL base: ~256MB
- Per connection (100 max): ~1GB
- Shared buffers for MV caching: 2-4GB
- OS overhead: ~1GB
- **Total needed: 4-8GB** → 16GB provides comfortable headroom

**Pros**: Simple pricing, no surprises, storage included, Storage Optimized tier
**Cons**: Fewer regions, less enterprise features
- [DigitalOcean Pricing](https://www.digitalocean.com/pricing/managed-databases)

#### Neon (Serverless PostgreSQL)
- **Free**: 0.5GB storage, 191 compute hours
- **Launch**: $19/month (10GB storage included)
- **Scale**: $69/month (50GB storage included)
- **Extra storage**: ~$0.35/GB/month
- **150GB estimate**: ~$150-350/month (Scale + overages)
- **1TB estimate**: ~$500-900/month
- **Pros**: Serverless, scale-to-zero, branching, modern
- **Cons**: Expensive at scale, still maturing
- **Note**: Acquired by Databricks (May 2025)
- [Neon Pricing](https://neon.com/pricing)

#### Supabase
- **Free**: 500MB database, 50K MAU
- **Pro**: $25/month (8GB database included)
- **Team**: $599/month (more compliance features)
- **Extra storage**: Usage-based
- **150GB estimate**: ~$100-200/month
- **Pros**: Great DX, auth/APIs included, real-time
- **Cons**: Not designed for large analytical DBs
- **Best for**: Apps <100GB, need auth/APIs
- [Supabase Pricing](https://supabase.com/pricing)

### Recommendation Matrix

| Use Case | Recommended | Why |
|----------|-------------|-----|
| **Development/Demo** | Route Office Proxmox | Free, fast LAN |
| **Production (budget)** | DigitalOcean | Simple, predictable |
| **Production (enterprise)** | Google Cloud SQL | Managed, scalable |
| **Heavy analytics** | Google AlloyDB | 100x faster queries |
| **Variable workload** | Neon | Scale-to-zero |
| **Full-stack app** | Supabase | Auth/APIs included |

### Route Office Proxmox (Preferred)

**Update**: Planning to use Route's office Proxmox server instead of MS-01.

| Item | Cost |
|------|------|
| Hardware | Company infrastructure |
| Electricity | Office overhead |
| External access | Pangolin tunnel (free) |
| **Total** | **~$0-40/month** |

**Advantages over MS-01**:
- Office network (more reliable?)
- Accessible during office hours
- Company-managed infrastructure
- Pangolin tunnel for external access

**Architecture**:
```
┌─────────────────────────────────────────────────┐
│            Route Office Proxmox                  │
│  ┌─────────────────────────────────────────┐    │
│  │         PostgreSQL Database              │    │
│  │    (Adwanted batch data, ~142GB-1TB)    │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
                      ↑
                      │ Pangolin/Newt Tunnel
                      ↓
┌─────────────────────────────────────────────────┐
│                 VPS (Pangolin)                   │
│  ┌─────────────────────────────────────────┐    │
│  │         Streamlit UI + Pocket ID         │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
                      ↑
                      │ HTTPS
                      ↓
                 External Users
```

---

## Next Steps

1. [ ] Get exact storage breakdown (raw vs MVs vs indexes)
2. [ ] Test Cloud SQL with MV-only dataset
3. [ ] Benchmark query performance Cloud SQL vs MS-01
4. [ ] Evaluate AlloyDB for large dataset scenario
5. [ ] Consider BigQuery for historical analytics (cold storage)

---

## Sources

- [Google Cloud SQL Pricing](https://cloud.google.com/sql/docs/postgres/pricing)
- [Google Cloud SQL Pricing Cheat Sheet - NetApp](https://www.netapp.com/blog/gcp-cvo-blg-google-cloud-sql-pricing-and-limits-a-cheat-sheet/)
- [Google Cloud SQL Pricing Guide - Pump.co](https://www.pump.co/blog/google-cloud-sql-pricing)
- [Understanding Google Cloud SQL Pricing - Bytebase](https://www.bytebase.com/blog/understanding-google-cloud-sql-pricing/)
- [PostgreSQL Hosting Comparison 2025 - Bytebase](https://www.bytebase.com/blog/postgres-hosting-options-pricing-comparison/)

---

*Document created for planning purposes. Prices are estimates and may vary by region.*
