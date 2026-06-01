"""
The core RAG engine: retrieve relevant passages, then generate an
answer that is grounded in (and cited from) those passages only.

This module has no UI code so it can be reused by both the CLI
(chat.py) and the web app (app.py).
"""
import ollama
import chromadb

import config

_client = chromadb.PersistentClient(path=config.CHROMA_DIR)


def _collection():
    return _client.get_or_create_collection(name=config.COLLECTION_NAME)


def list_authors() -> list[str]:
    """Return the distinct authors present in the store."""
    col = _collection()
    got = col.get(include=["metadatas"])
    authors = {m.get("author", "unknown") for m in got["metadatas"]}
    return sorted(authors)


def embed_query(text: str) -> list[float]:
    resp = ollama.embeddings(model=config.EMBED_MODEL,
                             prompt=config.QUERY_PREFIX + text)
    return resp["embedding"]


def retrieve(question: str, author: str | None = None, k: int = config.TOP_K):
    """
    Return the top-k passages most relevant to the question.

    If `author` is given, only that author's material is searched --
    this is what powers "ask Buffett specifically".
    """
    col = _collection()
    where = {"author": author} if author else None
    res = col.query(
        query_embeddings=[embed_query(question)],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )
    passages = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        passages.append({"text": doc, "meta": meta, "distance": dist})
    return passages


def _build_prompt(question: str, passages: list[dict]) -> list[dict]:
    context_blocks = []
    for i, p in enumerate(passages, start=1):
        m = p["meta"]
        context_blocks.append(
            f"[{i}] (author: {m['author']}, source: {m['source']})\n{p['text']}"
        )
    context = "\n\n".join(context_blocks)

    system = (
        "You answer questions about the philosophies and beliefs of famous "
        "investors and thinkers, using ONLY the passages provided. "
        "Rules:\n"
        "1. Base every claim strictly on the passages. Do not use outside "
        "knowledge.\n"
        "2. Cite the passage number(s) you used, like [1] or [2][3].\n"
        "3. Attribute views to the author named in the passage.\n"
        "4. If the passages do not contain the answer, say so plainly "
        "instead of guessing.\n"
        "5. Be concise and quote sparingly; explain ideas in your own words."
    )
    user = f"Passages:\n\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def answer(question: str, author: str | None = None, k: int = config.TOP_K):
    """
    Full RAG step: retrieve -> generate.

    Returns (answer_text, passages) so the UI can also show the sources.
    """
    passages = retrieve(question, author=author, k=k)
    if not passages:
        return ("I don't have any material to answer from. "
                "Have you run `python ingest.py`?"), []
    messages = _build_prompt(question, passages)
    resp = ollama.chat(model=config.GEN_MODEL, messages=messages)
    return resp["message"]["content"], passages
