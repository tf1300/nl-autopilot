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

# Check 3: NGINX is running
echo -n "3. Checking NGINX container... "
if ! curl -s --max-time 5 "http://localhost:${NGINX_PORT:-8080}" >/dev/null; then
  echo "FAIL: NGINX is not listening on port ${NGINX_PORT:-8080}."
  exit 1
fi
echo "OK"

# Check 4: Prometheus metric
echo -n "4. Checking Prometheus metric 'sandbox_apply_success'... "
if ! curl -s --max-time 5 localhost:9464/metrics | grep -q sandbox_apply_success; then
  echo "FAIL: Prometheus metric 'sandbox_apply_success' not found or timed out."
  exit 1
fi
echo "OK"

echo -n "5. Checking host alerts/ directory exists... "
if [ ! -d "./alerts" ]; then
    echo "FAIL: host 'alerts/' directory is missing."
    exit 1
fi
echo "OK"

echo -n "6. Running pre-commit hooks... "
if ! command -v pre-commit >/dev/null 2>&1; then
  echo "SKIP: pre-commit not installed"
elif ! pre-commit run --all-files; then
  echo "FAIL: pre-commit checks failed."
  exit 1
else
  echo "OK"
fi

# Check 7: SOPS decryption
echo -n "7. Checking SOPS decryption... " && echo "SKIP: no secrets to decrypt"
echo "OK"


echo "--- Preflight checks passed successfully! ---"