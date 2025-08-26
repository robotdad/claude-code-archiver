.PHONY: help install dev test check format lint type build clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync

dev: install ## Install dev dependencies
	uv sync --all-extras

test: ## Run tests with coverage
	uv run pytest tests/ -v --cov=src/claude_code_archiver --cov-report=term-missing

check: format lint type ## Run all checks (format, lint, type)

format: ## Format code with ruff
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

lint: ## Lint code with ruff
	uv run ruff check src/ tests/

type: ## Type check with pyright
	uv run pyright

build: ## Build distribution package
	uv build

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info .coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete