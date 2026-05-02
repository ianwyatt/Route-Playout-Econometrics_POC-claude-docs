#!/usr/bin/env bash
# ABOUTME: PreToolUse hook script — blocks `git push public ...` and equivalent
# ABOUTME: URL-form pushes per the public-repo policy in .claude/CLAUDE.md.

# Reads Claude Code's PreToolUse JSON envelope on stdin, inspects the
# Bash command, and if it would push to the `public` remote (by name or
# by URL), emits a permissionDecision="deny" JSON envelope. Otherwise
# stays silent and exits 0 (allow).
#
# This is a policy gate, not a security boundary — Claude can ask the
# user, get explicit permission naming `public`, and the user can
# approve the prompt. Pre-push git hook on the `public` remote remains
# the hard backstop for branch pushes.

set -uo pipefail

input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

[ -z "$cmd" ] && exit 0

# Extract the first `git push <target>` substring; <target> is the
# token after `push`. Tolerates `cd … && git push …` style prefixes
# because we look for the substring, not anchor at start.
target="$(printf '%s' "$cmd" \
  | grep -oE 'git[[:space:]]+push[[:space:]]+[^[:space:]]+' \
  | head -n1 \
  | awk '{print $NF}')"

[ -z "$target" ] && exit 0

block=false
case "$target" in
  public)
    block=true
    ;;
  *RouteResearch/Route-Playout-Econometrics_POC | \
  *RouteResearch/Route-Playout-Econometrics_POC.git)
    # Public-repo URL forms (HTTPS or SSH). The `-dev` suffix variant
    # is the private daily-driver and is NOT matched here.
    block=true
    ;;
esac

if $block; then
  jq -nc \
    --arg reason "Push to the public remote is policy-blocked. Per .claude/CLAUDE.md → \"Public-repo policy\", do NOT push (tags or branches) to public unless the user explicitly asks, naming the public remote. Ask for confirmation, then re-run." \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $reason}}'
fi

exit 0
