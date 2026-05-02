# Multi-Machine Setup and Repository Workflow

Captures the three-remote repository pattern, the daily workflow it implies, and the procedure for setting up the project on a new machine. Established 2026-04-28; updated 2026-05-01.

## Why This Exists

Adwanted use the public GitHub repo (`RouteResearch/Route-Playout-Econometrics_POC`) as their production reference. Continuing development on `main` of that repo would force them to track moving targets. Daily development therefore happens on a separate private repo, and the public repo only advances via tagged releases.

The docs repo (`Route-Playout-Econometrics_POC-claude-docs`) contains internal handover documents, plans, and CLAUDE.md instructions. It must never appear on public GitHub.

## Repository Layout

### Code repo — `Route-Playout-Econometrics_POC`

| Remote | URL | Role |
|---|---|---|
| `origin` | GitHub private — `RouteResearch/Route-Playout-Econometrics_POC-dev` | Daily driver. `git push` defaults here. |
| `public` | GitHub public — `RouteResearch/Route-Playout-Econometrics_POC` | **Tags only.** Adwanted's reference. Pre-push hook blocks branch pushes; requires annotated tags. |
| `zimacube` | Gitea over Tailscale | Backup mirror. Optional per machine. |

### Docs repo — `Route-Playout-Econometrics_POC-claude-docs`

| Remote | URL | Role |
|---|---|---|
| `origin` | GitHub private — `ianwyatt/Route-Playout-Econometrics_POC-claude-docs` | Daily driver. Permitted by `.claude/route-mode` marker. Personal account, not Route org, to keep noise off the company GitHub. |
| `zimacube` | Gitea over Tailscale | Backup mirror. Optional per machine. |

The docs repo never goes to public GitHub. Its pre-push hook blocks `github.com` URLs unless `.claude/route-mode` is present, and even then only the personal-account private repo URL is in use.

## Symlinks

The code repo has two symlinks pointing at the docs repo as a sibling directory:

```
Route-Playout-Econometrics_POC/.claude  →  ../Route-Playout-Econometrics_POC-claude-docs
Route-Playout-Econometrics_POC/Claude   →  ../Route-Playout-Econometrics_POC-claude-docs
```

Both are gitignored in the code repo, so they must be recreated on each machine. Both repos must be siblings in the same parent directory.

## Daily Workflow

### Code

```bash
git push                               # → private origin (daily driver)
git push zimacube <branch>             # → Gitea backup, if configured
git push public vX.Y-<theme>           # → public release, ANNOTATED TAGS ONLY — see policy below
```

Branch pushes to `public` are rejected by the pre-push hook. The annotated-tag mechanism is what's documented here; **whether to actually push to `public` is a separate policy decision.** See `.claude/CLAUDE.md` → "Public-repo policy" — current default is do NOT push to `public` (tag or branch) without an explicit user instruction naming the `public` remote. Annotated tags are created with `git tag -a vX.Y-name -m "release notes"`.

### Docs

```bash
git push                               # → private origin (daily driver)
git push zimacube main                 # → Gitea backup, if configured
```

Pushing the docs repo to public GitHub is rejected by the pre-push hook regardless of authentication.

## Pre-push Hooks

Hooks live in `.git/hooks/pre-push` per repo and are not version-controlled. When setting up a new machine, run `~/.claude/scripts/install_hooks.sh` from inside each repo to install them.

### Code repo hook behaviour

- Public-remote guard: rejects branch pushes to `public`; requires annotated tags
- Sensitive-data scan
- Generic-naming warning
- Documentation freshness warning (informational only)

### Docs repo hook behaviour

- Blocks any GitHub push unless `.claude/route-mode` is present in the working tree
- The `.claude/route-mode` file is a small marker committed to the docs repo; its presence asserts "this is a Route business project, private GitHub pushes are permitted"

## Setting Up on a New Machine

The procedure assumes you have GitHub access and are putting both repos under a `~/projects/` (or similar) parent.

### 1. Clone both repos as siblings

```bash
cd ~/projects

git clone https://github.com/RouteResearch/Route-Playout-Econometrics_POC-dev.git Route-Playout-Econometrics_POC

git clone https://github.com/ianwyatt/Route-Playout-Econometrics_POC-claude-docs.git
```

The trailing `Route-Playout-Econometrics_POC` argument on the first clone overrides the default directory name (which would otherwise be `…-dev`) so the symlinks resolve correctly.

### 2. Handle existing clones

If a prior clone of the code repo already exists with `origin` pointing at the public repo, rename remotes rather than re-cloning:

```bash
cd Route-Playout-Econometrics_POC
git remote rename origin public
git remote add origin https://github.com/RouteResearch/Route-Playout-Econometrics_POC-dev.git
git fetch --unshallow origin || git fetch origin
git branch --set-upstream-to=origin/main main
git pull origin main
```

If the docs repo's `origin` points elsewhere, fix it similarly. On a Mac with Tailscale you'll typically also want a `zimacube` remote; on machines without Tailscale, skip it.

