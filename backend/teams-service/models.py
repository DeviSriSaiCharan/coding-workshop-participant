"""Team domain model and input validation."""

from dataclasses import dataclass

from errors import ValidationError

MAX_FIELD_LENGTH = 100


@dataclass(frozen=True)
class TeamInput:
    """Validated data required to create or update a team."""

    name: str
    location: str = ""
    leader: str = ""

    @classmethod
    def from_payload(cls, payload: dict) -> "TeamInput":
        if not isinstance(payload, dict):
            raise ValidationError("Request body must be a JSON object")

        name = _clean_text(payload.get("name"), field="name")
        if not name:
            raise ValidationError("'name' is required")

        return cls(
            name=name,
            location=_clean_text(payload.get("location"), field="location"),
            leader=_clean_text(payload.get("leader"), field="leader"),
        )


def _clean_text(value, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValidationError(f"'{field}' must be a string")
    value = value.strip()
    if len(value) > MAX_FIELD_LENGTH:
        raise ValidationError(f"'{field}' must be at most {MAX_FIELD_LENGTH} characters")
    return value
