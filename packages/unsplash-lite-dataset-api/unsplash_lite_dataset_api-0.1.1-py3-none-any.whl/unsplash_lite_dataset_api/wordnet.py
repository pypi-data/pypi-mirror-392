"""Utilities for building synonym files using NLTK WordNet."""
from __future__ import annotations

import os
from typing import Set, Dict, List, Iterable
from collections import defaultdict

import nltk
from nltk.corpus import wordnet as wn


class WordnetInitializationError(RuntimeError):
    """Raised when the environment is missing required WordNet corpora."""


def describe_nltk_search_paths() -> str:
    """Return a human-readable description of the directories NLTK searches."""
    lines = ["NLTK is currently searching for corpora in the following directories:"]
    for path in nltk.data.path:
        lines.append(f"  - {path}")
    return "\n".join(lines)


def ensure_wordnet_data() -> None:
    """Validate that ``wordnet`` and ``omw-1.4`` corpora are installed."""
    required = ["wordnet", "omw-1.4"]
    missing: List[str] = []

    for resource in required:
        try:
            nltk.data.find(f"corpora/{resource}")
        except LookupError:
            missing.append(resource)

    if missing:
        missing_str = ", ".join(missing)
        raise WordnetInitializationError(
            f"Missing NLTK corpora: {missing_str}.\n"
            f"{describe_nltk_search_paths()}\n\n"
            "The corpora must be installed as extracted directories, not as .zip files.\n"
            "For example, ensure you have:\n"
            "  <nltk-data>/corpora/wordnet/\n"
            "  <nltk-data>/corpora/omw-1.4/\n"
        )


def _is_valid_token(text: str) -> bool:
    if not text:
        return False
    return any(ch.isalnum() for ch in text)


def _normalize_lemma_name(name: str) -> str:
    return name.replace("_", " ").strip().lower()


def build_synonym_sets_from_wordnet(
    *,
    include_hyponyms: bool = False,
    max_per_group: int = 5,
) -> List[Set[str]]:
    groups: Dict[str, Set[str]] = defaultdict(set)

    all_synsets = list(wn.all_synsets())
    for syn in all_synsets:
        lemmas = syn.lemmas(lang="eng")
        if not lemmas:
            continue

        base_terms: Set[str] = set()
        for lemma in lemmas:
            name = _normalize_lemma_name(lemma.name())
            if _is_valid_token(name):
                base_terms.add(name)

        if not base_terms:
            continue

        related_terms: Set[str] = set()
        if include_hyponyms:
            for hypo in syn.hyponyms():
                for lemma in hypo.lemmas(lang="eng"):
                    name = _normalize_lemma_name(lemma.name())
                    if _is_valid_token(name):
                        related_terms.add(name)

        combined = base_terms | related_terms
        if not combined:
            continue

        if len(combined) > max_per_group:
            combined = set(list(combined)[:max_per_group])

        key = sorted(combined)[0]
        groups[key].update(combined)

    synonym_sets: List[Set[str]] = [terms for terms in groups.values() if len(terms) > 1]
    return synonym_sets


def format_synonym_sets_for_opensearch(
    synonym_sets: Iterable[Set[str]],
) -> List[str]:
    lines: List[str] = []
    for terms in synonym_sets:
        sorted_terms = sorted(terms)
        if len(sorted_terms) <= 1:
            continue
        line = ", ".join(sorted_terms)
        lines.append(line)

    return sorted(set(lines))


def write_synonyms_file(lines: List[str], path: str) -> None:
    if not path:
        raise ValueError("Synonym file path must not be empty.")

    abs_path = os.path.abspath(path)
    directory = os.path.dirname(abs_path)
    if directory and not os.path.isdir(directory):
        raise RuntimeError(
            f"Directory for synonym file does not exist: {directory}\n"
            "Create the directory explicitly before running this function."
        )

    try:
        with open(abs_path, "w", encoding="utf-8") as handle:
            for line in lines:
                handle.write(line)
                handle.write("\n")
    except OSError as exc:
        raise RuntimeError(f"Failed to write synonyms file at {abs_path}: {exc}") from exc


def generate_wordnet_synonyms_file(
    output_path: str,
    *,
    include_hyponyms: bool = False,
    max_per_group: int = 5,
) -> None:
    ensure_wordnet_data()
    synonym_sets = build_synonym_sets_from_wordnet(
        include_hyponyms=include_hyponyms,
        max_per_group=max_per_group,
    )
    lines = format_synonym_sets_for_opensearch(synonym_sets)
    if not lines:
        raise RuntimeError("No synonyms generated from WordNet/OMW.")
    write_synonyms_file(lines, output_path)


__all__ = [
    "WordnetInitializationError",
    "describe_nltk_search_paths",
    "ensure_wordnet_data",
    "build_synonym_sets_from_wordnet",
    "format_synonym_sets_for_opensearch",
    "write_synonyms_file",
    "generate_wordnet_synonyms_file",
]
