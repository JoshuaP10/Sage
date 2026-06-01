"""
Ingest documents into the vector store.

Run this once (and again whenever you add new material):

    python ingest.py

It walks the data/ directory, reads every .txt, .md, and .pdf file,
splits each into overlapping chunks, embeds them with the local
embedding model, and stores them in a persistent Chroma database.

Each file should live in a subfolder named after the author, e.g.

    data/
      warren_buffett/
        1977_letter.txt
        1984_letter.txt
      ray_dalio/
        principles.txt

The subfolder name becomes the "author" metadata, which lets you
later ask "what would Buffett say?" and filter to just his material.
"""
import os
import re
import sys
import hashlib

import ollama
import chromadb

import config


def read_pdf(path: str) -> str:
    """Extract text from a PDF. Requires pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("  ! pypdf not installed; skipping PDF. Run: pip install pypdf")
        return ""
    text_parts = []
    reader = PdfReader(path)
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def read_file(path: str) -> str:
    """Read a supported file into plain text."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return read_pdf(path)
    if ext in (".txt", ".md"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """
    Split text into overlapping chunks.

    Snaps chunk boundaries to natural breaks (paragraph > sentence >
    line > space) when possible so we don't slice mid-sentence, which
    keeps each chunk semantically coherent and improves retrieval.
    """
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start, n = 0, len(text)
    while start < n:
        end = min(start + size, n)
        if end < n:
            window = text[start:end]
            for sep in ("\n\n", ". ", "\n", " "):
                idx = window.rfind(sep)
                if idx != -1 and idx > size * 0.5:
                    end = start + idx + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1)
    return chunks


def embed(text: str) -> list[float]:
    """Get an embedding vector for a stored document chunk."""
    resp = ollama.embeddings(model=config.EMBED_MODEL,
                             prompt=config.DOC_PREFIX + text)
    return resp["embedding"]


def discover_documents(data_dir: str):
    """Yield (author, filepath) for every supported file under data_dir."""
    for root, _dirs, files in os.walk(data_dir):
        author = os.path.basename(root) if root != data_dir else "unknown"
        for name in files:
            if name.startswith("."):
                continue
            if os.path.splitext(name)[1].lower() in (".txt", ".md", ".pdf"):
                yield author, os.path.join(root, name)


def main() -> None:
    if not os.path.isdir(config.DATA_DIR):
        sys.exit(f"Data directory not found: {config.DATA_DIR}")

    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    # Start fresh each run so re-ingesting is idempotent.
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(name=config.COLLECTION_NAME)

    total_chunks = 0
    documents = list(discover_documents(config.DATA_DIR))
    if not documents:
        sys.exit(
            "No documents found. Add .txt/.md/.pdf files under data/<author>/ "
            "and run again. See data/README.md for where to find source material."
        )

    for author, path in documents:
        raw = read_file(path)
        if not raw.strip():
            print(f"  - {path}: empty or unreadable, skipping")
            continue
        chunks = chunk_text(raw, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        if not chunks:
            continue

        ids, embeddings, docs, metas = [], [], [], []
        source = os.path.relpath(path, config.DATA_DIR)
        for i, chunk in enumerate(chunks):
            uid = hashlib.sha1(f"{source}:{i}".encode()).hexdigest()
            ids.append(uid)
            embeddings.append(embed(chunk))
            docs.append(chunk)
            metas.append({"author": author, "source": source, "chunk": i})

        collection.add(ids=ids, embeddings=embeddings,
                       documents=docs, metadatas=metas)
        total_chunks += len(chunks)
        print(f"  + {author:20s} {source:40s} {len(chunks):4d} chunks")

    print(f"\nDone. Stored {total_chunks} chunks from {len(documents)} files.")
    print(f"Vector store: {config.CHROMA_DIR}")


if __name__ == "__main__":
    main()
