# Complete Earnings Intelligence Agent: Phases 1-5

## Executive Summary

End-to-end pipeline for financial analysis: Extracts official SEC data via XBRL API, loads into PostgreSQL, extracts MD&A text from 10-K PDFs, and integrates semantic RAG with LLM for intelligent financial Q&A. Includes production REST API with real-time monitoring and evaluation dashboards.

```
┌─────────────────────────────────────────────────────────────────┐
│         SEC XBRL API: Official Financial Data                   │
│         (Audit-verified, standardized, free)                    │
└──────────────┬──────────────────────────────────────────────────┘
               │
        ┌──────▼────────────────────────────────────────────────────┐
        │ PHASE 1: Extract (You are here →)                        │
        │ • Endpoint 1: Company Facts (all financial data)         │
        │ • Endpoint 2: Company Concept (metrics over time)        │
        │ • Endpoint 3: Submissions (filing metadata)              │
        └──────┬─────────────────────────────────────────────────┬─┘
               │                                                 │
        ┌──────▼────────────────────────────────────────────┐   │
        │ PHASE 2: Transform & Load (Next)                 │   │
        │ • Transform data (types, timestamps)            │   │
        │ • Create dlt pipeline                           │   │
        │ • Load into DuckDB                              │   │
        │ • Create indexes                                │   │
        │ • Run SQL queries                               │   │
        └──────┬──────────────────────────────────────────┘   │
               │                                               │
        ┌──────▼───────────────────────────────────────────┐   │
        │ PHASE 3: RAG Integration (After)                │◄──┘
        │ • Query DuckDB from Claude                      │
        │ • Build context with financial data            │
        │ • Generate narratives                          │
        │ • Answer financial questions                   │
        └───────────────────────────────────────────────┘
```

---

## Phase 1: Extract - SEC XBRL API

### What You Get

Real, audit-verified financial data directly from SEC filings.

### Three Endpoints

#### Endpoint 1: Company Facts API
- **What:** All financial data ever filed by a company
- **Size:** 500+ financial concepts per company
- **Best for:** Bulk data ingestion, discovery
- **Example:** Get all revenue, income, assets, liabilities, etc. for Apple

```python
from sec_api_endpoint1 import get_company_facts
facts = get_company_facts("AAPL")  # Returns 444 concepts
```

#### Endpoint 2: Company Concept API
- **What:** Specific financial metric over time
- **Data:** Complete historical data (often back to 2009)
- **Best for:** Trend analysis, time series
- **Example:** Apple's revenue from 2010-2026

```python
from sec_api_endpoint2 import get_concept_over_time
revenues = get_concept_over_time("AAPL", concept="Revenues")  # 11 data points
```

#### Endpoint 3: Submissions API
- **What:** Filing metadata - dates, accession numbers, URLs
- **Best for:** Finding documents, building filing URLs
- **Example:** Links to actual 10-Q/10-K documents for text extraction

```python
from sec_api_endpoint3 import get_10q_filings_metadata
filings = get_10q_filings_metadata("AAPL", limit=5)
```

### Orchestrator: Unified Interface

```python
from sec_api_orchestrator import FinancialDataPipeline

pipeline = FinancialDataPipeline("AAPL")
data = pipeline.get_complete_data(
    metrics=["Revenues", "NetIncomeLoss"],
    facts_limit=3,
    filings_limit=5
)
# data["facts"] - all 444 concepts
# data["metrics"] - time series for 2 metrics
# data["filings"] - 5 recent 10-Q/10-K
```

### Phase 1 Files

```
learning/
├── sec_api_endpoint1.py              # Company Facts
├── sec_api_endpoint2.py              # Company Concept
├── sec_api_endpoint3.py              # Submissions
├── sec_api_orchestrator.py           # Combined interface
└── SEC_API_COMPLETE_GUIDE.md         # Full documentation
```

### Phase 1 Key Stats

| Company | Concepts | Revenues | Net Income | Assets |
|---------|----------|----------|-----------|--------|
| **MSFT** | 479 | 31 entries | 337 entries | Various |
| **AAPL** | 444 | 11 entries | Various | Various |
| **GOOGL** | 470 | 73 entries (70 with 10-Q/10-K) | Various | Various |

