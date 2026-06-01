"""
A polished web UI for Sage. This is the piece that makes the project
demo well in interviews and screenshots nicely for a portfolio.

    streamlit run app.py
"""
import streamlit as st

import rag
import config

st.set_page_config(page_title="Sage", page_icon="📜", layout="centered")

st.title("📜 Sage")
st.caption("Ask the great investors — answers grounded in their own words, with sources.")

# --- Sidebar: who to consult --------------------------------------------------
try:
    authors = rag.list_authors()
except Exception:
    authors = []

with st.sidebar:
    st.header("Consult")
    if not authors:
        st.warning("No material indexed. Run `python ingest.py` first.")
        st.stop()
    choice = st.selectbox("Whose thinking?", ["Everyone"] + authors)
    k = st.slider("Passages to retrieve", 1, 10, config.TOP_K)
    st.divider()
    st.caption(f"Generation model: `{config.GEN_MODEL}`")
    st.caption(f"Embedding model: `{config.EMBED_MODEL}`")

author = None if choice == "Everyone" else choice

# --- Chat state ---------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        if turn.get("passages"):
            with st.expander("Sources"):
                for i, p in enumerate(turn["passages"], start=1):
                    m = p["meta"]
                    st.markdown(f"**[{i}] {m['author']} — {m['source']}**")
                    st.caption(p["text"][:400] + ("…" if len(p["text"]) > 400 else ""))

# --- Input --------------------------------------------------------------------
if prompt := st.chat_input("e.g. How does Buffett think about market downturns?"):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consulting the sources…"):
            text, passages = rag.answer(prompt, author=author, k=k)
        st.markdown(text)
        if passages:
            with st.expander("Sources"):
                for i, p in enumerate(passages, start=1):
                    m = p["meta"]
                    st.markdown(f"**[{i}] {m['author']} — {m['source']}**")
                    st.caption(p["text"][:400] + ("…" if len(p["text"]) > 400 else ""))

    st.session_state.history.append(
        {"role": "assistant", "content": text, "passages": passages}
    )
