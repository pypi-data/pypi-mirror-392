from __future__ import annotations

"""
Simple command-line interface for RAGdb Core.

I mainly use this for quick experiments on my own machine.
"""

import argparse

from .core import RAGdb


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="RAGdb Core CLI")
    parser.add_argument("--db", default="RAGdb.ragdb", help="Path to database file")

    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest a file or folder")
    p_ingest.add_argument("path", help="Path to file or directory")

    p_search = sub.add_parser("search", help="Search the database")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--top-k", type=int, default=5)

    p_list = sub.add_parser("list", help="List documents")
    p_list.add_argument("--limit", type=int, default=20)

    p_delete = sub.add_parser("delete", help="Delete a stored document by path")
    p_delete.add_argument("path", help="Path used during ingestion")

    args = parser.parse_args(argv)
    db = RAGdb(args.db)

    if args.command == "ingest":
        db.ingest(args.path)
    elif args.command == "search":
        hits = db.search(args.query, top_k=args.top_k)
        for path, score, media_type, preview in hits:
            print(f"{score:8.4f}  {media_type:6s}  {path}")
            if preview:
                print("   ", preview[:120])
    elif args.command == "list":
        for path, media_type, updated_at in db.list_documents(limit=args.limit):
            print(f"{updated_at}  {media_type:6s}  {path}")
    elif args.command == "delete":
        db.delete_file(args.path)


if __name__ == "__main__":  # pragma: no cover
    main()
