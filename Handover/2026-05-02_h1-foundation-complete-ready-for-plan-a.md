# Handover — H1 Foundations Complete, Ready for Plan A

**Date:** 2026-05-02
**Context:** All foundational work for Horizon 1 is done. Spec written, three implementation plans written, infrastructure in place, pipeline-team coordination resolved. The next session should execute **Plan A (DuckDB swap)**.

**Scope decision (2026-05-02):** Postgres is being removed entirely from the POC, not maintained alongside DuckDB. Plan A has been simplified accordingly: no `BACKEND` env var, no dual-backend support, no Postgres regression test. The legacy `feature/mobile-volume-index` branch retains the old Postgres code path for reference but is not migrated.

**Postgres demos still possible** via a frozen git worktree at `v2.1-postgres-final` (commit `5ecf18c`). Lives at `~/projects/Route-Playout-Econometrics_POC-postgres-demo/` (or `~/PycharmProjects/...` on Mac). Stays valid for stakeholder demos throughout Plan A → C development. Full operational reference: `Claude/docs/postgres-demo-worktree.md`.

**Execution environment:** The next Claude session runs on an LXC connected to the Route Tailnet (`tag:iw-dev`), so Tailnet access to `playout-db` is automatic. The session can perform setup tasks (rsync the DuckDB snapshot, install deps, set `DUCKDB_PATH`, install hooks, run smoke tests) autonomously without manual intervention.

---

## Where we are

H1 (DuckDB swap → FastAPI layer → React advertiser-trends views) has moved from "idea" to "ready to execute" across the past three days. Specifically:

### Done

