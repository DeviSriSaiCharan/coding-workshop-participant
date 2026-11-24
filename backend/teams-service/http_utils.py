"""Helpers to read Lambda Function URL events and build HTTP responses."""

import base64
import json
from dataclasses import dataclass
from datetime import date, datetime

from errors import ValidationError

SERVICE_PREFIX = "/api/teams-service"


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    query: dict
    body: dict

    @classmethod
    def from_event(cls, event: dict) -> "Request":
        http = event.get("requestContext", {}).get("http", {})
        return cls(
            method=http.get("method", "GET").upper(),
            path=_normalize_path(event.get("rawPath", "/")),
            query=event.get("queryStringParameters") or {},
            body=_parse_body(event),
        )


def json_response(status_code: int, payload=None) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": "" if payload is None else json.dumps(payload, default=_json_default),
    }


def _normalize_path(raw_path: str) -> str:
    """Strip the CloudFront route prefix so routes look the same locally and in AWS.

    Locally the dev proxy removes '/api/teams-service'; CloudFront forwards it.
    """
    path = raw_path or "/"
    if path.startswith(SERVICE_PREFIX):
        path = path[len(SERVICE_PREFIX):]
    return "/" + path.strip("/")


def _parse_body(event: dict) -> dict:
    raw = event.get("body")
    if not raw:
        return {}
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValidationError("Request body must be valid JSON") from exc


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    raise TypeError(f"Cannot serialize {type(value).__name__}")
