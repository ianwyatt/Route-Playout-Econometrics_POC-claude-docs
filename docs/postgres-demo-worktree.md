# Postgres Demo Worktree — Frozen Reference for Stakeholder Demos

**Purpose:** A frozen, immutable copy of the Postgres-backed Streamlit app pinned to tag `v2.1-postgres-final` (commit `5ecf18c` from `feature/mobile-volume-index`). Used for stakeholder demos that need the working Postgres pipeline while DuckDB migration (Plan A) progresses on a feature branch.

**Created:** 2026-05-02
**Pinned to:** `v2.1-postgres-final` (`5ecf18c feat: excel export improvements — sheet renames, (000s) headers, MI columns, brand slugs`)

---

## What this is

A **git worktree** (not a fresh clone) sitting at `~/projects/Route-Playout-Econometrics_POC-postgres-demo/` (or `~/PycharmProjects/...` on Mac). It shares the same `.git/` as the main checkout but exposes the source code at a frozen tag, with its own working directory, virtualenv, and `.env`.

**Why a worktree, not a clone:** lighter (no `.git/` duplication), keeps refs in sync (`git fetch` in either updates both), faster setup. Trade-off: shares hooks with the main repo, so commit attempts from the worktree fire the same pre-commit/post-commit hooks.

**Why tagged not branched:** branches drift; tags don't. The worktree's HEAD is detached at the tag, which makes accidental commits awkward by design. Treat the worktree as **read-only** — if you need to update what it points at, retag and re-add.

---

## Directory layout

```
~/projects/                                                  (or ~/PycharmProjects on Mac)
├── Route-Playout-Econometrics_POC/                          # MAIN — active dev, Plan A on feature/duckdb-migration
├── Route-Playout-Econometrics_POC-postgres-demo/            # FROZEN — Postgres demo worktree at v2.1-postgres-final
└── Route-Playout-Econometrics_POC-claude-docs/              # docs repo (shared by both via Claude/.claude symlinks)
```

Both checkouts have `.claude` and `Claude` symlinks pointing at the docs repo, so they share documentation/plans/handover content. Claude Code skills, hooks, and project rules apply to both.

---

## How to run a demo

```bash
cd ~/projects/Route-Playout-Econometrics_POC-postgres-demo
startstream                          # default: primary database (MS-01), nothing anonymised
startstream demo                     # + brand anonymisation only
startstream global                   # selective: real Global brands, others anonymised
startstream local                    # local Postgres on this machine
startstream local demo               # local Postgres + brand anonymisation
startstream local global             # local Postgres + selective anonymisation
stopstream                           # stop all instances
```

`startstream` is a shell function in `~/.zshrc` — same one as the main checkout uses. Running it from within the worktree directory automatically runs the frozen v2.1 code with whatever Postgres credentials are in the worktree's `.env`.

The worktree opens on `localhost:8504` (same default port as the main checkout). To run the worktree alongside the main DuckDB checkout simultaneously, override the port:

```bash
USE_PRIMARY_DATABASE=true streamlit run src/ui/app.py --server.port 8505
```

### Demo invocation reference

`startstream demo` only anonymises **brands** by default. Media owners and buyers stay visible. For tighter anonymisation, use env-var prefixes (no shell-config change needed):

| Audience / scenario | Invocation |
|---|---|
| Internal team review (everything visible) | `startstream` |
| Brand-anonymised demo (default `demo`) | `startstream demo` |
| **Full client-safe demo** (brands + media owners + buyers hidden) | `DEMO_ANONYMISE_MEDIA_OWNERS=true DEMO_ANONYMISE_BUYERS=true startstream demo` |
| Brands + media owners hidden, buyers visible | `DEMO_ANONYMISE_MEDIA_OWNERS=true startstream demo` |
| Brands + buyers hidden, media owners visible | `DEMO_ANONYMISE_BUYERS=true startstream demo` |
| Global team presentation (real Global, anonymise competitors) | `startstream global` |

All variants accept `local` for the secondary database (`startstream demo local`, `startstream global local`, etc.).

**To make full client-safe anonymisation the default for this worktree**, edit the worktree's `.env` and add:

```
DEMO_ANONYMISE_MEDIA_OWNERS=true
DEMO_ANONYMISE_BUYERS=true
```

