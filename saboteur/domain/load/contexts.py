from dataclasses import dataclass, field

from saboteur.domain.base.contexts import BaseContext
from saboteur.domain.load.results import LoadRequestRecord


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
    random_interval: tuple[float, float] = (0.0, 1.0)
    responses: list[LoadRequestRecord] = field(default_factory=list)
