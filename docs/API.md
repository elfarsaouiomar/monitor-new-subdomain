# Subdomain Monitor API Documentation

Complete API reference for the Subdomain Monitoring System.

---

## 📋 Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
  - [Health & Status](#health--status)
  - [Domain Management](#domain-management)
  - [Monitoring Operations](#monitoring-operations)
  - [Scheduler Management](#scheduler-management)

---

## Base URL

```
http://localhost:8000
```

All API endpoints are prefixed with `/api/v1` unless otherwise specified.

**Interactive Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Authentication

Currently, the API does not require authentication. For production deployments, consider adding:
- API Keys
- JWT tokens
- OAuth2

---

## Response Format

### Success Response
```json
{
  "data": {},
  "message": "Success"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

---

## Error Handling

| Status Code | Description |
|-------------|-------------|
| `200` | Success |
| `201` | Created |
| `204` | No Content (successful deletion) |
| `400` | Bad Request |
| `404` | Not Found |
| `409` | Conflict (duplicate resource) |
| `422` | Validation Error |
| `500` | Internal Server Error |

### Example Error Response
```json
{
  "detail": "Domain not found"
}
```

---

## Rate Limiting

**Current Status:** No rate limiting implemented.

**Recommendations for Production:**
- Implement rate limiting middleware
- Suggested: 100 requests/minute per IP
- Use `slowapi` or `fastapi-limiter`

---

# Endpoints

## Health & Status

### Get Root Information
```http
GET /
```

**Description:** Get API information and status.

**Response:**
```json
{
  "name": "Subdomain Monitor",
  "version": "2.0.0",
  "status": "running",
  "scheduler_enabled": true,
  "scheduler_running": true
}
```

**Example:**
```bash
curl http://localhost:8000/
```

---

### Health Check
```http
GET /health
```

**Description:** Check API and database health.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "scheduler_enabled": true,
  "scheduler_running": true
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

## Domain Management

### List All Domains
```http
GET /api/v1/domains
```

**Description:** Get a list of all monitored domains.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | integer | No | 0 | Number of records to skip |
| `limit` | integer | No | 100 | Maximum records to return (1-1000) |

**Response:**
```json
{
  "domains": [
    "example.com",
    "test.com",
    "demo.org"
  ],
  "total": 3
}
```

**Examples:**
```bash
# Get all domains
curl http://localhost:8000/api/v1/domains

# With pagination
curl "http://localhost:8000/api/v1/domains?skip=0&limit=50"
```

---

### Add Domain
```http
POST /api/v1/domains
```

**Description:** Add a new domain to monitor.

**Request Body:**
```json
{
  "domain": "example.com",
  "notify_slack": false,
  "notify_telegram": false
}
```

**Request Body Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | Yes | Domain name to monitor (e.g., example.com) |
| `notify_slack` | boolean | No | Enable Slack notifications (default: false) |
| `notify_telegram` | boolean | No | Enable Telegram notifications (default: false) |

**Response (201 Created):**
```json
{
  "message": "Domain added successfully",
  "domain": "example.com",
  "subdomain_count": 45
}
```

**Errors:**
- `409 Conflict` - Domain already exists
- `422 Validation Error` - Invalid domain format
- `500 Internal Server Error` - Failed to add domain

**Examples:**
```bash
# Add domain without notifications
curl -X POST http://localhost:8000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Add domain with Slack notifications
curl -X POST http://localhost:8000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "notify_slack": true,
    "notify_telegram": false
  }'
```

---

### Get Subdomains for Domain
```http
GET /api/v1/domains/{domain}/subdomains
```

**Description:** Get all discovered subdomains for a specific domain.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | string | Yes | Domain name (e.g., example.com) |

**Response:**
```json
{
  "domain": "example.com",
  "subdomains": [
    "www.example.com",
    "mail.example.com",
    "api.example.com",
    "dev.example.com"
  ],
  "total": 4
}
```

**Errors:**
- `404 Not Found` - Domain not found in database

**Example:**
```bash
curl http://localhost:8000/api/v1/domains/example.com/subdomains
```

---

### Delete Domain
```http
DELETE /api/v1/domains/{domain}
```

**Description:** Remove a domain from monitoring.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | string | Yes | Domain name to delete |

**Response (204 No Content):**
```
(Empty response body)
```

**Errors:**
- `404 Not Found` - Domain not found in database

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/domains/example.com
```

---

### Check Domain for New Subdomains
```http
POST /api/v1/domains/{domain}/check
```

**Description:** Manually trigger a monitoring check for a specific domain.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | string | Yes | Domain name to check |

**Response:**
```json
{
  "message": "Monitoring check completed",
  "domain": "example.com",
  "new_subdomains_found": 3
}
```

**Errors:**
- `404 Not Found` - Domain not found in database

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/domains/example.com/check
```

---

## Monitoring Operations

### Monitor All Domains
```http
POST /api/v1/monitoring/check-all
```

**Description:** Manually trigger monitoring for all domains in the database.

**Response:**
```json
{
  "domains_monitored": 15,
  "new_subdomains_found": 8,
  "errors": 0,
  "timestamp": "2026-01-02T14:23:45.123456"
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `domains_monitored` | integer | Number of domains checked |
| `new_subdomains_found` | integer | Total new subdomains discovered |
| `errors` | integer | Number of errors during monitoring |
| `timestamp` | datetime | When monitoring completed |

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/monitoring/check-all
```

**Note:** This endpoint can take several minutes if you have many domains.

---

### Get Monitoring Statistics
```http
GET /api/v1/monitoring/stats
```

**Description:** Get overall monitoring statistics.

**Response:**
```json
{
  "total_domains": 15,
  "total_subdomains": 1247,
  "last_check": "2026-01-02T14:00:00",
  "new_subdomains_found": 8
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `total_domains` | integer | Total domains being monitored |
| `total_subdomains` | integer | Total subdomains discovered across all domains |
| `last_check` | datetime | Last monitoring check timestamp |
| `new_subdomains_found` | integer | New subdomains from last check |

**Example:**
```bash
curl http://localhost:8000/api/v1/monitoring/stats
```

---

## Scheduler Management

### Get Scheduler Status
```http
GET /api/v1/scheduler/status
```

**Description:** Get current scheduler status and configuration.

**Response (Enabled):**
```json
{
  "enabled": true,
  "running": true,
  "interval_minutes": 60,
  "timezone": "UTC",
  "next_run": "2026-01-02T15:00:00",
  "current_time": "2026-01-02T14:23:45"
}
```

**Response (Disabled):**
```json
{
  "enabled": false,
  "message": "Scheduler is disabled in configuration"
}
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Whether scheduler is enabled in config |
| `running` | boolean | Whether scheduler is currently running |
| `interval_minutes` | integer | Monitoring interval in minutes |
| `timezone` | string | Scheduler timezone |
| `next_run` | datetime | Next scheduled monitoring time |
| `current_time` | datetime | Current server time |

**Example:**
```bash
curl http://localhost:8000/api/v1/scheduler/status
```

---

### List Scheduled Jobs
```http
GET /api/v1/scheduler/jobs
```

**Description:** Get all scheduled jobs and their details.

**Response:**
```json
[
  {
    "id": "monitoring_job",
    "name": "Subdomain Monitoring",
    "next_run_time": "2026-01-02T15:00:00",
    "trigger": "interval[0:01:00:00]"
  }
]
```

**Response Schema:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique job identifier |
| `name` | string | Human-readable job name |
| `next_run_time` | datetime | When job will run next |
| `trigger` | string | Job trigger configuration |

**Errors:**
- `400 Bad Request` - Scheduler is not running

**Example:**
```bash
curl http://localhost:8000/api/v1/scheduler/jobs
```

---

### Trigger Monitoring Now
```http
POST /api/v1/scheduler/trigger
```

**Description:** Manually trigger the scheduled monitoring job immediately.

**Response:**
```json
{
  "message": "Monitoring job triggered successfully",
  "next_run": "2026-01-02T15:00:00"
}
```

**Errors:**
- `400 Bad Request` - Scheduler is not running

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/scheduler/trigger
```

**Note:** Use `/api/v1/monitoring/check-all` if scheduler is disabled.

---

### Pause Scheduler
```http
POST /api/v1/scheduler/pause
```

**Description:** Pause the scheduler (stops automatic monitoring).

**Response:**
```json
{
  "message": "Scheduler paused"
}
```

**Errors:**
- `400 Bad Request` - Scheduler is not running

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/scheduler/pause
```

---

### Resume Scheduler
```http
POST /api/v1/scheduler/resume
```

**Description:** Resume the scheduler after pausing.

**Response:**
```json
{
  "message": "Scheduler resumed",
  "next_run": "2026-01-02T15:00:00"
}
```

**Errors:**
- `400 Bad Request` - Scheduler is disabled in configuration

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/scheduler/resume
```

---

## Complete Workflow Examples

### Example 1: Add Domain and Monitor

```bash
# 1. Add a new domain
curl -X POST http://localhost:8000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "notify_slack": true}'

# Response: {"message": "Domain added successfully", "domain": "example.com", "subdomain_count": 45}

# 2. View discovered subdomains
curl http://localhost:8000/api/v1/domains/example.com/subdomains

# 3. Manually check for new subdomains
curl -X POST http://localhost:8000/api/v1/domains/example.com/check

# Response: {"message": "Monitoring check completed", "domain": "example.com", "new_subdomains_found": 2}
```

---

### Example 2: Bulk Import and Monitor

```bash
# 1. Add multiple domains
for domain in example.com test.com demo.org; do
  curl -X POST http://localhost:8000/api/v1/domains \
    -H "Content-Type: application/json" \
    -d "{\"domain\": \"$domain\"}"
done

# 2. Monitor all domains at once
curl -X POST http://localhost:8000/api/v1/monitoring/check-all

# Response: {"domains_monitored": 3, "new_subdomains_found": 5, "errors": 0}

# 3. Get statistics
curl http://localhost:8000/api/v1/monitoring/stats
```

---

### Example 3: Scheduler Management

```bash
# 1. Check if scheduler is enabled
curl http://localhost:8000/api/v1/scheduler/status

# 2. Trigger immediate monitoring
curl -X POST http://localhost:8000/api/v1/scheduler/trigger

# 3. Pause scheduler temporarily
curl -X POST http://localhost:8000/api/v1/scheduler/pause

# 4. Resume scheduler
curl -X POST http://localhost:8000/api/v1/scheduler/resume
```

---

## Configuration

### Environment Variables

Set these in your `.env` file:

```env
# Database
DB_HOST=localhost
DB_PORT=27017
DB_NAME=subdomain_monitor

# Notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Monitoring
MONITOR_INTERVAL_MINUTES=60
MAX_WORKERS=10
DNS_TIMEOUT=5

# Scheduler
ENABLE_SCHEDULER=true
SCHEDULER_TIMEZONE=UTC

# API
DEBUG=false
CORS_ORIGINS=["*"]
```

---

## Testing the API

### Using cURL

```bash
# Test connection
curl http://localhost:8000/health

# Add domain
curl -X POST http://localhost:8000/api/v1/domains \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# List domains
curl http://localhost:8000/api/v1/domains
```

### Using HTTPie

```bash
# Install HTTPie
pip install httpie

# Add domain
http POST http://localhost:8000/api/v1/domains domain=example.com

# Get subdomains
http GET http://localhost:8000/api/v1/domains/example.com/subdomains
```

### Using Python Requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Add domain
response = requests.post(
    f"{BASE_URL}/domains",
    json={
        "domain": "example.com",
        "notify_slack": True
    }
)
print(response.json())

# Get subdomains
response = requests.get(f"{BASE_URL}/domains/example.com/subdomains")
print(response.json())

# Monitor all domains
response = requests.post(f"{BASE_URL}/monitoring/check-all")
print(response.json())
```

---

## Production Considerations

### Security
- [ ] Add API authentication (API keys or JWT)
- [ ] Implement rate limiting
- [ ] Use HTTPS (TLS/SSL)
- [ ] Validate and sanitize all inputs
- [ ] Set CORS origins to specific domains

### Performance
- [ ] Use connection pooling for MongoDB
- [ ] Implement caching for frequent queries
- [ ] Use async operations throughout
- [ ] Monitor API response times

### Monitoring
- [ ] Set up API monitoring (Prometheus, Grafana)
- [ ] Log all API requests
- [ ] Track error rates
- [ ] Monitor database performance

### Deployment
- [ ] Use gunicorn/uvicorn workers
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure proper logging
- [ ] Use environment-specific configs

---

## Support

For issues or questions:
- GitHub Issues: [Your Repository]
- Email: [Your Email]
- Documentation: `http://localhost:8000/docs`

---

## Changelog

### Version 2.0.0
- Added automated scheduler
- Improved error handling
- Added comprehensive API documentation
- Async operations throughout
- Better notification system

---

**Last Updated:** January 2, 2026