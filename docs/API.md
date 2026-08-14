# API Guide

Interactive OpenAPI documentation is available at `http://localhost:8000/docs` after startup.

## Classify one ticket

```bash
curl -X POST http://localhost:8000/api/classify \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "Remote office cannot resolve internal DNS",
    "description": "An entire office cannot resolve internal services and no workaround exists.",
    "requester": "Service Desk",
    "affected_users": 140,
    "business_service": "Corporate Network"
  }'
```

The response includes category and priority alternatives, confidence, assignment group, SLA target, influential terms, recommended actions, and the human-review decision.

## Other endpoints

| Method | Route | Purpose |
|---|---|---|
| `POST` | `/api/classify/batch` | Classify up to 25 validated tickets |
| `GET` | `/api/queue` | Read recent decision records |
| `POST` | `/api/feedback` | Record an accepted or corrected decision |
| `GET` | `/api/metrics` | Model evaluation and operating counters |
| `GET` | `/api/model-card` | Machine-readable use and risk boundaries |
| `GET` | `/health` | Service and model readiness |