### 3. Create symlinks

```bash
cd ~/projects/Route-Playout-Econometrics_POC
ln -s ../Route-Playout-Econometrics_POC-claude-docs .claude
ln -s ../Route-Playout-Econometrics_POC-claude-docs Claude
```

Use `ln -sfn …` (force, no-deref) to replace existing broken or wrong symlinks safely.

Verify:

```bash
ls -la .claude Claude
ls Claude/Plans/
```

The `Plans/` listing should show the H1 spec and three implementation plans, confirming the symlink resolves into the docs repo.

### 4. Install hooks

```bash
cd ~/projects/Route-Playout-Econometrics_POC
~/.claude/scripts/install_hooks.sh

cd ../Route-Playout-Econometrics_POC-claude-docs
~/.claude/scripts/install_hooks.sh
```

For the docs repo, also confirm `.claude/route-mode` exists (it should arrive via `git pull` once `c193b66` is in history). If missing:

```bash
cd ~/projects/Route-Playout-Econometrics_POC-claude-docs
mkdir -p .claude
echo "Route business project — permits private GitHub pushes for docs repo." > .claude/route-mode
```

### 5. Python environment

```bash
cd ~/projects/Route-Playout-Econometrics_POC
uv sync
```

This installs `pyproject.toml` + `uv.lock` deps including `duckdb`, `psycopg2-binary`, `streamlit`, etc.

### 6. Environment configuration

Recreate `.env` from `.env.example`. Minimum entries to set:

```
BACKEND=duckdb                         # or postgres, depending on session
DUCKDB_PATH=/path/to/route_poc.duckdb  # required when BACKEND=duckdb

# Postgres credentials only required when BACKEND=postgres
USE_PRIMARY_DATABASE=false
POSTGRES_HOST_SECONDARY=localhost
…
```

### 7. DuckDB data file

Whatever path the in-flight `route-playout-pipeline` DuckDB build produces — set `DUCKDB_PATH` to point at it. Verify:

```bash
uv run python -c "import duckdb, os; conn = duckdb.connect(os.environ['DUCKDB_PATH'], read_only=True); print(conn.execute('SHOW TABLES').fetchall()[:5])"
```

Expected: prints a list of tables including `mv_campaign_browser`, cache tables, etc.

### 8. Smoke

```bash
uv run pytest -x                       # any tests should pass or skip cleanly
startstream                            # if shell function defined; otherwise streamlit run
```

For Plan A onward, see `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md`.

## Per-Machine Status (2026-05-01)

| Machine | Status | Notes |
|---|---|---|
| Mac (`ianwyatt`, primary) | Fully operational | Origin for all pushes; three-remote pattern in place; route-mode marker present; Streamlit + Postgres baseline working. Pending: CLAUDE.md trim still uncommitted in working tree (intentional, awaiting natural-flow commit). |
| Work device (Linux, `/home/dev/projects/`) | Repos cloned, remotes fixed, symlinks created, latest H1 spec/plans pulled | Outstanding: `uv sync`, `.env` recreated, DuckDB path, hooks installed, smoke test |
| Framework Desktop container | Not yet set up under three-remote pattern | When picked up, follow the procedure above |

## Outstanding (Work Device)

1. `uv sync` to install deps
2. `.env` file recreated from `.env.example`
3. `DUCKDB_PATH` set once the DuckDB data file is available
4. `~/.claude/scripts/install_hooks.sh` run in both repos
5. Smoke test: `uv run pytest -x`, browse the existing Streamlit UI on a small DB if possible
6. Confirm `.claude/route-mode` is present in the docs repo (should have arrived via `git pull`)

## Outstanding (General Workflow)

1. `c193b66` (three-remote-pattern documentation), `cd94940` (H1 spec), `07f0117` (H1 plans) have all been pushed to the docs repo's GitHub origin as of 2026-05-01.
2. The CLAUDE.md trim from the previous session is still uncommitted in the docs repo working tree on the Mac. Worth committing during the next docs-repo session — the trim removed ~74 lines of derivable content (source tree, env table, doc pointer list, tech stack) and added the "Next Directions" section flagging DuckDB as committed and React as under consideration.
3. Pre-existing dirty state in the docs repo (mobile-index file renames, `reference/route-api-reference.md`, `Handover/SESSION_2026-03-12_OUTLINE_DOCS_AND_PUBLIC_REPO_CLEANUP.md`) is unrelated to the infra work and should be triaged in its own session.

## Related References

- H1 spec: `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`
- H1A plan (DuckDB swap): `Claude/Plans/2026-04-29-h1a-duckdb-swap-plan.md`
- H1B plan (FastAPI): `Claude/Plans/2026-04-29-h1b-fastapi-layer-plan.md`
- H1C plan (React advertiser views): `Claude/Plans/2026-04-29-h1c-react-advertiser-views-plan.md`
- Project CLAUDE.md (Repository Setup section): `.claude/CLAUDE.md`
- Hooks documentation: `~/.claude/docs/HOOKS_SYSTEM.md`
