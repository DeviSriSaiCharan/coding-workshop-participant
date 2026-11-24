"""Business logic for teams. Independent of HTTP and of the database driver."""

from typing import Protocol

from errors import NotFoundError
from models import TeamInput


class TeamsStore(Protocol):
    def list(self, search: str = "") -> list[dict]: ...
    def get(self, team_id: int) -> dict | None: ...
    def create(self, team: TeamInput) -> dict: ...
    def update(self, team_id: int, team: TeamInput) -> dict | None: ...
    def delete(self, team_id: int) -> bool: ...


class TeamsService:
    def __init__(self, store: TeamsStore):
        self._store = store

    def list_teams(self, search: str = "") -> list[dict]:
        return self._store.list(search.strip())

    def get_team(self, team_id: int) -> dict:
        return self._require(self._store.get(team_id), team_id)

    def create_team(self, payload: dict) -> dict:
        return self._store.create(TeamInput.from_payload(payload))

    def update_team(self, team_id: int, payload: dict) -> dict:
        updated = self._store.update(team_id, TeamInput.from_payload(payload))
        return self._require(updated, team_id)

    def delete_team(self, team_id: int) -> None:
        if not self._store.delete(team_id):
            raise NotFoundError(f"Team {team_id} not found")

    @staticmethod
    def _require(team: dict | None, team_id: int) -> dict:
        if team is None:
            raise NotFoundError(f"Team {team_id} not found")
        return team
