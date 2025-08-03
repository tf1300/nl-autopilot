# Makefile helpers (docker compose v2)
.SILENT:
setup:  docker compose pull
start:  docker compose up -d && docker compose ps
stop:   docker compose down
logs:   docker compose logs --tail 50
smoke: ## Run smoke tests (stack must already be up: `make start`)
	@bash scripts/smoke.sh
	@curl -f http://localhost:${NGINX_PORT:-8080} || exit 1
sandbox: bash /home/tom/nl-autopilot/scripts/sandbox_apply.sh
clean:  docker compose down -v && docker system prune -f

pr-beta:      ## Open PR & ping Slack
	@bash scripts/open_beta_pr.sh