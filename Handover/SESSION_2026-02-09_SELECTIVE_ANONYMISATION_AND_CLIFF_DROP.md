# Session Handover: 9–10 February 2026

**Commits**: `9267c29` — selective brand anonymisation feature
**Pushed**: GitHub + Gitea

---

## 1. Selective Brand Anonymisation (COMPLETE)

Implemented `startstream global` mode for the Global commercial team presentation (30–50 people). When `DEMO_PROTECT_MEDIA_OWNER=Global` is set alongside `DEMO_MODE=true`, campaigns where Global is a media owner show real brand names; competitor campaigns are anonymised.

**Files modified (10):**

| File | Change |
|------|--------|
| `src/ui/config/anonymisation.py` | Added `protect_media_owner` config + `should_anonymise_brands_for_campaign()` |
| `src/utils/formatters.py` | `format_brands()` accepts `media_owner_names` for context-aware anonymisation |
| `src/ui/app.py` | Header brand display uses media owner context; `_get_display_brand()` helper |
| `src/ui/tabs/overview.py` | Uses `format_brands()` with full brand list and media owner context |
| `src/ui/tabs/executive_summary.py` | Same pattern as overview |
| `src/ui/tabs/detailed_analysis.py` | Two sites (daily + hourly frame tables) with selective anonymisation |
| `src/ui/utils/export/excel.py` | Summary sheet brand display |
| `src/ui/utils/export/data.py` | Frame daily + hourly export data |
| `src/ui/components/campaign_browser/browse_tab.py` | Per-row selective anonymisation in browser table |
| `src/ui/components/campaign_browser/manual_input.py` | "Enter Campaign ID" tab passes media owner context |

**Shell function** (`~/.zshrc`): `startstream global` sets `DEMO_MODE=true` + `DEMO_PROTECT_MEDIA_OWNER=Global`.

**Bugs found and fixed:**
- Manual input tab didn't pass `media_owner_names` → always anonymised Global campaigns
- Campaign header didn't pass media owner context to `format_brands()`
- Overview/executive summary showed only `primary_brand` (often a placeholder) instead of full brand list
- Label inconsistency: "Brands:" vs "Brand(s):" — standardised to "Brand(s):"

---

## 2. Global Presentation Script (COMPLETE)

Wrote and refined presentation script for Global commercial team (10 Feb 2026).

**Files in Dropbox** (`Route Dropbox/.../Global Presentation and Demo/`):

| File | Purpose |
|------|---------|
| `Route - Playout POC - Global - 20260209.pptx` | 7-slide deck |
| `Route - Playout POC - Global - 20260209.pdf` | PDF version |
| `GLOBAL_PRESENTATION_SCRIPT.md` | Full script with stage directions, notes, backups, tech checklist |
| `SCRIPT_CLEAN.md` | Clean spoken script only — for use as presentation aid |
| `SPEAKER_NOTES.md` | Bullet-point version (user prefers the clean script) |

**Key script decisions:**
- Demo campaign: **16699** (Channel Four) — Global + Bauer + JCDecaux, 452 frames, 52M impacts, 94 GRPs
- Run with `startstream global` — Channel Four brand visible, competitors anonymised
- No cliff-drop demo — parked as too risky/confusing for a large commercial audience
- Don't draw attention to the anonymisation — if someone asks about "Brand 1" labels, explain then
- Removed all TV/digital comparison language — reframed positively around strengthening OOH's position
- Softened data quality language — industry challenge framing, not blame
- Slide 6 (reach limitation): added note that this goes away with the new Route
- Backup campaigns: 18295 (Uber Eats), 18143 (Uber), 16860 (Specsavers), 18409 (Waitrose)

---

## 3. Cliff-Drop Campaign Research (PARKED)

Investigated campaign transition patterns for the presentation. Concluded it's not suitable for tomorrow's large audience — needs a side-by-side comparison view that doesn't exist yet.

**Key findings:**
- **McDonald's 16879 → 16882**: Best cliff-drop pattern, but 16879 has no Global → anonymised, 16882 has Global → real brand. Inconsistent.
- **Global-only sequential pairs** (McDonald's 16875→16877, British Gas chains, Specsavers): Clean handoffs but one campaign completely ends and another starts — scheduling boundaries, not cliff-drops.
- **Global-only overlapping pairs** (HSBC): Concurrent buys on different frame sets, not impact transfer.
- **Conclusion**: True cliff-drops occur across media owner boundaries in this dataset. Needs proper UI and more time.

**Future work tracked in** `Claude/todo/upcoming_tasks.md` under "Future: Cliff-Drop Campaign Comparison View".

---

## 4. DigitalOcean Deployment Plan (READY TO EXECUTE)

Full deployment plan created and documented. Zero code changes needed — `PGSSLMODE=require` in the droplet's `.env` is read natively by libpq/psycopg2.

**Runbook**: `Claude/docs/Documentation/DIGITALOCEAN_DEPLOYMENT_RUNBOOK.md` — 770+ lines of copy-paste commands covering all 9 phases.

**Phases:**

| Phase | What | Time |
|-------|------|------|
| 1–2 | Provision DB + Droplet, harden SSH | 25 min |
| 3 | Download dump from Dropbox, pg_restore | 90 min (background) |
| 4–5 | Install Python/UV, clone, configure, systemd | 35 min |
| 6–7 | Caddy reverse proxy + UFW firewall | 20 min |
| 8 | PocketID authentication (Docker) | 45 min |
| 9 | GB geo-blocking (GeoIP iptables) | 15 min |

**Total: ~4 hours** (DB restore overlaps with app setup).

**Key decisions:**
- IP address for now, domain later
- Self-signed cert (Caddy `tls internal`), swap to Let's Encrypt with domain
- PocketID from scratch via Docker — if it blocks, skip and add later
- Geo-blocking via UFW + GeoIP, switch to Cloudflare when domain added
- Cost: ~$67/month ($61 DB + $6 droplet)

**Task checklist in**: `Claude/todo/upcoming_tasks.md` under "Next Priority: DigitalOcean Deployment"

---

## Next Session: Execute DigitalOcean Deployment

Start with `Claude/docs/Documentation/DIGITALOCEAN_DEPLOYMENT_RUNBOOK.md` and work through the phases. Prerequisites:

- [ ] DigitalOcean account with payment method
- [ ] SSH key pair ready
- [ ] Fresh Dropbox link for the database dump (5.7 GB)

---

*Last Updated: 10 February 2026*
