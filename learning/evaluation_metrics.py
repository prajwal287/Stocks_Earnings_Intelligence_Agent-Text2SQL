"""
Evaluation Metrics for Financial RAG Agent

Measures:
1. Retrieval Quality - Are chunks relevant to query?
2. Answer Quality - Is the response accurate?
3. Citation Accuracy - Are sources correctly cited?
4. Latency - Response time
5. Cost - OpenAI API usage
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import psycopg2
from enum import Enum


class AnswerQuality(Enum):
    EXCELLENT = 5
    GOOD = 4
    FAIR = 3
    POOR = 2
    HARMFUL = 1


@dataclass
class RetrievalMetric:
    """Measures retrieval quality."""
    query: str
    retrieved_chunks: int
    avg_similarity_score: float
    top_chunk_similarity: float
    relevant_chunks: int  # User-rated as relevant
    precision: float  # relevant_chunks / retrieved_chunks
    recall: float  # relevant_chunks / total_relevant

    def __post_init__(self):
        self.timestamp = datetime.now()
        self.rating = "good" if self.precision > 0.7 else "fair" if self.precision > 0.5 else "poor"


@dataclass
class AnswerMetric:
    """Measures answer quality."""
    query: str
    answer: str
    sources: List[Dict]
    quality_rating: int  # 1-5
    has_citations: bool
    citation_accuracy: float  # 0-1
    confidence_score: float  # How confident is the model?
    response_time_ms: float

    def __post_init__(self):
        self.timestamp = datetime.now()
        self.cost_usd = response_time_ms * 0.0001  # Rough estimate


@dataclass
class QueryMetric:
    """Tracks individual query performance."""
    query_id: str
    query: str
    retrieval_metric: RetrievalMetric
    answer_metric: AnswerMetric
    end_to_end_time_ms: float
    success: bool
    error_message: Optional[str] = None


class EvaluationDatabase:
    """Store and analyze evaluation metrics."""

    def __init__(self):
        self.conn = None
        self.queries_log = []
        self.init_db()

    def init_db(self):
        """Create evaluation tables in PostgreSQL."""
        try:
            self.conn = psycopg2.connect(
                host='localhost', port=5432, database='financial_data',
                user='postgres', password='postgres'
            )
            cursor = self.conn.cursor()

            # Create evaluation log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evaluation_logs (
                    id SERIAL PRIMARY KEY,
                    query_id VARCHAR,
                    query_text VARCHAR,
                    answer_text TEXT,
                    retrieval_precision FLOAT,
                    answer_quality INT,
                    response_time_ms FLOAT,
                    cost_usd FLOAT,
                    user_feedback INT,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            ''')

            self.conn.commit()
            print("✅ Evaluation database initialized")
        except Exception as e:
            print(f"❌ Error initializing DB: {e}")

    def log_query(self, metric: QueryMetric):
        """Log a query evaluation."""
        self.queries_log.append(metric)

        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO evaluation_logs
                (query_id, query_text, answer_text, retrieval_precision,
                 answer_quality, response_time_ms, cost_usd)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                metric.query_id,
                metric.query,
                metric.answer_metric.answer,
                metric.retrieval_metric.precision,
                metric.answer_metric.quality_rating,
                metric.end_to_end_time_ms,
                metric.answer_metric.cost_usd
            ))
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error logging query: {e}")

    def get_metrics_summary(self, last_n: int = 100) -> Dict:
        """Get summary of recent metrics."""
        if not self.queries_log:
            return {}

        recent = self.queries_log[-last_n:]

        retrieval_precision = sum(q.retrieval_metric.precision for q in recent) / len(recent)
        avg_answer_quality = sum(q.answer_metric.quality_rating for q in recent) / len(recent)
        avg_response_time = sum(q.end_to_end_time_ms for q in recent) / len(recent)
        total_cost = sum(q.answer_metric.cost_usd for q in recent)
        success_rate = sum(1 for q in recent if q.success) / len(recent)

        return {
            "queries_evaluated": len(recent),
            "retrieval_precision": round(retrieval_precision, 3),
            "avg_answer_quality": round(avg_answer_quality, 2),
            "avg_response_time_ms": round(avg_response_time, 1),
            "total_cost_usd": round(total_cost, 4),
            "success_rate": round(success_rate, 3),
            "timestamp": datetime.now().isoformat()
        }


class AnswerEvaluator:
    """Evaluate answer quality."""

    @staticmethod
    def check_citations(answer: str, sources: List[Dict]) -> float:
        """Check if answer citations match sources."""
        if not sources:
            return 0.0

        matched = 0
        for source in sources:
            ticker = source.get('ticker', '')
            year = source.get('year', '')

            if ticker in answer and str(year) in answer:
                matched += 1

        return matched / len(sources) if sources else 0.0

    @staticmethod
    def get_confidence_score(answer: str) -> float:
        """Estimate confidence from answer text."""
        confidence_phrases = [
            "clearly", "definitely", "obviously", "certainly",
            "without doubt", "confirmed", "verified"
        ]

        hedge_phrases = [
            "may", "might", "could", "possibly", "appears",
            "suggests", "indicates", "seems", "reportedly"
        ]

        answer_lower = answer.lower()
        confidence = sum(1 for p in confidence_phrases if p in answer_lower)
        hedges = sum(1 for p in hedge_phrases if p in answer_lower)

        # Score: more confidence, fewer hedges = higher confidence
        score = (confidence - hedges) / max(len(confidence_phrases), len(hedge_phrases))
        return max(0.0, min(1.0, 0.5 + score * 0.5))  # Scale to 0-1


class RetrievalEvaluator:
    """Evaluate retrieval quality."""

    @staticmethod
    def evaluate_chunk_relevance(query: str, chunks: List[Dict]) -> Dict:
        """Evaluate relevance of retrieved chunks."""
        if not chunks:
            return {"precision": 0.0, "avg_similarity": 0.0}

        # Calculate average similarity
        avg_similarity = sum(c.get('similarity_score', 0) for c in chunks) / len(chunks)

        # Check if top chunk has high similarity
        top_similarity = chunks[0].get('similarity_score', 0) if chunks else 0

        # Heuristic: high similarity = likely relevant
        precision = 1.0 if top_similarity > 0.8 else 0.7 if top_similarity > 0.6 else 0.5

        return {
            "precision": precision,
            "avg_similarity": avg_similarity,
            "top_similarity": top_similarity,
            "chunks_count": len(chunks)
        }


if __name__ == "__main__":
    # Example usage
    db = EvaluationDatabase()

    # Simulate a query evaluation
    retrieval = RetrievalMetric(
        query="What are risks?",
        retrieved_chunks=3,
        avg_similarity_score=0.85,
        top_chunk_similarity=0.92,
        relevant_chunks=3,
        precision=1.0,
        recall=1.0
    )

    answer = AnswerMetric(
        query="What are risks?",
        answer="Based on AAPL 2024 filing, risks include market competition...",
        sources=[{"ticker": "AAPL", "year": "2024", "section": "Risk Factors"}],
        quality_rating=4,
        has_citations=True,
        citation_accuracy=1.0,
        confidence_score=0.85,
        response_time_ms=1500
    )

    metric = QueryMetric(
        query_id="q001",
        query="What are risks?",
        retrieval_metric=retrieval,
        answer_metric=answer,
        end_to_end_time_ms=1600,
        success=True
    )

    db.log_query(metric)
    print(json.dumps(db.get_metrics_summary(), indent=2))
