"""Command-line entry points for the ``files-unsplash`` package."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .config import (
    MissingEnvError,
    create_opensearch_client,
    create_pg_connection,
    load_opensearch_config,
    load_postgres_config,
)
from .indexer import (
    build_index,
    create_index_with_synonyms,
    generate_documents,
    load_synonyms_from_file,
)
from .search import search_images
from .wordnet import generate_wordnet_synonyms_file

DEFAULT_INDEX_NAME = "unsplash_photos"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Utilities for Unsplash-style OpenSearch indexing and querying.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Index command
    index_parser = subparsers.add_parser(
        "index",
        help="Build and populate the OpenSearch index from Postgres data.",
    )
    index_parser.add_argument(
        "--index-name",
        default=DEFAULT_INDEX_NAME,
        help="Name of the OpenSearch index to create.",
    )
    index_parser.add_argument(
        "--synonyms-path",
        required=True,
        help="Path to a synonyms file.",
    )
    index_parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Chunk size for OpenSearch bulk indexing.",
    )
    index_parser.add_argument(
        "--shards",
        type=int,
        default=3,
        help="Number of primary shards for the index.",
    )
    index_parser.add_argument(
        "--replicas",
        type=int,
        default=1,
        help="Number of replica shards for the index.",
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search the OpenSearch index for images.",
    )
    search_parser.add_argument(
        "--index-name",
        default=DEFAULT_INDEX_NAME,
        help="Name of the OpenSearch index to search.",
    )
    search_parser.add_argument(
        "--query-text",
        help="Free text query for images.",
    )
    search_parser.add_argument(
        "--color-name",
        help="Color name filter (e.g., 'blue').",
    )
    search_parser.add_argument(
        "--color-hex",
        help="Color hex filter (e.g., '0000FF').",
    )
    search_parser.add_argument(
        "--size",
        type=int,
        default=20,
        help="Number of results to return.",
    )
    search_parser.add_argument(
        "--from",
        dest="from_",
        type=int,
        default=0,
        help="Offset for pagination (0-based).",
    )

    # Extract command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract photo documents from Postgres and output to file or stdout.",
    )
    extract_parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: stdout).",
    )

    # Synonyms command
    synonyms_parser = subparsers.add_parser(
        "synonyms",
        help="Generate a synonyms file from WordNet.",
    )
    synonyms_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to write the synonyms file.",
    )
    synonyms_parser.add_argument(
        "--include-hyponyms",
        action="store_true",
        help="Include hyponym terms in synonym groups.",
    )
    synonyms_parser.add_argument(
        "--max-per-group",
        type=int,
        default=5,
        help="Maximum terms per synonym group.",
    )

    # Create-index command
    create_index_parser = subparsers.add_parser(
        "create-index",
        help="Create the OpenSearch index without loading data.",
    )
    create_index_parser.add_argument(
        "--index-name",
        default=DEFAULT_INDEX_NAME,
        help="Name of the OpenSearch index to create.",
    )
    create_index_parser.add_argument(
        "--synonyms-path",
        required=True,
        help="Path to a synonyms file.",
    )
    create_index_parser.add_argument(
        "--shards",
        type=int,
        default=3,
        help="Number of primary shards for the index.",
    )
    create_index_parser.add_argument(
        "--replicas",
        type=int,
        default=1,
        help="Number of replica shards for the index.",
    )

    # Delete-index command
    delete_index_parser = subparsers.add_parser(
        "delete-index",
        help="Delete the OpenSearch index.",
    )
    delete_index_parser.add_argument(
        "--index-name",
        default=DEFAULT_INDEX_NAME,
        help="Name of the OpenSearch index to delete.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command in {"index", "extract"}:
            pg_cfg = load_postgres_config()
        if args.command in {"index", "search", "create-index", "delete-index"}:
            os_cfg = load_opensearch_config()
    except MissingEnvError as exc:
        parser.error(f"Environment initialization error: {exc}")
        return 2

    if args.command == "index":
        pg_conn = create_pg_connection(pg_cfg)
        try:
            os_client = create_opensearch_client(os_cfg)
        except Exception:
            pg_conn.close()
            raise

        try:
            synonym_lines = load_synonyms_from_file(args.synonyms_path)
            build_index(
                os_client,
                pg_conn,
                index_name=args.index_name,
                synonyms=synonym_lines,
                shards=args.shards,
                replicas=args.replicas,
                batch_size=args.batch_size,
            )
        finally:
            pg_conn.close()

    elif args.command == "search":
        os_client = create_opensearch_client(os_cfg)
        results = search_images(
            os_client,
            index_name=args.index_name,
            query_text=args.query_text,
            color_name=args.color_name,
            color_hex=args.color_hex,
            size=args.size,
            from_=args.from_,
        )
        print(json.dumps(results, indent=2))

    elif args.command == "extract":
        pg_conn = create_pg_connection(pg_cfg)
        try:
            docs = list(generate_documents(pg_conn))
            output = json.dumps(docs, indent=2)
            if args.output:
                args.output.write_text(output, encoding="utf-8")
            else:
                print(output)
        finally:
            pg_conn.close()

    elif args.command == "synonyms":
        generate_wordnet_synonyms_file(
            args.output,
            include_hyponyms=args.include_hyponyms,
            max_per_group=args.max_per_group,
        )
        print(f"Synonyms file generated at: {args.output}")

    elif args.command == "create-index":
        os_client = create_opensearch_client(os_cfg)
        synonym_lines = load_synonyms_from_file(args.synonyms_path)
        create_index_with_synonyms(
            os_client,
            args.index_name,
            synonym_lines,
            shards=args.shards,
            replicas=args.replicas,
        )
        print(f"Index '{args.index_name}' created.")

    elif args.command == "delete-index":
        os_client = create_opensearch_client(os_cfg)
        if os_client.indices.exists(index=args.index_name):
            os_client.indices.delete(index=args.index_name)
            print(f"Index '{args.index_name}' deleted.")
        else:
            print(f"Index '{args.index_name}' does not exist.")

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI execution path
    sys.exit(main())

