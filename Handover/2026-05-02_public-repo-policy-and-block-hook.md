# Handover — public-repo policy + block hook

**Date:** 2026-05-02 (third session same day, after the floor-items-1+5 handover)
**Branch:** `feature/duckdb-migration` (unchanged, HEAD `ccf78b8` on `origin`)
**Docs repo HEAD:** `3e0562e` on `origin/main`
**Status:** Code repo untouched. All work was policy hardening + Claude Code harness configuration in the docs repo, plus one cross-team gotcha doc. Branch is still 71 commits ahead of `main` and ready to merge when the user gives the go-ahead.

---

## What shipped this session

Single docs-repo commit: `3e0562e` — `chore(claude): block pushes to public remote without explicit approval`. Six files, +111 / −18 lines.

| File | Change |
|---|---|
| `CLAUDE.md` | New "Public-repo policy" section. Default stance: do NOT push to `public` (tags or branches) without an explicit user instruction naming the `public` remote. Pre-push hook blocks branches as backstop; tags need policy compliance. The merge flow no longer assumes a public push as part of "publishing to Adwanted" — that's now its own opt-in. |
| `Handover/NEXT_SESSION_PROMPT_2026-05-05.md` | Merge flow rewritten — no public push, no auto-tag at merge time. Working-constraints section reflects the new policy. |
| `docs/multi-machine-setup-and-repo-workflow.md` | One-line policy pointer added to the release-mechanism block in §Daily Workflow → Code. |
| `docs/pipeline-coordination.md` | New "Operational gotcha" entry: `cache_campaign_reach_week` has two `reach_type` values (`individual` + `cumulative`) per `(campaign, week)`. Fixed in `ccf78b8`. Pipeline team's `POC_INTEGRATION.md` does not currently call this out — flag in next coordination round. Last-updated bumped. |
| `settings.json` *(new)* | Claude Code project settings — PreToolUse hook on `Bash` matcher, gated by `if: "Bash(git push *)"` for efficiency, calls the blocker script with 5s timeout. |
| `scripts/block-public-push.sh` *(new, 0755)* | Reads PreToolUse JSON envelope on stdin, extracts the `git push <target>` token, denies if `target` is `public` or matches the public-repo URL forms (HTTPS or SSH, with or without `.git` suffix). The `-dev` variant is correctly NOT matched. Emits `permissionDecision: "deny"` JSON envelope with the policy reason. Pipe-tested against 12 cases (block + allow + cd-prefixes + edge), all correct. `jq -e` schema validation passes. |

## Public-repo verification

Confirmed via `gh repo view`:

| Remote | URL | GitHub visibility |
|---|---|---|
| `origin` | `RouteResearch/Route-Playout-Econometrics_POC-dev` | **PRIVATE** |
| `public` | `RouteResearch/Route-Playout-Econometrics_POC` | **PUBLIC** |

So `git push public ...` does push to a genuinely public repo. The user's intent is to keep iterating on `origin` and treat the public repo as a frozen Adwanted reference — possibly indefinitely.

## Hook deployment status — IMPORTANT for next session

**The hook is committed and pushed but NOT YET ACTIVE in any session that started before `3e0562e` was created.**

Empirically confirmed: Claude Code's settings watcher does not pick up `settings.json` files that didn't exist at session start. Opening `/hooks` is a **read-only display dialog** — it does NOT trigger a config reload (verified via `/hooks` dismissed twice; trace sentinel inside the script never fired). There is no in-session reload mechanism.

**The hook will load automatically on the first new session that starts after `3e0562e`** (i.e. any session started from this point onward — the file exists before the watcher boots). To verify it's working, ask the assistant to run `git push public --dry-run` early in the next session — should report a `permissionDecision: deny` with the policy reason instead of contacting GitHub.

If you ever re-create the file mid-session in the future, the same limitation applies: restart is the only path.

## What was NOT done

- **Merge to `main`** — still pending the user's explicit "merge". `feature/duckdb-migration` is ready when you are.
- **Floor items `#2`/`#3`/`#4`/`#6`** — all still on the table. See active session prompt for status. With the tag-push policy now opt-in, post-merge cleanup commits land on `main` and stay on `origin` only.
- **Push docs commit to `zimacube`** — backup mirror, optional, can be done any time.

## Working notes worth carrying forward

- **Claude Code hook reload limitation**: newly-created `settings.json` files in dirs that didn't have one at session start require a full `/exit` + re-launch to take effect. Not a bug; just how the watcher initialises. `/hooks` is display-only.
- **Symlinked `.claude/`**: the hook setup goes through the symlink to the docs repo. Works fine for read; was undocumented whether the watcher follows symlinks but empirically the resolved settings.json file IS read at session start (the file existed at the start of any restarted session, so this isn't a confounder going forward).
- **Hook script is repo-root relative** (`.claude/scripts/block-public-push.sh`). If anyone ever runs Claude Code from a non-project-root cwd against this project, may need to reconsider — but the harness sets cwd to project root, so fine in practice.

## Pre-flight check at next session start

Same as `NEXT_SESSION_PROMPT_2026-05-03.md` (or whatever next-session prompt you point at). Headline checks:

```bash
cd /home/dev/projects/Route-Playout-Econometrics_POC
git log --oneline -1                  # confirm ccf78b8 is HEAD
git -C Claude log --oneline -1        # confirm 3e0562e is HEAD on docs
uv run pytest tests/api tests/db 2>&1 | tail -3       # 133/133 green
```

And the hook live-fire check (only meaningful in a fresh session):

> Ask assistant: "try `git push public --dry-run`". Should be denied by the hook before contacting GitHub.

## Next session

`Claude/Handover/NEXT_SESSION_PROMPT_2026-05-03.md` (rename to whatever date you actually open it). Same content as `NEXT_SESSION_PROMPT_2026-05-05.md` with the public-policy / hook context added.
