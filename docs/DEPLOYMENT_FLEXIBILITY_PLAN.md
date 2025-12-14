# Deployment Flexibility Plan

**Created**: 10 December 2025
**Purpose**: Scope and plan for flexible deployment architecture
**Status**: Planning (no code changes before demo)

---

## Executive Summary

This document analyses the current configuration architecture and plans for flexible deployment that allows:
- Database on different servers (local, Proxmox, Google Cloud, VPS)
- UI hosted separately from database (LXC on VPS, cloud hosting, etc.)
- Reverse proxy access for external users
- Easy environment switching via `.env` file

---

## Current State Assessment

### What's Already Well-Externalised

The codebase has a solid configuration system in `src/config.py`. Most values support environment variable overrides:

| Component | Default | Env Override | Status |
|-----------|---------|--------------|--------|
| PostgreSQL Host (MS01) | - | `POSTGRES_HOST_MS01` | Required, no default |
| PostgreSQL Host (Local) | `localhost` | `POSTGRES_HOST_LOCAL` | Default provided |
| PostgreSQL Port | `5432` | `POSTGRES_PORT_MS01/LOCAL` | Default provided |
| PostgreSQL Database | `route_poc` | `POSTGRES_DATABASE_MS01/LOCAL` | Default provided |
| PostgreSQL User | `postgres` | `POSTGRES_USER_MS01/LOCAL` | Default provided |
| PostgreSQL Password | - | `POSTGRES_PASSWORD_MS01/LOCAL` | Required |
| Database Selector | `true` (MS01) | `USE_MS01_DATABASE` | Working |
| Route API URL | `https://route.mediatelapi.co.uk` | `ROUTE_API_URL` | Default provided |
| Route API Playout | Hardcoded | `ROUTE_API_PLAYOUT_ENDPOINT` | Default provided |
| SPACE API URL | `https://oohspace.co.uk/api` | `SPACE_API_BASE_URL` | Default provided |
| Demo Mode | `false` | `DEMO_MODE` | Working |
| SSL Mode | `prefer` | `POSTGRES_SSL_MODE` | Default provided |
| SSL Cert/Key/CA | - | `POSTGRES_SSL_*` | Ready for cloud |

### Items Needing Attention

| Item | Current State | Issue | Priority |
|------|---------------|-------|----------|
| Streamlit Port | Hardcoded `8504` in shell function | Not in `.env` | Medium |
| Streamlit Address | `headless=true` only | No bind address config | High (for reverse proxy) |
| Generic DB fallback | Falls back to `POSTGRES_*` vars | Potentially confusing | Low |
| `route_releases.py` | Uses different env vars (`DATABASE_HOST`) | Inconsistent | Medium |

### Files with Hardcoded Values

```
src/config.py:274:    host: str = "localhost"           # OK - overridden by env
src/config.py:337:    host = os.getenv('POSTGRES_HOST_LOCAL', 'localhost')  # OK
src/db/route_releases.py:66:    'host': os.getenv('DATABASE_HOST', 'localhost')  # ISSUE - different env var name
src/db/queries/connection.py:36:    host=os.getenv('POSTGRES_HOST_LOCAL', 'localhost')  # OK
```

---

## Deployment Architecture Options

### Option A: All-in-One (Current)

```
┌─────────────────────────────────────┐
│           MS-01 Server              │
│  ┌─────────────────────────────┐    │
│  │     PostgreSQL Database     │    │
│  │     (1.28B records)         │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
              ↑
              │ LAN Connection
              ↓
┌─────────────────────────────────────┐
│         Developer MacBook           │
│  ┌─────────────────────────────┐    │
│  │   Streamlit UI (port 8504)  │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**Pros**: Simple, fast LAN speeds
**Cons**: No external access, tied to local network

---

### Option B: Split Architecture (Recommended for Flexibility)

```
┌─────────────────────────────────────┐
│    Database Server (Choice of):     │
│    - MS-01 Proxmox (current)        │
│    - Google Cloud SQL                │
│    - VPS with PostgreSQL            │
│    - Office Proxmox                 │
│  ┌─────────────────────────────┐    │
│  │     PostgreSQL Database     │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
              ↑
              │ Secure Connection (SSL/VPN)
              ↓
┌─────────────────────────────────────┐
│    UI Server (Choice of):           │
│    - LXC on VPS                     │
│    - Google Cloud Run               │
│    - Railway/Render                 │
│  ┌─────────────────────────────┐    │
│  │      Streamlit UI           │    │
│  │  (via reverse proxy)        │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
              ↑
              │ HTTPS (Cloudflare/nginx)
              ↓