**Data Quality:** 100% official, audit-verified, standardized (XBRL tags)

---

## Phase 2: Transform & Load - DuckDB with dlt

### What Happens

Raw financial data → Structured database with SQL queries

**Two notebooks:**
- **PHASE_2_DLT_DUCKDB.ipynb** - Load XBRL numbers (financial metrics)
- **PHASE_2B_LOAD_FILING_TEXT.ipynb** - Load MD&A text (filing narratives)

### Architecture

```
Phase 1 Output (JSON/Python dicts)
    ↓
Transform Layer
├── Add load timestamps
├── Convert types
├── Handle duplicates
└── Validate data
    ↓
dlt Pipeline
├── Auto schema creation
├── Duplicate detection
├── Type inference
└── Incremental loading
    ↓
DuckDB Database
├── financial_metrics table
├── sec_filings_metadata table
└── Indexes for fast queries
```

### Tables Created

#### Table 1: `financial_metrics`

Time-series financial data.

```sql
SELECT * FROM sec_filings.financial_metrics LIMIT 3;
```

| ticker | concept | period_end | filing_date | form | value | load_timestamp |
|--------|---------|-----------|-----------|------|-------|----------------|
| MSFT | Revenues | 2010-12-31 | 2011-01-27 | 10-Q | 36148000000 | 2026-07-12T08:40:00 |
| MSFT | Revenues | 2010-09-30 | 2010-10-28 | 10-Q | 19953000000 | 2026-07-12T08:40:00 |
| AAPL | Revenues | 2018-09-29 | 2018-11-05 | 10-K | 265595000000 | 2026-07-12T08:40:00 |

#### Table 2: `sec_filings_metadata`

Filing metadata with document links.

```sql
SELECT * FROM sec_filings.sec_filings_metadata LIMIT 2;
```

| ticker | form | filing_date | period_end | accession_number | filing_url |
|--------|------|-----------|-----------|-----------------|-----------|
| MSFT | 10-Q | 2026-04-29 | 2026-03-31 | 0001193125-26-191507 | https://www.sec.gov/Archives/... |
| AAPL | 10-Q | 2026-05-01 | 2026-03-29 | 0000320193-26-000013 | https://www.sec.gov/Archives/... |

### Indexes Created

Fast queries on:
- `ticker` - Company lookups
- `concept` - Metric lookups
- `period_end` - Time series queries
- `form` - Form type filtering
- `(ticker, concept)` - Common composite queries

### Example Queries

#### Revenue Trend
```sql
SELECT period_end, value/1000000000 as revenue_billions
FROM sec_filings.financial_metrics
WHERE ticker = 'AAPL' AND concept = 'Revenues'
ORDER BY period_end DESC LIMIT 5;
```

#### Financial Snapshot
```sql
SELECT 
    ticker,
    MAX(CASE WHEN concept = 'Revenues' THEN value END) / 1000000000 as revenue_b,
    MAX(CASE WHEN concept = 'NetIncomeLoss' THEN value END) / 1000000000 as net_income_b,
    MAX(CASE WHEN concept = 'Assets' THEN value END) / 1000000000 as assets_b
FROM sec_filings.financial_metrics
GROUP BY ticker;
```

### Phase 2 Files

```
learning/
├── PHASE_2_DLT_DUCKDB.ipynb              # Load financial metrics
├── PHASE_2_GUIDE.md                      # Complete Phase 2 & 2B guide
├── fetch_filing_text.py                  # MD&A extraction module
├── PHASE_2B_LOAD_FILING_TEXT.ipynb       # Load filing text
└── financial_data_for_rag.json           # Exported data
```

### Phase 2B: Download & Load Filing Text

After Phase 2 loads the XBRL numbers, Phase 2B downloads actual SEC documents and extracts MD&A sections.

**Tables created:**
1. `financial_metrics` (Phase 2) - XBRL financial data
2. `sec_filings_metadata` (Phase 2) - Filing metadata  
3. `filing_text_chunks` (Phase 2B) - MD&A narrative text

