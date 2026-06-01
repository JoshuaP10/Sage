"""
Central configuration for Sage.

Everything tunable lives here so you can experiment without hunting
through the codebase. Most values can be overridden with environment
variables, which is handy for trying different models.
"""
import os

# --- Models (served by your local Ollama instance) ---------------------------
# Generation model: produces the final answer.
#   Default is llama3.1:8b -> runs on ~6-8GB and is a safe all-rounder.
#   If you have the RAM, qwen3:8b (or larger) is the stronger 2026 pick:
#       export SAGE_GEN_MODEL=qwen3:8b
GEN_MODEL = os.getenv("SAGE_GEN_MODEL", "llama3.1:8b")

# Embedding model: turns text into vectors for semantic search.
#   nomic-embed-text is the local-RAG standard. Supports task prefixes
#   (search_document / search_query) which we use below for better recall.
EMBED_MODEL = os.getenv("SAGE_EMBED_MODEL", "nomic-embed-text")

# --- Paths -------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("SAGE_DATA_DIR", os.path.join(BASE_DIR, "data"))
CHROMA_DIR = os.getenv("SAGE_CHROMA_DIR", os.path.join(BASE_DIR, "chroma_db"))
COLLECTION_NAME = "sage"

# --- Retrieval / chunking ----------------------------------------------------
CHUNK_SIZE = int(os.getenv("SAGE_CHUNK_SIZE", "1000"))     # chars per chunk
CHUNK_OVERLAP = int(os.getenv("SAGE_CHUNK_OVERLAP", "150"))  # overlap between chunks
TOP_K = int(os.getenv("SAGE_TOP_K", "5"))                  # passages fed to the model

# nomic-embed-text works best when you tell it whether text is a
# stored document or a search query. These prefixes do that.
DOC_PREFIX = "search_document: "
QUERY_PREFIX = "search_query: "