┌─────────────────────────────────────┐
│          End Users                  │
│    (Browser access via URL)         │
└─────────────────────────────────────┘
```

---

### Option C: Containerised (Docker)

```
┌─────────────────────────────────────────────────────┐
│                 Docker Host                          │
│  ┌─────────────────┐  ┌─────────────────────────┐   │
│  │    PostgreSQL   │  │      Streamlit App      │   │
│  │    Container    │←→│       Container         │   │
│  └─────────────────┘  └─────────────────────────┘   │
│            ↓                        ↓                │
│  ┌──────────────────────────────────────────────┐   │
│  │              Traefik / nginx                  │   │
│  │           (Reverse Proxy + SSL)              │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## Required Changes for Full Flexibility

### Phase 1: Configuration Cleanup (Low Risk)

1. **Standardise database env var names in `route_releases.py`**
   - Change `DATABASE_HOST` → `POSTGRES_HOST_MS01` (or respect the switcher)
   - Ensures all DB connections use same config source

2. **Add Streamlit server config to `.env.example`**
   ```
   # Streamlit Server Configuration
   STREAMLIT_SERVER_PORT=8504
   STREAMLIT_SERVER_ADDRESS=0.0.0.0
   STREAMLIT_SERVER_HEADLESS=true
   ```

3. **Update `.streamlit/config.toml`** to read from env:
   ```toml
   [server]
   port = 8504  # Can override via STREAMLIT_SERVER_PORT
   address = "0.0.0.0"  # Bind to all interfaces for reverse proxy
   headless = true
   enableCORS = false
   enableXsrfProtection = true
   ```

### Phase 2: Reverse Proxy Support (Medium Risk)

1. **Add base URL configuration** for when running behind reverse proxy:
   ```
   APP_BASE_URL=https://econometrics.route.org.uk
   ```

2. **Configure Streamlit for reverse proxy**:
   ```toml
   [server]
   baseUrlPath = ""  # or "/econometrics" if subpath
   enableCORS = false
   enableXsrfProtection = true
   ```

3. **Example nginx config** (for documentation):
   ```nginx
   server {
       listen 443 ssl;
       server_name econometrics.route.org.uk;

       location / {
           proxy_pass http://localhost:8504;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 86400;
       }
   }
   ```

### Phase 3: Cloud Database Support (Medium Risk)

1. **SSL configuration already exists** - just needs testing:
   ```
   POSTGRES_SSL_MODE=require
   POSTGRES_SSL_CERT=/path/to/client-cert.pem
   POSTGRES_SSL_KEY=/path/to/client-key.pem
   POSTGRES_SSL_CA=/path/to/server-ca.pem
   ```

2. **Connection string generation** - already implemented in `DatabaseConfig.get_connection_string()`

3. **Google Cloud SQL specific**:
   ```
   # Using Cloud SQL Proxy
   POSTGRES_HOST_MS01=127.0.0.1
   POSTGRES_PORT_MS01=5433  # Cloud SQL Proxy port

   # Or direct with SSL
   POSTGRES_HOST_MS01=<PROJECT>:<REGION>:<INSTANCE>
   POSTGRES_SSL_MODE=require
   ```

### Phase 4: Docker Support (Optional, Higher Effort)

1. **Dockerfile** for UI:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8504
   CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8504"]
   ```

2. **docker-compose.yml**:
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8504:8504"
       env_file:
         - .env
       environment:
         - STREAMLIT_SERVER_ADDRESS=0.0.0.0
   ```

---

## Recommended Deployment Scenarios

### Scenario 1: Internal Demo (Current)

| Component | Location | Access |
|-----------|----------|--------|
| Database | MS-01 (192.168.1.34) | LAN only |
| UI | Developer laptop | localhost:8504 |
| Users | Same room | Direct |

**Config**: Current `.env` unchanged

---

### Scenario 2: Board Demo (Remote Access)

| Component | Location | Access |
|-----------|----------|--------|
| Database | MS-01 (192.168.1.34) | LAN/VPN |
| UI | Developer laptop | Via Tailscale/ngrok |
| Users | Remote | HTTPS URL |

**Config**:
```env
USE_MS01_DATABASE=true
POSTGRES_HOST_MS01=192.168.1.34
DEMO_MODE=true
```

**Quick option**: Use `ngrok http 8504` for temporary external access

---

### Scenario 3: Production (VPS + Cloud DB)

| Component | Location | Access |
|-----------|----------|--------|
| Database | Google Cloud SQL | SSL |
| UI | LXC on VPS | HTTPS via nginx |
| Users | Anywhere | Public URL |

**Config**:
```env
USE_MS01_DATABASE=true
POSTGRES_HOST_MS01=<cloud-sql-ip>
POSTGRES_SSL_MODE=require
POSTGRES_SSL_CA=/etc/ssl/server-ca.pem
DEMO_MODE=false
```

