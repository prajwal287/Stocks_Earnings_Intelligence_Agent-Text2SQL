# Phase 2: Complete Data Loading - XBRL Numbers + Filing Text

## Overview

**Single notebook for complete Phase 2 setup:**
- **Phase 2A:** Load XBRL financial metrics (Revenues, Net Income, Assets, etc.)
- **Phase 2B:** Download & extract SEC filing text (MD&A sections)

Both load into the same DuckDB database, creating 3 tables:
1. `financial_metrics` - Structured XBRL data
2. `sec_filings_metadata` - Filing dates and URLs
3. `filing_text_chunks` - MD&A narrative text

---

## Quick Start

### Run One Notebook (5 steps, ~7 minutes)

```bash
cd /Users/prajwalchambenandeeshappa/Github_Repos/Stocks_Earnings_Intelligence_Agent-Text2SQL
source .venv/bin/activate
jupyter notebook learning/PHASE_2_COMPLETE_DLT_DUCKDB.ipynb
```

**What it does:**
1. Connect to SEC API (Phase 1 results)
2. Load financial metrics (~2 min)
3. Load filing metadata
4. Download & extract MD&A (~5 min for 3 filings)
5. Create indexes & verify data

---

## Architecture

### Phase 2A: Load XBRL Metrics

```
SEC XBRL API (Phase 1)
    ↓
Fetch 6 metrics × 3 companies × 10 periods
    ↓
Transform (add types, timestamps)
    ↓
dlt Pipeline
    ↓
DuckDB: financial_metrics table
DuckDB: sec_filings_metadata table
```

### Phase 2B: Download & Extract Filing Text

```
sec_filings_metadata table (URLs from Phase 2A)
    ↓
Download HTML from SEC EDGAR
    ↓
Extract MD&A section (Item 2 for 10-Q, Item 7 for 10-K)
    ↓
Chunk text (1000 chars, 100 char overlap)
    ↓
dlt Pipeline
    ↓
DuckDB: filing_text_chunks table
```

---

## Database Schema

### Table 1: financial_metrics (Phase 2A)

```sql
SELECT * FROM sec_filings.financial_metrics LIMIT 1;
```

```
ticker            | MSFT
concept           | Revenues
period_end        | 2010-12-31
filing_date       | 2011-01-27
form              | 10-Q
value             | 36148000000
load_timestamp    | 2026-07-12T08:40:00
```

**Indexes:** (ticker), (concept), (period_end), (ticker, concept)

### Table 2: sec_filings_metadata (Phase 2A)

```sql
SELECT * FROM sec_filings.sec_filings_metadata LIMIT 1;
```

```
ticker            | AAPL
form              | 10-Q
filing_date       | 2026-05-01
period_end        | 2026-03-29
accession_number  | 0000320193-26-000013
filing_url        | https://www.sec.gov/Archives/...
load_timestamp    | 2026-07-12T08:40:00
```

### Table 3: filing_text_chunks (Phase 2B)

```sql
SELECT * FROM sec_filings.filing_text_chunks LIMIT 1;
```

```
ticker            | AAPL
form              | 10-Q
filing_date       | 2026-05-01
period_end        | 2026-03-29
accession_number  | 0000320193-26-000013
section           | MD&A
chunk_id          | 1
text              | "Apple Inc. reports quarterly results..."
text_length       | 987
extracted_at      | 2026-07-12T08:40:00
```

**Indexes:** (ticker), (filing_date), (ticker, filing_date)

---

## What the Notebook Does

### Part 1: Setup & Imports
- Import dlt, DuckDB, SEC API modules
- Setup logging

### Part 2A: Phase 2A - Load XBRL Metrics
- Fetch 6 metrics for 3 companies
- Transform for dlt
- Load financial_metrics table
- Load sec_filings_metadata table

### Part 3: Phase 2B - Download Filing Text
- Get filing URLs from Phase 2A
- Download 10-Q/10-K documents from SEC
- Extract MD&A sections
- Chunk text for RAG
- Load filing_text_chunks table

### Part 4: Verify Data
- Check all tables exist
- Show record counts
- Display summary statistics

### Part 5: Create Indexes
- Add indexes on ticker, concept, period_end
- Create composite indexes for fast queries

### Part 6: Example Queries
- Revenue trends
- Financial health snapshots

### Part 7: Complete!
- Summary of what was loaded
- Ready for Module 1 RAG

---

## Detailed Usage

### Run All Cells

Execute the notebook cells in order. Each section has clear output showing progress.

```
✅ All imports successful
🚀 PHASE 2A: Loading XBRL Financial Metrics
   Fetching from SEC API...
📊 MSFT...
📊 AAPL...
📊 GOOGL...
✅ Phase 2A: Data fetched
   Metrics: 180 records
   Filings: 15 records

✅ Data transformed

📝 Loading metrics...
   ✅ 180 metric records loaded
📝 Loading filing metadata...
   ✅ 15 filing records loaded

✅ Phase 2A complete!

🚀 PHASE 2B: Downloading & Extracting Filing Text
Processing 3 filings...

[1/3] MSFT 10-Q 2026-04-29
   ✅ 45 chunks
[2/3] AAPL 10-Q 2026-05-01
   ✅ 38 chunks
[3/3] GOOGL 10-Q 2026-04-30
   ✅ 42 chunks

✅ Extraction complete: 3 successful, 0 failed

📝 Prepared 125 chunks for loading...
✅ 125 chunks loaded into filing_text_chunks table

DATABASE SUMMARY
===============
✅ financial_metrics: 180 records
✅ sec_filings_metadata: 15 records
✅ filing_text_chunks: 125 records

✅ PHASE 2 COMPLETE!
```

