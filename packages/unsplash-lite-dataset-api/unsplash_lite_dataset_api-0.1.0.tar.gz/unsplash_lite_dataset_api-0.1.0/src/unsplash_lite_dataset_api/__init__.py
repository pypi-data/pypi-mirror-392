"""Utilities for building and querying an Unsplash-style OpenSearch index."""
from __future__ import annotations

from .config import (
    MissingEnvError,
    OpenSearchConfig,
    PostgresConfig,
    create_opensearch_client,
    create_pg_connection,
    load_opensearch_config,
    load_postgres_config,
)
from .documents import build_document
from .indexer import (
    build_index,
    bulk_index_documents,
    create_index_with_synonyms,
    generate_documents,
    load_synonyms_from_file,
)
from .search import build_search_body, search_images
from .wordnet import (
    WordnetInitializationError,
    build_synonym_sets_from_wordnet,
    describe_nltk_search_paths,
    ensure_wordnet_data,
    format_synonym_sets_for_opensearch,
    generate_wordnet_synonyms_file,
    write_synonyms_file,
)

__all__ = [
    "MissingEnvError",
    "OpenSearchConfig",
    "PostgresConfig",
    "create_opensearch_client",
    "create_pg_connection",
    "load_opensearch_config",
    "load_postgres_config",
    "build_index",
    "build_document",
    "bulk_index_documents",
    "create_index_with_synonyms",
    "generate_documents",
    "load_synonyms_from_file",
    "build_search_body",
    "search_images",
    "WordnetInitializationError",
    "build_synonym_sets_from_wordnet",
    "describe_nltk_search_paths",
    "ensure_wordnet_data",
    "format_synonym_sets_for_opensearch",
    "generate_wordnet_synonyms_file",
    "write_synonyms_file",
]
