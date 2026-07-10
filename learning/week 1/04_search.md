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

# 1.5 — Search

## Theory
Keyword search fundamentals via `minsearch` (the course's lightweight stand-in
for Elasticsearch): **text fields** get tokenized and ranked (e.g. filing text);
**keyword fields** are for exact match/filter, not ranking (e.g. `ticker`).
Boosting lets you weight one field's relevance higher than another.

This is one place worth using `minsearch` as-is — it's a teaching tool, not a
competing architecture choice for your real V2 (pgvector later).

```python
# pip install minsearch  (already in requirements.txt)
from minsearch import Index

# TODO: build 3-5 fake-but-realistic filing chunks using the Shape A schema
# from 03_rag_and_dataset_design.md
documents = [
    {
        "ticker": "TODO",
        "form_type": "10-Q",
        "filed_date": "2024-08-01",
        "fiscal_period": "2024-Q2",
        "text": "TODO: a chunk of MD&A-style text",
        "source_url": "TODO",
    },
    # add 2-4 more, at least 2 different tickers
]

index = Index(
    text_fields=["text"],
    keyword_fields=["ticker", "form_type", "fiscal_period"],
)
index.fit(documents)
```

```python
# TODO: query it, filtered to one ticker
results = index.search(
    query="gross margin change",
    filter_dict={"ticker": "TODO"},
    boost_dict={"text": 1.0},
    num_results=3,
)
for r in results:
    print(r["ticker"], "-", r["text"][:80])
```

## Checkpoint
- [ ] Filtering to a single ticker actually excludes the other companies' chunks
- [ ] The ranking changes sensibly when you change the query wording

If both hold, you've replicated 1.5 against your own corpus. Next: 1.6.
