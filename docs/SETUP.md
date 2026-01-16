# Environment Setup Guide

## Prerequisites

- **Python 3.11+** with Poetry installed
- **Node.js 20+** with npm
- **Docker & Docker Compose**

## Quick Start

```bash
# 1. Clone and navigate to project
cd undervalued

# 2. Copy environment file
cp .env.example .env

# 3. Start Docker services
make docker

# 4. Install backend dependencies
cd packages/backend
poetry install

# 5. Run database migrations
poetry run alembic upgrade head

# 6. Start backend
poetry run uvicorn src.main:app --reload --port 8000

# 7. In new terminal, install frontend dependencies
cd packages/frontend
npm install

# 8. Start frontend
npm run dev
```

## Accessing the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

## Docker Services

```bash
# Start PostgreSQL and Redis
make docker

# Stop services
make docker-down

# View logs
docker-compose -f infrastructure/docker/docker-compose.yml logs -f
```

## Environment Variables

Key variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `EPC_API_KEY` | EPC Register API key | (required for EPC lookup) |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | `http://localhost:8000` |

## Common Commands

```bash
make dev        # Start all development servers
make test       # Run all tests
make lint       # Run linters
make migrate    # Run database migrations
```
