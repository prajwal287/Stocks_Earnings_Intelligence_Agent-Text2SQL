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

# Module 1 Checkpoint

Straight from the source doc — answer all three before moving to Module 2
(Vector Search). Don't paraphrase the questions away; answer the specific
thing each one asks.

## 1. Walk through your function-calling loop (from 1.13)
What JSON did the LLM actually return when it decided to call the tool? What
did your code do with it before sending anything back to the model?

_(paste the raw `tool_calls` output here, then explain the two-round exchange
in your own words)_

## 2. Is 1.13 truly agentic, or a fixed pipeline with one extra step?
Compare `FinancialRAG` (1.8/1.12) against the fixed-pipeline-vs-agent
distinction from 1.11. Defend your answer — don't just assert it.

Prompts to push on your own answer:
- Does the model in 1.13 ever *choose not to* call the tool? You tested this
  with the "2 + 2" question — what happened?
- If the model always calls the same tool in the same way regardless of the
  question, is that meaningfully different from you hardcoding the call?
- What would make it *more* agentic — e.g. multiple tools, multi-step tool
  chaining, the model deciding to search again after seeing the first result?

_(your answer here)_

## 3. Temperature experiment (from 1.7)
Paste both output pairs (temperature=0 x2, temperature=0.9 x2). Did it behave
as expected — near-identical at 0, divergent at 0.9?

_(paste here)_

---

Once this is filled in, Module 1 / Week 1 is done. Module 2 (Vector Search)
picks up where 1.10's reflection left off — the minsearch index gets replaced
with something that scales past hand-copied chunks.
