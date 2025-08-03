#!/usr/bin/env bash
set -euo pipefail
BRANCH="beta/infra-prep"
LABEL="beta"

# Create or update PR
gh pr view "$BRANCH" >/dev/null 2>&1 || \
  gh pr create --base master --head "$BRANCH" --fill --label "$LABEL"

# Slack ping
if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
  PR_URL=$(gh pr view --json url -q .url)
  curl -s -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"Phase β-0 PR opened: <$PR_URL|link> — reviews welcome!\"}" \
    "$SLACK_WEBHOOK_URL"
fi