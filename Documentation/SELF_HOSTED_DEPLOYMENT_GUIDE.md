# Self-Hosted Deployment Guide: Pangolin + PocketID on Proxmox

**Created:** 9 December 2025
**Status:** Planning / Reference
**Author:** Claude (reviewed by Doctor Biz)

---

## Executive Summary

This guide covers deploying the Route Playout Econometrics POC with:

- **Pangolin** - Self-hosted tunnelled reverse proxy (Cloudflare Tunnel alternative)
- **PocketID** - Passkey-based OIDC authentication (passwordless)
- **Proxmox** - Virtualisation platform hosting everything
- **DMZ Architecture** - Secure network isolation

**Result:** Secure, authenticated access to your Streamlit app without exposing PostgreSQL to the internet.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS (443)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DMZ NETWORK (10.10.20.0/24)                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Pangolin Server (LXC)                             │   │
│  │                    10.10.20.10                                       │   │
│  │  • Reverse proxy with SSL termination                               │   │
│  │  • WireGuard tunnel endpoint                                        │   │
│  │  • Identity-aware access control                                    │   │
│  │  • Ports: 80, 443, 51820 (WireGuard)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    │ WireGuard Tunnel                       │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PocketID Server (LXC)                            │   │
│  │                    10.10.20.20                                       │   │
│  │  • OIDC provider (passkey authentication)                           │   │
│  │  • User/group management                                            │   │
│  │  • Audit logging                                                    │   │
│  │  • Port: 8080 (internal only)                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          Firewall (allow specific)
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      INTERNAL NETWORK (192.168.1.0/24)                      │
│  ┌──────────────────────────────┐  ┌──────────────────────────────────┐   │
│  │   Streamlit App (LXC/VM)     │  │   PostgreSQL (MS-01)             │   │
│  │   192.168.1.x                │  │   192.168.1.34                   │   │
│  │   • Route Playout POC        │──│   • route_poc database           │   │
│  │   • Newt tunnel client       │  │   • NOT exposed to DMZ           │   │
│  │   • Port: 8504 (internal)    │  │   • Port: 5432 (internal only)   │   │
│  └──────────────────────────────┘  └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Overview

### Pangolin

