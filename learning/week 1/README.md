# Week 1 — Module 1: Agentic RAG (Earnings Intelligence Agent)

Companion notebooks for LLM Zoomcamp's 01-agentic-rag (13 lessons), rebuilt against
your own corpus: SEC EDGAR filings instead of the Zoomcamp FAQ bot.

## How to use these files
Each `.md` file is a **jupytext markdown notebook** — plain text, but structured so
jupytext can open/run it as a real `.ipynb`.

```bash
pip install -r requirements.txt
jupytext --to notebook notebooks/01_intro.md   # generates 01_intro.ipynb
jupyter lab
```
Or in VS Code: install the "Jupytext" extension, then just open the `.md` file directly
and click "Run Cell" — no conversion step needed.

## Order
| File | Lesson(s) | What you build |
|---|---|---|
| 00_setup_overview.md | — | repo + env sanity check |
| 01_intro.md | 1.1 | prove cold LLM answers are unreliable |
| 02_environment.md | 1.2 | hello-world LLM call |
| 03_rag_and_dataset_design.md | 1.3, 1.4 | `call_llm`, manual context injection, schema design |
| 04_search.md | 1.5 | minsearch keyword index over filing chunks |
| 05_prompt_building.md | 1.6 | financial-domain prompt template |
| 06_llm_interface.md | 1.7 | swappable LLM client, temperature experiment |
| 07_rag_helper_class.md | 1.8 | `FinancialRAG` class |
| 08_ingestion_and_next_steps.md | 1.9, 1.10 | loader for real 10-Q text, scaling reflection |
| 09_agents_intro.md | 1.11 | reading/reflection only — no code |
| 10_rag_revision.md | 1.12 | consolidate into one clean file |
| 11_function_calling.md | 1.13 | the big one — real function-calling loop |
| 12_module1_checkpoint.md | — | the 3 checkpoint questions, answered by you |

Rule: theory identical to the course, target different (your corpus, your schema).
Don't skip ahead — 1.8's class gets reused and extended in 1.12 and 1.13.
