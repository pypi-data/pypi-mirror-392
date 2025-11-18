"""Public search helpers for querying the OpenSearch index."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from opensearchpy import OpenSearch
from opensearchpy.exceptions import TransportError


def build_search_body(
    *,
    query_text: Optional[str],
    color_name: Optional[str],
    color_hex: Optional[str],
    size: int,
) -> Dict[str, Any]:
    """Construct the OpenSearch query body for image search."""
    must_clauses = []

    if query_text:
        must_clauses.append(
            {
                "simple_query_string": {
                    "query": query_text,
                    "fields": [
                        "title^3",
                        "description^2",
                        "keywords^3",
                        "color_names^2",
                        "photographer_full_name",
                        "photographer_username",
                        "photo_location_name",
                        "ai_primary_landmark_name",
                        "collections.collection_title",
                    ],
                    "default_operator": "and",
                }
            }
        )

    if color_name:
        must_clauses.append({"match": {"color_names": {"query": color_name}}})

    if color_hex:
        must_clauses.append({"term": {"color_hexes": color_hex.lower()}})

    if not must_clauses:
        query: Dict[str, Any] = {"match_all": {}}
    else:
        query = {"bool": {"must": must_clauses}}

    body: Dict[str, Any] = {
        "query": query,
        "_source": [
            "photo_id",
            "title",
            "photo_image_url",
            "blur_hash",
            "photo_url",
        ],
        "size": size,
    }
    return body


def search_images(
    client: OpenSearch,
    *,
    index_name: str,
    query_text: Optional[str] = None,
    color_name: Optional[str] = None,
    color_hex: Optional[str] = None,
    size: int = 20,
) -> List[Dict[str, Any]]:
    """Search for images using ``client`` against ``index_name``."""
    if size <= 0:
        raise ValueError("size must be positive.")

    body = build_search_body(
        query_text=query_text,
        color_name=color_name,
        color_hex=color_hex,
        size=size,
    )

    try:
        res = client.search(index=index_name, body=body)
    except TransportError as exc:  # pragma: no cover - requires OpenSearch
        msg = str(exc)
        if "too many nested clauses" in msg or "maxClauseCount" in msg:
            raise RuntimeError(
                "OpenSearch rejected the query because it contains too many nested clauses "
                "(maxClauseCount exceeded). This is a server-side safety limit.\n\n"
                "Query body was:\n"
                f"{body}"
            ) from exc
        raise RuntimeError(f"Search request failed with TransportError: {exc}") from exc
    except Exception as exc:  # pragma: no cover - requires OpenSearch
        raise RuntimeError(f"Search request failed: {exc}") from exc

    hits = res.get("hits", {}).get("hits", [])
    results: List[Dict[str, Any]] = []
    for h in hits:
        src = h.get("_source", {})
        results.append(
            {
                "photo_id": src.get("photo_id"),
                "title": src.get("title"),
                "photo_image_url": src.get("photo_image_url"),
                "blur_hash": src.get("blur_hash"),
                "photo_url": src.get("photo_url"),
                "score": h.get("_score"),
            }
        )

    return results


__all__ = ["build_search_body", "search_images"]
