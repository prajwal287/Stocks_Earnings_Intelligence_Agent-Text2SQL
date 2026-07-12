"""
SEC XBRL API - Endpoint 3: Submissions API (Filing Metadata)

This module fetches filing metadata - dates, accession numbers, and document links.
Essential for finding 10-Q/10-K document URLs for RAG text extraction.

Usage:
    from sec_api_endpoint3 import get_10q_filings_metadata, get_filing_url

    # Get 10-Q metadata for Apple
    filings = get_10q_filings_metadata("AAPL", limit=5)

    # Get direct link to filing document
    url = get_filing_url(ticker="AAPL", accession_number="0000320193-24-000077")
"""

import requests
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COMPANY_CIKS = {
    "MSFT": "0000789019",
    "AAPL": "0000320193",
    "GOOGL": "0001652044",
}

SEC_HEADERS = {"User-Agent": "MyCompany info@example.com"}


def get_10q_filings_metadata(ticker: str, limit: int = 5, include_10k: bool = True) -> List[Dict]:
    """
    Fetch 10-Q (and optionally 10-K) filing metadata from SEC.

    Args:
        ticker: Stock ticker (MSFT, AAPL, GOOGL, etc.)
        limit: Maximum number of filings to return
        include_10k: If True, include 10-K (annual) filings too

    Returns:
        List of dictionaries with keys:
            - ticker: Stock ticker
            - form: Filing type (10-Q or 10-K)
            - filing_date: Date the filing was submitted to SEC
            - period_end: End date of the reporting period
            - accession_number: SEC's unique filing identifier
            - filing_url: URL to the filing document

    Example:
        >>> filings = get_10q_filings_metadata("AAPL", limit=3)
        >>> for f in filings:
        ...     print(f"{f['filing_date']} - {f['accession_number']}")
        2024-11-08 - 0000320193-24-000077
        2024-08-07 - 0000320193-24-000061
        2024-05-07 - 0000320193-24-000045
    """

    cik = COMPANY_CIKS.get(ticker.upper())
    if not cik:
        logger.error(f"❌ Unknown ticker: {ticker}")
        return []

    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    logger.info(f"📍 Fetching 10-Q metadata for: {ticker}")
    logger.info(f"🔗 URL: {url}")

    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract CIK without leading zeros (for URL building)
        cik_clean = str(int(cik))

        entity_name = data.get("entityName", "Unknown")
        logger.info(f"✅ Company: {entity_name}")

        # Get recent filings
        recent = data.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        filing_dates = recent.get("filingDate", [])
        period_ends = recent.get("reportDate", [])
        accessions = recent.get("accessionNumber", [])

        logger.info(f"📊 Total recent filings: {len(forms)}")

        results = []
        count = 0

        for form, filing_date, period_end, accession in zip(forms, filing_dates, period_ends, accessions):
            # Filter for 10-Q (or 10-Q and 10-K if include_10k=True)
            target_forms = ["10-Q", "10-K"] if include_10k else ["10-Q"]

            if form in target_forms and count < limit:
                # Build filing URL
                # Format: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=...&type=10-Q
                # Or direct: https://www.sec.gov/Archives/edgar/{cik}/{accession}/0000320193-24-000077-index.htm

                accession_clean = accession.replace("-", "")
                filing_url = f"https://www.sec.gov/Archives/edgar/{cik_clean}/{accession_clean}/{accession}-index.htm"

                results.append({
                    "ticker": ticker,
                    "form": form,
                    "filing_date": filing_date,
                    "period_end": period_end,
                    "accession_number": accession,
                    "filing_url": filing_url,
                })

                logger.info(f"  {count+1}. {filing_date} ({form}) - {accession}")
                count += 1

        logger.info(f"✅ Got {len(results)} filings")
        return results

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_filing_url(ticker: str, accession_number: str) -> str:
    """
    Build the URL for a specific SEC filing document.

    Args:
        ticker: Stock ticker (MSFT, AAPL, GOOGL, etc.)
        accession_number: Filing accession number (e.g., "0000320193-24-000077")

    Returns:
        URL string to the filing index page

    Example:
        >>> url = get_filing_url("AAPL", "0000320193-24-000077")
        >>> print(url)
        https://www.sec.gov/Archives/edgar/320193/000032019324000077/0000320193-24-000077-index.htm
    """

    cik = COMPANY_CIKS.get(ticker.upper())
    if not cik:
        logger.error(f"Unknown ticker: {ticker}")
        return ""

    cik_clean = str(int(cik))
    accession_clean = accession_number.replace("-", "")

    url = f"https://www.sec.gov/Archives/edgar/{cik_clean}/{accession_clean}/{accession_number}-index.htm"
    return url


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ENDPOINT 3: Submissions API (Filing Metadata)")
    print("="*70 + "\n")

    # Test with all three companies
    for ticker in ["MSFT", "AAPL", "GOOGL"]:
        filings = get_10q_filings_metadata(ticker, limit=3)
        print(f"✅ {ticker}: Got {len(filings)} 10-Q/10-K filings\n")

    # Demonstrate URL building
    print("\n" + "="*70)
    print("Example: Build filing URLs for Apple")
    print("="*70 + "\n")
    apple_filings = get_10q_filings_metadata("AAPL", limit=2)
    for filing in apple_filings:
        print(f"  {filing['filing_date']}: {filing['filing_url']}\n")
