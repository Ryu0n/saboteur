from pydantic import Field

from saboteur.domain.load.enums import HTTPMethod
from saboteur.domain.base.configs import BaseConfig
from saboteur.domain.load.strategies import LoadStrategy


class LoadConfig(BaseConfig[LoadStrategy]):
    """Configuration for a load test."""

    url: str = Field(..., description="Target URL for the load test.")
    method: HTTPMethod = Field(
        default="GET", description="HTTP method (e.g., GET, POST)."
    )
    headers: dict = Field(
        default_factory=dict, description="HTTP headers to include in the requests."
    )
    body: dict | None = Field(
        default=None, description="Request body for POST/PUT requests."
    )

    duration_seconds: int = Field(
        default=60, gt=0, description="Duration of the load test in seconds."
    )
    interval_seconds: float = Field(
        default=1.0,
        gt=0,
        description="Interval between requests in seconds. (For linear load strategy)",
    )
    concurrency: int = Field(
        default=1, gt=0, description="Number of concurrent requests."
    )
