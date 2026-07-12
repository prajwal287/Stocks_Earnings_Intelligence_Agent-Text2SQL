# Complete SEC XBRL API Guide: All 3 Endpoints

## Overview

The SEC provides **3 endpoints** for accessing official financial data in XBRL format. Each serves a different purpose in the financial data pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             SEC XBRL API (Official Source of Truth)         │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
    ┌─────▼──────┐    ┌────▼─────┐    ┌────▼─────┐
    │ Endpoint 1 │    │Endpoint 2 │    │Endpoint 3│
    │  ALL Facts │    │  Metrics  │    │Metadata  │
    │  (544 tags)│    │Over Time  │    │& URLs    │
    └─────┬──────┘    └────┬─────┘    └────┬─────┘
          │                │               │
    ┌─────▼────────────────┼───────────────▼──────────┐
    │  Extract + Transform                             │
    │  • Filter for 10-Q/10-K                         │
    │  • Normalize currencies                         │
    │  • Handle duplicates                            │
    └────────────┬────────────────────────────────────┘
                 │
          ┌──────▼──────────┐
          │   DuckDB        │
          │   (Phase 2)     │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │  RAGPipeline    │
          │  (Phase 3)      │
          └─────────────────┘
```

---

## Endpoint 1: Company Facts API

**What it does:** Returns ALL financial data ever filed by a company in XBRL format.

**Best for:**
- Bulk data ingestion
- Getting complete financial picture
- Discovering available metrics

**Characteristics:**
- Most comprehensive (500+ concepts)
- Contains all filing history
- Covers 10-Q, 10-K, 8-K, etc.
- No rate limiting concerns

### Usage

```python
from sec_api_endpoint1 import get_company_facts

# Get all facts for a company
facts = get_company_facts("AAPL", limit_per_concept=5)

# facts is a dict like:
# {
#     "Revenues": [
#         {"period_end": "2018-09-29", "form": "10-K", "value": 265595000000, ...},
#         {...}
#     ],
#     "NetIncomeLoss": [...],
#     ...
# }

# Iterate over all concepts
for concept_name, data_points in facts.items():
    print(f"{concept_name}: {len(data_points)} entries")
```

**Data Retrieved (per company):**
- MSFT: 479 concepts
- AAPL: 444 concepts
- GOOGL: 470 concepts

---

## Endpoint 2: Company Concept API

**What it does:** Returns a SPECIFIC financial metric over time (e.g., Revenues from 2010-2026).

**Best for:**
- Time series analysis
- Trend analysis
- Specific metric tracking
- Most recent data

**Characteristics:**
- Single metric focus
- Complete historical data
- Mixed 10-Q and 10-K data
- Sometimes has older data

### Usage

```python
from sec_api_endpoint2 import get_concept_over_time

# Get Apple's revenue over time
revenues = get_concept_over_time("AAPL", concept="Revenues")

# Returns list of dicts:
# [
#     {
#         "ticker": "AAPL",
#         "concept": "Revenues",
#         "period_end": "2018-09-29",
#         "filing_date": "2018-11-05",
#         "form": "10-K",
#         "value": 265595000000
#     },
#     ...
# ]

# Filter by period
recent_10_quarters = revenues[:10]
```

**Common Concepts:**
- `Revenues` - Total revenue
- `NetIncomeLoss` - Net income/loss
- `OperatingIncomeLoss` - Operating income
- `Assets` - Total assets
- `Liabilities` - Total liabilities
- `StockholdersEquity` - Shareholders' equity
- `CostOfRevenue` - COGS
- `OperatingExpenses` - OpEx
- `IncomeTaxExpense` - Tax expense

---

## Endpoint 3: Submissions API

**What it does:** Returns filing METADATA - dates, accession numbers, links to actual documents.

**Best for:**
- Finding filing URLs
- Getting filing dates
- Accessing MD&A text
- Building document URLs for RAG

**Characteristics:**
- Metadata only (not numbers)
- Links to actual filings
- Recent filings focus
- Essential for RAG text extraction

### Usage

```python
from sec_api_endpoint3 import get_10q_filings_metadata, get_filing_url

# Get recent 10-Q/10-K metadata
filings = get_10q_filings_metadata("AAPL", limit=5)

# Returns list of dicts:
# [
#     {
#         "ticker": "AAPL",
#         "form": "10-Q",
#         "filing_date": "2026-05-01",
#         "period_end": "2026-03-29",
#         "accession_number": "0000320193-26-000013",
#         "filing_url": "https://www.sec.gov/Archives/edgar/..."
#     },
#     ...
# ]

# Build filing URLs
for filing in filings:
    print(f"{filing['filing_date']}: {filing['filing_url']}")
