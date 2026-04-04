import time
from collections import Counter

from saboteur.domain.base.runners import AsyncBaseRunner
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.strategies import LoadStrategy
from saboteur.domain.load.contexts import LoadContext
from saboteur.domain.load.results import (
    LoadResult,
    LoadSummary,
    LoadStrategyReport,
    LoadRequestRecord,
)


class LoadRunner(
    AsyncBaseRunner[
        LoadConfig,
        LoadStrategy,
        LoadContext,
        LoadResult,
    ]
):
    def _build_summary(self, responses: list[LoadRequestRecord]) -> LoadSummary:
        total_requests = len(responses)
        success_count = sum(1 for response in responses if response.ok)
        failure_count = total_requests - success_count
        latencies = [response.latency_ms for response in responses]
        status_code_counts = dict(Counter(response.status for response in responses))

        return LoadSummary(
            total_requests=total_requests,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=(success_count / total_requests) if total_requests else 0.0,
            average_latency_ms=(sum(latencies) / total_requests) if total_requests else 0.0,
            max_latency_ms=max(latencies, default=0.0),
            status_code_counts=status_code_counts,
        )

    def _wrap_into_context(self, config: LoadConfig) -> LoadContext:
        return LoadContext(
            url=config.url,
            method=config.method,
            headers=config.headers,
            body=config.body,
            duration_seconds=config.duration_seconds,
            interval_seconds=config.interval_seconds,
            concurrency=config.concurrency,
        )

    async def load(self) -> dict:
        responses = {}
        strategy_reports: list[LoadStrategyReport] = []
        context = self._wrap_into_context(self._config)
        strategies = await self._get_applicable_strategies(context)
        for strategy in strategies:
            context_with_response = await strategy.apply(context)
            assert context_with_response.responses is not None, (
                "Strategy did not return a response"
            )
            strategy_name = type(strategy).__name__
            responses[strategy_name] = [response.model_dump() for response in context_with_response.responses]
            strategy_reports.append(
                LoadStrategyReport(
                    strategy=strategy_name,
                    responses=context_with_response.responses,
                    summary=self._build_summary(context_with_response.responses),
                )
            )
        return responses, strategy_reports

    async def run(self) -> LoadResult:
        start = time.monotonic()
        responses, strategy_reports = await self.load()
        elapsed_time = time.monotonic() - start
        return LoadResult(
            result=responses,
            strategy_reports=strategy_reports,
            elapsed_time=elapsed_time,
        )
