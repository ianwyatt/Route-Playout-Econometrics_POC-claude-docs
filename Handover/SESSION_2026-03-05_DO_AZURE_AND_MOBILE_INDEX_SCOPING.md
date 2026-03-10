# Session Handover: DO/Azure Deployment + Mobile Index Feature Scoping

**Date:** 5 March 2026
**Session Focus:** Deployment platform decision, mobile data index feature scoping

---

## What Was Done

### 1. DigitalOcean Deployment Runbook (Previous Session, 10 Feb)

- Full deployment runbook created: `Claude/docs/Documentation/DIGITALOCEAN_DEPLOYMENT_RUNBOOK.md`
- **Key decision: Option A (zero code changes)** for SSL support
  - `PGSSLMODE=require` set in DO `.env` file
  - libpq reads this natively via python-dotenv -> os.environ -> psycopg2
  - No modifications to `connection.py` or any source file
  - Public GitHub repo and Adwanted's local setup completely unaffected

### 2. Azure vs DigitalOcean (This Session)

- Doctor Biz has a Visual Studio subscription with $50/month Azure credit
- Azure pricing fits within $50: B2s DB (~$26) + 64 GB storage (~$7) + B1s VM (~$7) = ~$40/mo
- **Caveat:** VS subscription credits are dev/test only (not production), acceptable for POC
- Azure requires SSL for managed PostgreSQL — same `PGSSLMODE=require` approach works
- Runbook commands (systemd, Caddy, UFW, PocketID) are identical on Azure Ubuntu VM
- **Decision pending:** Azure vs DO — Azure is free (credit), DO is $67/mo
- Skipped Azure Cache for Redis — unnecessary, app uses pre-built cache tables + `@st.cache_data`

### 3. Mobile Data Index Feature — Scoping Started

New feature request to overlay mobile volume indexes onto impact data. See next section.

---

## Mobile Data Index Feature — Brief

**What:** Overlay mobile device volume data as a multiplicative index on playout impacts.

**Data flow:**
1. Analyst provides pre-calculated indexes: `frame_id + datetime + index_value`
2. Indexes based on Output Area (OA) mobile volumes vs yearly average
3. 2024 data date-shifted to match 2025 playout dates (same day-of-week mapping)
4. Index applied at frame level, per hour, to impacts only (NOT reach/cover/GRP/frequency)

**Scope:**
- UI toggle to apply/remove mobile index overlay
- Frame-level application confirmed
- Campaign-level aggregation TBD (multiply frame audiences by index, then sum)
- Feed through to CSV/Excel exports when enabled
- Exploratory/POC — testing suitability of mobile data as a factor

**Key constraints:**
- Impacts only — reach, cover, GRP, frequency are unaffected
- 69-day playout window in 2025
- Date shifting: Wed 28 Aug 2024 -> Thu 29 Aug 2025 (day-of-week alignment)

**Status:** Brainstorming/scoping in progress

---

## Files Created/Modified This Session

| File | Action |
|------|--------|
| `Claude/handover/SESSION_2026-03-05_DO_AZURE_AND_MOBILE_INDEX_SCOPING.md` | Created — this file |

---

## What's Next

1. Complete brainstorming/scoping of mobile index feature
2. Decide Azure vs DO for deployment
3. Execute deployment runbook on chosen platform

---

*Last Updated: 5 March 2026*