- **Three-remote repository pattern established** for both code and docs repos. Private GitHub origin (daily driver) + public GitHub (tags only, Adwanted's reference) + Gitea backup. `route-mode` marker permits private GitHub pushes for the docs repo. Pre-push hooks updated.
- **Multi-machine setup documented** in `Claude/docs/multi-machine-setup-and-repo-workflow.md`. Both Mac and Linux work device set up against the new pattern.
- **H1 brainstorming complete.** Architecture, scope, milestones, sequencing, testing all locked in. Spec at `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`.
- **Three implementation plans written:**
  - `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md` — Plan A (M1)
  - `Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md` — Plan B (M2 + M4)
  - `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md` — Plan C (M3 + M5 + M6 + M7)
- **Pipeline-team coordination resolved.** Three round-trips covering `spot_break_id` audit, `mv_campaign_browser` rebuild scope, dim-refresh, MV delivery, and rsync ops. Living record at `Claude/docs/pipeline-coordination.md`.
- **DuckDB substrate ready.** Pipeline team rebuilt `mv_campaign_browser` (3,064 rows × 29 cols, 22 populated / 7 NULL until Phase 5) and `mv_campaign_browser_summary` (1 × 24 cols). Snapshot live at `/var/lib/route/snapshots/route_poc_cache.latest.duckdb` (~87 GB). Rsync ops note delivered (`Claude/Handover/POC_RSYNC_OPS.md`).
- **CLAUDE.md updated** to reflect current reality (dual-backend transitional state, H1 active work, key documents pointer table).

### What's deliberately NOT done

- **No POC code changes yet.** The H1 work begins with Plan A; nothing in `src/` has been modified for this work. The current `feature/mobile-volume-index` branch is unrelated and remains as-is.
- **No DuckDB pull on either machine.** That's the first concrete task the next session should do, before any code changes.
- **CLAUDE.md edits are committed** but a few pre-existing unrelated dirty bits in the docs repo (mobile-index file renames, `reference/route-api-reference.md`, `Handover/SESSION_2026-03-12_OUTLINE_DOCS_AND_PUBLIC_REPO_CLEANUP.md`) remain untriaged. They're not blocking H1.

### Open coordination items (pipeline team)

| Item | Status | When |
|---|---|---|
| Phase 5 (campaign-reach rebuild) — fills 7 NULL columns in `mv_campaign_browser` | Tracking | ~2026-05-08 (pipeline ETA) |
| MI summary tables (`cache_mi_*`) extension to full year | Open, deferred | Will plan into pipeline Phase 5 or 5a |

Neither blocks Plan A. Both are needed before stakeholder demos, but Plan A's ship signal is "Streamlit on DuckDB works" — reach absence is acceptable for that.

---

## What the next session should do

**Execute Plan A — DuckDB swap on the existing Streamlit app.** The plan is at `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md`, decomposed into 15 bite-sized tasks plus pre-flight setup.

### Pre-flight (Claude session can run these autonomously)

The LXC has Tailnet access to `playout-db` already, so steps 1–6 below run without manual intervention. Walk through them with the user but don't expect setup blockers.

1. **Pull latest on both repos** (in case the work device is stale):
   ```bash
   cd ~/projects/Route-Playout-Econometrics_POC && git fetch origin && git pull origin main
   cd ../Route-Playout-Econometrics_POC-claude-docs && git pull origin main
   ```

2. **Verify Tailnet + playout-db access:**
   ```bash
   tailscale status | grep playout-db
   ssh routeapp@playout-db 'hostname; date'
   ```

3. **Pull the DuckDB snapshot:**
   ```bash
   mkdir -p ~/data
   rsync -avP --partial --inplace \
       routeapp@playout-db:/var/lib/route/snapshots/route_poc_cache.latest.duckdb \
       ~/data/route_poc_cache.duckdb
   ```
   ~87 GB, ~15–30 min over Tailscale on first pull. Resumable.

4. **Read these in order** before touching code:
   - `.claude/CLAUDE.md` — project rules and key documents pointer
   - `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md` — the plan itself (now DuckDB-only, no dual-backend)
   - `Claude/docs/pipeline-coordination.md` — current cross-team state, schema contracts, gotchas
   - `Claude/Handover/POC_INTEGRATION.md` — pipeline team's canonical operational reference

5. **Branch off `main` — but check for the anonymisation fix first:**
   ```bash
   cd ~/projects/Route-Playout-Econometrics_POC
   git checkout main
   git pull origin main
   git merge-base --is-ancestor cf3c716 HEAD && echo "OK" || echo "MISSING — branch off feature/mobile-volume-index instead"
   git checkout -b feature/duckdb-migration
   ```
   Commit `cf3c716` wires the `DEMO_ANONYMISE_MEDIA_OWNERS` and `DEMO_ANONYMISE_BUYERS` toggles through the UI. If `main` lacks it (because `feature/mobile-volume-index` hasn't been merged yet), branch off `feature/mobile-volume-index` to inherit the fix. Plan A Task 0 covers this in detail.

6. **Set `DUCKDB_PATH`** in `.env`:
   ```
   DUCKDB_PATH=/home/<user>/data/route_poc_cache.duckdb
   DEMO_MODE=false
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   ```
   No `BACKEND` env var, no Postgres credentials — Postgres is gone.

7. **Run pre-flight Task 0** from Plan A: `uv sync` (installs deps including `duckdb`), verify `import duckdb` works, verify the file connects read-only and `SHOW TABLES` returns the expected tables (`mv_campaign_browser`, `cache_route_impacts_15min_by_demo`, `cache_mi_*`, etc.).

### Then execute the plan

Plan A is 15 tasks plus pre-flight, ~2–3 sessions of focused work. The TDD spine is **the parity test (Task 5)** — write it once against every `get_*_sync` query function, run it, watch failures pinpoint each query module that needs dialect fixes (Tasks 6–13), iterate until green.

Critical things to know upfront (also covered in pipeline-coordination.md):

- **Param style sweep:** `%s` → `?` across `src/db/queries/*.py`. Mechanical.
- **Result-format helper:** new `_dict_cursor.py` wrapping `cursor.description` to produce psycopg2-style `RealDictCursor` dicts from DuckDB's tuple results.
- **`buyercampaignref` sanitisation:** if any query touches `mv_playout_15min` directly, apply `TRIM(REGEXP_REPLACE(buyercampaignref, '[\t\n\r]', '', 'g'))` — DuckDB's bare `TRIM()` doesn't strip tabs.
- **`route_release_id`:** bare number (53/54/55/56) on cache tables and `mv_campaign_browser`; FK on `route_frames.release_id`. Different conventions on similarly-named columns.
- **`read_only=True`** always when connecting. Multiple POC processes can attach concurrently this way.
- **DuckDB memory-maps the 87 GB file:** budget 8–16 GB RAM headroom for analytical queries on the impacts table.

### Ship signal for Plan A

- All ~32 shape tests pass on DuckDB
- Streamlit smoke test passes on DuckDB across every tab for at least one campaign
- NULL reach columns render gracefully (existing flighted-campaign N/A handling)
- `.env.example` documents `DUCKDB_PATH`; Postgres env vars removed
- No `psycopg2` imports remain in `src/db/queries/*.py`
- Branch pushed to private origin

---

## Then what

After Plan A ships:
- **Plan B (FastAPI layer)** can begin. Depends on Plan A. ~2 sessions.
- **Plan C (React advertiser views)** depends on Plan B. ~6–8 sessions.
- Both can be picked up in fresh sessions; neither depends on Phase 5 reach data, though the demo experience benefits from it landing before any external showing.

The H1 spec covers all three in detail. H2–H4 (more tabs ported, multi-user, custom audiences) are explicitly out of scope until H1 ships.

---

## Files referenced in this handover

| File | What |
|---|---|
| `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md` | H1 spec |
| `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md` | Plan A — execute this next |
| `Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md` | Plan B — after A |
| `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md` | Plan C — after B |
| `Claude/docs/pipeline-coordination.md` | Current cross-team state |
| `Claude/docs/multi-machine-setup-and-repo-workflow.md` | Repo + machine setup |
| `Claude/Handover/POC_INTEGRATION.md` | Pipeline team's operational reference |
| `Claude/Handover/POC_RSYNC_OPS.md` | How to pull the DuckDB snapshot |
| `.claude/CLAUDE.md` | Project rules + key documents pointer |
