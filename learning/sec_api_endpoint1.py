"""
SEC XBRL API - Endpoint 1: Company Facts (All Financial Data)

This module fetches ALL financial data ever filed by a company in XBRL format.
Most comprehensive endpoint - contains all XBRL-tagged facts.

Usage:
    from sec_api_endpoint1 import get_company_facts

    # Get all facts for Apple
    facts = get_company_facts("AAPL", limit_per_concept=3)

    # Extract specific concept
    revenues = facts.get("Revenues", [])
"""

import requests
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COMPANY_CIKS = {
    "MSFT": "0000789019",
    "AAPL": "0000320193",
    "GOOGL": "0001652044",
}

SEC_HEADERS = {"User-Agent": "MyCompany info@example.com"}


def get_company_facts(ticker: str, limit_per_concept: int = 5) -> Dict[str, List[Dict]]:
    """
    Fetch ALL financial facts for a company from SEC XBRL API.

    Args:
        ticker: Stock ticker (MSFT, AAPL, GOOGL, etc.)
        limit_per_concept: Maximum entries per financial concept to return

    Returns:
        Dictionary where keys are concept names (e.g., "Revenues", "NetIncomeLoss")
        and values are lists of dictionaries with:
            - period_end: End date of the period
            - filing_date: Date filed with SEC
            - form: Filing type (10-Q, 10-K, etc.)
            - value: Numeric value
            - unit: Unit (USD, shares, etc.)

    Example:
        >>> facts = get_company_facts("AAPL")
        >>> print(facts.keys())
        dict_keys(['Revenues', 'NetIncomeLoss', 'OperatingIncomeLoss', ...])
        >>> revenues = facts['Revenues'][:2]
        >>> for r in revenues:
        ...     print(f"{r['period_end']}: ${r['value']:,.0f}")
    """

    cik = COMPANY_CIKS.get(ticker.upper())
    if not cik:
        logger.error(f"❌ Unknown ticker: {ticker}")
        return {}

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    logger.info(f"📍 Fetching Company Facts for: {ticker}")
    logger.info(f"🔗 URL: {url}")

    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        entity_name = data.get("entityName", "Unknown")
        logger.info(f"✅ Company: {entity_name}")

        # Extract facts (all XBRL-tagged data)
        facts_raw = data.get("facts", {}).get("us-gaap", {})
        logger.info(f"📊 Total XBRL concepts: {len(facts_raw)}")

        results = {}

        # Process each concept
        for concept_name, concept_data in facts_raw.items():
            units = concept_data.get("units", {}).get("USD", [])

            # Filter for 10-Q and 10-K only
            quarterly = [u for u in units if u.get("form") in ["10-Q", "10-K"]]

            # Sort by date (most recent first) and limit
            quarterly = sorted(quarterly, key=lambda x: x.get("end", ""), reverse=True)[:limit_per_concept]

            if quarterly:
                results[concept_name] = [
                    {
                        "period_end": fact.get("end"),
                        "filing_date": fact.get("filed"),
                        "form": fact.get("form"),
                        "value": fact.get("val", 0),
                    }
                    for fact in quarterly
                ]

        logger.info(f"✅ Extracted {len(results)} concepts with financial data")

        # Show top concepts
        top_concepts = sorted(results.keys())[:5]
        logger.info(f"📈 Sample concepts: {', '.join(top_concepts)}")

        return results

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {}


def extract_metric_from_facts(facts: Dict, metric: str) -> List[Dict]:
    """
    Extract a specific metric from facts dictionary.

    Args:
        facts: Output from get_company_facts()
        metric: Concept name (e.g., "Revenues", "NetIncomeLoss")

    Returns:
        List of data points for that metric
    """
    return facts.get(metric, [])


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ENDPOINT 1: Company Facts (All Financial Data)")
    print("="*70 + "\n")

    # Test with all three companies
    for ticker in ["MSFT", "AAPL", "GOOGL"]:
        facts = get_company_facts(ticker, limit_per_concept=2)
        print(f"✅ {ticker}: Got {len(facts)} concepts with data\n")

    # Demonstrate extraction
    print("\n" + "="*70)
    print("Example: Extract Revenues from GOOGL facts")
    print("="*70 + "\n")
    googl_facts = get_company_facts("GOOGL", limit_per_concept=3)
    revenues = extract_metric_from_facts(googl_facts, "Revenues")
    for r in revenues[:2]:
        print(f"  {r['period_end']} ({r['form']}): ${r['value']:,.0f}")