Then any `startstream demo*` invocation hides everything. Won't affect non-demo runs (the master `DEMO_MODE=true` gate still applies).

Full anonymisation reference (env vars, where applied, cookbook): `docs/03-demo-mode.md` in the code repo.

---

## What the worktree contains (and what it doesn't)

**Tracked files:** identical to `v2.1-postgres-final` — Streamlit app, query layer (psycopg2-based), tabs, components.

**Gitignored / untracked but set up at creation:**
- `.claude/` — symlink to docs repo (relative `../Route-Playout-Econometrics_POC-claude-docs`)
- `Claude/` — symlink to docs repo (same target)
- `.env` — copied from the main checkout's `.env` at worktree creation; edit if Postgres credentials differ
- `.venv/` — own virtualenv via `uv sync`

**Not present (not needed for demos):**
- `tests/fixtures/route_poc_test.duckdb` — DuckDB fixture, only relevant on the dev checkout
- DuckDB-related env vars (`DUCKDB_PATH`) — Postgres-only worktree

---

## When to use the worktree (vs main checkout)

| Use case | Where |
|---|---|
| Stakeholder demo of the existing Postgres-backed app | **postgres-demo worktree** |
| Reproducing a Postgres-specific bug for triage | **postgres-demo worktree** |
| Testing whether a query returns the same value on Postgres vs DuckDB | both — postgres-demo for Postgres side, main for DuckDB side |
| Active development (Plan A, DuckDB migration, FastAPI, React) | **main checkout**, on `feature/duckdb-migration` |
| Running the parity test (Plan A Task 5) | **main checkout** |
| Adding new features to either Postgres or DuckDB versions | **main checkout** (don't add features to the worktree — it's frozen) |

---

## Critical rules for Claude sessions

When a Claude session is operating in the postgres-demo worktree (or knows it exists), these rules apply:

1. **Never commit from the worktree.** It's at detached HEAD on a tag. Commits made there become orphans. Git will warn but not stop you. **Don't fight the warning — switch to the main checkout if code changes are needed.**

2. **Never `git checkout <branch>` inside the worktree.** That moves the worktree off the tag, defeating its purpose. If you ever need to update what the worktree points at, do it deliberately:
   ```bash
   cd ~/projects/Route-Playout-Econometrics_POC-postgres-demo
   git checkout v2.X-new-tag                # only when intentionally re-pinning
   ```

3. **Never `git pull` inside the worktree.** Pulls happen in the main checkout. The worktree's HEAD is fixed.

4. **Never run migrations or schema-modifying scripts in the worktree.** It's a demo target — not a development surface.

5. **Don't modify source code in the worktree.** Any change there is by definition not in version control (or worse, an orphan commit). Make changes in the main checkout, on the appropriate branch.

6. **`uv sync` in the worktree** is fine — it's a local venv operation, doesn't affect git state.

7. **`.env` edits in the worktree** are fine — gitignored, local-only.

8. **Pre-push hook will reject any push attempts from the worktree** going to public GitHub (per the standard pre-push guard). Daily push to `origin` (private) would technically work but should never be needed since you're not making commits.

---

## Troubleshooting

### "Streamlit won't start / import error"

Likely cause: virtualenv stale or `uv sync` not run.

```bash
cd ~/projects/Route-Playout-Econometrics_POC-postgres-demo
rm -rf .venv
uv sync
startstream
```

### "Postgres connection refused / can't reach database"

Likely cause: `.env` has wrong credentials or the Postgres server isn't running.

```bash
# Verify .env has the right Postgres credentials (compare against main checkout's .env)
diff ~/projects/Route-Playout-Econometrics_POC/.env ~/projects/Route-Playout-Econometrics_POC-postgres-demo/.env

# Verify local Postgres is up (if using local backend)
psql -h localhost -U ianwyatt -d route_poc -c '\dt' | head

# Verify primary Postgres is reachable (if using MS-01)
psql -h $POSTGRES_HOST_PRIMARY -U $POSTGRES_USER_PRIMARY -d $POSTGRES_DATABASE_PRIMARY -c '\dt' | head
```

### "Port 8504 already in use"

