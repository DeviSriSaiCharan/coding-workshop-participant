"""Maps HTTP method + path to TeamsService calls."""

import re
from typing import Callable

from errors import NotFoundError, ValidationError
from http_utils import Request, json_response
from teams_service import TeamsService

_TEAM_ID_PATH = re.compile(r"^/(?P<team_id>[^/]+)$")


def route(request: Request, service: TeamsService) -> dict:
    if request.path == "/":
        return _route_collection(request, service)

    match = _TEAM_ID_PATH.match(request.path)
    if match:
        return _route_item(request, service, _parse_id(match["team_id"]))

    raise NotFoundError(f"Route {request.path} not found")


def _route_collection(request: Request, service: TeamsService) -> dict:
    handlers: dict[str, Callable[[], dict]] = {
        "GET": lambda: json_response(200, service.list_teams(request.query.get("search", ""))),
        "POST": lambda: json_response(201, service.create_team(request.body)),
    }
    return _dispatch(request.method, handlers)


def _route_item(request: Request, service: TeamsService, team_id: int) -> dict:
    def delete() -> dict:
        service.delete_team(team_id)
        return json_response(204)

    handlers: dict[str, Callable[[], dict]] = {
        "GET": lambda: json_response(200, service.get_team(team_id)),
        "PUT": lambda: json_response(200, service.update_team(team_id, request.body)),
        "DELETE": delete,
    }
    return _dispatch(request.method, handlers)


def _dispatch(method: str, handlers: dict[str, Callable[[], dict]]) -> dict:
    if method == "OPTIONS":
        return json_response(204)
    handler = handlers.get(method)
    if handler is None:
        return json_response(405, {"error": f"Method {method} not allowed"})
    return handler()


def _parse_id(raw_id: str) -> int:
    if not raw_id.isdigit():
        raise ValidationError("Team id must be a positive integer")
    return int(raw_id)
