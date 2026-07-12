"""
Phase 5: Financial Intelligence Agent API

Production-ready REST API for the Text2SQL + RAG pipeline.

Endpoints:
- POST /query: Ask a financial question
- GET /health: Check API status
- POST /search: Vector semantic search
- GET /metrics/{ticker}: Get company metrics
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import psycopg2
import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Intelligence Agent API",
    description="Vector-based RAG for SEC filing analysis",
    version="1.0.0"
)

# Initialize clients
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

client = OpenAI(api_key=api_key)

# Load data on startup
@app.on_event("startup")
async def load_data():
    """Load data from PostgreSQL on startup."""
    global metrics_data, chunks_data

    try:
        conn = psycopg2.connect(
            host='localhost', port=5432, database='financial_data',
            user='postgres', password='postgres'
        )
        cursor = conn.cursor()

        # Load metrics
        cursor.execute('SELECT ticker, concept, period_end, form, value FROM sec_filings.financial_metrics')
        metrics_data = [dict(zip(['ticker','concept','period_end','form','value'], row)) for row in cursor.fetchall()]

        # Load chunks
        cursor.execute('SELECT ticker, year, section, text, text_length, chunk_id FROM sec_filings.filing_text_chunks ORDER BY ticker, year DESC')
        chunks_data = [dict(zip(['ticker','year','section','text','text_length','chunk_id'], row)) for row in cursor.fetchall()]

        conn.close()

        logger.info(f"✅ Loaded {len(metrics_data)} metrics, {len(chunks_data)} chunks")

        # Generate embeddings
        logger.info("🔄 Generating embeddings...")
        embedded_count = 0
        for i, chunk in enumerate(chunks_data, 1):
            if i % 20 == 0:
                logger.info(f"   [{i}/{len(chunks_data)}] Embedding...")

            try:
                response = client.embeddings.create(
                    input=chunk['text'],
                    model="text-embedding-3-small"
                )
                chunk['embedding'] = response.data[0].embedding
                embedded_count += 1
            except Exception as e:
                logger.warning(f"Failed to embed chunk {i}: {e}")

        logger.info(f"✅ Generated {embedded_count} embeddings")

    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict]
    model: str = "gpt-4-turbo"

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    section_filter: Optional[str] = None

class SearchResult(BaseModel):
    ticker: str
    year: str
    section: str
    text: str
    similarity_score: float

class MetricsResponse(BaseModel):
    ticker: str
    metrics: List[Dict]

# Helper functions
def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity."""
    a, b = np.array(vec1), np.array(vec2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def vector_search(query: str, top_k: int = 3, section_filter: Optional[str] = None) -> List[Dict]:
    """Semantic search using embeddings."""
    try:
        response = client.embeddings.create(input=query, model="text-embedding-3-small")
        query_embedding = response.data[0].embedding
    except:
        return []

    similarities = []
    for chunk in chunks_data:
        if section_filter and chunk['section'] != section_filter:
            continue
        if 'embedding' not in chunk:
            continue

        similarity = cosine_similarity(query_embedding, chunk['embedding'])
        similarities.append((similarity, chunk))

    similarities.sort(reverse=True, key=lambda x: x[0])

    return [
        {
            'ticker': c['ticker'],
            'year': c['year'],
            'section': c['section'],
            'text': c['text'][:500],
            'similarity_score': float(sim)
        }
        for sim, c in similarities[:top_k]
    ]

# Endpoints
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "metrics_loaded": len(metrics_data) if 'metrics_data' in globals() else 0,
        "chunks_loaded": len(chunks_data) if 'chunks_data' in globals() else 0
    }

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Query the financial intelligence agent."""
    if 'chunks_data' not in globals():
        raise HTTPException(status_code=503, detail="Data not loaded yet")

    # Vector search
    retrieved_chunks = vector_search(request.question, top_k=request.top_k)

    if not retrieved_chunks:
        return QueryResponse(
            question=request.question,
            answer="No relevant financial data found for this query.",
            sources=[]
        )

    # Build context
    context = "\n".join([
        f"[{c['ticker']} {c['year']} - {c['section']} | Similarity: {c['similarity_score']:.2f}]\n{c['text']}"
        for c in retrieved_chunks
    ])

    # Add metrics if ticker mentioned
    words = request.question.upper().split()
    tickers = [w for w in words if w in set(m['ticker'] for m in metrics_data)]

    for ticker in tickers[:2]:
        ticker_metrics = [m for m in metrics_data if m['ticker'] == ticker]
        if ticker_metrics:
            context += f"\n\n{ticker} Financial Data:\n"
            for m in ticker_metrics[-5:]:
                val = m['value'] / 1e9 if m['value'] > 1e9 else m['value'] / 1e6
                unit = 'B' if m['value'] > 1e9 else 'M'
                context += f"  {m['period_end']} ({m['form']}): ${val:.2f}{unit}\n"

    # Get GPT response
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst. Answer using the provided context. Be specific and cite sources."
                },
                {
                    "role": "user",
                    "content": f"Question: {request.question}\n\nContext:\n{context}\n\nProvide a detailed answer."
                }
            ]
        )

        answer = response.choices[0].message.content

        return QueryResponse(
            question=request.question,
            answer=answer,
            sources=retrieved_chunks
        )

    except Exception as e:
        logger.error(f"Error getting response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_documents(request: SearchRequest) -> List[SearchResult]:
    """Vector semantic search for MD&A chunks."""
    if 'chunks_data' not in globals():
        raise HTTPException(status_code=503, detail="Data not loaded yet")

    results = vector_search(request.query, request.top_k, request.section_filter)
    return [SearchResult(**r) for r in results]

@app.get("/metrics/{ticker}")
async def get_ticker_metrics(ticker: str) -> MetricsResponse:
    """Get all metrics for a company."""
    if 'metrics_data' not in globals():
        raise HTTPException(status_code=503, detail="Data not loaded yet")

    ticker = ticker.upper()
    ticker_metrics = [m for m in metrics_data if m['ticker'] == ticker]

    if not ticker_metrics:
        raise HTTPException(status_code=404, detail=f"No metrics found for {ticker}")

    return MetricsResponse(
        ticker=ticker,
        metrics=ticker_metrics
    )

@app.get("/companies")
async def list_companies():
    """List all companies in the database."""
    if 'chunks_data' not in globals():
        raise HTTPException(status_code=503, detail="Data not loaded yet")

    tickers = sorted(set(c['ticker'] for c in chunks_data))
    return {
        "companies": tickers,
        "count": len(tickers)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
