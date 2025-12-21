SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON := .venv/bin/python
PIP := .venv/bin/python -m pip

.PHONY: help install fmt lint test dev dev-backend dev-frontend clean

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make <target>\n\nTargets:\n"} /^[a-zA-Z0-9_-]+:.*##/ { printf "  %-14s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## Install backend and frontend dependencies
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	cd frontend && npm install

fmt: ## Format Python and frontend code
	$(PYTHON) -m black backend tests scripts
	$(PYTHON) -m ruff format backend tests scripts
	cd frontend && npm run fmt

lint: ## Lint Python and frontend code
	$(PYTHON) -m ruff check backend tests scripts
	cd frontend && npm run lint

test: ## Run test suites (pytest; vitest if configured)
	@set -e; \
	$(PYTHON) -m pytest || { status=$$?; if [ $$status -eq 5 ]; then echo "pytest: no tests collected (ok for now)"; else exit $$status; fi; }; \
	if [ -x frontend/node_modules/.bin/vitest ]; then (cd frontend && npx vitest run); else echo "vitest: not configured yet"; fi

dev: ## Run backend and frontend dev servers
	@set -e; \
	trap 'kill 0' INT TERM; \
	trap 'kill 0' EXIT; \
	$(PYTHON) -m uvicorn backend.main:app --reload --port 8000 & \
	(cd frontend && npm run dev) & \
	wait

dev-backend: ## Run backend dev server
	$(PYTHON) -m uvicorn backend.main:app --reload --port 8000

dev-frontend: ## Run frontend dev server
	cd frontend && npm run dev

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage
	rm -rf frontend/dist