**Phase 2B Pipeline:**
```
SEC Filing URL (from Phase 2)
    ↓
Download HTML from SEC EDGAR
    ↓
Extract MD&A section (Item 2 for 10-Q, Item 7 for 10-K)
    ↓
Chunk text (1000 chars, 100 char overlap)
    ↓
Load into DuckDB with dlt
    ↓
Create indexes for fast RAG search
```

### Phase 2 Key Benefits

1. **No manual SQL** - dlt creates tables automatically
2. **Type safety** - Automatic type conversion
3. **Fast queries** - Indexes + DuckDB performance
4. **Incremental loading** - Run multiple times safely
5. **Export ready** - Export to JSON for other tools

---

## Phase 3: RAG Integration (Planned)

### Concept

Query DuckDB from Claude AI to answer financial questions.

```
User Question
    ↓
Claude AI
    ├─ Generate SQL query
    ├─ Query DuckDB
    ├─ Get financial context
    └─ Generate response
    ↓
Answer with Financial Data
```

### Example Flow

**User:** "What was Apple's revenue trend over the last 3 years?"

**Claude:**
1. Query DuckDB: `SELECT period_end, value FROM financial_metrics WHERE ticker='AAPL' AND concept='Revenues' ORDER BY period_end DESC LIMIT 10`
2. Get data: Revenue values from 2024-2026
3. Analyze: Calculate growth rates
4. Generate: "Apple's revenue grew from $394B in 2024 to $402B in 2025, a 2% increase..."

### Phase 3 Files (To Be Created)

```
learning/
├── PHASE_3_RAG_PIPELINE.ipynb        # RAG integration
├── PHASE_3_GUIDE.md                  # Documentation
└── financial_rag_functions.py        # Helper functions
```

### Phase 3 Capabilities

- Query DuckDB from Claude
- Answer financial questions
- Generate earnings narratives
- Compare companies
- Trend analysis
- Ratio calculations

---

## Data Flow: End to End

### Step 1: Extract (Phase 1)

```python
# User specifies tickers and metrics
pipeline = FinancialDataPipeline("AAPL")
data = pipeline.get_complete_data()
# Returns:
# - 444 financial concepts
# - Revenues over time
# - Recent 10-Q/10-K filings with URLs
```

### Step 2: Transform (Phase 2)

```python
# Add types and timestamps
metrics_transformed = transform_metric_for_dlt(data)
# Now has proper types:
# - ticker: TEXT
# - value: INTEGER
# - period_end: DATE
# - load_timestamp: TIMESTAMP
```

### Step 3: Load (Phase 2)

```python
# dlt loads into DuckDB
pipeline.run(metrics_transformed, table_name="financial_metrics")
# Creates table with auto schema
# Detects and skips duplicates
# Creates indexes
```

### Step 4: Query (Phase 2)

```sql
-- SQL queries on financial data
SELECT ticker, concept, value 
FROM financial_metrics 
WHERE ticker = 'AAPL' AND concept = 'Revenues'
ORDER BY period_end DESC;
```

### Step 5: RAG (Phase 3)

```python
# Claude queries database and generates narratives
result = rag_query("What's Apple's profit margin trend?")
# RAG system:
# 1. Converts question to SQL
# 2. Queries DuckDB
# 3. Generates response with data
```

---

## Technology Stack

### Phase 1: Data Extraction
- **SEC XBRL API** - Official source
- **requests** - HTTP client
- **Python 3.11+** - Language

### Phase 2: Transform & Load
- **dlt** - ETL pipeline tool
- **DuckDB** - Embedded SQL database
- **Pandas** - Data manipulation
- **Python** - Script language

### Phase 3: RAG Integration
- **DuckDB** - Query execution
- **Claude API** - AI model
- **Python** - Integration

### Infrastructure
- **uv** - Python package manager
- **Jupyter** - Interactive notebooks
- **Git** - Version control

---

## Files Organization