Main checkout's Streamlit is also running. Either `stopstream` first, or run the worktree on a different port:

```bash
USE_PRIMARY_DATABASE=true streamlit run src/ui/app.py --server.port 8505
```

### "Symlinks don't resolve / docs not found inside worktree"

Symlinks weren't created at worktree setup. Recreate:

```bash
cd ~/projects/Route-Playout-Econometrics_POC-postgres-demo
ln -sfn ../Route-Playout-Econometrics_POC-claude-docs .claude
ln -sfn ../Route-Playout-Econometrics_POC-claude-docs Claude
ls Claude/Plans/   # should list H1 plans
```

### "Worktree shows files I don't recognise / wrong commit"

Verify HEAD pinning:

```bash
cd ~/projects/Route-Playout-Econometrics_POC-postgres-demo
git rev-parse HEAD                # should print 5ecf18c... (or whatever v2.1-postgres-final points at)
git describe --tags                # should print v2.1-postgres-final
```

If HEAD has drifted (someone ran `git checkout` in the worktree against guidance), reset:

```bash
git checkout v2.1-postgres-final
```

### "I made a commit by accident in the worktree"

The commit is an orphan (detached HEAD). To recover:

```bash
git rev-parse HEAD                # capture the orphan SHA, e.g. abc1234
# Switch to main checkout
cd ~/projects/Route-Playout-Econometrics_POC
# Cherry-pick to the appropriate branch
git checkout feature/duckdb-migration   # or wherever it should land
git cherry-pick abc1234
# Then in the worktree, reset back to the tag
cd ~/projects/Route-Playout-Econometrics_POC-postgres-demo
git checkout v2.1-postgres-final
```

### "I want to update the worktree to a newer Postgres version"

Two paths:

**Option A — re-tag and re-pin (recommended):** create a new tag pointing at the desired commit, then move the worktree:
```bash
cd ~/projects/Route-Playout-Econometrics_POC
git tag -a v2.2-postgres-final <commit-sha> -m "<reason>"
git push origin v2.2-postgres-final
cd ../Route-Playout-Econometrics_POC-postgres-demo
git checkout v2.2-postgres-final
uv sync                            # in case deps changed
```

**Option B — destroy and recreate:**
```bash
git -C ~/projects/Route-Playout-Econometrics_POC worktree remove ../Route-Playout-Econometrics_POC-postgres-demo
git -C ~/projects/Route-Playout-Econometrics_POC worktree add ../Route-Playout-Econometrics_POC-postgres-demo v2.2-postgres-final
# then: ln -s symlinks, cp .env, uv sync
```

### "I want to delete the worktree entirely"

When DuckDB demos replace Postgres demos:

```bash
git -C ~/projects/Route-Playout-Econometrics_POC worktree remove ../Route-Playout-Econometrics_POC-postgres-demo
# Optional: delete the tag too if archiving
git tag -d v2.1-postgres-final
git push origin --delete v2.1-postgres-final
```

---

## How worktree git operations differ from a normal checkout

The worktree shares `.git/` with the main checkout. Practical implications:

- **`git fetch` in either checkout updates both.** New refs land in the shared `.git/`.
- **Branches and tags are visible from both.** `git branch -a` in the worktree lists everything from the main repo's view.
- **Hooks (`.git/hooks/`) are shared.** A pre-commit, pre-push, or post-commit hook installed in `.git/hooks/` fires for commits/pushes attempted from either working tree.
- **The worktree has a `.git` *file*** (not a directory) pointing at `.git/worktrees/<name>/` in the main repo. Don't rm it.

---

## On creation date

This worktree was set up on 2026-05-02 as part of the H1 foundation work, immediately before Plan A (DuckDB swap) execution begins. The decision rationale and Postgres-removal scope decision are recorded in:

- `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md` § Scope note
- `Claude/Handover/2026-05-02_h1-foundation-complete-ready-for-plan-a.md`
- `Claude/docs/pipeline-coordination.md` § "2026-05-02 (later) — POC scope decision"

The expected lifetime is **until DuckDB-backed advertiser-trends views are demo-ready** (post-Plan-C, post-Phase-5-reach-data) — at which point the new app supersedes the Postgres demo and this worktree can be destroyed.
