# Earnings Intelligence Agent — Interactive Learning Guide

## Project Overview
Build an AI agent that answers financial questions about stocks using SEC filings, starting from raw LLM calls → retrieval (RAG) → autonomous agents.

**Duration:** 13 lessons (Week 1, Module 1)  
**Corpus:** SEC EDGAR filings (10-Q, 10-K, 8-K)  
**Tech Stack:** OpenAI API, Python, minsearch (keyword search), LLM agents

---

## Quick Start Checklist

### 1. Environment Setup (do this first!)
```bash
# Create .env file in project root
cp learning/week\ 1/.env.example .env  # if it exists
# Otherwise create it manually:
echo "OPENAI_API_KEY=your-key-here" > .env

# Install dependencies
pip install -r learning/week\ 1/requirements.txt

# Verify setup
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Ready' if os.getenv('OPENAI_API_KEY') else '✗ Missing API key')"
```

---

## Learning Path (13 Lessons)

| Lesson | File | Duration | What You Build | Key Concepts |
|--------|------|----------|--------|---|
| **Setup** | `00_setup_overview.md` | 5 min | Verify Python + API key | Repo structure, .env |
| **1.1** | `01_intro.md` | 15 min | Cold LLM call (no retrieval) | Hallucination, why RAG matters |
| **1.2** | `02_environment.md` | 10 min | Hello-world OpenAI call | API basics, model selection |
| **1.3-1.4** | `03_rag_and_dataset_design.md` | 30 min | Manual RAG, schema design | Context injection, data structure |
| **1.5** | `04_search.md` | 20 min | Keyword search index | minsearch, chunking strategy |
| **1.6** | `05_prompt_building.md` | 20 min | Financial domain prompts | Prompt engineering, system prompts |
| **1.7** | `06_llm_interface.md` | 15 min | Swappable LLM client | Temperature tuning, abstraction |
| **1.8** | `07_rag_helper_class.md` | 25 min | Reusable `FinancialRAG` class | OOP, composition, interface design |
| **1.9-1.10** | `08_ingestion_and_next_steps.md` | 20 min | Load real 10-Q filings | Data pipeline, parsing, scaling |
| **1.11** | `09_agents_intro.md` | 10 min | Agent concepts (reading only) | Agentic RAG theory |
| **1.12** | `10_rag_revision.md` | 20 min | Consolidate into one file | Refactoring, code organization |
| **1.13** | `11_function_calling.md` | 45 min | Full agentic loop | Function calling, ReAct pattern |
| **Checkpoint** | `12_module1_checkpoint.md` | 30 min | Answer 3 reflection questions | Synthesis, mastery check |

**Total Time:** ~4-5 hours of hands-on building

---

## How We'll Work Together

### Per Lesson:
1. **I explain** the learning goal and key concepts (1-2 sentences)
2. **You read** the notebook to understand theory
3. **We code** together — I help you implement, explain tricky parts, debug
4. **You reflect** — capture what you learned (your insights matter)
5. **Move to next** lesson once checkpoint passes

### Red Flags (Pause Here):
- ❌ You don't understand *why* we're doing something — ask me to explain differently
- ❌ Code works but you don't know why — we backtrack and diagram it
- ❌ Test fails — we debug together, don't skip to the next lesson
- ❌ Stuck > 10 min on syntax — I'll live-code it

### Your Job:
- **Ask questions early** — confusion compounds
- **Type the code** (don't copy-paste) — muscle memory + catch bugs
- **Write one-sentence reflections** after each lesson (will use these at checkpoint)
- **Test as we go** — run cells, print outputs, verify assumptions

---

## File Structure (What We're Building)

```
.
├── learning/week 1/          # ← Lesson notebooks (start here)
│   ├── 00_setup_overview.md
│   ├── 01_intro.md
│   ├── 02_environment.md
│   ├── ... (11 more)
│   ├── 12_module1_checkpoint.md
│   └── requirements.txt
├── .env                       # ← You create this (add to .gitignore)
├── notebooks/ (optional)      # ← Where we may save .ipynb versions
└── LEARNING_GUIDE.md         # ← You're reading this
```

---

## Vocabulary (Bookmark This)

- **RAG:** Retrieval-Augmented Generation — fetch relevant docs, pass to LLM as context
- **Agentic RAG:** LLM decides *when* and *what* to retrieve (vs. always retrieving)
- **SEC EDGAR:** Electronic Data Gathering database — public company filings
- **10-Q:** Quarterly financial report (company-filed)
- **Hallucination:** LLM inventing plausible-sounding false facts
- **minsearch:** Lightweight keyword search library (no ML needed)
- **Prompt Engineering:** Crafting system + user prompts for better LLM output
- **Function Calling:** LLM calls your code as a tool (enables agents)
- **ReAct:** Reasoning + Acting loop — LLM thinks, then takes action, then observes

---

## Getting Help

**If you're stuck:**
1. Re-read the theory section of the current lesson
2. Check the "Reflect" questions — they hint at what went wrong
3. Try printing intermediate values (`print(search_results)`, etc.)
4. Ask me — I'll explain, live-code, or pair debug

**If you want to go deeper:**
- Lesson 9 (agents theory) has recommended reading — great for conceptual depth
- After Module 1, the Zoomcamp has Modules 2-4 (search, deployment, etc.)
- OpenAI docs: https://platform.openai.com/docs/ (reference as needed)

---

## Success Criteria

✓ Lessons 1-12 all run without errors  
✓ Checkpoint questions answered with your own words  
✓ You can explain RAG and agents to a friend  
✓ You have a working financial Q&A system by the end  

---

## Ready?

👉 **Next step:** Let's run `00_setup_overview.md` and verify your .env is set up. I'll walk you through it.

Any questions before we start?
