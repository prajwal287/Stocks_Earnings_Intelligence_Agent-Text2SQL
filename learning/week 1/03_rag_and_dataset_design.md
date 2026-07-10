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

# 1.3 — RAG  &  1.4 — Dataset

## Theory (1.3)
You can't just paste the question to the LLM — it has no access to your specific
knowledge base. The course builds a bare `def llm(prompt)` black box first, shows
it fails without context, then manually pastes context into the prompt to prove
the fix works — no search index yet, just proving the *mechanism*.

## Your build (1.3)
Write a bare `call_llm` function. Then manually paste a real chunk of 10-Q text
into the prompt alongside a question and confirm the answer improves.

```python
from openai import OpenAI

client = OpenAI()

def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    """Bare LLM call — no retrieval, no tools. The black box from 1.3."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

```python
# TODO: paste a real MD&A excerpt from an actual 10-Q you pull from SEC EDGAR.
# https://www.sec.gov/cgi-bin/browse-edgar -> pick a company -> latest 10-Q -> MD&A section
mdna_excerpt = """
TODO: paste 1-2 paragraphs of real MD&A text here
"""

question = "Why did operating margin change, according to this text?"

prompt_with_context = f"""Answer the question using ONLY the context below.

CONTEXT:
{mdna_excerpt}

QUESTION: {question}
"""

print(call_llm(prompt_with_context))
```

**Compare**: run the *same* question with no context (call `call_llm(question)`
directly) and diff the two answers. That difference is the entire value
proposition of RAG in one cell.

---

## Theory (1.4)
A good knowledge base has structured fields that support both search and
filtering. Filtering by a keyword field (e.g. `course == 'llm-zoomcamp'`) means
you don't mix irrelevant knowledge bases into search results.

## Your build (1.4)
This is design work, not code yet — write out both schemas you'll actually need.
You have two different data shapes, not one:

```python
# agents/schemas.py (design only, no logic yet)

# Shape A: unstructured filing text, chunked for keyword/semantic search
# ticker: str        -- keyword field, exact-match filterable (e.g. "AAPL")
# form_type: str      -- keyword field (e.g. "10-Q", "10-K")
# filed_date: str     -- keyword field, ISO date, filterable/sortable
# fiscal_period: str  -- keyword field (e.g. "2024-Q2")
# text: str           -- text field, tokenized + ranked (the actual MD&A chunk)
# source_url: str     -- keyword field, not searched, just carried through for citation

# Shape B: structured XBRL facts, exact lookups, not "search" at all
# ticker: str
# concept: str        -- e.g. "GrossProfit", "OperatingIncomeLoss"
# value: float
# unit: str           -- e.g. "USD"
# fiscal_period: str
```

## Reflect
Why are `ticker` and `fiscal_period` keyword fields and not text fields? What
would break in search ranking if you made them text fields instead?

_(your answer here)_
