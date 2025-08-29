#!/usr/bin/env bash
set -euo pipefail

echo "=== Thesis Smoke Test ==="

# Wait for decoder health
echo -n "Waiting for decoder health..."
for i in {1..30}; do
    if curl -sf http://localhost:8001/healthz >/dev/null 2>&1; then
        echo " OK"
        break
    fi
    echo -n "."
    sleep 1
done

# Test /selftest endpoint
echo -n "Testing /selftest endpoint..."
SELTTEST_RESPONSE=$(curl -fsS http://localhost:8001/selftest)
if echo "$SELTTEST_RESPONSE" | grep -q '"ok":true'; then
    if echo "$SELTTEST_RESPONSE" | grep -q '"windows":[1-9]'; then # Check for windows >= 1
        echo " OK"
    else
        echo " FAILED (windows not > 0)"
        echo "Response: $SELTTEST_RESPONSE"
        exit 1
    fi
else
    echo " FAILED (ok is not true)"
    echo "Response: $SELTTEST_RESPONSE"
    exit 1
fi

echo "=== Smoke test passed ==="
