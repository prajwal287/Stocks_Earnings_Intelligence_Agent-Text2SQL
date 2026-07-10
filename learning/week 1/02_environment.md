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

# 1.2 — Environment

## Theory
Course uses GitHub Codespaces. You already have `uv`/venv + your own repo — this
lesson is just a checklist match, not new tooling to learn.

## Your build
One throwaway script: call the LLM, print a response. This is your
"hello world" checkpoint before Module 1 gets real.

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Reply with exactly: pipeline is live"}],
)
print(response.choices[0].message.content)
```

## Checkpoint
- [ ] `agents/` folder exists in your actual repo (not just this notebooks folder)
- [ ] API key loads from `.env`, not hardcoded
- [ ] The call above returns cleanly, no auth errors

Once all three are checked, move to `03_rag_and_dataset_design.md`.