---

## Authentication & Access Stack

### Chosen Stack: Pangolin + Pocket ID

#### Pangolin - Tunnelled Reverse Proxy
- **What**: Self-hosted Cloudflare Tunnel alternative
- **Repo**: https://github.com/fosrl/pangolin
- **Docs**: https://docs.pangolin.net/
- **Key Features**:
  - Built on WireGuard + Traefik
  - No port forwarding needed - punches through firewalls
  - Dashboard UI for management
  - "Newt" client creates tunnels from services
  - Automatic SSL via Let's Encrypt
  - Zero Trust architecture
- **License**: AGPL-3 (free for personal/hobbyist, businesses <$100K USD)

#### Pocket ID - OIDC Authentication
- **What**: Lightweight self-hosted OIDC provider with passkey-only auth
- **Repo**: https://github.com/pocket-id/pocket-id
- **Key Features**:
  - Passkey authentication only (no passwords)
  - Works with Yubikeys and device biometrics
  - Much lighter than Keycloak/Authentik (~30MB vs 2GB RAM)
  - Simple setup via Docker
  - SSO across all services
- **Use case**: Central authentication for all Route tools

#### Architecture with Pangolin + Pocket ID

```
┌─────────────────────────────────────────────────────────────┐
│                        VPS Host                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    Pangolin                          │    │
│  │         (Reverse Proxy + Tunnel Server)              │    │
│  │              ↓ WireGuard Tunnel                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│  ┌───────────────┐  ┌────┴────────────┐                     │
│  │   Pocket ID   │  │  Streamlit UI   │                     │
│  │  (OIDC Auth)  │  │   (port 8504)   │                     │
│  └───────────────┘  └─────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
              ↑                    ↑
              │ Newt Tunnel        │ Newt Tunnel
              │                    │
┌─────────────┴────────────────────┴──────────────────────────┐
│                    Internal Network                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PostgreSQL (MS-01)                      │    │
│  │                (1.28B records)                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## User Features (Future Scope)

### Phase 1: Authentication
- [ ] Integrate Pocket ID with Streamlit
- [ ] User login via passkey
- [ ] Session management

### Phase 2: User Areas
- [ ] User profile storage in PostgreSQL
- [ ] Saved campaign lists per user
- [ ] Campaign history/recently viewed

### Phase 3: Collaboration (Future)
- [ ] Cross-campaign comparison
- [ ] Shared campaign lists
- [ ] Team workspaces

### Database Schema Addition (Future)

```sql
-- User profiles (linked to Pocket ID)
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY,  -- From Pocket ID OIDC subject
    email VARCHAR(255),
    display_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Saved campaigns per user
CREATE TABLE user_saved_campaigns (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id),
    campaign_id VARCHAR(50),
    saved_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    UNIQUE(user_id, campaign_id)
);

-- Campaign view history
CREATE TABLE user_campaign_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(user_id),
    campaign_id VARCHAR(50),
    viewed_at TIMESTAMP DEFAULT NOW()
);
```

---

## Security Considerations

1. **Never expose PostgreSQL directly to internet** - always use SSL + firewall rules
2. **Passkey authentication** via Pocket ID (no passwords to leak)
3. **Enable Streamlit XSRF protection** when behind reverse proxy
4. **Pangolin provides Zero Trust access** - identity-aware routing
5. **API keys in environment only** - never in code or git

---

## Next Steps (Post-Demo)

1. [ ] Test current config with different POSTGRES_HOST values
2. [ ] Update `route_releases.py` to use standard env var names
3. [ ] Add Streamlit server config to `.env.example`
4. [ ] Create nginx config documentation
5. [ ] Test SSL connection to Cloud SQL (if pursuing cloud option)
6. [ ] Consider Docker for portable deployment
7. [ ] Evaluate hosting options (VPS providers, cloud platforms)

---

## Questions for Decision

1. **Where should the database live long-term?**
   - MS-01 Proxmox (current) - fast, local, free
   - Google Cloud SQL - managed, scalable, costs money
   - Office Proxmox - accessible from office network
   - VPS provider - middle ground

2. **Where should the UI live?**
   - Local laptop (current) - simple, no external access
   - LXC on VPS - always available, costs ~$5-20/month
   - Cloud Run/Railway - serverless, pay per use
   - Docker on existing server - uses existing infrastructure

3. **Who needs access?**
   - Just the team (Tailscale/VPN sufficient)
   - External stakeholders (needs public URL + auth)
   - Clients (needs proper hosting + security audit)

---

*Document created for planning purposes. No code changes to be made before demo.*
