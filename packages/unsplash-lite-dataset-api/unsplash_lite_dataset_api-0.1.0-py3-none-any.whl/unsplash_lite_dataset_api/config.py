"""Configuration helpers for Postgres and OpenSearch."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import DictCursor
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from .connection_timeout import get_opensearch_connect_timeout, TimeoutConfigError

load_dotenv()


class MissingEnvError(RuntimeError):
    """Raised when a required environment variable is missing or invalid."""


def _get_env_str(key: str, required: bool = True, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    if required and not value:
        raise MissingEnvError(f"Missing required environment variable: {key}")
    return value


def _get_env_bool(
    key: str, *, required: bool = False, default: Optional[bool] = None
) -> Optional[bool]:
    raw = os.getenv(key)
    if raw is None:
        if required:
            raise MissingEnvError(f"Missing required environment variable: {key}")
        return default
    val = raw.strip().lower()
    if val in {"1", "true", "yes", "y", "on"}:
        return True
    if val in {"0", "false", "no", "n", "off"}:
        return False
    raise MissingEnvError(
        f"Environment variable {key} must be a boolean-like value (true/false), got: {raw}"
    )


@dataclass
class PostgresConfig:
    host: str
    port: int
    db: str
    user: str
    password: str


@dataclass
class OpenSearchConfig:
    host: str
    port: int
    use_ssl: bool
    verify_certs: bool
    region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_session_token: Optional[str]


def load_postgres_config() -> PostgresConfig:
    host = _get_env_str("PG_HOST")
    port_str = _get_env_str("PG_PORT")
    db = _get_env_str("PG_DB")
    user = _get_env_str("PG_USER")
    password = _get_env_str("PG_PASSWORD", required=False)

    try:
        port = int(port_str)
    except ValueError as exc:
        raise MissingEnvError(f"PG_PORT must be an integer, got: {port_str}") from exc

    return PostgresConfig(
        host=host,
        port=port,
        db=db,
        user=user,
        password=password,
    )


def load_opensearch_config() -> OpenSearchConfig:
    host = _get_env_str("OPENSEARCH_HOST")
    port_str = _get_env_str("OPENSEARCH_PORT")
    use_ssl = _get_env_bool("OPENSEARCH_USE_SSL", required=True)
    verify_certs = _get_env_bool("OPENSEARCH_VERIFY_CERTS", required=True)
    region = _get_env_str("OPENSEARCH_REGION")

    aws_access_key_id = _get_env_str("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = _get_env_str("AWS_SECRET_ACCESS_KEY")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN")

    try:
        port = int(port_str)
    except ValueError as exc:
        raise MissingEnvError(
            f"OPENSEARCH_PORT must be an integer, got: {port_str}"
        ) from exc

    return OpenSearchConfig(
        host=host,
        port=port,
        use_ssl=bool(use_ssl),
        verify_certs=bool(verify_certs),
        region=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )


def create_pg_connection(cfg: PostgresConfig):
    try:
        conn = psycopg2.connect(
            host=cfg.host,
            port=cfg.port,
            dbname=cfg.db,
            user=cfg.user,
            password=cfg.password,
            cursor_factory=DictCursor,
        )
        return conn
    except Exception as exc:  # pragma: no cover - pass through error context
        raise RuntimeError(f"Failed to connect to Postgres: {exc}") from exc


def create_opensearch_client(cfg: OpenSearchConfig) -> OpenSearch:
    service = "es"

    aws_auth = AWS4Auth(
        cfg.aws_access_key_id,
        cfg.aws_secret_access_key,
        cfg.region,
        service,
        session_token=cfg.aws_session_token,
    )

    try:
        timeout = get_opensearch_connect_timeout()
    except TimeoutConfigError as exc:
        raise RuntimeError(
            f"Invalid OpenSearch timeout configuration: {exc}"
        ) from exc

    try:
        client = OpenSearch(
            hosts=[{"host": cfg.host, "port": cfg.port}],
            http_auth=aws_auth,
            use_ssl=cfg.use_ssl,
            verify_certs=cfg.verify_certs,
            ssl_assert_hostname=cfg.verify_certs,
            ssl_show_warn=True,
            connection_class=RequestsHttpConnection,
            timeout=timeout,
            connect_timeout=timeout,
        )
        client.info()
        return client
    except Exception as exc:  # pragma: no cover - network failure path
        raise RuntimeError(
            "Failed to create or reach OpenSearch with AWS SigV4 auth: "
            f"{exc}"
        ) from exc
