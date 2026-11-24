"""Data access for the teams table. Contains SQL only, no business rules."""

from contextlib import contextmanager

from psycopg import Connection
from psycopg.errors import UniqueViolation

from errors import ConflictError
from models import TeamInput

_COLUMNS = "id, name, location, leader, created_at, updated_at"


class TeamsRepository:
    def __init__(self, connection: Connection):
        self._connection = connection

    def list(self, search: str = "") -> list[dict]:
        pattern = f"%{search}%"
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {_COLUMNS} FROM teams "
                "WHERE name ILIKE %s OR location ILIKE %s OR leader ILIKE %s "
                "ORDER BY name",
                (pattern, pattern, pattern),
            )
            return cursor.fetchall()

    def get(self, team_id: int) -> dict | None:
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT {_COLUMNS} FROM teams WHERE id = %s", (team_id,))
            return cursor.fetchone()

    def create(self, team: TeamInput) -> dict:
        with self._connection.cursor() as cursor, _unique_name_guard(team.name):
            cursor.execute(
                f"INSERT INTO teams (name, location, leader) VALUES (%s, %s, %s) "
                f"RETURNING {_COLUMNS}",
                (team.name, team.location, team.leader),
            )
            return cursor.fetchone()

    def update(self, team_id: int, team: TeamInput) -> dict | None:
        with self._connection.cursor() as cursor, _unique_name_guard(team.name):
            cursor.execute(
                "UPDATE teams SET name = %s, location = %s, leader = %s, updated_at = NOW() "
                f"WHERE id = %s RETURNING {_COLUMNS}",
                (team.name, team.location, team.leader, team_id),
            )
            return cursor.fetchone()

    def delete(self, team_id: int) -> bool:
        with self._connection.cursor() as cursor:
            cursor.execute("DELETE FROM teams WHERE id = %s", (team_id,))
            return cursor.rowcount > 0


@contextmanager
def _unique_name_guard(name: str):
    """Translate a duplicate-name database error into a domain ConflictError."""
    try:
        yield
    except UniqueViolation as exc:
        raise ConflictError(f"A team named '{name}' already exists") from exc