---

## Database Location

```
~/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb
```

On your system:
```
/Users/prajwalchambenandeeshappa/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb
```

### Connect Manually

```python
import duckdb

conn = duckdb.connect('/Users/prajwalchambenandeeshappa/.dlt/pipelines/financial_data_pipeline/sec_filings.duckdb')

# Query metrics
result = conn.execute("""
    SELECT ticker, COUNT(*) as records
    FROM sec_filings.financial_metrics
    GROUP BY ticker
""").df()

print(result)
```

---

## Common Queries

### Query 1: Revenue Trend

```sql
SELECT 
    ticker,
    period_end,
    value / 1000000000 as revenue_billions
FROM sec_filings.financial_metrics
WHERE concept = 'Revenues'
  AND ticker = 'AAPL'
ORDER BY period_end DESC
LIMIT 5;
```

### Query 2: Financial Snapshot

```sql
SELECT 
    ticker,
    MAX(CASE WHEN concept = 'Revenues' THEN value END) / 1000000000 as revenue_b,
    MAX(CASE WHEN concept = 'NetIncomeLoss' THEN value END) / 1000000000 as net_income_b,
    ROUND(
        MAX(CASE WHEN concept = 'NetIncomeLoss' THEN value END) * 100.0 
        / MAX(CASE WHEN concept = 'Revenues' THEN value END)
    , 1) as profit_margin_pct
FROM sec_filings.financial_metrics
WHERE concept IN ('Revenues', 'NetIncomeLoss')
GROUP BY ticker
ORDER BY ticker;
```

### Query 3: Get Filing Text for RAG Context

```sql
-- Get all MD&A chunks for Apple, concatenated
SELECT STRING_AGG(text, ' ')
FROM sec_filings.filing_text_chunks
WHERE ticker = 'AAPL' 
  AND filing_date = (
      SELECT MAX(filing_date) 
      FROM sec_filings.filing_text_chunks 
      WHERE ticker = 'AAPL'
  )
ORDER BY chunk_id;
```

### Query 4: Search Filing Text

```sql
-- Find chunks mentioning specific topics
SELECT ticker, chunk_id, SUBSTR(text, 1, 200) as preview
FROM sec_filings.filing_text_chunks
WHERE text ILIKE '%liquidity%'
  AND ticker = 'MSFT'
LIMIT 5;
```

---

## Files

### Main Notebook
- **PHASE_2_COMPLETE_DLT_DUCKDB.ipynb** - Single notebook with Phase 2A + 2B (all in one place)

### Supporting Modules
- **sec_api_orchestrator.py** - Unified SEC API access (Phase 1)
- **fetch_filing_text.py** - MD&A extraction for Phase 2B

### Documentation
- **PHASE_2_GUIDE.md** - This file
- **COMPLETE_PIPELINE_ARCHITECTURE.md** - Full system overview

---

## Indexes Created

For fast queries:

```
idx_metrics_ticker              - Company lookups
idx_metrics_concept             - Metric lookups
idx_metrics_period              - Time series queries
idx_metrics_ticker_concept      - Combined company + metric
idx_chunks_ticker               - Filing text by company
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sec_api_orchestrator'"

**Solution:** Make sure sys.path is set correctly in notebook:
```python
sys.path.insert(0, '/Users/prajwalchambenandeeshappa/Github_Repos/Stocks_Earnings_Intelligence_Agent-Text2SQL/learning')
```

### Issue: "Failed to download filing"

**Solution:** SEC filing URLs may be temporary. The notebook logs which failed - you can manually adjust URLs if needed.

### Issue: DuckDB file not found

**Solution:** Run the notebook fully. dlt creates the database automatically. Check path:
```bash
ls -la ~/.dlt/pipelines/financial_data_pipeline/
```

---

## Performance

| Phase | Task | Time | Output |
|-------|------|------|--------|
| **2A** | Fetch XBRL metrics | ~2 min | 180 records, 15 filings |
| **2B** | Download & extract text | ~5 min | 125+ text chunks |
| **Indexes** | Create indexes | <1 min | 5 indexes |
| **Total** | Complete Phase 2 | ~7 min | Ready for Module 1 |

---

## Next: Module 1 - Agentic RAG

Once Phase 2 completes, you have:
✅ Structured financial data (XBRL numbers)
✅ Narrative business context (MD&A text)
✅ Indexed for fast search
✅ Ready for RAG queries

See: `MODULE_1_AGENTIC_RAG.ipynb` (coming next)

---

## Key Learnings

1. **dlt handles complexity** - Schema management, duplicates, types
2. **DuckDB is fast** - SQL queries on local data
3. **Two data types matter** - Numbers (XBRL) + narratives (MD&A)
4. **Indexes critical** - Even small datasets benefit from proper indexing
5. **Single source of truth** - Combined notebook easier to maintain
