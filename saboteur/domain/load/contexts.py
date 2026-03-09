from dataclasses import dataclass, field

from saboteur.domain.base.contexts import BaseContext


@dataclass
class LoadContext(BaseContext):
    """Context for HTTP request load testing."""
    url: str
    method: str
    headers: dict
    body: dict | None
    duration_seconds: int
    interval_seconds: float
    concurrency: int
    responses: list[dict] = field(default_factory=list)
