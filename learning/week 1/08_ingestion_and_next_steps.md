---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

# 1.9 — Data Ingestion  &  1.10 — RAG Next Steps

## Theory (1.9)
Moving from hardcoded examples to loading a real dataset programmatically. Full
pipeline automation (dlt, EDGAR's XBRL API) comes later in the capstone — for
now this is the bridge: prove you can load real text into the index, not just
fake chunks.

## Your build (1.9)
Hand-copy 2-3 real MD&A sections from actual 10-Q filings on SEC EDGAR and load
them through your Week 1.5 index via a small loader function.

```python
# TODO: pull real text from https://www.sec.gov/cgi-bin/browse-edgar
# Pick 2-3 companies, grab their latest 10-Q, copy the MD&A section text.

RAW_FILINGS = [
    {
        "ticker": "TODO",
        "form_type": "10-Q",
        "filed_date": "TODO",
        "fiscal_period": "TODO",
        "text": "TODO: real MD&A text, at least a full paragraph",
        "source_url": "TODO",
    },
    # 1-2 more from a *different* company
]

def load_filings(index, filings: list[dict]) -> None:
    index.append(filings)  # or index.fit() again if minsearch requires refit — check its API
```

```python
# TODO: load into your existing index from 04_search.md and re-run a query
load_filings(index, RAW_FILINGS)
results = index.search(query="TODO: something these real chunks can answer", num_results=3)
for r in results:
    print(r["ticker"], "-", r["text"][:100])
```

---

## Theory (1.10)
Bridge lesson before the module goes agentic: what breaks at scale, what's
still manual. No new code — this is a reflection checkpoint.

## Reflect (this is the actual deliverable for 1.10 — write it out)
If you scaled `FinancialRAG` from 3 hand-copied chunks to 50 companies' full
filing history, what breaks first?

- _(e.g. minsearch's in-memory index doesn't scale — what replaces it?)_
- _(e.g. hand-copying text doesn't scale — what replaces it, and when do you
  build it? hint: this is your dlt + EDGAR XBRL API work, coming later)_
- _(e.g. one flat text field per chunk — does chunking strategy need to change
  once MD&A sections get long?)_

_(your answer here — a short paragraph is genuinely enough, per the source doc)_
