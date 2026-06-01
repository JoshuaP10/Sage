# 📜 Sage — Ask the Great Investors

A fully local, private RAG (Retrieval-Augmented Generation) system that answers
questions about the philosophies of famous investors and thinkers — Warren
Buffett, Ray Dalio, Charlie Munger, and anyone else you add — grounded **only**
in their actual writing, with citations.

No cloud APIs. No keys. No per-token cost. Everything runs on your machine.

> *"How does Buffett think about market downturns?"*
> → an answer drawn strictly from his shareholder letters, citing the passages it used.

---

## How it works

```
                ┌─────────────┐
  documents ──▶ │   ingest    │  chunk → embed → store
  (data/)       └─────────────┘        │
                                       ▼
                              ┌──────────────────┐
                              │  Chroma vector   │
                              │     database     │
                              └──────────────────┘
                                       ▲
  question ──▶ embed query ──▶ semantic search (top-k)
                                       │
                                       ▼
                       relevant passages + question
                                       │
                                       ▼
                              ┌──────────────────┐
                              │  local LLM       │  grounded, cited answer
                              │  (via Ollama)    │
                              └──────────────────┘
```

1. **Ingest** — your documents are split into overlapping chunks, each turned
   into a vector by an embedding model, and stored in a local Chroma database.
2. **Retrieve** — your question is embedded and used to find the most
   semantically similar passages.
3. **Generate** — those passages are handed to a local LLM with strict
   instructions to answer *only* from them and cite its sources.

The model never answers from its own training data — only from what the real
authors actually wrote. That's the whole point: grounded, attributable answers.

---

## Setup

### 1. Install Ollama and pull the models

Install Ollama from [ollama.com](https://ollama.com), then:

```bash
ollama pull nomic-embed-text   # embeddings (small, ~275MB)
ollama pull llama3.1:8b        # generation (runs on ~6-8GB)
```

Have more RAM/VRAM? `qwen3:8b` (or larger) is the stronger 2026 pick — just set
`export SAGE_GEN_MODEL=qwen3:8b` before running.

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Add source material

Drop text files into `data/<author>/`. See [`data/README.md`](data/README.md)
for where to find freely-available, shareable material (e.g. Berkshire
Hathaway's public shareholder letters).

### 4. Build the index

```bash
python ingest.py
```

### 5. Ask away

```bash
# Terminal:
python chat.py
python chat.py --author warren_buffett

# Web UI (nicer for demos):
streamlit run app.py
```

---

## Configuration

All settings live in `config.py` and can be overridden with environment
variables: `SAGE_GEN_MODEL`, `SAGE_EMBED_MODEL`, `SAGE_TOP_K`,
`SAGE_CHUNK_SIZE`, `SAGE_CHUNK_OVERLAP`, `SAGE_DATA_DIR`, `SAGE_CHROMA_DIR`.

---

## What this project demonstrates

For a portfolio or résumé, this shows you can:

- Build an end-to-end **RAG pipeline** (chunking, embeddings, vector search,
  grounded generation) — currently one of the most in-demand LLM skills.
- Work with **local model infrastructure** via Ollama and an OpenAI-style
  workflow, with an eye to privacy, cost, and offline operation.
- Use a **vector database** (Chroma) with metadata filtering.
- Apply real retrieval craft: paragraph-aware chunking with overlap, task-typed
  embeddings (`search_document` / `search_query`), and citation-enforcing prompts.
- Ship a clean, documented, runnable codebase with both a CLI and a web UI.

## Ideas to take it further

- **Compare thinkers:** retrieve from two authors and ask the model to contrast
  their views ("Buffett vs. Dalio on diversification").
- **Re-ranking:** add a cross-encoder re-ranker to sharpen retrieval.
- **Streaming:** stream the model's response token-by-token in the UI.
- **Evaluation:** add a small test set and measure retrieval/answer quality.
- **Conversation memory:** feed prior turns back in for follow-up questions.

---

*Built with Ollama, Chroma, and Streamlit. All answers are grounded in
user-provided source documents.*
