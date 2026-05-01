# POC team — DuckDB snapshot pull (rsync ops note)

**Last updated:** 2026-05-02
**Audience:** POC team building against `mv_campaign_browser` + `cache_route_impacts_15min_by_demo`.
**Status:** Live. Latest snapshot is `route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb` (87 GB).

This is the operational pull path until Phase 5a wires automatic fanout to `playout-frontend`. You pull from `playout-db` directly, on demand, after we ping you that a new snapshot is available.

---

## TL;DR

```bash
# One-off pull (run from your POC dev box)
rsync -avP --partial --inplace \
    routeapp@playout-db:/var/lib/route/snapshots/route_poc_cache.latest.duckdb \
    /path/to/your/local/route_poc_cache.duckdb
```

Then attach read-only:

```python
import duckdb
con = duckdb.connect("/path/to/your/local/route_poc_cache.duckdb", read_only=True)
con.execute("SELECT COUNT(*) FROM mv_campaign_browser").fetchone()
```

That's the whole loop. The rest of this doc is setup + cadence + gotchas.

---

## Step 1 — Tailnet access (one-time)

`playout-db` lives on the Route Tailscale tailnet (`tailafc0d.ts.net`) under tag `tag:iw-dev`. You need:

1. A Tailscale account on the Route tailnet using your `@route.org.uk` Google identity. Sign in at <https://login.tailscale.com> with that account; if you can't see Route's tailnet, ping Ian to invite you.
2. Tailscale installed on the box you'll rsync from (Mac, Linux, whatever). `brew install tailscale` on macOS, or follow <https://tailscale.com/download> for your platform.
3. An ACL grant. Ping Ian (`ianw@route.org.uk`) with your Tailscale identity. The ACL change is one rule — already-paved pattern, takes a minute:
   ```jsonc
   {
     "action": "accept",
     "src":    ["<your-email>@route.org.uk"],
     "dst":    ["tag:iw-dev"],
     "users":  ["routeapp"]
   }
   ```

**Verify access** before you try rsync:

```bash
tailscale status | grep playout-db        # should show the host as active
ssh routeapp@playout-db 'hostname; date'  # should print "playout-db" + UTC
```

If `ssh` hangs or returns "Permission denied", the ACL hasn't landed yet — ping Ian.

No `~/.ssh/authorized_keys` setup needed. Tailscale SSH (port 22) handles auth via the tailnet ACL.

---

## Step 2 — The pull command

The canonical source is **always** the symlink, not a date-stamped file:

```
routeapp@playout-db:/var/lib/route/snapshots/route_poc_cache.latest.duckdb
```

This is a CHECKPOINTed, immutable snapshot. The pipeline team updates the symlink atomically after each rebuild. **Never rsync the live DB** (`/var/lib/route/route_poc_cache.duckdb`) — it's single-writer-locked during cacher runs.

Recommended flags:

```bash
rsync -avP --partial --inplace \
    routeapp@playout-db:/var/lib/route/snapshots/route_poc_cache.latest.duckdb \
    /path/to/local/route_poc_cache.duckdb
```

Why each flag:
- `-a` archive mode (preserves perms + times)
- `-v` progress + final stats
- `-P` = `--progress --partial` — show transfer progress, keep partial on interrupt
- `--inplace` write directly into the destination, don't churn a temp file (saves disk on 87 GB)

**Throughput**: expect ~50-100 MB/s over Tailscale (depends on your relay path; direct UDP is faster than DERP). 87 GB ≈ 15-30 min on a good link, longer if you're DERP-relayed.

**Resumability**: `--partial` + `--inplace` means an interrupted pull resumes where it left off. Re-run the same command.

### Faster after the first pull

After the first full pull, subsequent pulls are delta-only — rsync diffs against your local copy and only ships changed blocks. A typical post-cacher snapshot delta is small (1-5 GB) because the bulk of the DuckDB file is the 2.32B-row impacts table that's append-only.

---

## Step 3 — Attach read-only

```python
import duckdb
con = duckdb.connect("/path/to/local/route_poc_cache.duckdb", read_only=True)

# Quick sanity check
con.execute("SELECT COUNT(*) FROM mv_campaign_browser").fetchone()
# expect: (3064,)

con.execute("""
    SELECT route_release_id, COUNT(*) AS pairs, SUM(impacts) AS total_impacts
    FROM cache_route_impacts_15min_by_demo
    WHERE campaign_id = '<some_campaign>'
    GROUP BY 1 ORDER BY 1
""").fetchall()
```

`read_only=True` is **strongly recommended** — it lets multiple processes attach the same file concurrently and prevents accidental writes. You don't need DuckDB's write side for any POC use case.

**Multiple readers OK.** If your POC has a Streamlit + a notebook + a parity test all reading the same file, that's fine — DuckDB serialises reads internally.

---

## Step 4 — Snapshot cadence (when to pull)

**Cadence: per-event, not scheduled.** We don't push snapshots on a clock; we update the symlink after meaningful changes and ping you.

