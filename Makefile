# Makefile helpers (docker compose v2)
.SILENT:
setup:  docker compose pull
start:
	@docker compose up -d
	@docker compose ps
stop:   docker compose down
logs:   docker compose logs --tail 50
smoke: ## Run smoke tests (stack must already be up: `make start`)
	@bash scripts/smoke.sh
	@curl -f http://localhost:${NGINX_PORT:-8080} || exit 1
sandbox: bash /home/tom/nl-autopilot/scripts/sandbox_apply.sh
clean:  docker compose down -v && docker system prune -f

pr-beta:      ## Open PR & ping Slack
	@bash scripts/open_beta_pr.sh

preflight:      ## Run β-0 preflight checks
	@bash scripts/preflight_check.sh

ENV_FILE ?= .env.thesis
COMPOSE   = docker compose -p nl-autopilot --env-file $(ENV_FILE) -f docker-compose.yml -f docker-compose.thesis.yml

thesis-start: ## Start the thesis stack
	$(COMPOSE) --profile thesis up -d

thesis-stop: ## Stop the thesis stack
	$(COMPOSE) --profile thesis down

thesis-logs: ## Tail logs for the thesis stack
	$(COMPOSE) --profile thesis logs -f --tail=200

thesis-ps: ## Show status of thesis services
	$(COMPOSE) --profile thesis ps

thesis-smoke: ## Run thesis smoke tests
	@bash scripts/thesis_smoke.sh
