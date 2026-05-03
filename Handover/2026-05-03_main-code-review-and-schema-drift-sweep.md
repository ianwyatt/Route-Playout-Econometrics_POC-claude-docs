# Handover — main code review + schema-drift sweep merged

**Date:** 2026-05-03
**Branch state:** `main` at `dd02243` (merged + pushed to `origin`).
**Suite:** 209/209 backend (was 212; three lost from deleted
`test_import_mobile_index.py`); frontend 8/8 + clean build.

This session executed floor items #1 (code review) and #2 (schema-drift
sweep) from the 2026-05-08 next-session prompt, in that order. Items
#3-#5 untouched; #6 still pipeline-blocked; #7 still pending.

---

## Floor item #1 — Code review of `main`

Deliverable: `Claude/Plans/2026-05-08_main-code-review.md`. Four
parallel `feature-dev:code-reviewer` agents covered backend + DB,
Streamlit UI, React frontend, tests + deps + hygiene. CRITICAL claims
spot-verified before promotion.

Headline counts: 6 CRITICAL, 11 HIGH, 13 MEDIUM, handful of LOW.
Dominant theme was Postgres residue from the H1A migration not having
been swept.

The review proposes a prioritised fix sequence in §6 — that section
drove the work in floor #2 and is the canonical reference for what
remains to be folded into floor items #3–#5.

---

## Floor item #2 — Schema-drift sweep — MERGED

Branch `chore/schema-drift-sweep` (now deleted) → merged to `main`
via `--no-ff` → pushed to `origin`. **Public remote NOT touched** per
project policy.

11 commits, 28 files, **+387 / −3070 lines**:

| SHA | Item | Summary |
|---|---|---|
| `8055776` | H10 + C6 | `frontend/.vite/` to `.gitignore`; app.py PostgreSQL→DuckDB |
| `fc0c7cd` | LOWs | index.html title, `lang="en-GB"`; shadcn → devDependencies |
| `6d05cf3` | follow-up | Re-apply index.html edits silently dropped by `fc0c7cd` |
| `3f60bdf` | C3 | Delete `src/db/route_releases.py` (–648 lines); reduce `src/db/__init__.py` |
| `3150c7c` | M1 | Strip `PostgreSQLConfig` + `DatabaseConfig` from `src/config.py` (–204 lines) |
| `91deff8` | M11 | Clarify `.env.example` STREAMLIT_URL note |
| `fa9efe4` | H11 (interim) | Mark docs/ index pre-DuckDB legacy (later superseded) |
| `b04ae4c` | C2 | Delete five Postgres-era scripts + orphan test (–1222 lines) |
| `fdfefea` | C4 | Drop `psycopg2-binary` + `asyncpg` from `pyproject.toml` + `uv.lock` |
| `db9400a` | docs | Delete six Postgres-era docs (01/04/05/09/10/11), rewrite README (–873 lines) |
| `864352a` | docs | Fix Postgres residue in 02/03/08 |

Single merge commit `dd02243`.

### User decisions captured during the work

1. **Mobile-index ingest scripts** (C2): pipeline team owns this going
   forward. Consequence: deleted both `import_mobile_index.py` and
   `import_mobile_index_from_db.py` outright (including
   `parse_mobile_index_csv` which had no live consumer), plus three
   self-marked-obsolete shell scripts (`refresh_local_mvs.sh`,
   `refresh_mv_campaign_browser.sh`, `export_demo_database.sh`).
2. **`use_primary` UI cleanup**: defer to its own branch/session. Not
   touched in this sweep.
3. **Postgres-era docs**: delete outright (git history preserves).

### What was deliberately NOT swept

- **`use_primary` parameter chain in `src/ui/`** — ~100 sites across
  loaders, components, tabs, plus the `os.environ["USE_PRIMARY_DATABASE"]`
  toggle in `src/ui/components/campaign_browser/header.py:24-27`.
  Removing the radio button is UI-visible. Belongs to its own branch.
- **Orphan tests + dead `validators.py`**: the review's §6 split puts
  H1 (delete `tests/conftest.py`, `tests/test_validators.py`,
  `src/utils/validators.py`) into floor item #3. Trivial when picked
  up.
- **Other shell scripts under `scripts/`**: `build_test_duckdb.py`
  remains live. None of the deleted ones had any live consumer.

### Gotchas discovered

- **`Edit` calls can silently fail to land at commit time.** Two
  `Edit` calls on `frontend/index.html` (lang + title) returned
  "updated successfully" but the changes were absent from the working
  tree at the next `git diff`. Re-running the same `Edit` calls in a
  later turn worked. Cause unknown — possibly a race between the Edit
  tool's filesystem write and a subsequent npm install rebuild, or a
  Claude Code tool quirk. **Always verify with `git diff` before
  staging if you've done parallel Edits across multiple files.**
- **`docs/` was bigger than the review estimated.** Six fully-Postgres
  files needed deletion (not just the README). Three more (02, 03, 08)
  had small residue. Two (06, 07) were clean. Net –873 lines.
- **`scripts/` had three more dead Postgres files** beyond the
  reviewer's C2 target. Two literally self-document as obsolete; one
  is `pg_dump`-based and structurally impossible without Postgres.
  All deleted in the same C2 commit.
- **The `parse_mobile_index_csv` parser was orphan code with tests** —
  same shape as the validators situation. Tests inflate the green
  count without exercising anything live. Fold this kind of thing
  into floor #3.

---

## State of `main` after merge

```
dd02243  Merge branch 'chore/schema-drift-sweep'
864352a  docs: fix Postgres residue in surviving in-repo docs
db9400a  docs: delete Postgres-era reference docs
fdfefea  chore(deps): drop psycopg2-binary and asyncpg
b04ae4c  chore(scripts): delete Postgres-era ingest/export tooling
fdfefea  ...
89ed99e  Merge branch 'fix/mobile-index-integration-tests'
```

- Backend: 209/209 green (3 fewer tests vs prior — orphan
  `test_import_mobile_index.py` removed).
- Frontend: vitest 8/8, build clean, ~320 KB main + 4.6 MB lazy.
- `uv sync --extra dev` produces a clean install with two fewer
  runtime packages.
- Working tree clean (the `.claude/` and `Claude/` symlinks are
  intentionally untracked per `.gitignore`).
- Public remote not touched.

---

## Outstanding / what the next session should do

The 2026-05-09 next-session prompt re-orders the remaining work and
folds in the deferred review items. Read it next.

Brief recap of what's still open:

| # | Item | Source |
|---|---|---|
| 3 | Backend test-coverage gap audit + orphan-test removal (H1) | floor #3 + review H1 |
| 4 | mypy strict-mode pass | floor #4 + review M7 |
| C5 | Overview vs Geographic ×1000 forensics + fix | review C5 |
| C1 | `/reach/weekly` endpoint contract (split or document) | review C1 |
| use_primary UI | ~100 sites + radio button removal | user-deferred |
| H batch | H2 (CI), H3 (tabs/__init__), H4 (frame_hourly cache), H5 (frontend null), H6 (per-section error UI), H7 (advertiser timeseries N+1), H8 (advertiser detail dup scans), H9 (LIMIT param) | review §6 |
| 6 | Shape descriptor — pipeline-blocked until Phase 5 reach lands | floor #6 |
| 7 | Visual fidelity review | floor #7, needs user eyes |

The shape-descriptor item (#6) remains gated on Phase 5 reach data
landing in `mv_campaign_browser` — check
`Claude/docs/pipeline-coordination.md` first when picking it up.
