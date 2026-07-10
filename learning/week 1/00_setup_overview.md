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

# Week 1 Setup — Earnings Intelligence Agent

Before touching Module 1 content, get the repo skeleton and env sanity-checked.
This mirrors lesson 1.2 but as a pre-flight check so every later notebook "just works".

```python
import sys
print("Python:", sys.version)
```

## What you need
- A `.env` file (copy `.env.example`, fill in `OPENAI_API_KEY`)
- `pip install -r ../requirements.txt`

```python
from dotenv import load_dotenv
import os

load_dotenv()
key_present = bool(os.getenv("OPENAI_API_KEY"))
print("OPENAI_API_KEY loaded:", key_present)
```

**Checkpoint**: if `key_present` is `False`, stop here and fix your `.env` before
moving to `01_intro.md`. Everything downstream assumes this works.
