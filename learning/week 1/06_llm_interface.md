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

# 1.7 — LLM

## Theory
The LLM should be an interchangeable component behind one interface — swap
models/providers without touching the rest of your pipeline. `temperature`
controls output randomness: `temperature=0` gives deterministic, reproducible
outputs (critical for anything SQL-adjacent, which is exactly where this
capstone is headed).

## Your build
Extend `call_llm` from 1.3 to accept `model` and `temperature` explicitly.

```python
from openai import OpenAI

client = OpenAI()

def call_llm(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.0) -> str:
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

## The experiment (do this — it's checkpoint material)

```python
question = "What was Apple's total revenue in its most recent fiscal year? Answer in one sentence."

print("--- temperature=0, run 1 ---")
print(call_llm(question, temperature=0.0))
print("--- temperature=0, run 2 ---")
print(call_llm(question, temperature=0.0))
```

```python
print("--- temperature=0.9, run 1 ---")
print(call_llm(question, temperature=0.9))
print("--- temperature=0.9, run 2 ---")
print(call_llm(question, temperature=0.9))
```

## Checkpoint (save this — Module 1 checkpoint asks for it verbatim)
- [ ] The two `temperature=0` outputs are near-identical
- [ ] The two `temperature=0.9` outputs differ noticeably in wording (possibly
      in the actual number stated, since neither run has real retrieval yet)

Paste both output pairs into `12_module1_checkpoint.md` when you get there.