```
learning/
├── COMPLETE_PIPELINE_ARCHITECTURE.md      ← You are here
├── PHASE_2_GUIDE.md                       ← Phase 2 tutorial
├── PHASE_2_DLT_DUCKDB.ipynb              ← Phase 2 notebook
│
├── SEC_API_COMPLETE_GUIDE.md              ← Phase 1 reference
├── sec_api_endpoint1.py                   ← Endpoint 1
├── sec_api_endpoint2.py                   ← Endpoint 2
├── sec_api_endpoint3.py                   ← Endpoint 3
├── sec_api_orchestrator.py                ← Combined
│
├── financial_data_for_rag.json            ← Phase 2 output
└── (Phase 3 files coming next)
```

---

## Getting Started

### Quick Start (Phase 1)

Fetch data from SEC API:

```bash
cd learning
python sec_api_orchestrator.py
```

### Run Full Pipeline (Phases 1 & 2)

Load data into DuckDB:

```bash
jupyter notebook PHASE_2_DLT_DUCKDB.ipynb
# Run all cells
```

### Access the Database

Query loaded data:

```python
import duckdb

conn = duckdb.connect('~/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb')

result = conn.execute("""
    SELECT ticker, COUNT(*) as records
    FROM sec_filings.financial_metrics
    GROUP BY ticker
""").df()

print(result)
```

---

## Key Advantages

✅ **Official Data** - Direct from SEC, audit-verified
✅ **Scalable** - Works for thousands of companies
✅ **Automatic** - No manual downloading each quarter
✅ **Standardized** - Same XBRL tags for all companies
✅ **Free** - No API keys or subscription costs
✅ **Local** - Everything runs on your machine
✅ **Queryable** - SQL access to all financial data
✅ **RAG-Ready** - Easy integration with Claude AI

---

## Data Quality

### ✅ What's Official
- Numbers come directly from SEC XBRL filings
- Audited by external auditors
- Immutable (never changes once filed)
- Complete filing history available

### ⚠️ Considerations
- Different filing schedules (10-Q quarterly, 10-K annual)
- Some metrics only available in 10-K (not quarterly)
- Historical data varies by company
- Duplicate handling: dlt automatically deduplicates

---

## What's Next

1. **Now (Phase 1):** ✅ Modules built and tested
2. **Next (Phase 2):** Run PHASE_2_DLT_DUCKDB.ipynb to load into DuckDB
3. **Then (Phase 3):** Build RAG pipeline to query with Claude

---

## Learnings & Best Practices

### From Phase 1
- SEC XBRL API is superior to scraped data
- Three endpoints serve different purposes
- Orchestrator pattern simplifies integration
- Standardization (XBRL) enables consistency

### From Phase 2
- dlt handles complexity (schema, duplicates, types)
- DuckDB perfect for local analytics
- Indexes critical even on small datasets
- JSON export bridges tools

### For Phase 3
- Keep queries simple (avoid CTEs)
- Filter at source (DuckDB can't optimize everything)
- Use indexes for common patterns
- Cache results for repeated queries

---

## Resources

- **SEC XBRL API:** https://www.sec.gov/cgi-bin/browse-edgar
- **dlt Documentation:** https://dlthub.com/docs
- **DuckDB:** https://duckdb.org/docs/
- **XBRL Tags:** https://www.sec.gov/cgi-bin/viewer

---

## Troubleshooting

### Phase 1 Issues
- See SEC_API_COMPLETE_GUIDE.md

### Phase 2 Issues
- See PHASE_2_GUIDE.md

### Integration Issues
- Check sys.path includes learning/
- Verify virtual environment is activated
- Confirm all dependencies installed (uv sync)

---

## Contact & Feedback

For questions or issues:
1. Check the phase-specific guides
2. Review example queries
3. Check GitHub issues
4. Examine the code (well-commented)

---

**Status:** Phase 1 ✅ Complete | Phase 2 ✅ Ready | Phase 3 📋 Planned

Ready to load data into DuckDB? → [PHASE_2_DLT_DUCKDB.ipynb](./PHASE_2_DLT_DUCKDB.ipynb)
