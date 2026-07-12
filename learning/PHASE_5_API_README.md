# Phase 5: Financial Intelligence Agent API

Production-ready REST API for the Text2SQL + Vector RAG pipeline.

## Quick Start

### 1. Start the API Server

```bash
uv run python phase5_api.py
```

Or with uvicorn directly:

```bash
uv run uvicorn phase5_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. Interactive API Docs

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test the API

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Query the Agent
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main risks for technology companies?",
    "top_k": 3
  }'
```

#### Vector Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue growth",
    "top_k": 3,
    "section_filter": "Results of Operations"
  }'
```

#### Get Company Metrics
```bash
curl http://localhost:8000/metrics/AAPL
```

#### List Companies
```bash
curl http://localhost:8000/companies
```

## API Endpoints

### POST /query
**Answer a financial question using RAG**

Request:
```json
{
  "question": "What drove revenue growth for tech companies?",
  "top_k": 3
}
```

Response:
```json
{
  "question": "What drove revenue growth for tech companies?",
  "answer": "Based on the SEC filings...",
  "sources": [
    {
      "ticker": "MSFT",
      "year": "2024",
      "section": "Results of Operations",
      "text": "Revenue grew primarily due to...",
      "similarity_score": 0.87
    }
  ],
  "model": "gpt-4-turbo"
}
```

### POST /search
**Vector semantic search for MD&A chunks**

Request:
```json
{
  "query": "liquidity position",
  "top_k": 3,
  "section_filter": "Liquidity & Capital Resources"
}
```

Response:
```json
[
  {
    "ticker": "AAPL",
    "year": "2024",
    "section": "Liquidity & Capital Resources",
    "text": "The company maintains strong liquidity...",
    "similarity_score": 0.92
  }
]
```

### GET /metrics/{ticker}
**Get all financial metrics for a company**

Example: `GET /metrics/MSFT`

Response:
```json
{
  "ticker": "MSFT",
  "metrics": [
    {
      "ticker": "MSFT",
      "concept": "Revenues",
      "period_end": "2024-06-30",
      "form": "10-Q",
      "value": 245000000000
    }
  ]
}
```

### GET /companies
**List all companies in the database**

Response:
```json
{
  "companies": ["AAPL", "AMZN", "DASH", "GOOG", "META", ...],
  "count": 10
}
```

### GET /health
**Check API health status**

Response:
```json
{
  "status": "ok",
  "metrics_loaded": 180,
  "chunks_loaded": 850
}
```

## Architecture

```
Client Request
    ↓
FastAPI Server
    ↓
┌───────────────────────────────┐
│  Phase 5: API Layer           │
│  - Request validation         │
│  - Response formatting        │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  Phase 4: Vector Search       │
│  - Query embedding            │
│  - Cosine similarity          │
│  - Top-k retrieval            │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  Phase 3/4: RAG Agent         │
│  - Context building           │
│  - GPT-4 response generation  │
│  - Citation formatting        │
└───────────────────────────────┘
    ↓
┌───────────────────────────────┐
│  Phase 2: Data Layer          │
│  - PostgreSQL metrics         │
│  - MD&A chunks                │
│  - Embeddings                 │
└───────────────────────────────┘
    ↓
Response to Client
```

## Deployment Options

### Local Development
```bash
uv run uvicorn phase5_api:app --reload
```

### Production with Gunicorn
```bash
uv run gunicorn -w 4 -k uvicorn.workers.UvicornWorker phase5_api:app
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install uv && uv sync
CMD ["uv", "run", "uvicorn", "phase5_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Platforms
- **Heroku**: `Procfile` with gunicorn
- **AWS Lambda**: Use with API Gateway
- **Google Cloud Run**: Container deployment
- **Azure App Service**: Python runtime

## Performance Metrics

| Operation | Time | Cost |
|-----------|------|------|
| Query embedding | ~100ms | $0.00002 |
| Vector search (850 chunks) | ~50ms | Free |
| GPT-4 response | ~1-2s | $0.01-0.05 |
| Total query | ~1.2-2.2s | $0.01-0.05 |

## Complete Pipeline

```
✅ Phase 1: SEC API extraction (XBRL endpoints)
✅ Phase 2A: Load metrics → PostgreSQL
✅ Phase 2B: Extract & categorize MD&A
✅ Phase 3: Keyword-based RAG
✅ Phase 4: Vector-based Semantic RAG
✅ Phase 5: Production REST API ← YOU ARE HERE
```

## Next Steps

- Deploy to cloud platform
- Add authentication (JWT tokens)
- Add rate limiting
- Add caching layer (Redis)
- Add monitoring & logging
- Scale embeddings storage (pgvector)

## Support

For issues or questions, check:
- `/health` endpoint for status
- API docs at `/docs`
- Logs in console output
