# Snowflake Deployment Discovery - Route Playout Econometrics POC

**Created:** 9 December 2025
**Status:** Discovery / Planning
**Author:** Claude (reviewed by Doctor Biz)

---

## Executive Summary

Deploying the Route Playout Econometrics POC to Snowflake is **feasible but requires significant work**. The main challenges are:

| Area | Difficulty | Effort |
|------|------------|--------|
| User authentication | ✅ Easy | Built-in with Snowflake RBAC |
| External user access | ✅ Easy | Create users in your account for anyone |
| Data migration | ⚠️ Medium | SQL syntax changes, type mappings |
| Streamlit app migration | ⚠️ Medium | Database layer rewrite, package constraints |
| External API access | ⚠️ Medium | Requires External Access Integrations |
| Materialized views | ⚠️ Medium | Must convert to Dynamic Tables |

**Estimated effort:** 2-4 weeks of development work

**Key advantage:** You can create user accounts for **external users** (clients, partners, econometricians) who don't have their own Snowflake subscription - they log into YOUR account with credentials you provide.

---

## 1. What Snowflake Offers

### 1.1 Streamlit in Snowflake (SiS)

Snowflake has **native Streamlit hosting** with these benefits:

- **Built-in authentication** - Users log into Snowflake, app access via RBAC
- **No infrastructure** - Snowflake hosts and scales the app
- **Direct data access** - Queries run inside Snowflake (no external DB connections)
- **Security** - Data never leaves Snowflake's environment
- **Current version:** Streamlit 1.46 supported (as of late 2025)

### 1.2 User Authentication (Your Requirement)

**Yes, this is straightforward.** Snowflake provides:

| Feature | How It Works |
|---------|--------------|
| Username/password | Standard Snowflake login |
| SSO (SAML/OAuth) | Integrate with your IdP (Okta, Azure AD, etc.) |
| MFA | Optional, configurable per user |
| Role-based access | Grant `USAGE` on app to specific roles |
| Audit logging | All access logged in Snowflake |

**Access control example:**
```sql
-- Create role for POC users
CREATE ROLE route_playout_viewer;

-- Grant access to the Streamlit app
GRANT USAGE ON STREAMLIT route_playout_poc TO ROLE route_playout_viewer;

-- Assign users to the role
GRANT ROLE route_playout_viewer TO USER analyst1;
GRANT ROLE route_playout_viewer TO USER analyst2;
```

**Owner's Rights Model:** Apps run with the owner's privileges, not the viewer's. Viewers don't need direct table access - the app provides it.

---

## 2. Critical Blockers & Challenges

### 2.1 🚨 BLOCKER: No Direct PostgreSQL Access

**Current state:** App connects to MS-01 PostgreSQL database via `psycopg2`/`asyncpg`.

**Problem:**
- `psycopg2` is **not available** in Snowflake's Anaconda channel (requires compiled extensions)
- Even if available, external database connections need explicit configuration

**Solution:** Must migrate all data to Snowflake first. Cannot query PostgreSQL from SiS.

### 2.2 ⚠️ External API Access (Route API, SPACE API)

**Current state:** App calls external APIs for reach calculations (placeholder code, not currently used).

**In Snowflake:** External HTTP calls require configuration:

```sql
-- 1. Create network rule
CREATE NETWORK RULE route_api_rule
  TYPE = HOST_PORT
  VALUE_LIST = ('route.mediatelapi.co.uk:443');

-- 2. Create secret for API key
CREATE SECRET route_api_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = 'your-api-key';

-- 3. Create external access integration
CREATE EXTERNAL ACCESS INTEGRATION route_api_integration
  ALLOWED_NETWORK_RULES = (route_api_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (route_api_secret)
  ENABLED = TRUE;

-- 4. Attach to Streamlit app
ALTER STREAMLIT route_playout_poc
  SET EXTERNAL_ACCESS_INTEGRATIONS = (route_api_integration)
  SECRETS = ('route_api_key' = route_api_secret);
```

**Verdict:** Possible, but adds complexity.

### 2.3 ⚠️ Package Availability

**Available in Snowflake Anaconda channel:**
- ✅ streamlit (1.46)
- ✅ pandas
- ✅ numpy
- ✅ plotly
- ✅ openpyxl (must add to environment.yml)

