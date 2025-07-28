#!/usr/bin/env bash
set -euo pipefail

echo " Waiting for containers to be healthy…"
docker compose ps --services --filter "status=running" >/dev/null

# Wait up to 60 s for n8n
for i in {1..12}; do
  if curl -s http://localhost:5678/healthz | grep -q '"status":"ok"'; then
    echo "✅ n8n healthy"
    break
  fi
  sleep 5
done

echo " Checking DB row count…"
COUNT=$(docker compose exec -T postgres psql -U "$POSTG_USER" -tAc 'SELECT COUNT(*) FROM jobs_live;')
if [[ "$COUNT" == "1" ]]; then
  echo "✅ jobs_live count = 1"
else
  echo "❌ Expected 1 row, got $COUNT"
  exit 1
fi

echo " Smoke test passed"
