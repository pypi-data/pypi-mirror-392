install: ## installer les dépendances
	uv sync
.PHONY: install

build: ## construire le paquet
	uv build
.PHONY: build

publish:build ## publier le paquet
	uv publish
.PHONY: build

format: ## formater les sources
	uv run ruff format src/geler
.PHONY: format

check:  ## vérifier les sources
	uv run ruff check --fix
.PHONY: check

help: ## Show this help
	@echo "\nChoisissez une commande. Les choix sont:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""
.PHONY: help
