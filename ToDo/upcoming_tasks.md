# Upcoming Tasks

## Next Priority: DigitalOcean Deployment

**Status**: Runbook complete. Ready to execute on DO infrastructure.

### Key Decision

**SSL support: Option A (zero code changes)** — `PGSSLMODE=require` is set in the DO droplet's `.env` file. libpq reads this natively via python-dotenv → os.environ → psycopg2. No modifications to `connection.py` or any other source file. The public GitHub repo and Adwanted's local setup are completely unaffected.

### Background

- **5 Feb 2026**: Database cleanup — 114 GB → 57 GB (dropped 64 indexes + 24 tables)
- **5 Feb 2026**: Fresh export: `exports/route_poc_adwanted_20260205.dump` (5.7 GB compressed, 57 GB restored)
- **5 Feb 2026**: Repo made public: `https://github.com/RouteResearch/Route-Playout-Econometrics_POC`
- **6 Feb 2026**: VM database swapped to reduced export — 114 GB → 57 GB, app verified working
- **10 Feb 2026**: Deployment runbook created, zero code changes approach confirmed
- Adwanted handover package shared via Dropbox (database + source + README)

### Deployment Phases

**Phase 1–2: Infrastructure (~25 min)**
- [ ] Provision DO Managed PostgreSQL (London, Basic 4 GB, 60 GB, PG 17) — ~$61/mo
- [ ] Provision Droplet (London, Ubuntu 24.04, 1 GB) — ~$6/mo
- [ ] Add droplet to DB trusted sources
- [ ] Create deploy user, SSH hardening (disable root, key-only)

**Phase 3: Database (~90 min)**
- [ ] Download dump from Dropbox to droplet
- [ ] Restore with `pg_restore -j 4` (runs in background)
- [ ] Create read-only `app_readonly` user
- [ ] Verify data integrity (expect 836 rows in mv_campaign_browser)

**Phase 4–5: App + Process Management (~35 min)**
- [ ] Install Python 3.11, UV, clone repo, `uv sync`
- [ ] Configure `.env` with DO credentials + `PGSSLMODE=require`
- [ ] Test app manually, verify campaign 16699
- [ ] Create systemd service (`pharos.service`)
- [ ] Set up log rotation

