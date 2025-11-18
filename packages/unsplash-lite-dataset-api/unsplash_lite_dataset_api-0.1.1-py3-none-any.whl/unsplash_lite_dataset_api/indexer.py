"""High-level helpers for constructing an OpenSearch index."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Dict, Any, Iterator, Sequence

from opensearchpy import OpenSearch, helpers

from .documents import (
    fetch_photos,
    fetch_keywords,
    fetch_colors,
    fetch_collections,
    build_document,
)


def load_synonyms_from_file(path: str | Path) -> list[str]:
    """Return a list of synonym rules read from ``path``."""
    try:
        with Path(path).expanduser().open("r", encoding="utf-8") as handle:
            lines = [line.strip() for line in handle.readlines()]
    except FileNotFoundError as exc:
        raise RuntimeError(f"Synonym file not found at path: {path}") from exc
    except OSError as exc:
        raise RuntimeError(f"Error reading synonym file at path {path}: {exc}") from exc

    synonyms = [line for line in lines if line and not line.startswith("#")]
    if not synonyms:
        raise RuntimeError(
            f"Synonym file {path} is empty or contains only comments."
        )
    return synonyms


def create_index_with_synonyms(
    client: OpenSearch,
    index_name: str,
    synonym_list: Sequence[str],
    *,
    shards: int = 3,
    replicas: int = 1,
) -> None:
    """Create (or recreate) ``index_name`` using ``synonym_list``."""
    if not synonym_list:
        raise ValueError("synonym_list must not be empty.")

    settings = {
        "settings": {
            "number_of_shards": shards,
            "number_of_replicas": replicas,
            "analysis": {
                "filter": {
                    "synonym_graph_filter": {
                        "type": "synonym_graph",
                        "synonyms": list(synonym_list),
                        "expand": True,
                    }
                },
                "analyzer": {
                    "text_search_analyzer": {
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding"],
                    },
                    "synonym_text_analyzer": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding",
                            "synonym_graph_filter",
                        ],
                    },
                },
            },
        },
        "mappings": {
            "dynamic": "false",
            "properties": {
                "photo_id": {"type": "keyword"},
                "photo_url": {"type": "keyword"},
                "photo_image_url": {"type": "keyword"},
                "photo_submitted_at": {"type": "date"},
                "photo_featured": {"type": "boolean"},
                "photo_width": {"type": "integer"},
                "photo_height": {"type": "integer"},
                "photo_aspect_ratio": {"type": "float"},
                "title": {
                    "type": "text",
                    "analyzer": "text_search_analyzer",
                    "fields": {
                        "raw": {"type": "keyword"},
                    },
                },
                "description": {
                    "type": "text",
                    "analyzer": "text_search_analyzer",
                },
                "photographer_username": {"type": "keyword"},
                "photographer_full_name": {
                    "type": "text",
                    "analyzer": "text_search_analyzer",
                },
                "photo_location_name": {
                    "type": "text",
                    "analyzer": "text_search_analyzer",
                },
                "photo_location_country": {"type": "keyword"},
                "photo_location_city": {
                    "type": "text",
                    "analyzer": "text_search_analyzer",
                },
                "photo_location_latitude": {"type": "float"},
                "photo_location_longitude": {"type": "float"},
                "stats_views": {"type": "long"},
                "stats_downloads": {"type": "long"},
                "ai_primary_landmark_name": {
                    "type": "text",
                    "analyzer": "text_search_analyzer",
                },
                "ai_primary_landmark_latitude": {"type": "float"},
                "ai_primary_landmark_longitude": {"type": "float"},
                "ai_primary_landmark_confidence": {"type": "keyword"},
                "blur_hash": {"type": "keyword"},
                "keywords": {
                    "type": "text",
                    "analyzer": "synonym_text_analyzer",
                    "fields": {
                        "raw": {"type": "keyword"},
                    },
                },
                "color_names": {
                    "type": "text",
                    "analyzer": "synonym_text_analyzer",
                    "fields": {
                        "raw": {"type": "keyword"},
                    },
                },
                "color_hexes": {"type": "keyword"},
                "colors": {
                    "type": "nested",
                    "properties": {
                        "hex": {"type": "keyword"},
                        "red": {"type": "integer"},
                        "green": {"type": "integer"},
                        "blue": {"type": "integer"},
                        "keyword": {
                            "type": "text",
                            "analyzer": "synonym_text_analyzer",
                        },
                        "ai_coverage": {"type": "float"},
                        "ai_score": {"type": "float"},
                    },
                },
                "collections": {
                    "type": "nested",
                    "properties": {
                        "collection_id": {"type": "keyword"},
                        "collection_title": {
                            "type": "text",
                            "analyzer": "text_search_analyzer",
                        },
                        "photo_collected_at": {"type": "date"},
                        "collection_type": {"type": "keyword"},
                    },
                },
            },
        },
    }

    try:
        if client.indices.exists(index=index_name):
            client.indices.delete(index=index_name)
        client.indices.create(index=index_name, body=settings)
    except Exception as exc:  # pragma: no cover - relies on OpenSearch
        raise RuntimeError(f"Failed to create index '{index_name}': {exc}") from exc


def bulk_index_documents(
    client: OpenSearch,
    index_name: str,
    docs: Iterable[Dict[str, Any]],
    *,
    batch_size: int = 500,
) -> None:
    """Index ``docs`` into ``index_name`` using the bulk helper."""
    actions = (
        {
            "_index": index_name,
            "_id": doc["photo_id"],
            "_source": doc,
        }
        for doc in docs
    )

    try:
        success, errors = helpers.bulk(
            client,
            actions,
            chunk_size=batch_size,
            raise_on_error=False,
            stats_only=False,
        )
    except Exception as exc:  # pragma: no cover - network failure path
        raise RuntimeError(f"Bulk indexing failed: {exc}") from exc

    if errors:
        error_count = len(errors)
        sample = errors[0]
        raise RuntimeError(
            f"Bulk indexing completed with {error_count} errors. Sample error: {sample}"
        )
    if success is None:
        raise RuntimeError("Bulk indexing returned no success count, unknown state.")


def generate_documents(conn) -> Iterator[Dict[str, Any]]:
    """Yield OpenSearch-ready documents sourced from Postgres."""
    keywords_by_photo = fetch_keywords(conn)
    colors_by_photo = fetch_colors(conn)
    collections_by_photo = fetch_collections(conn)

    for photo_row in fetch_photos(conn):
        yield build_document(
            photo=photo_row,
            keywords_by_photo=keywords_by_photo,
            colors_by_photo=colors_by_photo,
            collections_by_photo=collections_by_photo,
        )


def build_index(
    client: OpenSearch,
    conn,
    *,
    index_name: str,
    synonyms: Sequence[str],
    shards: int = 3,
    replicas: int = 1,
    batch_size: int = 500,
) -> None:
    """Create the index and stream docs from Postgres into OpenSearch."""
    create_index_with_synonyms(
        client,
        index_name,
        synonyms,
        shards=shards,
        replicas=replicas,
    )
    docs_iter = generate_documents(conn)
    bulk_index_documents(
        client,
        index_name,
        docs_iter,
        batch_size=batch_size,
    )
