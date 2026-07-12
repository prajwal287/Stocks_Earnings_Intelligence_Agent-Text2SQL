# Phase 2: Load SEC Data into DuckDB with dlt

## Overview

**Phase 2** takes real financial data from SEC XBRL API (Phase 1) and loads it into DuckDB using **dlt** (data load tool).

### What Happens:

```
SEC API Endpoints (Phase 1)
    ↓
[Real Financial Data]
    ↓
Transform & Type Hints
    ↓
dlt Pipeline
    ↓
DuckDB Tables ← YOU ARE HERE
    ↓
SQL Queries + RAG (Phase 3)
```

---

## Key Concepts

### dlt (Data Load Tool)

**What it does:**
- Automatically creates tables from Python data
- Handles schema inference and type conversion
- Manages duplicates automatically
- Tracks load history
- Perfect for DuckDB

**Why dlt?**
- No manual SQL CREATE TABLE statements
- Automatic duplicate detection
- Schema management built-in
- Incremental loading support
- Type safety

### DuckDB

**Why DuckDB?**
- File-based (no database server needed)
- SQL queries on local data
- Fast analytics
- Pandas integration
- Perfect for local development

---

## What the Notebook Does

### Part 1: Fetch Data from SEC API
- Uses the SEC API modules from Phase 1
- Fetches 6 key financial metrics (Revenues, NetIncome, Operating Income, Assets, Liabilities, Equity)
- Gets filing metadata for all companies

### Part 2: Transform Data
- Adds load timestamps
- Converts to proper types
- Ensures numeric fields are integers
- Prepares for dlt loading

### Part 3: Create dlt Pipeline
- Creates a pipeline named `financial_data_pipeline`
- Destination: DuckDB
- Dataset: `sec_filings`

### Part 4: Load Data into DuckDB
- Creates table: `financial_metrics` (time series data)
- Creates table: `sec_filings_metadata` (filing dates and URLs)

### Part 5: Verify Data
- Connects to DuckDB
- Shows table structures
- Displays sample data

### Part 6: Create Indexes
- Index on ticker (company lookups)
- Index on concept (metric lookups)
- Index on period_end (time series queries)
- Composite index on (ticker, concept)

### Part 7: Example Queries
- Apple's revenue trend
- Net income comparison across companies
- Total assets by company
- Filing timeline
- Financial health snapshot

### Part 8: Export for RAG
- Exports recent financial data to JSON
- Saved as `financial_data_for_rag.json`
- Ready for Phase 3 integration

---

## Running the Notebook

### Option 1: Run in Jupyter (Recommended)

```bash
# Navigate to project directory
cd /Users/prajwalchambenandeeshappa/Github_Repos/Stocks_Earnings_Intelligence_Agent-Text2SQL

# Activate virtual environment
source .venv/bin/activate

# Start Jupyter
jupyter notebook

# Navigate to: learning/PHASE_2_DLT_DUCKDB.ipynb
```

### Option 2: Run Individual Cells

You can run the notebook cell by cell, or copy specific cells to a Python script.

### Option 3: Convert to Python Script

```bash
jupyter nbconvert --to script learning/PHASE_2_DLT_DUCKDB.ipynb
python learning/PHASE_2_DLT_DUCKDB.py
```

---

## Expected Output

When you run the notebook, you should see:

```
✅ Dependencies loaded
   dlt version: 1.28.2
   DuckDB available

🚀 Phase 2: Loading SEC Data into DuckDB

📊 Companies: MSFT, AAPL, GOOGL
📈 Metrics: Revenues, NetIncomeLoss, OperatingIncomeLoss...

Fetching data from SEC XBRL API...

[Progress output...]

✅ Data collection complete!
   Total metric records: 180
   Total filing records: 15

✅ dlt pipeline created
   Pipeline name: financial_data_pipeline
   Destination: DuckDB
   Dataset: sec_filings
   Database file: ~/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb

📊 Loading financial metrics into DuckDB...
✅ Metrics loaded!
   Records loaded: 180
   Table: financial_metrics

📄 Loading SEC filings metadata into DuckDB...
✅ Filings loaded!
   Records loaded: 15
   Table: sec_filings_metadata

📂 Database location: /Users/.../.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb

📊 Tables in database:
   - dlt_loads
   - financial_metrics
   - sec_filings_metadata

[Query Results...]

✅ PHASE 2 SUMMARY
📊 Database Statistics:
   Metrics: 180 records, 3 companies, 6 concepts
   Filings: 15 records, 3 companies, 2 forms

✅ WHAT WE ACCOMPLISHED:
1. ✅ Fetched real SEC data from 3 endpoints
2. ✅ Transformed data for dlt
3. ✅ Loaded into DuckDB using dlt pipeline
4. ✅ Created optimized indexes
5. ✅ Ran example queries
6. ✅ Exported data for RAG pipeline
```

