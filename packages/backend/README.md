# Undervalued Backend

Python FastAPI backend for the UK Property Opportunity Finder.

## Setup

```bash
# Install dependencies
poetry install

# Run migrations
poetry run alembic upgrade head

# Start development server
poetry run uvicorn src.main:app --reload --port 8000
```

## API Documentation

When running, visit http://localhost:8000/docs for Swagger UI.

## Testing

```bash
poetry run pytest --cov=src
```