**Phase 6–7: Reverse Proxy + Firewall (~20 min)**
- [ ] Install Caddy, configure reverse proxy with WebSocket support
- [ ] Self-signed cert for IP-only (swap to Let's Encrypt with domain)
- [ ] UFW: allow 22/80/443 only, port 8504 NOT exposed

**Phase 8: PocketID Authentication (~45 min)**
- [ ] Install Docker, deploy PocketID container
- [ ] Configure forward auth with Caddy
- [ ] *If this blocks, skip and add later — app is already HTTPS + firewall secured*

**Phase 9: Geo-Blocking (~15 min)**
- [ ] GeoIP iptables rules for GB-only access
- [ ] *Switch to Cloudflare when domain added*

### Reference Files

| File | Purpose |
|------|---------|
| `Claude/docs/Documentation/DIGITALOCEAN_DEPLOYMENT_RUNBOOK.md` | Complete step-by-step deployment commands |
| `Claude/docs/Documentation/SELF_HOSTED_DEPLOYMENT_GUIDE.md` | Pangolin/PocketID reference (Proxmox version) |
| `exports/README.md` | Adwanted handover README with restore instructions |
| `exports/route_poc_adwanted_20260205.dump` | Fresh database export (5.7 GB) |

---

## Completed: Mobile Volume Index Overlay (5 March 2026)

- Built mobile volume index feature allowing econometricians to overlay mobile footfall-adjusted impacts on charts
- CSV import script (`scripts/import_mobile_index.py`) with ISO week date-shifting (2024 to 2025)
- Query layer: LEFT JOIN at frame x hour granularity, COALESCE to 1.0 for missing index data
- Time Series tab: dual-line charts (raw blue solid, indexed orange dashed) + weekly comparison section
- Detailed Analysis tab: coverage indicator when index data is available
- Exports: three columns (impacts, mobile_index, impacts_mobile_indexed) when toggle is active
- Scope limited to impacts only — reach, cover, GRP, frequency are unaffected
- Documentation: `Claude/docs/Documentation/MOBILE_VOLUME_INDEX.md`
- Branch: `feature/mobile-volume-index`

---

## Completed: Flighted Campaign Handling (10 February 2026)

- Researched baseline detection patterns — 30 campaigns with 7+ day scheduling gaps
- Zero-fill charts with boundary-only approach (clean V-drop, no cluttered markers)
- N/A for reach/GRP/cover/frequency on flighted campaigns across all tabs
- Flighted-aware tooltips and context-aware reach unavailability messages
- Updated campaign browser indicators: "Flighted campaign with scheduling gaps"
- Shared `fill_date_gaps_with_boundary_zeros()` utility in `src/ui/utils/`
- 9 files modified, commit `9abf67a`, pushed to GitHub + Gitea
- Documentation: `Claude/docs/Documentation/FLIGHTED_CAMPAIGN_BASELINE_DETECTION.md`
- Handover: `Claude/handover/SESSION_2026-02-10_FLIGHTED_CAMPAIGNS_AND_CHART_FIXES.md`

---

## Completed: Code Quality Review (5 February 2026)

- Agent-based review of all documentation and source code (4 rounds)
- Fixed 17 documentation inaccuracies across 10 files
- Updated 15 stale MV references across 9 source files
- Deleted 7 dead code files (2,411 lines removed)
- Fixed runtime bug: frame count query referenced dropped table
- Fixed null safety issue in campaign count query
- 4 commits: `183766c`, `4b9b7bd`, `cc34147`, `bdf4ed0`
- Handover: `handover/SESSION_2026-02-05_CODE_QUALITY_REVIEW.md`

---

## Completed: Database Cleanup (5 February 2026)

- Audited all 101 indexes and 42 tables against every SQL query in `src/db/`
- Dropped 64 unused indexes (38 GB) + 24 unused tables (19 GB)
- Database: 114 GB → 57 GB (57 GB freed, 50% reduction)
- 18 tables + 1 view + 14 indexes remaining — all used by app
- Kept `idx_impacts_demo_campaign` (2.8 GB) as fallback safety net
- Documentation: `docs/Documentation/DATABASE_INDEX_CLEANUP.md`
- Handover: `handover/SESSION_2026-02-05_INDEX_CLEANUP.md`

---

## Completed: VM Database Swap (6 February 2026)

- Dropped 114 GB database on Ubuntu 24.04 Parallels VM
- Restored from reduced export (5.7 GB → 57 GB)
- VM disk: 138 GB → 81 GB used (159 GB free)
- Pulled latest code (6 commits), synced deps
- Installed openssh-server on VM
- App verified working on `http://10.211.55.5:8504`
- Handover: `Handover/SESSION_2026-02-06_VM_DATABASE_SWAP.md`

---

## Completed: Adwanted Handover (5 February 2026)

- All dead code removed from codebase and documentation
- VM installation tested successfully (Ubuntu 24.04)
- GitHub fine-grained token auth documented
- Tag `v2.0-adwanted-handover` updated to commit `76e0aca` (was `eb5a7c8`)
- Fresh database export: `exports/route_poc_adwanted_20260205.dump` (5.7 GB)
- GitHub repo made public (issues/wiki/discussions disabled)
- Handover package shared with Adwanted via Dropbox

---

## Completed: Codex Code Review Fixes (4 February 2026)

All 12 actionable findings addressed across 6 rounds. Score: 6.4 → 7.8/10.

---

## Pre-Existing Test Failures (Local DB)

Two test failures when running against local database:

1. `test_empty_demographic_segments_list` — returns all data instead of empty
2. `test_query_performance_under_100ms` — 214ms on local DB

Not blocking; investigate separately.

---

## Completed: Selective Brand Anonymisation (9 February 2026)

- Implemented `startstream global` mode for Global commercial team presentation
- `DEMO_PROTECT_MEDIA_OWNER=Global` shows real brands on Global campaigns, anonymises competitors
- 10 files modified across anonymisation config, UI tabs, components, formatters, and exports
- Fixed 4 bugs during implementation (manual input, header, overview, label consistency)
- Commit: `9267c29`, pushed to GitHub + Gitea
- Handover: `handover/SESSION_2026-02-09_SELECTIVE_ANONYMISATION_AND_CLIFF_DROP.md`

---

## Future: Cliff-Drop Campaign Comparison View

**Status**: Research complete, UI not built. Parked for post-presentation work.

### What we know
- McDonald's 16879 → 16882 is the best cliff-drop example (impacts flatten in 16879, 16882 picks up immediately on Sep 22)
- 16882 appears in TWO different campaign transitions — interesting for demonstrating campaign ID reuse
- British Gas has a 25-pair continuous chain of weekly Global campaigns — good for chain visualisation
- The true cliff-drop pattern tends to occur across media owner boundaries, not within Global-only pairs

### What needs building
- [ ] Side-by-side or overlaid daily impact chart for two campaign IDs
- [ ] Data source: `mv_cache_campaign_impacts_day` for daily totals
- [ ] Handle anonymisation mismatch when paired campaigns have different media owners
- [ ] Consider campaign chain visualisation (British Gas weekly rotation)

---

## Future Enhancements

- Cliff-drop campaign comparison view (see above)
- Cumulative build with daily data (smoother charts)
- Cost and financial tracking
- Natural language query interface
- AI-powered insights
- Classic frame support
- Multi-user support with role-based access
- Demographic filtering for Weekly Reach/GRP tab
- User areas with saved campaigns

---

*Last Updated: 5 March 2026*
