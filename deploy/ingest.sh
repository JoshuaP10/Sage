#!/usr/bin/env bash
#
# Build (or rebuild) the Chroma vector store from the PDFs/text files
# under data/<author>/. Run this AFTER you've copied your source files
# onto the VM, and again whenever you add new material.
#
#     bash deploy/ingest.sh
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

export SAGE_GEN_MODEL="${SAGE_GEN_MODEL:-qwen3:8b}"
export SAGE_EMBED_MODEL="${SAGE_EMBED_MODEL:-nomic-embed-text}"

./.venv/bin/python ingest.py
