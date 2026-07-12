"""
SEC XBRL API - Complete Orchestrator

Coordinates all three SEC API endpoints:
  1. Company Facts (Endpoint 1) - All financial data
  2. Company Concept (Endpoint 2) - Specific metric over time
  3. Submissions API (Endpoint 3) - Filing metadata & document links

This module shows how to combine them for a complete financial data pipeline.
"""

import logging
from typing import Dict, List, Any

# Import the individual endpoint modules
from sec_api_endpoint1 import get_company_facts
from sec_api_endpoint2 import get_concept_over_time
from sec_api_endpoint3 import get_10q_filings_metadata, get_filing_url

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinancialDataPipeline:
    """
    Orchestrates fetching financial data from SEC XBRL API.

    Usage:
        pipeline = FinancialDataPipeline("AAPL")

        # Get all financial concepts
        facts = pipeline.get_facts()

        # Get specific metric over time
        revenues = pipeline.get_metric("Revenues")

        # Get filing metadata
        filings = pipeline.get_filings()
    """

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        logger.info(f"🚀 Initializing pipeline for {self.ticker}")

    def get_facts(self, limit_per_concept: int = 5) -> Dict[str, List[Dict]]:
        """
        Get ALL financial facts for the company.

        Returns dictionary of concepts to data points.
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"PHASE 1: Fetching Company Facts (Endpoint 1)")
        logger.info(f"{'='*70}")

        facts = get_company_facts(self.ticker, limit_per_concept=limit_per_concept)
        return facts

    def get_metric(self, concept: str, include_annual: bool = True, limit: int = 10) -> List[Dict]:
        """
        Get a specific financial metric over time.

        Example:
            revenues = pipeline.get_metric("Revenues")
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"PHASE 2: Fetching Specific Metric (Endpoint 2)")
        logger.info(f"{'='*70}")

        results = get_concept_over_time(
            self.ticker,
            concept=concept,
            include_annual=include_annual,
            limit=limit
        )
        return results

    def get_filings(self, limit: int = 5, include_10k: bool = True) -> List[Dict]:
        """
        Get filing metadata (dates, accession numbers, URLs).

        Useful for finding 10-Q/10-K documents for RAG text extraction.
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"PHASE 3: Fetching Filing Metadata (Endpoint 3)")
        logger.info(f"{'='*70}")

        filings = get_10q_filings_metadata(
            self.ticker,
            limit=limit,
            include_10k=include_10k
        )
        return filings

    def get_complete_data(
        self,
        metrics: List[str] = None,
        facts_limit: int = 3,
        filings_limit: int = 3
    ) -> Dict[str, Any]:
        """
        Orchestrate complete data fetch: facts + metrics + filings.

        Args:
            metrics: List of concepts to fetch over time
            facts_limit: Limit per concept when fetching all facts
            filings_limit: Number of recent filings to fetch

        Returns:
            Dictionary with keys: 'facts', 'metrics', 'filings'
        """

        if metrics is None:
            metrics = ["Revenues", "NetIncomeLoss", "OperatingIncomeLoss"]

        complete_data = {
            "ticker": self.ticker,
            "facts": self.get_facts(limit_per_concept=facts_limit),
            "metrics": {},
            "filings": self.get_filings(limit=filings_limit),
        }

        # Fetch each metric over time
        for metric in metrics:
            logger.info(f"\n📊 Fetching {metric}...")
            complete_data["metrics"][metric] = self.get_metric(metric, limit=5)

        return complete_data


def main():
    """Demo: Full pipeline for AAPL, MSFT, GOOGL"""

    print("\n" + "="*70)
    print("SEC XBRL API - Complete Orchestrator Demo")
    print("="*70 + "\n")

    # Create pipelines for each company
    for ticker in ["MSFT", "AAPL", "GOOGL"]:
        print("\n\n")
        pipeline = FinancialDataPipeline(ticker)

        # Get just the most recent filings and a couple metrics
        data = pipeline.get_complete_data(
            metrics=["Revenues", "NetIncomeLoss"],
            facts_limit=2,
            filings_limit=2
        )

        print(f"\n✅ {ticker} Complete Data:")
        print(f"   Facts: {len(data['facts'])} concepts")
        print(f"   Metrics: {list(data['metrics'].keys())}")
        print(f"   Filings: {len(data['filings'])} recent 10-Q/10-K")


if __name__ == "__main__":
    main()
