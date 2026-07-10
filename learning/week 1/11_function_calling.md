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

# 1.13 — Function Calling

This is the big one. Everything else in Module 1 was setup for this lesson.

## Theory
The LLM doesn't literally execute code — it outputs **structured JSON**
describing which function to call with what arguments. Your code then executes
that function and feeds the *result* back to the model as a new message. The
model then produces its final answer using that result. That loop — model
decides → your code executes → result goes back in → model answers — is the
actual mechanism behind every "agentic" behavior in this whole capstone. It's
the direct ancestor of your later `table_selector.py` and the 5-stage
pipeline: same mechanism, applied to picking database tables instead of
picking documents to search.

## Your build
A minimal function-calling loop with exactly one tool: `search_filings(ticker, query)`.

```python
from openai import OpenAI
import json

client = OpenAI()

# --- Step 1: the actual Python function the model can "call" ---
def search_filings(ticker: str, query: str) -> str:
    """This is the real function. The model never runs this — your code does,
    after the model asks for it."""
    # TODO: wire this to your real `index` from 10_rag_revision.md
    results = index.search(query=query, filter_dict={"ticker": ticker}, num_results=3)
    return json.dumps([{"ticker": r["ticker"], "text": r["text"]} for r in results])


# --- Step 2: describe that function to the model in its expected schema ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_filings",
            "description": "Search a company's SEC filings for relevant text given a ticker and a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker, e.g. AAPL"},
                    "query": {"type": "string", "description": "What to search for in the filing text"},
                },
                "required": ["ticker", "query"],
            },
        },
    }
]
```

```python
def agent_answer(question: str) -> str:
    messages = [{"role": "user", "content": question}]

    # Round 1: let the model decide whether to call the tool
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=messages,
        tools=tools,
    )
    msg = response.choices[0].message

    # TODO: inspect msg.tool_calls -- print it raw first so you SEE the JSON
    # the model actually returns, before writing the branching logic
    print("Raw tool_calls:", msg.tool_calls)

    if not msg.tool_calls:
        # Model decided it didn't need the tool at all
        return msg.content

    # Round 2: execute the tool call the model asked for, feed result back
    messages.append(msg)
    for tool_call in msg.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = search_filings(**args)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

    final = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=messages,
        tools=tools,
    )
    return final.choices[0].message.content
```

```python
# TODO: ask something that clearly needs a lookup vs. something that doesn't,
# and confirm the model's tool-call decision differs between the two.
print(agent_answer("TODO: a question needing your indexed filing data"))
```

```python
print(agent_answer("What is 2 + 2?"))  # sanity check: model should NOT call the tool for this
```

## Checkpoint (this feeds directly into 12_module1_checkpoint.md)
1. Paste the raw `tool_calls` JSON from your print statement above.
2. Confirm: did the "What is 2 + 2?" question correctly skip the tool call?
   If it called the tool anyway, that's worth noting — models don't always
   decide correctly, and that's a real failure mode you'll need to handle
   later in the capstone.
