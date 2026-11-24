"""Lambda entry point for the teams CRUD API.

Routes (prefix '/api/teams-service' is optional):
    GET    /            list teams (optional ?search=)
    POST   /            create a team
    GET    /{id}        get one team
    PUT    /{id}        replace a team
    DELETE /{id}        delete a team
"""

import logging

from psycopg import OperationalError

from database import get_connection, reset_connection
from errors import AppError
from http_utils import Request, json_response
from router import route
from teams_repository import TeamsRepository
from teams_service import TeamsService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event=None, context=None):
    event = event or {}
    try:
        request = Request.from_event(event)
        logger.info("%s %s", request.method, request.path)
        service = TeamsService(TeamsRepository(get_connection()))
        return route(request, service)
    except AppError as error:
        return json_response(error.status_code, {"error": error.message})
    except OperationalError:
        logger.exception("Database connection failed")
        reset_connection()
        return json_response(503, {"error": "Database unavailable, please retry"})
    except Exception:
        logger.exception("Unhandled error")
        return json_response(500, {"error": "Internal server error"})
