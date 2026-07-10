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

# 1.8 — RAG Helper (class-based refactor)

## Theory
Wrap the RAG flow into a reusable class where the search index is swappable
without touching the RAG logic itself — separation of concerns between
retrieval and generation. This is the seed of a class you'll extend for the
rest of the capstone (V2 swaps the index for pgvector; the class shape doesn't
change).

## Your build
Refactor 1.3–1.7 into `FinancialRAG`.

```python
from openai import OpenAI

client = OpenAI()

PROMPT_TEMPLATE = """You are a financial data expert. Answer the QUESTION using
ONLY the information in CONTEXT below. If the context does not contain enough
information to answer, say so plainly — do not guess.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


class FinancialRAG:
    def __init__(self, index, model: str = "gpt-4o-mini", temperature: float = 0.0):
        # `index` must implement .search(query, num_results) -> list[dict with "text"]
        self.index = index
        self.model = model
        self.temperature = temperature

    def _build_prompt(self, question: str, results: list[dict]) -> str:
        context = "\n\n".join(r["text"] for r in results)
        return PROMPT_TEMPLATE.format(context=context, question=question)

    def _call_llm(self, prompt: str) -> str:
        response = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def answer(self, question: str, num_results: int = 3) -> str:
        # TODO: call self.index.search(...), then build prompt, then call LLM
        results = self.index.search(query=question, num_results=num_results)
        prompt = self._build_prompt(question, results)
        return self._call_llm(prompt)
```

```python
# TODO: reuse the `index` you built in 04_search.md
rag = FinancialRAG(index=index)
print(rag.answer("TODO: a question your indexed chunks can answer"))
```

## Checkpoint
Swap `index` for a *different* minsearch index (different documents, same
schema) and confirm `FinancialRAG` still works with zero changes to the class
itself. That's the separation-of-concerns test — if you had to touch the class
to swap data, the abstraction is leaking.
