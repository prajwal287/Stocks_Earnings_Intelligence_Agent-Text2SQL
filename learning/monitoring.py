"""
Monitoring & Logging for Financial RAG Agent

Tracks:
1. API Performance - Latency, throughput
2. Error Rates - Failures, timeouts
3. Cost - OpenAI API usage
4. User Feedback - Quality ratings
5. System Health - Uptime, resource usage
"""

import logging
import time
from typing import Dict, Optional, Callable
from functools import wraps
from datetime import datetime
from collections import defaultdict
import json


class PerformanceMonitor:
    """Track API performance metrics."""

    def __init__(self):
        self.requests = []
        self.errors = defaultdict(int)
        self.latencies = []
        self.costs = []
        self.start_time = datetime.now()

        # Setup logging
        self.logger = logging.getLogger("FinancialRAG")
        handler = logging.FileHandler("financial_rag.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def track_request(self, endpoint: str, method: str, status_code: int,
                     latency_ms: float, tokens_used: int = 0):
        """Track individual request."""
        request_log = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "cost_usd": (tokens_used / 1000) * 0.002  # Rough estimate for GPT-4
        }

        self.requests.append(request_log)
        self.latencies.append(latency_ms)
        self.costs.append(request_log["cost_usd"])

        # Log errors
        if status_code >= 400:
            self.errors[status_code] += 1
            self.logger.error(f"Error {status_code} on {endpoint}")
        else:
            self.logger.info(f"{method} {endpoint} - {latency_ms}ms")

    def get_metrics(self, last_n: int = 100) -> Dict:
        """Get performance metrics."""
        if not self.requests:
            return {}

        recent = self.requests[-last_n:]
        recent_latencies = self.latencies[-last_n:]
        recent_costs = self.costs[-last_n:]

        return {
            "total_requests": len(recent),
            "avg_latency_ms": round(sum(recent_latencies) / len(recent_latencies), 1),
            "p95_latency_ms": round(sorted(recent_latencies)[int(len(recent_latencies) * 0.95)], 1) if recent_latencies else 0,
            "p99_latency_ms": round(sorted(recent_latencies)[int(len(recent_latencies) * 0.99)], 1) if recent_latencies else 0,
            "min_latency_ms": min(recent_latencies) if recent_latencies else 0,
            "max_latency_ms": max(recent_latencies) if recent_latencies else 0,
            "error_count": sum(self.errors.values()),
            "error_rate": f"{(sum(self.errors.values()) / len(recent) * 100):.1f}%",
            "total_cost_usd": round(sum(recent_costs), 4),
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600
        }


class CostTracker:
    """Track OpenAI API costs."""

    # Pricing (as of 2024)
    EMBEDDING_COST = 0.02 / 1_000_000  # per token
    GPT4_INPUT_COST = 0.03 / 1_000
    GPT4_OUTPUT_COST = 0.06 / 1_000

    def __init__(self):
        self.costs = []

    def track_embedding(self, tokens_used: int):
        """Track embedding API call."""
        cost = tokens_used * self.EMBEDDING_COST
        self.costs.append({"type": "embedding", "cost": cost, "tokens": tokens_used})
        return cost

    def track_gpt4(self, input_tokens: int, output_tokens: int):
        """Track GPT-4 API call."""
        input_cost = input_tokens * self.GPT4_INPUT_COST
        output_cost = output_tokens * self.GPT4_OUTPUT_COST
        total_cost = input_cost + output_cost
        self.costs.append({
            "type": "gpt4",
            "cost": total_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        })
        return total_cost

    def get_cost_summary(self) -> Dict:
        """Get cost breakdown."""
        if not self.costs:
            return {}

        embedding_costs = sum(c["cost"] for c in self.costs if c["type"] == "embedding")
        gpt4_costs = sum(c["cost"] for c in self.costs if c["type"] == "gpt4")
        total_cost = embedding_costs + gpt4_costs

        return {
            "embedding_cost_usd": round(embedding_costs, 4),
            "gpt4_cost_usd": round(gpt4_costs, 4),
            "total_cost_usd": round(total_cost, 4),
            "total_requests": len(self.costs),
            "avg_cost_per_request": round(total_cost / len(self.costs), 4) if self.costs else 0
        }


class FeedbackCollector:
    """Collect user feedback on answers."""

    def __init__(self):
        self.feedback = []

    def submit_feedback(self, query_id: str, rating: int, comment: str = ""):
        """Submit user feedback on answer."""
        feedback = {
            "query_id": query_id,
            "rating": rating,  # 1-5
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        self.feedback.append(feedback)

    def get_feedback_summary(self) -> Dict:
        """Summarize feedback."""
        if not self.feedback:
            return {}

        ratings = [f["rating"] for f in self.feedback]
        avg_rating = sum(ratings) / len(ratings)

        return {
            "total_feedback": len(self.feedback),
            "avg_rating": round(avg_rating, 2),
            "rating_distribution": {
                "5_stars": ratings.count(5),
                "4_stars": ratings.count(4),
                "3_stars": ratings.count(3),
                "2_stars": ratings.count(2),
                "1_star": ratings.count(1)
            }
        }


def timeit(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed_ms = (time.time() - start) * 1000
        print(f"⏱️  {func.__name__} took {elapsed_ms:.1f}ms")
        return result
    return wrapper


# Global instances
performance_monitor = PerformanceMonitor()
cost_tracker = CostTracker()
feedback_collector = FeedbackCollector()


def get_system_metrics() -> Dict:
    """Get all system metrics."""
    return {
        "performance": performance_monitor.get_metrics(),
        "costs": cost_tracker.get_cost_summary(),
        "feedback": feedback_collector.get_feedback_summary(),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Example usage
    monitor = PerformanceMonitor()
    tracker = CostTracker()
    feedback = FeedbackCollector()

    # Simulate requests
    monitor.track_request("/query", "POST", 200, 1250, tokens_used=500)
    tracker.track_gpt4(input_tokens=150, output_tokens=250)
    feedback.submit_feedback("q001", 5, "Excellent answer with proper citations")

    print(json.dumps(get_system_metrics(), indent=2))
