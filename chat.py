"""
A simple terminal chat loop.

    python chat.py                # consult everyone
    python chat.py --author ray_dalio   # consult one thinker

Type your question and press enter. Type 'authors' to list available
thinkers, or 'quit' to exit.
"""
import argparse

import rag
import config


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the great investors.")
    parser.add_argument("--author", default=None,
                        help="restrict to one author (folder name under data/)")
    parser.add_argument("-k", type=int, default=config.TOP_K,
                        help="number of passages to retrieve")
    args = parser.parse_args()

    authors = rag.list_authors()
    if not authors:
        print("No documents indexed yet. Run `python ingest.py` first.")
        return

    print("Sage — grounded answers from the great investors")
    print(f"Model: {config.GEN_MODEL}   Available: {', '.join(authors)}")
    if args.author:
        print(f"Consulting: {args.author}")
    print("Type 'authors', 'quit', or ask a question.\n")

    while True:
        try:
            q = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            continue
        if q.lower() in ("quit", "exit"):
            break
        if q.lower() == "authors":
            print("  " + ", ".join(authors))
            continue

        text, passages = rag.answer(q, author=args.author, k=args.k)
        print(f"\nsage > {text}\n")
        if passages:
            print("  sources:")
            for i, p in enumerate(passages, start=1):
                m = p["meta"]
                print(f"    [{i}] {m['author']} — {m['source']} (chunk {m['chunk']})")
            print()


if __name__ == "__main__":
    main()
