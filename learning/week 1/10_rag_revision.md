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

# 1.12 — RAG Revision

## Theory
Consolidate everything from 1.3–1.11 into one clean, working implementation
before adding agentic behavior on top of it. Refactor checkpoint, not new
functionality — resist the urge to add features here.

## Your build
Pull `call_llm`, `PROMPT_TEMPLATE`, `FinancialRAG`, and your index-building
logic into a single clean cell (this becomes `agents/financial_rag.py` in your
real repo later).

```python
from openai import OpenAI
from minsearch import Index

client = OpenAI()

PROMPT_TEMPLATE = """You are a financial data expert. Answer the QUESTION using
ONLY the information in CONTEXT below. If the context does not contain enough
information to answer, say so plainly — do not guess.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def build_index(documents: list[dict]) -> Index:
    index = Index(
        text_fields=["text"],
        keyword_fields=["ticker", "form_type", "fiscal_period"],
    )
    index.fit(documents)
    return index


class FinancialRAG:
    def __init__(self, index: Index, model: str = "gpt-4o-mini", temperature: float = 0.0):
        self.index = index
        self.model = model
        self.temperature = temperature

    def _build_prompt(self, question: str, results: list[dict]) -> str:
        context = "\n\n".join(r["text"] for r in results)
        return PROMPT_TEMPLATE.format(context=context, question=question)

    def answer(self, question: str, num_results: int = 3) -> str:
        results = self.index.search(query=question, num_results=num_results)
        prompt = self._build_prompt(question, results)
        response = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
```

```python
# TODO: end-to-end smoke test with your real filing chunks from 1.9
documents = [...]  # reuse RAW_FILINGS from 08_ingestion_and_next_steps.md
index = build_index(documents)
rag = FinancialRAG(index=index)
print(rag.answer("TODO: your test question"))
```

## Checkpoint
- [ ] Everything runs from a fresh kernel restart, top to bottom, no hidden state
- [ ] No leftover scratch variables from earlier notebooks required

This file is your save-point before 1.13 makes it agentic.