**NOT available:**
- ❌ psycopg2 / asyncpg (PostgreSQL drivers)
- ❌ httpx (use `requests` instead with External Access)

**Must verify:**
- ⚠️ Any other dependencies

### 2.4 ⚠️ Caching Behaviour Change

**Current:** `st.cache_data` persists across sessions and users.

**In Snowflake:** Cache is **per-session only**. No cross-user or cross-session cache.

**Impact:** First load for each user may be slower. Consider:
- Pre-computing aggregations in Snowflake tables
- Using Snowflake's result cache (24hr TTL, automatic)

### 2.5 ⚠️ UI Limitations

| Feature | Status in SiS |
|---------|---------------|
| `st.segmented_control` | ✅ Works (Streamlit 1.39+) |
| `st.download_button` | ✅ Works (32MB limit) |
| `st.set_page_config(page_title=...)` | ❌ Not supported |
| `st.set_page_config(page_icon=...)` | ❌ Not supported |
| Custom CSS (unsafe_allow_html) | ⚠️ Limited (CSP restrictions) |
| Logo from filesystem | ⚠️ Must embed or use Snowflake stage |

---

## 3. Data Migration

### 3.1 Tables to Migrate

| Table | Size (Est.) | Priority | Notes |
|-------|-------------|----------|-------|
| `mv_campaign_browser` | Small | High | Main listing view |
| `mv_frame_audience_daily` | Large (~3M rows) | High | Frame-day impacts |
| `mv_frame_audience_hourly` | Very Large (~46M rows) | High | Frame-hour impacts |
| `cache_campaign_reach_day` | Medium | High | Daily reach metrics |
| `cache_campaign_reach_week` | Medium | High | Weekly reach metrics |
| `cache_campaign_reach_full` | Medium | High | Campaign totals |
| `cache_route_impacts_15min` | Very Large | Medium | Raw impacts cache |
| `cache_space_*` | Small | Low | SPACE API lookups |

### 3.2 Critical Type Conversions

| PostgreSQL | Snowflake | ⚠️ Watch Out |
|------------|-----------|--------------|
| `NUMERIC(15,3)` | `NUMBER(15,3)` | **MUST specify precision** or data rounds to integers! |
| `TIMESTAMP` | `TIMESTAMP_NTZ` | Use `_NTZ` variant to match PostgreSQL |
| `VARCHAR[]` | `VARIANT` | Arrays work differently - use VARIANT for JSON arrays |
| `BOOLEAN` | `BOOLEAN` | Direct mapping |

### 3.3 SQL Syntax Changes Required

**FILTER clause (not supported):**
```sql
-- PostgreSQL
ARRAY_AGG(DISTINCT name) FILTER (WHERE name IS NOT NULL)

-- Snowflake
ARRAY_AGG(DISTINCT CASE WHEN name IS NOT NULL THEN name END)
```

**DISTINCT ON (not supported):**
```sql
-- PostgreSQL
SELECT DISTINCT ON (campaign_id) * FROM playouts ORDER BY campaign_id, date DESC;

-- Snowflake
SELECT * FROM playouts QUALIFY ROW_NUMBER() OVER (PARTITION BY campaign_id ORDER BY date DESC) = 1;
```

**Date arithmetic:**
```sql
-- PostgreSQL
WHERE date >= CURRENT_DATE - INTERVAL '7 days'

-- Snowflake
WHERE date >= DATEADD(day, -7, CURRENT_DATE())
```

**UPSERT:**
```sql
-- PostgreSQL
INSERT INTO table VALUES (...) ON CONFLICT (id) DO UPDATE SET ...

-- Snowflake
MERGE INTO table AS target
USING (SELECT ...) AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```

### 3.4 Materialized Views → Dynamic Tables

PostgreSQL MVs must be converted. **Recommended approach: Dynamic Tables**

```sql
-- Snowflake Dynamic Table (replaces PostgreSQL MV)
CREATE DYNAMIC TABLE dyn_campaign_browser
  TARGET_LAG = '1 hour'  -- Auto-refresh within 1 hour of base table changes
  WAREHOUSE = 'route_wh_xsmall'
AS
  SELECT
    campaign_id,
    -- ... rest of query with Snowflake syntax
  FROM cache_campaign_reach_day
  JOIN ...;
```

