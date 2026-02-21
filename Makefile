.PHONY: help setup backend-dev ui-dev docker-up docker-down docker-dev \
       infra-init infra-plan infra-apply infra-destroy \
       bootstrap policy-test test lint clean

SHELL := /bin/bash
ENV ?= dev

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Setup
# =============================================================================

setup: ## Install all dependencies
	cd backend && uv sync
	cd ui && npm install
	cd policy-agent && go mod download
	pre-commit install

# =============================================================================
# Local Development
# =============================================================================

backend-dev: ## Run FastAPI backend with hot-reload
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

ui-dev: ## Run Next.js UI with hot-reload
	cd ui && npm run dev

docker-up: ## Start all services via Docker Compose
	docker compose up -d

docker-down: ## Stop all services
	docker compose down

docker-dev: ## Start services with hot-reload overrides
	docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up -d

docker-logs: ## Tail logs from all services
	docker compose logs -f

# =============================================================================
# Infrastructure
# =============================================================================

infra-init: ## Initialize Terraform
	cd infrastructure && terraform init

infra-plan: ## Run Terraform plan
	cd infrastructure && terraform plan -var-file=envs/$(ENV).tfvars

infra-apply: ## Apply Terraform changes
	cd infrastructure && terraform apply -var-file=envs/$(ENV).tfvars

infra-destroy: ## Destroy Terraform resources
	cd infrastructure && terraform destroy -var-file=envs/$(ENV).tfvars

# =============================================================================
# Platform Bootstrap
# =============================================================================

bootstrap: ## Bootstrap platform on EKS (Argo CD + ESO)
	./scripts/bootstrap.sh

create-secrets: ## Push config to AWS Secrets Manager
	./scripts/create-config-secrets.sh

get-urls: ## Print platform service URLs
	./scripts/get-urls.sh

# =============================================================================
# Policy Agent
# =============================================================================

policy-build: ## Build Go policy agent
	cd policy-agent && go build -o bin/policy-agent ./cmd/policy-agent

policy-test: ## Run policy agent tests
	cd policy-agent && go test ./...

policy-validate: ## Validate example configs against policies
	cd policy-agent && ./bin/policy-agent validate --policies-dir ../policies --domain kubernetes --file ../examples/deployment.yaml

# =============================================================================
# Testing & Linting
# =============================================================================

test: ## Run all tests
	cd backend && uv run pytest tests/
	cd ui && npm test
	cd policy-agent && go test ./...

lint: ## Run all linters
	cd backend && uv run ruff check .
	cd ui && npm run lint
	cd policy-agent && go vet ./...
	cd infrastructure && terraform fmt -check -recursive

# =============================================================================
# Cleanup
# =============================================================================

clean: ## Clean build artifacts
	rm -rf backend/.ruff_cache backend/__pycache__
	rm -rf ui/.next ui/node_modules
	rm -rf policy-agent/bin
	rm -rf infrastructure/.terraform
