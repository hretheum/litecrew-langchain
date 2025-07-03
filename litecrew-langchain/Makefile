# Makefile for LiteCrew-LangChain

.PHONY: help build up down test lint format clean install dev prod logs shell

# Default target
help:
	@echo "LiteCrew Development Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start development environment"
	@echo "  make down       - Stop all containers"
	@echo "  make test       - Run tests in container"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"
	@echo "  make clean      - Clean cache and temp files"
	@echo "  make shell      - Open shell in dev container"
	@echo "  make logs       - Show container logs"
	@echo "  make benchmark  - Run performance benchmarks"

# Install dependencies locally
install:
	pip install -e ".[dev]"
	pre-commit install

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Services running at:"
	@echo "  - API: http://localhost:8000"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Ollama: http://localhost:11434"

down:
	docker-compose down

# Development commands
dev: up
	docker-compose exec dev bash

shell:
	docker-compose exec dev bash

logs:
	docker-compose logs -f

# Testing commands
test:
	docker-compose run --rm test pytest -v

test-watch:
	docker-compose run --rm test pytest-watch

coverage:
	docker-compose run --rm test pytest --cov=litecrew --cov-report=html --cov-report=term

# Code quality
lint:
	docker-compose run --rm dev ruff check src/ tests/
	docker-compose run --rm dev mypy src/

format:
	docker-compose run --rm dev black src/ tests/
	docker-compose run --rm dev ruff check --fix src/ tests/

# Benchmarking
benchmark:
	docker-compose run --rm test python -m pytest benchmarks/ -v --benchmark-only

benchmark-compare:
	docker-compose run --rm test python benchmarks/compare_with_baseline.py

# Database commands
db-migrate:
	docker-compose exec dev alembic upgrade head

db-reset:
	docker-compose exec postgres psql -U litecrew -c "DROP DATABASE IF EXISTS litecrew_dev;"
	docker-compose exec postgres psql -U litecrew -c "CREATE DATABASE litecrew_dev;"
	$(MAKE) db-migrate

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

# Production
prod:
	docker build --target production -t litecrew:latest .
	docker run -p 8000:8000 litecrew:latest

# GitLab CI simulation
ci-test:
	docker build --target test -t litecrew:test .
	docker run --rm litecrew:test

# Quick start for new developers
quickstart: build up
	@echo "LiteCrew is ready! Run 'make dev' to start developing."