# Project Context: AI-Powered Restaurant Recommendation System

This document captures the full context of the Zomato-inspired restaurant recommendation problem. Use it as the single source of truth for scope, workflow, and deliverables when implementing or extending the project.

---

## Overview

Build an **AI-powered restaurant recommendation service** inspired by Zomato. The system combines **structured restaurant data** with a **Large Language Model (LLM)** to produce personalized, human-like suggestions based on user preferences.

---

## Objective

Design and implement an application that:

1. Accepts user preferences (location, budget, cuisine, ratings, and more).
2. Uses a real-world restaurant dataset.
3. Leverages an LLM to generate personalized, natural-language recommendations.
4. Displays clear, useful results to the user.

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:
  - **Dataset URL:** https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
- Extract relevant fields, including but not limited to:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating
  - Other fields as needed for filtering and display

### 2. User Input

Collect user preferences:

| Preference | Examples / Notes |
|------------|------------------|
| **Location** | Delhi, Bangalore, etc. |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese, etc. |
| **Minimum rating** | Numeric or threshold filter |
| **Additional preferences** | family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare restaurant records that match user input.
- Pass structured, filtered results into an LLM prompt.
- Design prompts so the LLM can **reason** and **rank** options effectively.

### 4. Recommendation Engine (LLM)

Use the LLM to:

- **Rank** restaurants against user criteria.
- **Explain** why each recommendation fits the user.
- **Optionally** summarize the set of choices.

### 5. Output Display

Present top recommendations in a user-friendly format. Each result should include:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation (why it was recommended)

---

## Data Source

| Item | Value |
|------|--------|
| Provider | Hugging Face |
| Dataset | `ManikaSaini/zomato-restaurant-recommendation` |
| Link | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |

---

## Architecture Summary

```
User preferences → Filter dataset → Structured candidates → LLM (rank + explain) → Formatted UI output
```

**Layers:**

1. **Data layer** — ingest and preprocess Hugging Face Zomato data.
2. **Input layer** — collect and validate user preferences.
3. **Integration layer** — filter data and build LLM prompts.
4. **LLM layer** — ranking, explanations, optional summary.
5. **Presentation layer** — display top picks with structured fields + narrative explanation.

---

## Key Requirements Checklist

- [x] Hugging Face Zomato dataset loaded and preprocessed
- [x] User can specify location, budget, cuisine, min rating, and extra preferences
- [x] Filtering logic narrows candidates before LLM call
- [x] Prompt design supports reasoning and ranking
- [x] LLM returns ranked recommendations with explanations
- [x] UI (or equivalent) shows name, cuisine, rating, cost, and AI explanation

---

## Out of Scope (unless extended later)

The problem statement does not specify:

- Specific tech stack (Python, web framework, LLM provider)
- Authentication or user accounts
- Deployment target
- Exact number of recommendations to return

Implementers should choose reasonable defaults and document them in the README or project config.

---

## Source

Derived from `docs/Problem statement.txt` — AI-Powered Restaurant Recommendation System (Zomato Use Case).
