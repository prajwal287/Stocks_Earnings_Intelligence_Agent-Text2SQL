"""
SEC XBRL API - Endpoint 2: Company Concept (Specific Metrics Over Time)

This module fetches a specific financial metric (e.g., Revenues, NetIncomeLoss)
for a company across all periods (quarterly and annual).

Usage:
    from sec_api_endpoint2 import get_concept_over_time

    # Get Apple's revenue history (both 10-Q and 10-K)
    results = get_concept_over_time("AAPL", concept="Revenues")

    # Get Microsoft's net income (quarterly only)
    results = get_concept_over_time("MSFT", concept="NetIncomeLoss", include_annual=False)
"""

import requests
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SEC's Company Central Index Keys (CIK)
COMPANY_CIKS = {
    "MSFT": "0000789019",
    "AAPL": "0000320193",
    "GOOGL": "0001652044",
}

# SEC requires a User-Agent header
SEC_HEADERS = {"User-Agent": "MyCompany info@example.com"}

# Common XBRL financial concepts
XBRL_CONCEPTS = {
    "Revenues": "Total revenue",
    "NetIncomeLoss": "Net income or loss",
    "OperatingIncomeLoss": "Operating income",
    "GrossProfit": "Gross profit",
    "Assets": "Total assets",
    "Liabilities": "Total liabilities",
    "StockholdersEquity": "Shareholders' equity",
    "CostOfRevenue": "Cost of goods sold",
    "OperatingExpenses": "Operating expenses",
    "IncomeTaxExpense": "Income tax expense",
}


def get_concept_over_time(
    ticker: str,
    concept: str = "Revenues",
    include_annual: bool = True,
    limit: int = 10
) -> List[Dict]:
    """
    Fetch a specific financial concept over time from SEC XBRL API.

    Args:
        ticker: Stock ticker (MSFT, AAPL, GOOGL, etc.)
        concept: XBRL concept name (Revenues, NetIncomeLoss, etc.)
        include_annual: If True, include both 10-Q (quarterly) and 10-K (annual) filings.
                       If False, 10-Q (quarterly) only.
        limit: Maximum number of results to return (sorted by date, most recent first)

    Returns:
        List of dictionaries with keys:
            - ticker: Stock ticker
            - concept: Financial concept name
            - period_end: End date of the period
            - filing_date: Date the filing was submitted to SEC
            - form: Filing type (10-Q or 10-K)
            - value: Numeric value of the concept for this period

    Example:
        >>> results = get_concept_over_time("AAPL", concept="Revenues")
        >>> for r in results[:3]:
        ...     print(f"{r['period_end']} ({r['form']}): ${r['value']:,.0f}")
        2018-09-29 (10-K): $265,595,000,000
        2018-06-30 (10-K): $53,265,000,000
        2018-03-31 (10-K): $61,137,000,000
    """

    cik = COMPANY_CIKS.get(ticker.upper())
    if not cik:
        logger.error(f"❌ Unknown ticker: {ticker}")
        logger.info(f"   Available: {', '.join(COMPANY_CIKS.keys())}")
        return []

    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json"
    logger.info(f"📍 Fetching: {ticker} | {concept}")
    logger.info(f"🔗 URL: {url}")

    try:
        # Fetch from SEC API
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        logger.info(f"✅ Response: {data.get('entityName')}")

        results = []
        units = data.get("units", {}).get("USD", [])

        # Show data summary
        logger.info(f"📊 Total entries in SEC database: {len(units)}")

        # Count entries by form type
        form_counts = {}
        for entry in units:
            form = entry.get("form")
            form_counts[form] = form_counts.get(form, 0) + 1

        for form in sorted(form_counts.keys()):
            logger.info(f"   {form}: {form_counts[form]} entries")

        # Filter for accepted forms
        accepted_forms = ["10-Q", "10-K"] if include_annual else ["10-Q"]
        logger.info(f"🔍 Filtering for: {accepted_forms}")

        quarterly = [u for u in units if u.get("form") in accepted_forms]
        logger.info(f"✅ Matched entries: {len(quarterly)}")

        # Sort by date (most recent first) and limit
        quarterly = sorted(quarterly, key=lambda x: x.get("end", ""), reverse=True)[:limit]

        logger.info(f"📈 Top {limit} results:")

        for i, fact in enumerate(quarterly, 1):
            results.append({
                "ticker": ticker,
                "concept": concept,
                "period_end": fact.get("end"),
                "filing_date": fact.get("filed"),
                "form": fact.get("form"),
                "value": fact.get("val", 0),
            })

            value_display = f"${fact.get('val', 0):,.0f}" if fact.get('val') else "N/A"
            logger.info(f"  {i}. {fact['end']} ({fact['form']}) - {value_display}")

        logger.info("")  # Blank line for readability
        return results

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.error(f"❌ Concept not found: {concept}")
            logger.info(f"   Available concepts: {', '.join(list(XBRL_CONCEPTS.keys())[:5])}...")
        else:
            logger.error(f"❌ HTTP Error: {e}")
        return []

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # Test the function with all three companies
    print("\n" + "="*70)
    print("ENDPOINT 2: Company Concept (Specific Metrics Over Time)")
    print("="*70 + "\n")

    # Test 1: All companies, Revenues
    for ticker in ["MSFT", "AAPL", "GOOGL"]:
        results = get_concept_over_time(ticker, concept="Revenues", include_annual=True)
        print(f"✅ {ticker}: Got {len(results)} entries\n")

    # Test 2: Different concept
    print("\n" + "="*70)
    print("Testing different concept: NetIncomeLoss")
    print("="*70 + "\n")
    results = get_concept_over_time("MSFT", concept="NetIncomeLoss")
    print(f"✅ MSFT NetIncomeLoss: Got {len(results)} entries")
