# API Documentation

## Overview

The Undervalued API provides endpoints for finding undervalued UK properties.

**Base URL:** `http://localhost:8000/api/v1`

## Authentication

Currently no authentication required (MVP). Admin endpoints will require bearer tokens in production.

---

## Endpoints

### Opportunities

#### `GET /api/v1/opportunities`

Find undervalued properties in a postcode district.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `postcode_district` | string | Yes | e.g., "SW15", "W14" |
| `min_discount_pct` | float | No | Minimum discount (0.1 = 10%) |
| `max_price` | float | No | Maximum asking price (GBP) |
| `property_types` | array | No | Filter by types |
| `sort_by` | string | No | Sorting: `undervalued_index_desc`, `price_asc` |
| `page` | int | No | Page number (default: 1) |
| `per_page` | int | No | Items per page (default: 20, max: 100) |

**Response:** `200 OK`
```json
{
  "items": [...],
  "total": 45,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

---

### Properties

#### `GET /api/v1/properties/{uprn}/analysis`

Get detailed analysis for a specific property.

**Path Parameters:**
- `uprn`: Unique Property Reference Number

**Response:** `200 OK` - Property details, metrics, transactions, comparables

**Error:** `404 Not Found` - Property not found

---

### System (Admin)

#### `POST /api/v1/system/ingest`

Trigger data ingestion pipeline.

**Request Body:**
```json
{
  "source": "all",
  "postcode_districts": ["SW15", "W14"],
  "force_refresh": false
}
```

**Response:** `202 Accepted`
```json
{
  "task_id": "abc123",
  "status": "queued",
  "estimated_completion": "2026-01-16T09:00:00Z"
}
```

#### `GET /api/v1/system/status`

Get system health status.

---

## Interactive Documentation

When running locally:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
