# Database Schema Documentation

## Overview

The database uses PostgreSQL 16 with SQLAlchemy 2.0 async ORM. All models include timestamps and proper relationships.

## Entity Relationship Diagram

```mermaid
erDiagram
    PROPERTY ||--o{ HISTORICAL_TRANSACTION : has
    PROPERTY ||--o| ACTIVE_LISTING : has
    PROPERTY ||--o| VALUATION_METRICS : has

    PROPERTY {
        string uprn PK "Unique Property Reference Number"
        jsonb address_bs7666 "BS7666 address format"
        float floor_area_sqft "From EPC"
        enum property_type "Detached/Semi/Terraced/Flat"
        string epc_rating "A-G"
        uuid current_listing_id FK
    }

    HISTORICAL_TRANSACTION {
        uuid transaction_id PK
        string uprn FK
        decimal price_paid "GBP"
        date date_of_transfer
        enum transaction_category
    }

    ACTIVE_LISTING {
        uuid listing_id PK
        string external_url UK
        decimal asking_price "GBP"
        date listing_date
        string agent_name
        string source "rightmove/zoopla"
        jsonb raw_data
    }

    VALUATION_METRICS {
        uuid id PK
        string uprn FK UK
        float current_ppsf
        float market_ppsf_12m
        float undervalued_index
        float projected_yield
        int comparable_count
        enum priority "High/Medium/Low"
    }
```

## Tables

### properties
Primary property records anchored by UPRN.

| Column | Type | Description |
|--------|------|-------------|
| `uprn` | `VARCHAR(12)` PK | Unique Property Reference Number |
| `address_bs7666` | `JSONB` | Address with paon, saon, street, town, postcode |
| `floor_area_sqft` | `FLOAT` | Floor area from EPC register |
| `property_type` | `ENUM` | Detached, Semi-Detached, Terraced, Flat |
| `epc_rating` | `VARCHAR(1)` | A through G |
| `current_listing_id` | `UUID` FK | Active listing if on market |

### historical_transactions
Land Registry price paid data.

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | `UUID` PK | Auto-generated UUID |
| `uprn` | `VARCHAR(12)` FK | Link to property |
| `price_paid` | `DECIMAL(12,2)` | Transaction price in GBP |
| `date_of_transfer` | `DATE` | Sale completion date |
| `transaction_category` | `ENUM` | Standard or Additional |

### active_listings
Scraped listings from property portals.

| Column | Type | Description |
|--------|------|-------------|
| `listing_id` | `UUID` PK | Auto-generated UUID |
| `external_url` | `VARCHAR(500)` UK | Original listing URL |
| `asking_price` | `DECIMAL(12,2)` | Current asking price |
| `listing_date` | `DATE` | When listed |
| `source` | `VARCHAR(50)` | rightmove, zoopla |

### valuation_metrics
Pre-computed analysis results.

| Column | Type | Description |
|--------|------|-------------|
| `id` | `UUID` PK | Auto-generated UUID |
| `uprn` | `VARCHAR(12)` FK,UK | One per property |
| `current_ppsf` | `FLOAT` | Asking price / sqft |
| `market_ppsf_12m` | `FLOAT` | 12-month average PPSF |
| `undervalued_index` | `FLOAT` | Discount percentage |
| `priority` | `ENUM` | High (>15%), Medium (>5%), Low |

## Migrations

```bash
# Run migrations
cd packages/backend
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# View migration history
poetry run alembic history
```