---

## Database Location

The DuckDB database is created at:
```
~/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb
```

Expand `~` to your home directory. On your system:
```
/Users/prajwalchambenandeeshappa/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb
```

### Connect to Database Manually

```python
import duckdb

# Connect to the database
conn = duckdb.connect('/Users/prajwalchambenandeeshappa/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb')

# Run queries
result = conn.execute("""
    SELECT ticker, concept, COUNT(*) as count
    FROM sec_filings.financial_metrics
    GROUP BY ticker, concept
    ORDER BY ticker
""").df()

print(result)
```

---

## Tables Created

### Table 1: `financial_metrics`

Contains all financial metrics over time.

**Columns:**
- `ticker` (TEXT) - Stock ticker
- `concept` (TEXT) - Financial concept (Revenues, NetIncomeLoss, etc.)
- `period_end` (DATE) - End date of the reporting period
- `filing_date` (DATE) - Date the filing was submitted to SEC
- `form` (TEXT) - Filing type (10-Q, 10-K, etc.)
- `value` (INTEGER) - Numeric value in USD
- `load_timestamp` (TIMESTAMP) - When data was loaded

**Example Query:**
```sql
SELECT 
    ticker,
    period_end,
    value / 1000000000 as revenue_billions
FROM sec_filings.financial_metrics
WHERE ticker = 'AAPL' AND concept = 'Revenues'
ORDER BY period_end DESC
LIMIT 5;
```

### Table 2: `sec_filings_metadata`

Contains filing metadata and document links.

**Columns:**
- `ticker` (TEXT) - Stock ticker
- `form` (TEXT) - Filing type (10-Q, 10-K)
- `filing_date` (DATE) - When filed
- `period_end` (DATE) - End of reporting period
- `accession_number` (TEXT) - SEC's unique filing ID
- `filing_url` (TEXT) - URL to the filing document
- `load_timestamp` (TIMESTAMP) - When data was loaded

**Example Query:**
```sql
SELECT 
    ticker,
    form,
    filing_date,
    accession_number
FROM sec_filings.sec_filings_metadata
WHERE ticker = 'MSFT'
ORDER BY filing_date DESC
LIMIT 3;
```

---

## Common Queries

### Query 1: Revenue Over Time for One Company

```sql
SELECT 
    period_end,
    value / 1000000000 as revenue_billions
FROM sec_filings.financial_metrics
WHERE ticker = 'AAPL' AND concept = 'Revenues'
ORDER BY period_end DESC
LIMIT 10;
```

### Query 2: Compare Companies (Most Recent)

```sql
SELECT 
    ticker,
    concept,
    value / 1000000000 as value_billions,
    period_end
FROM sec_filings.financial_metrics
WHERE concept = 'Revenues'
  AND period_end >= DATE_SUB(CURRENT_DATE, INTERVAL 365 DAY)
ORDER BY period_end DESC, ticker;
```

### Query 3: Financial Ratios

```sql
SELECT 
    ticker,
    MAX(period_end) as period,
    MAX(CASE WHEN concept = 'NetIncomeLoss' THEN value END) * 100.0 /
    MAX(CASE WHEN concept = 'Revenues' THEN value END) as profit_margin_pct,
    MAX(CASE WHEN concept = 'Assets' THEN value END) / 1000000000 as assets_billions
FROM sec_filings.financial_metrics
WHERE concept IN ('NetIncomeLoss', 'Revenues', 'Assets')
GROUP BY ticker
ORDER BY ticker;
```

