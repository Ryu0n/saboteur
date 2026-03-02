from pydantic import Field

from saboteur.domain.load.enums import HTTPMethod
from saboteur.domain.base.configs import BaseConfig
from saboteur.domain.load.strategies import LoadStrategy


class LoadTestConfig(BaseConfig[LoadStrategy]):
    """Configuration for a load test."""

    total_requests: int = Field(
        ..., gt=0, description="Total number of requests to send."
    )
    concurrency: int = Field(
        default=1, gt=0, description="Number of concurrent requests."
    )
    url: str = Field(..., description="Target URL for the load test.")
    method: HTTPMethod = Field(
        default="GET", description="HTTP method (e.g., GET, POST)."
    )
    headers: dict = Field(
        default_factory=dict, description="HTTP headers to include in the requests."
    )
    body: dict = Field(default="", description="Request body for POST/PUT requests.")