Triggering events (what causes a new snapshot):
- Cacher rebuild — full or partial re-cache of `cache_route_impacts_15min_by_demo`
- MV rebuild — `mv_campaign_browser`, `mv_campaign_browser_summary`, etc.
- Schema change — column add/drop/rename, type change
- Phase milestone landing — Phase 5 (campaign-reach) when it ships

How you'll find out:
- **Slack/email ping** from Ian noting "new snapshot, pull when convenient" + a one-line summary of what changed.
- The handover note in `Claude/Handover/<date>_*_handover.md` (private docs repo) records it too, but the ping is the operational signal.

Between pings, the symlink may stay stable for days. You can re-pull harmlessly — rsync will detect no changes and exit fast.

**You do not need to pull every snapshot.** Pull when you're about to deploy/test something, or when the ping flags a change you care about (e.g. Phase 5 reach cols going from NULL → real values).

### Verifying you got the right snapshot

```bash
ssh routeapp@playout-db 'readlink /var/lib/route/snapshots/route_poc_cache.latest.duckdb'
# e.g. route_poc_cache.post-mv-rebuild.20260501T122821Z.duckdb
```

That filename is the snapshot's identity. Compare against your local file:

```bash
ssh routeapp@playout-db 'md5sum /var/lib/route/snapshots/route_poc_cache.latest.duckdb'
md5sum /path/to/local/route_poc_cache.duckdb
```

MD5s match → you're current.

---

## Gotchas

### `read_only=True` is a strong recommendation, not optional

If two processes try to attach the same file with one of them as writer, the second gets `IO Error: Could not set lock on file ...`. Always `read_only=True`. There's no POC use case that needs write.

### The 87 GB file expands on attach

DuckDB memory-maps the file; resident memory grows as you query. Budget at least 8-16 GB RAM headroom for analytical queries on the impacts table (2.32B rows). If you're on a small dev box, the LXC has 256 GB RAM and is happy to run queries directly — see "Direct query, no pull" below.

### Phase 5 reach columns are still NULL/0

`mv_campaign_browser` has 7 reach-derived columns currently NULL/0 (per the agreed partial-v1 contract). Phase 5 fills these — ETA next Friday-ish. Build your query layer to handle NULL gracefully; don't filter rows out where reach IS NULL or you'll lose all 3,064 rows on v1.

### Sanitise `buyercampaignref` if you join from `mv_playout_15min`

`cache_route_impacts_15min_by_demo.campaign_id` is already sanitised. If you join back to `mv_playout_15min.buyercampaignref`, sanitise that side too — DuckDB's bare `TRIM()` doesn't strip tabs, and there's a known TAB-suffix bug in some values:

```sql
TRIM(REGEXP_REPLACE(buyercampaignref, '[\t\n\r]', '', 'g'))
```

### Two `route_release_id` conventions

- `cache_route_impacts_15min_by_demo.route_release_id` = bare number (53 = R53)
- `route_frames.release_id` = FK (10 = R53, joins to `route_releases.id`)

Different conventions on similarly-named columns. Check which side you're on. Detail in `docs/POC_INTEGRATION.md` § "Operational gotchas".

---

## Direct query, no pull (alternative)

If your team prefers, you can skip the rsync entirely and query `playout-db` over SSH:

```bash
ssh routeapp@playout-db ".venv/bin/python -c '
import duckdb
con = duckdb.connect(\"/var/lib/route/route_poc_cache.duckdb\", read_only=True)
print(con.execute(\"SELECT COUNT(*) FROM mv_campaign_browser\").fetchone())
'"
```

The LXC has 16 cores / 256 GB RAM and DuckDB caches column data internally, so analytical queries are fast. Trade-off: you're network-dependent, and you can't iterate on schema/queries offline. Most teams prefer pulling a local copy. Either path is supported.

---

## When something goes wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| `ssh: connect to host playout-db: ...` | Not on tailnet, or ACL not landed | `tailscale status`, ping Ian |
| `Permission denied (publickey)` | Tailscale SSH not granted to `routeapp` | ACL needs `users: ["routeapp"]` |
| rsync hangs at 0% | DERP relay path; very rarely the LXC is offline | Wait or check `tailscale status` |
| `IO Error: Could not set lock on file …` on attach | You opened the live DB, or you didn't pass `read_only=True` | Always pull from `snapshots/`, always `read_only=True` |
| Query returns 0 rows but used to work | Your local snapshot is stale; symlink moved | Re-pull |
| MD5 mismatch after rsync | Interrupted pull, or local file got truncated | Re-run rsync — `--partial --inplace` resumes cleanly |

For anything else: ping Ian (`ianw@route.org.uk`).

---

## Cross-references

- `docs/POC_INTEGRATION.md` — schema contract, what's ready/stale/coming, query patterns
- `docs/CURRENT_INFRASTRUCTURE.md` — full operational stack (hosts, secrets, networking)
- `docs/CACHER_GUIDE.md` — how the cacher writes data (informational; POC doesn't run it)
