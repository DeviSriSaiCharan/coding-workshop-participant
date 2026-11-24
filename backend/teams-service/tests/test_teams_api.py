"""Unit tests for routing, validation and service logic using an in-memory store."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from errors import ConflictError, NotFoundError, ValidationError  # noqa: E402
from http_utils import Request  # noqa: E402
from router import route  # noqa: E402
from teams_service import TeamsService  # noqa: E402


class InMemoryTeamsStore:
    def __init__(self):
        self._teams: dict[int, dict] = {}
        self._next_id = 1

    def list(self, search=""):
        search = search.lower()
        return [t for t in self._teams.values() if search in t["name"].lower()]

    def get(self, team_id):
        return self._teams.get(team_id)

    def create(self, team):
        if any(t["name"] == team.name for t in self._teams.values()):
            raise ConflictError(f"A team named '{team.name}' already exists")
        record = {"id": self._next_id, **team.__dict__}
        self._teams[self._next_id] = record
        self._next_id += 1
        return record

    def update(self, team_id, team):
        if team_id not in self._teams:
            return None
        self._teams[team_id] = {"id": team_id, **team.__dict__}
        return self._teams[team_id]

    def delete(self, team_id):
        return self._teams.pop(team_id, None) is not None


def make_event(method, path, body=None, query=None):
    return {
        "requestContext": {"http": {"method": method}},
        "rawPath": path,
        "queryStringParameters": query,
        "body": json.dumps(body) if body is not None else None,
    }


class TeamsApiTest(unittest.TestCase):
    def setUp(self):
        self.service = TeamsService(InMemoryTeamsStore())

    def call(self, method, path, body=None, query=None):
        response = route(Request.from_event(make_event(method, path, body, query)), self.service)
        payload = json.loads(response["body"]) if response["body"] else None
        return response["statusCode"], payload

    def test_create_and_get_team(self):
        status, created = self.call("POST", "/", {"name": " Alpha ", "location": "NYC"})
        self.assertEqual(status, 201)
        self.assertEqual(created["name"], "Alpha")

        status, fetched = self.call("GET", f"/{created['id']}")
        self.assertEqual((status, fetched), (200, created))

    def test_cloudfront_prefix_is_stripped(self):
        self.call("POST", "/api/teams-service", {"name": "Alpha"})
        status, teams = self.call("GET", "/api/teams-service/")
        self.assertEqual(status, 200)
        self.assertEqual(len(teams), 1)

    def test_search_filters_teams(self):
        self.call("POST", "/", {"name": "Alpha"})
        self.call("POST", "/", {"name": "Beta"})
        _, teams = self.call("GET", "/", query={"search": "bet"})
        self.assertEqual([t["name"] for t in teams], ["Beta"])

    def test_update_and_delete_team(self):
        _, created = self.call("POST", "/", {"name": "Alpha"})
        status, updated = self.call("PUT", f"/{created['id']}", {"name": "Alpha 2"})
        self.assertEqual((status, updated["name"]), (200, "Alpha 2"))

        status, _ = self.call("DELETE", f"/{created['id']}")
        self.assertEqual(status, 204)
        with self.assertRaises(NotFoundError):
            self.call("GET", f"/{created['id']}")

    def test_missing_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.call("POST", "/", {"location": "NYC"})

    def test_invalid_id_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.call("GET", "/abc")

    def test_unsupported_method_returns_405(self):
        status, _ = self.call("PATCH", "/")
        self.assertEqual(status, 405)


if __name__ == "__main__":
    unittest.main()
