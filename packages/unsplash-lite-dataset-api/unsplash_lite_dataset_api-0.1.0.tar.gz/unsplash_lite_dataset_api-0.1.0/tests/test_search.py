from __future__ import annotations

from pathlib import Path
import sys

import pytest

# Ensure the src layout is importable when running tests locally without installing.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from unsplash_lite_dataset_api.search import build_search_body
from unsplash_lite_dataset_api.indexer import load_synonyms_from_file


def test_build_search_body_match_all():
    body = build_search_body(
        query_text=None,
        color_name=None,
        color_hex=None,
        size=5,
    )
    assert body["query"] == {"match_all": {}}
    assert body["size"] == 5


def test_build_search_body_filters():
    body = build_search_body(
        query_text="ocean",
        color_name="blue",
        color_hex="ABCDEF",
        size=10,
    )
    bool_query = body["query"]
    assert "bool" in bool_query
    clauses = bool_query["bool"]["must"]
    assert any("simple_query_string" in clause for clause in clauses)
    assert any("match" in clause for clause in clauses)
    assert any(
        clause.get("term", {}).get("color_hexes") == "abcdef" for clause in clauses
    )


def test_load_synonyms_from_file(tmp_path: Path):
    target = tmp_path / "synonyms.txt"
    target.write_text("sky, heavens\nblue, azure\n", encoding="utf-8")
    lines = load_synonyms_from_file(target)
    assert lines == ["sky, heavens", "blue, azure"]


def test_load_synonyms_from_file_empty(tmp_path: Path):
    target = tmp_path / "synonyms.txt"
    target.write_text("# comment only\n", encoding="utf-8")
    with pytest.raises(RuntimeError):
        load_synonyms_from_file(target)
