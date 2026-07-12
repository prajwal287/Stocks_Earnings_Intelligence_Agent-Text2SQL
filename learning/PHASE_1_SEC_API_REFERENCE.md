# Phase 1: SEC XBRL API Reference

## Quick Start

Run the Phase 1 notebook:

```bash
jupyter notebook learning/PHASE_1_SEC_API_EXTRACTION.ipynb
```

This shows all 3 endpoints + orchestrator in action.

---

## 3 Endpoints Overview

### Endpoint 1: Company Facts (All Data)
Returns ALL financial data ever filed by a company (~500+ concepts)

```python
from sec_api_endpoint1 import get_company_facts

facts = get_company_facts("AAPL", limit_per_concept=5)
# Returns: dict of all concepts with historical data
```

### Endpoint 2: Company Concept (Specific Metric)
Returns one metric over time (e.g., Revenues from 2010-2026)

```python
from sec_api_endpoint2 import get_concept_over_time

revenues = get_concept_over_time("AAPL", concept="Revenues", limit=10)
# Returns: list of revenue entries over time
```

### Endpoint 3: Submissions (Filing Metadata)
Returns filing dates, accession numbers, and document URLs

```python
from sec_api_endpoint3 import get_10q_filings_metadata

filings = get_10q_filings_metadata("AAPL", limit=5)
# Returns: list of recent 10-Q/10-K filings with URLs
```

---

## Orchestrator (Recommended)

Simple interface combining all 3 endpoints:

```python
from sec_api_orchestrator import FinancialDataPipeline

pipeline = FinancialDataPipeline("AAPL")

# Get everything
data = pipeline.get_complete_data(
    metrics=["Revenues", "NetIncomeLoss"],
    facts_limit=3,
    filings_limit=5
)

# Access results
data["facts"]       # All concepts
data["metrics"]     # Time series for each metric
data["filings"]     # Recent filings with URLs
```

---

## Module Files

**Core Modules:**
- `sec_api_endpoint1.py` - Company Facts endpoint
- `sec_api_endpoint2.py` - Company Concept endpoint
- `sec_api_endpoint3.py` - Submissions endpoint
- `sec_api_orchestrator.py` - Unified interface

**Notebooks:**
- `PHASE_1_SEC_API_EXTRACTION.ipynb` - Complete demo (run this first)
- `PHASE_2_COMPLETE_DLT_DUCKDB.ipynb` - Load Phase 1 data into DuckDB

---

## Common XBRL Concepts

```
Revenues                - Total revenue
NetIncomeLoss           - Net income or loss
OperatingIncomeLoss     - Operating income
GrossProfit             - Gross profit
Assets                  - Total assets
Liabilities             - Total liabilities
StockholdersEquity      - Shareholders' equity
CostOfRevenue           - Cost of goods sold
OperatingExpenses       - Operating expenses
IncomeTaxExpense        - Tax expense
```

---

## Why SEC XBRL API?

✅ **Official** - Direct from SEC, audit-verified
✅ **Standardized** - Same XBRL tags for all companies
✅ **Free** - No API key, no cost
✅ **Scalable** - Works for all public companies
✅ **Consistent** - Data never changes once filed
✅ **Complete** - Full history available

---

## Next: Phase 2

After Phase 1 extracts data, Phase 2 loads it into DuckDB:

```bash
jupyter notebook learning/PHASE_2_COMPLETE_DLT_DUCKDB.ipynb
```

---

## For Questions

See detailed docs in each module:
- Function docstrings explain parameters and return values
- Example code in notebook shows real usage
- Error messages provide helpful context
