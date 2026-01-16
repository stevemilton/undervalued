.PHONY: help dev test lint migrate docker docker-down clean

help:
	@echo "Available commands:"
	@echo "  make dev         - Start development servers"
	@echo "  make test        - Run all tests"
	@echo "  make lint        - Run linters"
	@echo "  make migrate     - Run database migrations"
	@echo "  make docker      - Start Docker services"
	@echo "  make docker-down - Stop Docker services"
	@echo "  make clean       - Clean build artifacts"

docker:
	docker-compose -f infrastructure/docker/docker-compose.yml up -d

docker-down:
	docker-compose -f infrastructure/docker/docker-compose.yml down

migrate:
	cd packages/backend && poetry run alembic upgrade head

dev:
	@echo "Starting Docker services..."
	docker-compose -f infrastructure/docker/docker-compose.yml up -d postgres redis
	@echo "Starting backend..."
	cd packages/backend && poetry run uvicorn src.main:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd packages/frontend && npm run dev &
	@echo "Development servers started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"

test:
	cd packages/backend && poetry run pytest --cov=src --cov-report=html
	cd packages/frontend && npm run test

lint:
	cd packages/backend && poetry run ruff check . && poetry run mypy src
	cd packages/frontend && npm run lint

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