**Benefits over Snowflake MVs:**
- More flexible SQL (fewer restrictions)
- Configurable refresh lag
- No Enterprise Edition requirement for basic features

---

## 4. Application Code Changes

### 4.1 Database Layer Rewrite

**Current:** `src/db/streamlit_queries.py` uses `psycopg2`

**New:** Must use `snowflake-snowpark-python`

```python
# Current (PostgreSQL)
import psycopg2
conn = psycopg2.connect(host="192.168.1.34", database="route_poc", ...)
cursor = conn.cursor()
cursor.execute("SELECT * FROM mv_campaign_browser")

# New (Snowflake)
from snowflake.snowpark.context import get_active_session
session = get_active_session()
df = session.sql("SELECT * FROM dyn_campaign_browser").to_pandas()
```

### 4.2 Files Requiring Changes

| File | Change Required |
|------|-----------------|
| `src/db/connection.py` | Replace PostgreSQL pool with Snowflake session |
| `src/db/streamlit_queries.py` | Rewrite all queries for Snowpark |
| `src/db/queries/*.py` | Rewrite all query modules |
| `src/ui/app.py` | Update database connection logic, remove psycopg2 imports |
| `src/services/cache_service.py` | Rewrite for Snowflake (if used) |

### 4.3 Logo/Asset Handling

**Current:** Logo loaded from filesystem
```python
logo_path = Path(__file__).parent / "assets" / "Route Logo White-01.png"
```

**In Snowflake:** Must use one of:
1. **Base64 embed** in code (increases app size)
2. **Snowflake stage** - upload to `@stage/assets/logo.png`
3. **External URL** (requires external access integration)

---

## 5. Authentication Deep Dive

### 5.1 How It Works

```
User → Snowflake Login → Role Check → Streamlit App Access
         ↓                    ↓
    MFA (optional)     RBAC grants USAGE
```

### 5.2 Role-Based Access Control

```sql
-- Create roles
CREATE ROLE route_playout_admin;    -- Can modify app
CREATE ROLE route_playout_analyst;  -- Can view only

-- Grant app access
GRANT USAGE ON STREAMLIT my_db.my_schema.route_playout_poc
  TO ROLE route_playout_analyst;

-- Grant data access (owner's rights makes this optional for basic viewing)
GRANT SELECT ON ALL TABLES IN SCHEMA my_schema
  TO ROLE route_playout_analyst;

-- Assign users
GRANT ROLE route_playout_analyst TO USER john_smith;
```

### 5.3 SSO Integration

Snowflake supports:
- SAML 2.0 (Okta, Azure AD, OneLogin, etc.)
- OAuth 2.0 (for programmatic access)
- SCIM (user provisioning)

Configuration is at the Snowflake account level, not app-specific.

### 5.4 External Users (Clients, Partners, Econometricians) ⭐

**This is a key Snowflake advantage.** You can create user accounts for anyone - they don't need their own Snowflake subscription.

#### How It Works

```
Your Snowflake Account (you pay for it)
├── Internal Users (your team)
│   ├── john.smith@route.org.uk
│   └── jane.doe@route.org.uk
│
└── External Users (no Snowflake subscription needed)
    ├── analyst@clientcompany.com
    ├── researcher@university.ac.uk
    ├── consultant@mediaagency.com
    └── econometrician@brandowner.com
```

All users log into **your account** - you control everything, you pay the compute costs.

#### Creating External Users

```sql
-- Create external user with their email as login
CREATE USER external_analyst
  LOGIN_NAME = 'analyst@clientcompany.com'
  EMAIL = 'analyst@clientcompany.com'
  DISPLAY_NAME = 'External Analyst - Client Company'
  DEFAULT_ROLE = 'route_playout_viewer'
  DEFAULT_WAREHOUSE = 'route_wh_xsmall'
  MUST_CHANGE_PASSWORD = TRUE;

-- Create restrictive role for external users
CREATE ROLE external_viewer;

-- Grant ONLY Streamlit app access (no raw data, no SQL)
GRANT USAGE ON STREAMLIT my_db.my_schema.route_playout_poc
  TO ROLE external_viewer;

-- Assign user to role
GRANT ROLE external_viewer TO USER external_analyst;
```

#### What External Users Can and Cannot Do