[Pangolin](https://github.com/fosrl/pangolin) is a self-hosted reverse proxy with WireGuard tunnelling:

- **What it does:** Exposes internal services securely without port forwarding
- **Key features:**
  - SSL/TLS termination with automatic Let's Encrypt certificates
  - Identity-aware access control (OIDC integration)
  - WireGuard tunnels punch through firewalls/CGNAT
  - Dashboard UI for management
- **Why use it:** Full control, no reliance on Cloudflare

### PocketID

[PocketID](https://github.com/pocket-id/pocket-id) is a lightweight OIDC provider:

- **What it does:** Provides passkey-based authentication (no passwords!)
- **Key features:**
  - WebAuthn/passkey only (YubiKey, fingerprint, Face ID)
  - OIDC-compliant (works with Pangolin, TinyAuth, etc.)
  - User and group management
  - Audit logging
  - SQLite backend (simple, no external DB needed)
- **Why use it:** Modern, passwordless security for homelabs

### Alternative: TinyAuth

[TinyAuth](https://github.com/steveiliop56/tinyauth) is simpler middleware if you want username/password:

- Lightweight authentication layer
- Works with Pangolin, Traefik, Nginx, Caddy
- Supports OAuth (Google, GitHub) and TOTP
- Good for homelabs, not intended for enterprise

**Recommendation:** Use PocketID for passkey auth (more secure), or TinyAuth if you need simpler username/password.

---

## Prerequisites

### Hardware/Infrastructure

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Proxmox host | 4 cores, 8GB RAM | 8 cores, 16GB RAM |
| Storage | 50GB SSD | 100GB+ SSD |
| Network | 1 NIC | 2 NICs (separate DMZ) |

### Domain & DNS

You'll need:
- A domain name (e.g., `yourdomain.com`)
- Access to DNS management
- Public IP address (static preferred)

### DNS Records to Create

| Record | Type | Value | Purpose |
|--------|------|-------|---------|
| `@` | A | Your public IP | Root domain |
| `*` | A | Your public IP | Wildcard for subdomains |
| `pangolin` | A | Your public IP | Pangolin dashboard |
| `auth` | A | Your public IP | PocketID |
| `playout` | A | Your public IP | Streamlit app |

---

## Part 1: Proxmox DMZ Network Setup

### 1.1 Create DMZ Bridge

SSH into your Proxmox host and edit `/etc/network/interfaces`:

```bash
nano /etc/network/interfaces
```

Add the DMZ bridge configuration:

```bash
# Existing management bridge (keep as-is)
auto vmbr0
iface vmbr0 inet static
    address 192.168.1.100/24
    gateway 192.168.1.1
    bridge-ports eno1
    bridge-stp off
    bridge-fd 0

# NEW: DMZ Bridge (isolated network)
auto vmbr1
iface vmbr1 inet static
    address 10.10.20.1/24
    bridge-ports none
    bridge-stp off
    bridge-fd 0
    # Enable IP forwarding for this bridge
    post-up echo 1 > /proc/sys/net/ipv4/ip_forward
    # NAT for DMZ to access internet
    post-up iptables -t nat -A POSTROUTING -s 10.10.20.0/24 -o vmbr0 -j MASQUERADE
    post-down iptables -t nat -D POSTROUTING -s 10.10.20.0/24 -o vmbr0 -j MASQUERADE
```

Apply changes:

```bash
ifreload -a
# Or reboot if ifreload unavailable
```

### 1.2 Configure Proxmox Firewall

Enable the firewall at datacenter level:

**Datacenter → Firewall → Options:**
- Enable: Yes
- Input Policy: DROP
- Output Policy: ACCEPT

**Datacenter → Firewall → Rules:**

```
# Allow SSH to Proxmox (management)
Direction: IN
Action: ACCEPT
Source: 192.168.1.0/24
Dest port: 22
Protocol: tcp
Comment: SSH from LAN

# Allow Proxmox Web UI (management)
Direction: IN
Action: ACCEPT
Source: 192.168.1.0/24
Dest port: 8006
Protocol: tcp
Comment: Proxmox UI from LAN

# Allow HTTP/HTTPS to DMZ
Direction: IN
Action: ACCEPT
Dest: 10.10.20.0/24
Dest port: 80,443
Protocol: tcp
Comment: Web traffic to DMZ

# Allow WireGuard to DMZ
Direction: IN
Action: ACCEPT
Dest: 10.10.20.10
Dest port: 51820
Protocol: udp
Comment: WireGuard to Pangolin

# Block DMZ from accessing internal network
Direction: FORWARD
Action: DROP
Source: 10.10.20.0/24
Dest: 192.168.1.0/24
Comment: DMZ cannot reach internal

# Allow internal to DMZ (for management)
Direction: FORWARD
Action: ACCEPT
Source: 192.168.1.0/24
Dest: 10.10.20.0/24
Comment: Internal can reach DMZ
```

### 1.3 Port Forwarding (Router/Firewall)

On your edge router/firewall, forward these ports to Pangolin (10.10.20.10):

| External Port | Internal IP | Internal Port | Protocol |
|---------------|-------------|---------------|----------|
| 80 | 10.10.20.10 | 80 | TCP |
| 443 | 10.10.20.10 | 443 | TCP |
| 51820 | 10.10.20.10 | 51820 | UDP |

---

## Part 2: Create LXC Containers

### 2.1 Download Container Template

In Proxmox web UI:
1. Select storage (e.g., `local`)
2. Click **CT Templates**
3. Click **Templates** button
4. Download: `debian-12-standard` (or `ubuntu-24.04-standard`)

### 2.2 Create Pangolin Container

**Datacenter → Create CT:**

| Setting | Value |
|---------|-------|
| CT ID | 200 |
| Hostname | pangolin |
| Password | (set secure password) |
| Template | debian-12-standard |
| Disk | 8 GB |
| CPU | 2 cores |
| Memory | 1024 MB |
| Network | Bridge: vmbr1, IPv4: 10.10.20.10/24, Gateway: 10.10.20.1 |
| DNS | 8.8.8.8, 8.8.4.4 |

**Options to set after creation:**
- Features: Enable `nesting` (for Docker)
- Start at boot: Yes

### 2.3 Create PocketID Container

**Datacenter → Create CT:**

| Setting | Value |
|---------|-------|
| CT ID | 201 |
| Hostname | pocketid |
| Password | (set secure password) |
| Template | debian-12-standard |
| Disk | 4 GB |
| CPU | 1 core |
| Memory | 512 MB |
| Network | Bridge: vmbr1, IPv4: 10.10.20.20/24, Gateway: 10.10.20.1 |
| DNS | 8.8.8.8, 8.8.4.4 |

### 2.4 Create Streamlit Container

**Datacenter → Create CT:**

| Setting | Value |
|---------|-------|
| CT ID | 202 |
| Hostname | streamlit |
| Password | (set secure password) |
| Template | debian-12-standard |
| Disk | 16 GB |
| CPU | 2 cores |
| Memory | 2048 MB |
| Network | Bridge: vmbr0, IPv4: 192.168.1.50/24, Gateway: 192.168.1.1 |
| DNS | 8.8.8.8, 8.8.4.4 |

**Note:** Streamlit container is on the **internal network** (vmbr0), not DMZ.

---

## Part 3: Install Pangolin

### 3.1 Prepare Container

Start the Pangolin container and attach:

```bash
pct start 200
pct enter 200
```

Update and install prerequisites:

```bash
apt update && apt upgrade -y
apt install -y curl ca-certificates gnupg
```

### 3.2 Install Docker

```bash
# Add Docker GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 3.3 Install Pangolin

```bash
# Create installation directory
mkdir -p /opt/pangolin && cd /opt/pangolin

# Download installer
curl -fsSL https://pangolin.net/get-installer.sh | bash

# Run installer
sudo ./installer
```

**Installer prompts:**

| Prompt | Value |
|--------|-------|
| Base Domain Name | `yourdomain.com` |
| Dashboard Domain Name | `pangolin.yourdomain.com` |
| Email (Let's Encrypt) | `admin@yourdomain.com` |
| Admin Password | (strong password, 8+ chars, mixed case, numbers, special) |
| Install Gerbil (tunnelling)? | Yes |

### 3.4 Verify Installation

```bash
# Check containers are running
docker ps

# Should see: pangolin, gerbil, traefik
```

Access the dashboard at: `https://pangolin.yourdomain.com`

---

## Part 4: Install PocketID

### 4.1 Prepare Container

```bash
pct start 201
pct enter 201

apt update && apt upgrade -y
apt install -y curl ca-certificates gnupg
```

### 4.2 Install Docker

(Same as Pangolin - repeat Docker installation steps)

### 4.3 Deploy PocketID

```bash
mkdir -p /opt/pocketid && cd /opt/pocketid
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  pocket-id:
    image: stonith404/pocket-id
    container_name: pocket-id
    restart: unless-stopped
    ports:
      - "8080:80"
    environment:
      - PUBLIC_APP_URL=https://auth.yourdomain.com
      - TRUST_PROXY=true
      - MAXMIND_LICENSE_KEY=  # Optional: for geolocation
    volumes:
      - ./data:/app/data
```

Start PocketID:

```bash
docker compose up -d
```

### 4.4 Initial PocketID Setup

1. Access PocketID at `http://10.10.20.20:8080` (internal only for now)
2. Complete initial setup wizard
3. Register your first passkey (admin account)
4. Note down the OIDC endpoints for Pangolin configuration

---

## Part 5: Configure Pangolin + PocketID Integration

### 5.1 Add PocketID as Identity Provider

In Pangolin dashboard:

1. Go to **Server Admin → Identity Providers**
2. Click **+ Add Provider**
3. Select **OpenID Connect**

Configure:

| Setting | Value |
|---------|-------|
| Name | PocketID |
| Client ID | (from PocketID OIDC Clients) |
| Client Secret | (from PocketID OIDC Clients) |
| Issuer URL | `https://auth.yourdomain.com` |
| Authorization URL | `https://auth.yourdomain.com/authorize` |
| Token URL | `https://auth.yourdomain.com/api/oidc/token` |
| User Info URL | `https://auth.yourdomain.com/api/oidc/userinfo` |
| Scopes | `openid email profile groups` |

### 5.2 Create PocketID OIDC Client

In PocketID:

1. Go to **OIDC Clients → Create Client**
2. Configure:

| Setting | Value |
|---------|-------|
| Name | Pangolin |
| Redirect URLs | `https://pangolin.yourdomain.com/api/v1/auth/oidc/callback` |
| Allowed Scopes | openid, email, profile, groups |

3. Note the **Client ID** and **Client Secret**

### 5.3 Configure Access Rules

In Pangolin, create a resource for the Streamlit app:

1. Go to **Resources → + Add Resource**
2. Configure:

| Setting | Value |
|---------|-------|
| Name | Route Playout POC |
| Domain | `playout.yourdomain.com` |
| Backend URL | `http://192.168.1.50:8504` |
| Authentication | Required |
| Identity Provider | PocketID |

---

## Part 6: Install Newt Tunnel Client

The Newt client runs on your Streamlit container to create a secure tunnel back to Pangolin.

### 6.1 Prepare Streamlit Container

```bash
pct start 202
pct enter 202

apt update && apt upgrade -y
apt install -y curl ca-certificates gnupg python3 python3-pip python3-venv git
```

### 6.2 Install Docker (for Newt)

(Repeat Docker installation steps)

### 6.3 Create Newt Site in Pangolin

In Pangolin dashboard:

1. Go to **Sites → + Add Site**
2. Name: `streamlit-internal`
3. Click **Create**
4. Note the **Newt ID** and **Newt Secret**

### 6.4 Deploy Newt Client

```bash
mkdir -p /opt/newt && cd /opt/newt
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  newt:
    image: fosrl/newt
    container_name: newt
    restart: unless-stopped
    environment:
      - PANGOLIN_ENDPOINT=https://pangolin.yourdomain.com
      - NEWT_ID=your_newt_id_here
      - NEWT_SECRET=your_newt_secret_here
      - LOG_LEVEL=INFO
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

Start Newt:

```bash
docker compose up -d

# Check logs
docker logs -f newt
```

### 6.5 Configure Target in Pangolin

Back in Pangolin:

1. Go to **Sites → streamlit-internal → Targets**
2. Click **+ Add Target**
3. Configure:

| Setting | Value |
|---------|-------|
| Name | streamlit-app |
| Target | `localhost:8504` |
| Protocol | HTTP |

---

## Part 7: Deploy Streamlit App

### 7.1 Clone Repository

```bash
cd /opt
git clone https://github.com/yourusername/Route-Playout-Econometrics_POC.git
cd Route-Playout-Econometrics_POC
```

### 7.2 Setup Python Environment

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 7.3 Configure Environment

Create `.env` file:

```bash
# Database (internal network - NOT exposed to DMZ)
POSTGRES_HOST_MS01=192.168.1.34
POSTGRES_PORT=5432
POSTGRES_DB=route_poc
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Application
USE_MS01_DATABASE=true
DEMO_MODE=false
```

### 7.4 Create Systemd Service

Create `/etc/systemd/system/streamlit.service`:

```ini
[Unit]
Description=Route Playout Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/Route-Playout-Econometrics_POC
Environment="PATH=/opt/Route-Playout-Econometrics_POC/.venv/bin"
ExecStart=/opt/Route-Playout-Econometrics_POC/.venv/bin/streamlit run src/ui/app.py --server.port 8504 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
systemctl daemon-reload
systemctl enable streamlit
systemctl start streamlit

# Check status
systemctl status streamlit
```

---

## Part 8: Security Hardening

### 8.1 DMZ Firewall Rules (iptables)

On the Proxmox host, add these rules to `/etc/network/interfaces` (in the vmbr1 section):

```bash
# Block DMZ from reaching internal network
post-up iptables -I FORWARD -s 10.10.20.0/24 -d 192.168.1.0/24 -j DROP

# Allow only Pangolin to reach Streamlit via tunnel
post-up iptables -I FORWARD -s 10.10.20.10 -d 192.168.1.50 -p tcp --dport 8504 -j ACCEPT

# Allow return traffic
post-up iptables -I FORWARD -s 192.168.1.50 -d 10.10.20.10 -p tcp --sport 8504 -j ACCEPT
```

### 8.2 Container Security

For each LXC container, set:

```bash
# Unprivileged container (more secure)
pct set <CTID> --unprivileged 1

# Disable unnecessary features
pct set <CTID> --features keyctl=0,fuse=0
```

### 8.3 PocketID Security

In PocketID settings:

- Enable **audit logging**
- Set **session timeout** (e.g., 8 hours)
- Configure **allowed groups** for Streamlit access
- Review login attempts regularly

### 8.4 Pangolin Security

In Pangolin settings:

- Enable **rate limiting**
- Configure **IP blocklists** if needed
- Set up **access policies** per resource
- Enable **request logging**

---

## Part 9: Testing & Verification

### 9.1 Test Authentication Flow

1. Open `https://playout.yourdomain.com`
2. Should redirect to PocketID login
3. Authenticate with passkey
4. Should redirect back to Streamlit app
5. Verify app loads correctly

### 9.2 Test DMZ Isolation

From DMZ container (Pangolin):

```bash
# This should FAIL (DMZ cannot reach internal)
ping 192.168.1.34
curl http://192.168.1.34:5432
```

From Streamlit container:

```bash
# This should SUCCEED (internal can reach PostgreSQL)
psql -h 192.168.1.34 -U your_user -d route_poc -c "SELECT 1"
```

### 9.3 Verify Tunnel

In Pangolin dashboard:

- Sites → streamlit-internal should show **Online**
- Check Newt logs: `docker logs newt`

---

## Part 10: Maintenance

### 10.1 Updating Components

**Pangolin:**
```bash
cd /opt/pangolin
docker compose pull
docker compose up -d
```

**PocketID:**
```bash
cd /opt/pocketid
docker compose pull
docker compose up -d
```

**Newt:**
```bash
cd /opt/newt
docker compose pull
docker compose up -d
```

### 10.2 Backup

**PocketID data:**
```bash
# Backup SQLite database
cp /opt/pocketid/data/pocket-id.db /backup/pocketid-$(date +%Y%m%d).db
```

**Pangolin config:**
```bash
# Backup Pangolin data
tar -czvf /backup/pangolin-$(date +%Y%m%d).tar.gz /opt/pangolin
```

### 10.3 Monitoring

Check container health:

```bash
# Pangolin
docker logs pangolin --tail 50

# PocketID
docker logs pocket-id --tail 50

# Newt
docker logs newt --tail 50

# Streamlit
journalctl -u streamlit -f
```

---

## Troubleshooting

### Tunnel Won't Connect

1. Check Newt logs: `docker logs newt`
2. Verify NEWT_ID and NEWT_SECRET match Pangolin
3. Ensure Pangolin endpoint is accessible from Streamlit container
4. Check firewall rules allow WireGuard (UDP 51820)

### Authentication Fails

1. Verify PocketID is accessible at auth URL
2. Check OIDC client configuration in both systems
3. Verify redirect URLs match exactly
4. Check PocketID audit log for errors

### Streamlit Not Loading

1. Check Streamlit service: `systemctl status streamlit`
2. Verify PostgreSQL connection from Streamlit container
3. Check Newt tunnel is online in Pangolin
4. Review Streamlit logs: `journalctl -u streamlit`

### SSL Certificate Issues

1. Verify DNS records point to correct IP
2. Check Let's Encrypt logs in Pangolin
3. Ensure ports 80/443 are open to Pangolin
4. Try forcing certificate renewal in Pangolin dashboard

---

## Alternative: TinyAuth Instead of PocketID

If you prefer username/password over passkeys, use TinyAuth:

### TinyAuth Docker Compose

```yaml
version: '3.8'

services:
  tinyauth:
    image: ghcr.io/steveiliop56/tinyauth:latest
    container_name: tinyauth
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - SECRET=your-long-random-secret-here
      - APP_URL=https://auth.yourdomain.com
      - USERS=admin:$$2a$$10$$hashedpasswordhere
      # Or use OAuth
      - PROVIDERS_POCKETID_CLIENT_ID=xxx
      - PROVIDERS_POCKETID_CLIENT_SECRET=xxx
```

TinyAuth integrates with Pangolin similarly - configure it as a forward auth middleware.

---

## Quick Reference

### URLs

| Service | URL |
|---------|-----|
| Pangolin Dashboard | `https://pangolin.yourdomain.com` |
| PocketID | `https://auth.yourdomain.com` |
| Streamlit App | `https://playout.yourdomain.com` |

### Container IPs

| Container | IP | Network |
|-----------|----|---------|
| Pangolin | 10.10.20.10 | DMZ (vmbr1) |
| PocketID | 10.10.20.20 | DMZ (vmbr1) |
| Streamlit | 192.168.1.50 | Internal (vmbr0) |
| PostgreSQL | 192.168.1.34 | Internal (vmbr0) |

### Ports

| Port | Protocol | Service |
|------|----------|---------|
| 80 | TCP | HTTP (redirect to HTTPS) |
| 443 | TCP | HTTPS (Pangolin) |
| 51820 | UDP | WireGuard tunnel |
| 8504 | TCP | Streamlit (internal only) |
| 5432 | TCP | PostgreSQL (internal only) |

---

## Sources

- [Pangolin GitHub](https://github.com/fosrl/pangolin)
- [Pangolin Documentation](https://docs.pangolin.net/self-host/quick-install)
- [PocketID GitHub](https://github.com/pocket-id/pocket-id)
- [PocketID + Pangolin Integration](https://docs.pangolin.net/manage/identity-providers/pocket-id)
- [TinyAuth GitHub](https://github.com/steveiliop56/tinyauth)
- [TinyAuth + PocketID Guide](https://tinyauth.app/docs/guides/pocket-id/)
- [Newt Tunnel Client](https://github.com/fosrl/newt)
- [Proxmox Firewall Documentation](https://pve.proxmox.com/wiki/Firewall)
- [Proxmox LXC Containers](https://pve.proxmox.com/wiki/Linux_Container)
- [DMZ Setup in Proxmox](https://forum.proxmox.com/threads/vm-in-a-dmz.75963/)
- [Pangolin Self-Hosting Guide](https://pimylifeup.com/pangolin-linux/)
- [Complete Pangolin + Authentik Guide](https://www.serverion.com/uncategorized/complete-self-hosting-guide-pangolin-authentik/)

---

*Document created: 9 December 2025*
*Status: Ready for implementation*
