"""PostgreSQL connection management.

The connection is cached at module level so warm Lambda invocations reuse it.
"""

import logging

from psycopg import Connection, connect
from psycopg.rows import dict_row

from config import DatabaseConfig

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS teams (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    location    VARCHAR(100) NOT NULL DEFAULT '',
    leader      VARCHAR(100) NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);
"""

_connection: Connection | None = None


def get_connection() -> Connection:
    """Return an open connection, creating it (and the schema) on first use."""
    global _connection
    if _connection is None or _connection.closed:
        config = DatabaseConfig.from_env()
        logger.info("Connecting to PostgreSQL at %s:%s", config.host, config.port)
        _connection = connect(config.to_conninfo(), autocommit=True, row_factory=dict_row)
        _ensure_schema(_connection)
    return _connection


def reset_connection() -> None:
    """Drop the cached connection so the next call reconnects."""
    global _connection
    if _connection is not None and not _connection.closed:
        _connection.close()
    _connection = None


def _ensure_schema(connection: Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(SCHEMA_SQL)
