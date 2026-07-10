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

# 1.1 — Intro

## Theory
RAG exists because LLMs don't know your private/specific data, and retraining is not
the fix — retrieval is. This module builds a *fixed* RAG pipeline first, then makes
it *agentic* (the model decides its own search steps instead of you hardcoding
"always search, then always generate").

Your corpus for this whole module: SEC filings / XBRL facts, not the Zoomcamp FAQ.

## Your build
Ask the LLM a specific, dated financial question **with no retrieval at all**.
The goal is to *feel* the failure mode before you fix it — don't skip this.

```python
from openai import OpenAI
client = OpenAI()

# TODO: pick a specific, dated, checkable financial question, e.g.
# "What was Apple's gross margin in fiscal Q2 2024?"
question = "TODO: your question here"

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": question}],
)
print(response.choices[0].message.content)
```

## Reflect
Answer these in a markdown cell below (don't skip — this is the "why" for the
entire module):
1. Is the answer's number *correct*? How would you even check, right now, with
   no tools?
2. Did the model hedge, hallucinate a plausible-sounding number, or refuse?
3. What's missing that retrieval would give it?

_(your answer here)_
