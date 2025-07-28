# Makefile – Alpha-Skeleton helpers
.SILENT:

setup:          ## Pull latest images
docker compose pull

start:          ## Up stack & show ps
docker compose up -d
docker compose ps

stop:           ## Down stack
docker compose down

logs:           ## Tail logs
docker compose logs --tail 50

smoke:          ## Run automated smoke test
bash scripts/smoke.sh

clean:          ## Remove volumes & prune
docker compose down -v
docker system prune -f
