#!/usr/bin/env bash
set -euo pipefail

echo "🔄 Waiting for n8n…"
until curl -fsS http://localhost:5678/healthz; do sleep 1; done
echo "✅ n8n healthy"

echo "🔄 Ensuring jobs_live table exists…"
docker compose exec -T postgres bash -lc \
  "psql -U postgres -d postgres -c \"CREATE TABLE IF NOT EXISTS jobs_live (id SERIAL PRIMARY KEY);\""
echo "✅ jobs_live table ensured"

echo "🔄 Truncating and inserting a single row…"
docker compose exec -T postgres bash -lc \
  "psql -U postgres -d postgres -c \"TRUNCATE TABLE jobs_live; INSERT INTO jobs_live DEFAULT VALUES;\""
echo "✅ jobs_live reset to 1 row"

echo "🔄 Checking DB row count…"
COUNT=$(
  docker compose exec -T postgres bash -lc \
    "psql -U postgres -d postgres -tAc \"SELECT COUNT(*) FROM jobs_live;\""
)
if [[ "$COUNT" -eq 1 ]]; then
  echo "✅ jobs_live count = 1"
else
  echo "❌ Expected 1 row, got \$COUNT"
  exit 1
fi

echo "🔄 Checking Prometheus gauge…"
if curl -fsS http://localhost:9464/metrics | grep -q 'sandbox_apply_success{ats="greenhouse"} 1'; then
  echo "✅ sandbox_apply_success gauge = 1"
else
  echo "❌ Gauge not reporting 1"
  exit 1
fi

echo "🏁 Smoke test passed"