| Capability | Internal Users | External Users (Restricted) |
|------------|----------------|----------------------------|
| Login with own credentials | ✅ | ✅ |
| MFA enforcement | ✅ | ✅ |
| Access Streamlit app | ✅ | ✅ |
| View data through app | ✅ | ✅ |
| Export data (via app) | ✅ | ✅ (if app allows) |
| Run SQL queries directly | ✅ | ❌ (unless granted) |
| Access raw tables | ✅ | ❌ (unless granted) |
| Create own warehouses | ✅ | ❌ |
| Modify app | Admin only | ❌ |

#### Security Controls for External Users

```sql
-- Create a network policy to restrict external user access by IP (optional)
CREATE NETWORK POLICY external_users_policy
  ALLOWED_IP_LIST = ('203.0.113.0/24', '198.51.100.0/24')  -- Client office IPs
  BLOCKED_IP_LIST = ();

-- Apply to specific users
ALTER USER external_analyst SET NETWORK_POLICY = external_users_policy;

-- Set session timeout (force re-login after period)
ALTER USER external_analyst SET MINS_TO_BYPASS_MFA = 0;  -- Always require MFA
ALTER USER external_analyst SET CLIENT_SESSION_KEEP_ALIVE = FALSE;

-- Disable user when project ends
ALTER USER external_analyst SET DISABLED = TRUE;
```

#### Cost Implications

External users consume **your** Snowflake credits:

| Activity | Who Pays | Control |
|----------|----------|---------|
| App usage (queries) | You | Warehouse auto-suspend limits costs |
| Data exports | You | App can limit export size |
| Storage | You | N/A - data is yours |

**Cost management tips:**
- Set warehouse auto-suspend to 60 seconds
- Use XSMALL warehouse for external users
- Monitor usage via `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- Set resource monitors to alert on high usage

```sql
-- Monitor external user activity
SELECT
  user_name,
  COUNT(*) as query_count,
  SUM(credits_used_cloud_services) as credits_used
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE user_name = 'EXTERNAL_ANALYST'
  AND start_time > DATEADD(day, -30, CURRENT_TIMESTAMP())
GROUP BY user_name;
```

#### Audit Trail

Every external user action is logged:

```sql
-- View login history for external user
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY
WHERE user_name = 'EXTERNAL_ANALYST'
ORDER BY event_timestamp DESC
LIMIT 100;

-- View what they accessed
SELECT *
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE user_name = 'EXTERNAL_ANALYST'
ORDER BY query_start_time DESC;
```

#### Use Cases for External Users

| User Type | Access Level | Example |
|-----------|--------------|---------|
| Client analysts | View their campaigns only | Filter app by client brand |
| Econometricians | Full POC access | All campaigns, exports enabled |
| Agency partners | Specific campaign views | Buyer-filtered access |
| Auditors | Read-only, time-limited | Temporary accounts |
| Demo users | Anonymised data only | DEMO_MODE enabled |

#### Onboarding External Users

1. **Create user account** with temporary password
2. **Email credentials** securely (separate email for password)
3. **User logs in** and sets their own password
4. **User registers MFA** (if required)
5. **User accesses app** at `https://app.snowflake.com`

No software installation required - just a web browser.

---

## 6. Estimated Costs

### 6.1 Snowflake Pricing (Standard Edition, AWS)

| Component | Estimate | Monthly Cost |
|-----------|----------|--------------|
| Storage (50GB compressed) | 50GB × $0.80 | ~$40 |
| Compute (XS warehouse, 2hr/day) | 60 credits | ~$120 |
| Compute (Medium, 1hr/week) | 16 credits | ~$32 |
| Data transfer (10GB egress) | 10GB | ~$10 |
| **Total** | | **~$200/month** |

### 6.2 Comparison to Current Setup

| Current | Snowflake |
|---------|-----------|
| Self-hosted PostgreSQL | Managed Snowflake |
| Manual user management | Built-in RBAC + SSO |
| No authentication | Full authentication |
| Streamlit on local machine | Hosted Streamlit |

**Value add:** Authentication, hosting, scaling, security, audit logging

---

## 7. Migration Plan

### Phase 1: Schema Migration (1 week)
1. Create Snowflake database and schema
2. Convert PostgreSQL types to Snowflake equivalents
3. Create all tables with correct types
4. Convert MVs to Dynamic Tables
5. Test SQL syntax fixes