```

---

## Complete Pipeline: Orchestrator

The **Orchestrator** combines all 3 endpoints into one unified pipeline:

```python
from sec_api_orchestrator import FinancialDataPipeline

# Create pipeline for a company
pipeline = FinancialDataPipeline("AAPL")

# Get all financial facts (Endpoint 1)
facts = pipeline.get_facts()

# Get specific metrics over time (Endpoint 2)
revenues = pipeline.get_metric("Revenues")
net_income = pipeline.get_metric("NetIncomeLoss")

# Get filing metadata (Endpoint 3)
filings = pipeline.get_filings()

# Or get everything at once
complete_data = pipeline.get_complete_data(
    metrics=["Revenues", "NetIncomeLoss", "OperatingIncomeLoss"],
    facts_limit=3,
    filings_limit=5
)
```

---

## Endpoint Comparison

| Feature | Endpoint 1 | Endpoint 2 | Endpoint 3 |
|---------|-----------|-----------|-----------|
| **Purpose** | All facts | Specific metric | Filing metadata |
| **Data Type** | Numeric | Numeric | URLs & dates |
| **Scope** | All history | All history | Recent filings |
| **Concepts** | 500+ | 1 metric | N/A |
| **Forms** | All | Mixed 10-Q/10-K | 10-Q/10-K |
| **Update Frequency** | Daily | Daily | Daily |
| **Best Use** | Bulk ingest | Trend analysis | RAG setup |

---

## Data Quality Notes

### ✅ What's Official:
- Numbers come directly from SEC filings
- Audited by external auditors
- XBRL-tagged by companies (required)
- Never changes (immutable once filed)

### ⚠️ What to Watch:
- Endpoint 2 sometimes has older data (2009-2010 for MSFT)
- Different companies file on different schedules
- Some concepts only have 10-K (annual), not 10-Q (quarterly)
- 8-K and other forms have different cadence

### 🔍 How to Filter:
```python
# Always filter for form type
quarterly = [u for u in units if u.get("form") in ["10-Q", "10-K"]]

# Skip unusual forms
skip = [u for u in units if u.get("form") in ["8-K", "10-Q/A"]]
```

---

## Integration Path

### Phase 1: Extract ✅ (COMPLETE)
- Endpoint 1 → Get all financial facts
- Endpoint 2 → Get specific metrics
- Endpoint 3 → Get filing URLs

### Phase 2: Transform & Load (NEXT)
- Normalize data
- Handle duplicates
- Load into DuckDB with dlt
- Create indexed tables

### Phase 3: Query & Generate (AFTER)
- Query DuckDB
- Feed to RAGPipeline
- Generate narratives with Claude

---

## Files in This Module

```
learning/
├── sec_api_endpoint1.py          # Company Facts API
├── sec_api_endpoint2.py          # Company Concept API
├── sec_api_endpoint3.py          # Submissions API
├── sec_api_orchestrator.py       # Combined orchestrator
└── SEC_API_COMPLETE_GUIDE.md     # This file
```

---

## Quick Start

### 1. Get Facts (Everything)
```python
from sec_api_endpoint1 import get_company_facts
facts = get_company_facts("AAPL")
print(f"Got {len(facts)} concepts")
```

### 2. Get Metric Over Time
```python
from sec_api_endpoint2 import get_concept_over_time
revenues = get_concept_over_time("AAPL", concept="Revenues")
for r in revenues[:3]:
    print(f"{r['period_end']}: ${r['value']:,.0f}")
```

### 3. Get Filings & URLs
```python
from sec_api_endpoint3 import get_10q_filings_metadata
filings = get_10q_filings_metadata("AAPL", limit=3)
for f in filings:
    print(f"{f['filing_date']}: {f['filing_url']}")
```

### 4. Orchestrate All Three
```python
from sec_api_orchestrator import FinancialDataPipeline
pipeline = FinancialDataPipeline("AAPL")
data = pipeline.get_complete_data()
```

---

## Key Learnings

1. **Official Data Only:** SEC XBRL is the source of truth - audit-verified, immutable, standardized
2. **Three Complementary Views:** Facts (bulk), Concepts (trend), Submissions (URLs)
3. **No Manual Work:** Automatically scales to thousands of companies
4. **Standards Matter:** XBRL tags are consistent across all companies
5. **Free & Fast:** No API key needed, generous rate limits (10 req/sec)

---

## What's Next

Once you have data extracted:

1. **Load into DuckDB** using dlt (Phase 2)
2. **Create indexed tables** for fast queries
3. **Feed into RAGPipeline** with Claude (Phase 3)
4. **Generate narratives** based on financial data

See `COMPLETE_PIPELINE_END_TO_END.ipynb` for full integration.
