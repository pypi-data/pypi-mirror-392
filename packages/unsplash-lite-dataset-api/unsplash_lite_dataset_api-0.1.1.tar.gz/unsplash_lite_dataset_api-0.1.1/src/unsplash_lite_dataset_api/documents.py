"""Helpers for extracting documents from Postgres to index into OpenSearch."""
from __future__ import annotations

from typing import Dict, Any, Iterable, List

from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import DictCursor


def fetch_photos(conn: PGConnection) -> Iterable[Dict[str, Any]]:
    sql = """
    SELECT
        p.photo_id,
        p.photo_url,
        p.photo_image_url,
        p.photo_submitted_at,
        p.photo_featured,
        p.photo_width,
        p.photo_height,
        p.photo_aspect_ratio,
        p.photo_description,
        p.photographer_username,
        p.photographer_first_name,
        p.photographer_last_name,
        p.exif_camera_make,
        p.exif_camera_model,
        p.exif_iso,
        p.exif_aperture_value,
        p.exif_focal_length,
        p.exif_exposure_time,
        p.photo_location_name,
        p.photo_location_latitude,
        p.photo_location_longitude,
        p.photo_location_country,
        p.photo_location_city,
        p.stats_views,
        p.stats_downloads,
        p.ai_description,
        p.ai_primary_landmark_name,
        p.ai_primary_landmark_latitude,
        p.ai_primary_landmark_longitude,
        p.ai_primary_landmark_confidence,
        p.blur_hash
    FROM unsplash_photos p;
    """
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(sql)
        for row in cur:
            yield dict(row)


def fetch_keywords(conn: PGConnection) -> Dict[str, List[Dict[str, Any]]]:
    sql = """
    SELECT
        photo_id,
        keyword,
        ai_service_1_confidence,
        ai_service_2_confidence,
        suggested_by_user,
        user_suggestion_source
    FROM unsplash_keywords;
    """
    by_photo: Dict[str, List[Dict[str, Any]]] = {}
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(sql)
        for row in cur:
            d = dict(row)
            pid = d["photo_id"]
            by_photo.setdefault(pid, []).append(
                {
                    "keyword": d["keyword"],
                    "ai_service_1_confidence": d["ai_service_1_confidence"],
                    "ai_service_2_confidence": d["ai_service_2_confidence"],
                    "suggested_by_user": d["suggested_by_user"],
                    "user_suggestion_source": d["user_suggestion_source"],
                }
            )
    return by_photo


def fetch_colors(conn: PGConnection) -> Dict[str, List[Dict[str, Any]]]:
    sql = """
    SELECT
        photo_id,
        hex,
        red,
        green,
        blue,
        keyword,
        ai_coverage,
        ai_score
    FROM unsplash_colors;
    """
    by_photo: Dict[str, List[Dict[str, Any]]] = {}
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(sql)
        for row in cur:
            d = dict(row)
            pid = d["photo_id"]
            by_photo.setdefault(pid, []).append(
                {
                    "hex": d["hex"],
                    "red": d["red"],
                    "green": d["green"],
                    "blue": d["blue"],
                    "keyword": d["keyword"],
                    "ai_coverage": d["ai_coverage"],
                    "ai_score": d["ai_score"],
                }
            )
    return by_photo


def fetch_collections(conn: PGConnection) -> Dict[str, List[Dict[str, Any]]]:
    sql = """
    SELECT
        photo_id,
        collection_id,
        collection_title,
        photo_collected_at,
        collection_type
    FROM unsplash_collections;
    """
    by_photo: Dict[str, List[Dict[str, Any]]] = {}
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(sql)
        for row in cur:
            d = dict(row)
            pid = d["photo_id"]
            by_photo.setdefault(pid, []).append(
                {
                    "collection_id": d["collection_id"],
                    "collection_title": d["collection_title"],
                    "photo_collected_at": d["photo_collected_at"],
                    "collection_type": d["collection_type"],
                }
            )
    return by_photo


def build_document(
    photo: Dict[str, Any],
    keywords_by_photo: Dict[str, List[Dict[str, Any]]],
    colors_by_photo: Dict[str, List[Dict[str, Any]]],
    collections_by_photo: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    pid = photo["photo_id"]

    keywords = keywords_by_photo.get(pid, [])
    colors = colors_by_photo.get(pid, [])
    collections = collections_by_photo.get(pid, [])

    keyword_values = [k["keyword"] for k in keywords]
    color_keywords = [c["keyword"] for c in colors if c.get("keyword")]
    color_hexes = [c["hex"] for c in colors if c.get("hex")]
    color_names = list({ck for ck in color_keywords if ck})

    title = photo.get("ai_description") or photo.get("photo_description") or ""
    description = photo.get("photo_description") or photo.get("ai_description") or ""
    photographer_full_name = " ".join(
        [
            part
            for part in [
                photo.get("photographer_first_name"),
                photo.get("photographer_last_name"),
            ]
            if part
        ]
    ).strip()

    doc: Dict[str, Any] = {
        "photo_id": pid,
        "photo_url": photo.get("photo_url"),
        "photo_image_url": photo.get("photo_image_url"),
        "photo_submitted_at": photo.get("photo_submitted_at"),
        "photo_featured": photo.get("photo_featured"),
        "photo_width": photo.get("photo_width"),
        "photo_height": photo.get("photo_height"),
        "photo_aspect_ratio": photo.get("photo_aspect_ratio"),
        "title": title,
        "description": description,
        "photographer_username": photo.get("photographer_username"),
        "photographer_full_name": photographer_full_name or None,
        "photo_location_name": photo.get("photo_location_name"),
        "photo_location_country": photo.get("photo_location_country"),
        "photo_location_city": photo.get("photo_location_city"),
        "photo_location_latitude": photo.get("photo_location_latitude"),
        "photo_location_longitude": photo.get("photo_location_longitude"),
        "stats_views": photo.get("stats_views"),
        "stats_downloads": photo.get("stats_downloads"),
        "ai_primary_landmark_name": photo.get("ai_primary_landmark_name"),
        "ai_primary_landmark_latitude": photo.get("ai_primary_landmark_latitude"),
        "ai_primary_landmark_longitude": photo.get("ai_primary_landmark_longitude"),
        "ai_primary_landmark_confidence": photo.get("ai_primary_landmark_confidence"),
        "blur_hash": photo.get("blur_hash"),
        "keywords": keyword_values,
        "colors": colors,
        "color_names": color_names,
        "color_hexes": color_hexes,
        "collections": collections,
    }

    return doc
