from pydantic import BaseModel, Field

from saboteur.domain.base.results import BaseResult


class LoadRequestRecord(BaseModel):
    status: int = Field(..., description="HTTP status code or synthesized error status.")
    ok: bool = Field(..., description="Whether the request completed with a successful status.")
    latency_ms: float = Field(..., ge=0.0, description="End-to-end request latency in milliseconds.")
    error: str | None = Field(default=None, description="Captured exception message, if any.")


class LoadSummary(BaseModel):
    total_requests: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    average_latency_ms: float = Field(default=0.0, ge=0.0)
    max_latency_ms: float = Field(default=0.0, ge=0.0)
    status_code_counts: dict[int, int] = Field(default_factory=dict)


class LoadStrategyReport(BaseModel):
    strategy: str = Field(..., description="Strategy class name used for the load test.")
    responses: list[LoadRequestRecord] = Field(default_factory=list)
    summary: LoadSummary = Field(default_factory=LoadSummary)


class LoadResult(BaseResult):
    strategy_reports: list[LoadStrategyReport] = Field(
        default_factory=list,
        description="Detailed per-strategy request records and summary metrics.",
    )
