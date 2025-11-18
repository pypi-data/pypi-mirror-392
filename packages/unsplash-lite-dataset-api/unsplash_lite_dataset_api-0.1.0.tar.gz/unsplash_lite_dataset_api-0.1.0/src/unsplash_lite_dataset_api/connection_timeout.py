"""Utilities for reading timeout settings from the environment."""
from __future__ import annotations

import os
from typing import Optional


class TimeoutConfigError(RuntimeError):
    """Raised when timeout-related environment configuration is invalid."""


def _get_env_str(key: str, required: bool = False) -> Optional[str]:
    """Read an environment variable as a string."""
    value = os.getenv(key)
    if required and not value:
        raise TimeoutConfigError(f"Missing required environment variable: {key}")
    return value


def get_opensearch_connect_timeout(default_seconds: float = 10.0) -> float:
    """Return the OpenSearch connection timeout in seconds."""
    raw = _get_env_str("OPENSEARCH_CONNECT_TIMEOUT", required=False)
    if raw is None or not raw.strip():
        return float(default_seconds)

    try:
        value = float(raw)
    except ValueError as exc:
        raise TimeoutConfigError(
            "OPENSEARCH_CONNECT_TIMEOUT must be a number (seconds), "
            f"got: {raw}"
        ) from exc

    if value <= 0:
        raise TimeoutConfigError(
            f"OPENSEARCH_CONNECT_TIMEOUT must be positive, got: {value}"
        )

    return value
