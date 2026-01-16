# Undervalued - UK Property Opportunity Finder

Automated property investment sourcing platform that identifies undervalued UK properties by cross-referencing HM Land Registry historical price data with active listings.

## Quick Start

```bash
# Start Docker services (PostgreSQL + Redis)
make docker

# Run database migrations
make migrate

# Start development servers
make dev
```

## Project Structure

```
undervalued/
├── packages/
│   ├── backend/          # Python FastAPI Backend
│   └── frontend/         # Next.js Frontend
├── infrastructure/       # Docker, Terraform, Scripts
├── docs/                # Documentation
└── .github/workflows/   # CI/CD
```

## Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL 16
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, React Query
- **Infrastructure**: Docker, Redis

## Documentation

- [Setup Guide](docs/SETUP.md) - Environment setup instructions
- [Database Schema](docs/DATABASE.md) - Database models and migrations
- [API Documentation](http://localhost:8000/docs) - OpenAPI/Swagger UI (when running)

## License

Proprietary - All Rights Reserved
