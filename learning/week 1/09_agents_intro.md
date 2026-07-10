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

# 1.11 — Agents Intro

## Theory
The core shift of this entire module: instead of *you* deciding "always
search, then always generate," the LLM decides **when and what** to search.
This is the conceptual leap from "RAG pipeline" to "agent."

Everything before this lesson (1.3–1.10) was a fixed pipeline — you called
search, then you called the LLM, in a hardcoded order, every time. Nothing the
model did changed that order. Lesson 1.13 (Function Calling) is where that
control actually transfers to the model.

## No code this lesson — read it twice
This is the theoretical foundation for your later table-selector / pipeline
work. When you get there, you'll be asked to explain how it's an instance of
this exact pattern — so don't skim it.

## Reflect
In your own words, not the doc's:
1. What decision does a *fixed pipeline* make for the model, that an *agent*
   instead lets the model make for itself?
2. Is `FinancialRAG.answer()` from 1.8 a fixed pipeline or an agent, as it
   stands right now? Why?

_(your answer here — you'll be asked to defend this again in the Module 1
checkpoint, so make it a real answer, not a placeholder)_
