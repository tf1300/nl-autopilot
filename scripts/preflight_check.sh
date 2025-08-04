#!/bin/bash

set -euo pipefail

echo "--- Running preflight checks ---"

# Check 1: Current branch
echo -n "1. Checking current branch... "
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "beta/infra-prep" ]]; then
  echo "FAIL: Not on branch beta/infra-prep (current: $current_branch)"
  exit 1
fi
echo "OK"

# Check 2: Tag v0.2.0-beta.0 on master
echo -n "2. Checking for tag v0.2.0-beta.0 on remote 'origin'... "
if ! git ls-remote --tags origin refs/tags/v0.2.0-beta.0 | grep -q v0.2.0-beta.0; then
  echo "FAIL: Tag v0.2.0-beta.0 not found on remote 'origin'."
  exit 1
fi
echo "OK"

# Check 3: make start and make smoke
echo "3. Running 'make start' and 'make smoke' (timeout 25s)..."
if ! timeout 25s make start; then
    echo "FAIL: 'make start' failed or timed out."
    exit 1
fi

if ! timeout 25s make smoke; then
    echo "FAIL: 'make smoke' failed or timed out."
    exit 1
fi
echo "   'make start' and 'make smoke' OK"


# Check 4: NGINX is running
echo -n "4. Checking NGINX container... "
if ! curl -sf "http://localhost:${NGINX_PORT:-8080}"; then
  echo "FAIL: NGINX is not responding on port ${NGINX_PORT:-8080}."
  exit 1
fi
echo "OK"

# Check 5: Prometheus metric
echo -n "5. Checking Prometheus metric 'sandbox_apply_success'... "
if ! curl -s localhost:9464/metrics | grep -q sandbox_apply_success; then
  echo "FAIL: Prometheus metric 'sandbox_apply_success' not found."
  exit 1
fi
echo "OK"

# Check 6: Prometheus logs
echo -n "6. Checking Prometheus logs for alert rule loading... "
if ! docker-compose logs prometheus 2>&1 | grep -q "Loading alert rule files from /etc/prometheus/rules.d"; then
    echo "FAIL: Prometheus logs do not confirm alert rule loading."
    exit 1
fi
echo "OK"

# Check 7: Pre-commit hooks
echo "7. Running pre-commit hooks..."
if ! pre-commit run --all-files; then
  echo "FAIL: pre-commit checks failed."
  exit 1
fi
echo "   pre-commit OK"

# Check 8: SOPS decryption
echo -n "8. Checking SOPS decryption... "
if ! sops -d secrets/.gitkeep > /dev/null 2>&1; then
  echo "FAIL: SOPS decryption failed for 'secrets/.gitkeep'."
  exit 1
fi
echo "OK"


echo "--- Preflight checks passed successfully! ---"