### Phase 2: Data Migration (1 week)
1. Export PostgreSQL data to CSV/Parquet
2. Upload to Snowflake stage
3. Load with `COPY INTO`
4. Validate row counts and data integrity
5. Verify NUMERIC precision preserved

### Phase 3: Application Migration (1-2 weeks)
1. Rewrite database layer for Snowpark
2. Update all SQL queries
3. Configure External Access for APIs (if needed)
4. Test all tabs and features
5. Handle logo/assets

### Phase 4: Authentication & Deployment (1 week)
1. Create roles and permissions
2. Configure SSO (if required)
3. Deploy Streamlit app to Snowflake
4. User acceptance testing
5. Documentation and training

---

## 8. Decision Points

### 8.1 Do You Need This?

**Pros of Snowflake deployment:**
- ✅ Built-in user authentication
- ✅ **External user support** - Create accounts for clients, partners, econometricians without them needing Snowflake subscriptions
- ✅ No infrastructure to manage
- ✅ Enterprise-grade security and audit (full audit trail per user)
- ✅ Scalable
- ✅ SSO integration possible
- ✅ IP-based access restrictions per user
- ✅ MFA enforcement
- ✅ Automatic session management and timeout

**Cons:**
- ❌ Significant migration effort (2-4 weeks)
- ❌ Ongoing Snowflake costs (~$200+/month, scales with users)
- ❌ Less flexibility than self-hosted
- ❌ 32MB data limit for UI components (affects large exports)
- ❌ No cross-session caching
- ❌ You pay for external user compute usage

### 8.2 Alternatives to Consider

| Option | Auth | External Users | Hosting | Effort | Cost |
|--------|------|----------------|---------|--------|------|
| **Snowflake SiS** | Built-in RBAC | ✅ Easy (built-in) | Snowflake | High | $200+/mo |
| **Self-hosted + Pangolin/PocketID** | PocketID passkeys | ✅ Yes (self-managed) | Self | Medium | $0 (+ server) |
| **Streamlit Cloud + Auth0** | Auth0/OAuth | ⚠️ Auth0 pricing | Streamlit | Medium | $50-100/mo |
| **AWS + Cognito** | AWS Cognito | ⚠️ Cognito pricing | EC2/ECS | Medium | $100+/mo |

**Key insight:** Snowflake's external user support is **included** - no extra auth service costs. Other options require separate identity management that may have per-user pricing.

### 8.3 Recommendation

**If you need external user access (clients, econometricians, partners):**
- **Snowflake is the strongest option** - external users built-in at no extra auth cost
- Full audit trail, MFA, IP restrictions per user
- Users just need a browser - no software to install
- You control everything, revoke access instantly

**If primary goal is internal authentication only:**
- Consider **self-hosted + Pangolin/PocketID** - full control, no ongoing costs
- Or **Streamlit Community Cloud + Auth0** - less effort but can't connect to on-prem DB

**If primary goal is enterprise deployment with full Snowflake integration:**
- Proceed with Snowflake migration
- Budget 3-4 weeks and $200+/month
- Worth it if you're already invested in Snowflake ecosystem or need external users

---

## 9. Next Steps

1. **Decide:** Is Snowflake the right choice, or would simpler auth work?
2. **Verify packages:** Check all dependencies against Snowflake Anaconda channel
3. **Test queries:** Run converted SQL in Snowflake to verify syntax
4. **Prototype:** Build minimal Streamlit app in Snowflake with one tab
5. **Cost estimate:** Get actual Snowflake pricing for your account

---

## 10. Resources

- [Streamlit in Snowflake Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [SiS Limitations](https://docs.snowflake.com/en/developer-guide/streamlit/limitations)
- [External Access Integrations](https://docs.snowflake.com/en/developer-guide/external-network-access/external-access-overview)
- [Snowflake Data Type Mappings](https://docs.snowflake.com/en/migrations/snowconvert-docs/translation-references/postgres/data-types)
- [Dynamic Tables](https://docs.snowflake.com/en/user-guide/dynamic-tables-intro)
- [Snowflake RBAC](https://docs.snowflake.com/en/user-guide/security-access-control-overview)

---

*Document created: 9 December 2025*
*Last updated: 9 December 2025*
*Status: Discovery complete - external user capability highlighted*