### Query 4: Check What's Loaded

```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT ticker) as companies,
    COUNT(DISTINCT concept) as metrics,
    COUNT(DISTINCT form) as form_types,
    MIN(period_end) as earliest_data,
    MAX(period_end) as latest_data
FROM sec_filings.financial_metrics;
```

---

## Indexes Created

The notebook creates the following indexes for fast queries:

```
idx_metrics_ticker          - Fast company lookups
idx_metrics_concept         - Fast metric lookups
idx_metrics_period          - Fast time series queries
idx_metrics_form            - Fast filtering by form type
idx_metrics_ticker_concept  - Fast company + metric queries
```

---

## Data Flow Summary

### Input (Phase 1 - SEC API)
```
SEC XBRL API
├── Endpoint 1: Company Facts (all financial data)
├── Endpoint 2: Company Concept (specific metrics over time)
└── Endpoint 3: Submissions (filing metadata)
```

### Processing (Phase 2 - This Notebook)
```
Extract from SEC
    ↓
Transform (add types, timestamps)
    ↓
dlt Pipeline
    ↓
DuckDB Tables
    ↓
Create Indexes
    ↓
Verify + Test Queries
```

### Output (Phase 2 - Ready for Phase 3)
```
DuckDB Database
├── financial_metrics (180 records)
├── sec_filings_metadata (15 records)
└── Indexed for fast queries

JSON Export
└── financial_data_for_rag.json (for RAG pipeline)
```

---

## Troubleshooting

### Issue: Module not found (sec_api_*)

**Solution:** Make sure you're running from the correct directory and the path is in sys.path.

```python
import sys
sys.path.insert(0, '/Users/prajwalchambenandeeshappa/Github_Repos/Stocks_Earnings_Intelligence_Agent-Text2SQL/learning')
```

### Issue: dlt or DuckDB not installed

**Solution:** Install dependencies using uv:

```bash
cd /Users/prajwalchambenandeeshappa/Github_Repos/Stocks_Earnings_Intelligence_Agent-Text2SQL
source .venv/bin/activate
uv sync
```

### Issue: Database file not found

**Solution:** The database is created automatically when the notebook runs. Check the path:

```bash
ls ~/.dlt/pipelines/financial_data_pipeline/
```

### Issue: Duplicate key error when running twice

**Solution:** dlt handles duplicates automatically with `write_disposition="append"`. You can safely re-run the notebook.

To start fresh:

```bash
rm -rf ~/.dlt/pipelines/financial_data_pipeline/
```

---

## Next Steps: Phase 3

Once Phase 2 is complete:

1. ✅ Financial data is in DuckDB
2. ✅ Can run SQL queries
3. ✅ Data exported as JSON

**Next:** Phase 3 - RAG Pipeline Integration

See `PHASE_3_RAG_PIPELINE.ipynb` to:
- Connect to DuckDB from Claude AI
- Query financial data in prompts
- Generate narratives based on financials
- Answer questions about earnings and trends

---

## Key Learnings from Phase 2

1. **dlt is powerful** - Automatic schema management, type inference, duplicate detection
2. **DuckDB is fast** - Local file database with SQL queries
3. **Indexes matter** - Even small datasets benefit from proper indexing
4. **Combine all endpoints** - Orchestrator class makes it easy to get all data types
5. **Export early** - JSON export lets you use data in other tools (RAG, notebooks, etc.)

---

## Files Related to Phase 2

```
learning/
├── PHASE_2_DLT_DUCKDB.ipynb          ← Main notebook (THIS)
├── PHASE_2_GUIDE.md                  ← This guide
├── sec_api_orchestrator.py           ← Data fetching
├── sec_api_endpoint1.py              ← All facts
├── sec_api_endpoint2.py              ← Specific metrics
├── sec_api_endpoint3.py              ← Filing metadata
├── SEC_API_COMPLETE_GUIDE.md         ← Phase 1 reference
└── financial_data_for_rag.json       ← Output (exported data)
```

---

**Ready to run Phase 2?** Open `PHASE_2_DLT_DUCKDB.ipynb` in Jupyter and execute the cells! 🚀
