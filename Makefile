# Makefile helpers (docker compose v2)
.SILENT:
setup:  docker compose pull
start:  docker compose up -d && docker compose ps
stop:   docker compose down
logs:   docker compose logs --tail 50
smoke:  bash scripts/smoke.sh
sandbox: bash /home/tom/nl-autopilot/scripts/sandbox_apply.sh
clean:  docker compose down -v && docker system prune -f
