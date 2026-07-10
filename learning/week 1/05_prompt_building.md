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

# 1.6 — Building the Prompt

## Theory
Prompt template = fixed instruction block + injected context + injected question.
Be explicit about what the LLM should and shouldn't do — e.g. "answer only using
the CONTEXT, don't use outside knowledge." This discipline is the direct
precursor to your later table-selector prompt (same rigor, simpler task here).

## Your build
Write the financial-domain prompt template you'll reuse for the rest of this
module.

```python
PROMPT_TEMPLATE = """You are a financial data expert. Answer the QUESTION using
ONLY the information in CONTEXT below. If the context does not contain enough
information to answer, say "I don't have enough information in the provided
filings to answer that" — do not use outside knowledge or guess a number.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

def build_prompt(question: str, search_results: list[dict]) -> str:
    # TODO: join the `text` field of each search result into one context block
    context = "\n\n".join(r["text"] for r in search_results)
    return PROMPT_TEMPLATE.format(context=context, question=question)
```

```python
# Wire it to last lesson's index + this module's call_llm
# TODO: import/reuse `index` from 04_search.md and `call_llm` from 03_...md
# (for now, copy the function bodies in if running notebooks standalone)

question = "TODO: a question your indexed chunks can actually answer"
results = index.search(query=question, num_results=3)
prompt = build_prompt(question, results)
print(prompt)
```

## Reflect
Try asking a question your indexed chunks *cannot* answer. Does the model
correctly say "I don't have enough information," or does it quietly fall back
to outside knowledge? If it leaks outside knowledge, tighten the instruction
block and re-test.

_(your answer here)_
