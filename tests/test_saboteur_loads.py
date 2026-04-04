import asyncio
import logging

import pytest

from saboteur.application.facade import Saboteur
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.results import LoadRequestRecord
from saboteur.domain.load.runners import LoadRunner
from saboteur.domain.load.strategies import LoadStrategy
from saboteur.infrastructure.load.strategies.linear import LinearLoadStrategy


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")


def test_saboteur_loads(logger, monkeypatch):
    async def fake_single_request(self, session, context):
        return LoadRequestRecord(status=200, ok=True, latency_ms=12.5)

    monkeypatch.setattr(LoadStrategy, "_single_request", fake_single_request)
    results = asyncio.run(
        Saboteur(
            async_runners=[
                LoadRunner(
                    config=LoadConfig(
                        strategies=[LinearLoadStrategy()],
                        apply_all_strategies=False,
                        num_strategies_to_apply=1,
                        url="https://example.com",
                        method="GET",
                        duration_seconds=1,
                        interval_seconds=0.1,
                        concurrency=2,
                    )
                )
            ]
        ).run_async()
    )

    logger.debug(f"Results: {results}")

    result = next(iter(results.values()))
    report = result.strategy_reports[0]

    assert "LinearLoadStrategy" in result.result
    assert report.strategy == "LinearLoadStrategy"
    assert report.summary.total_requests >= 2
    assert report.summary.failure_count == 0
    assert report.summary.success_rate == 1.0
    assert report.summary.average_latency_ms == 12.5
    assert report.summary.status_code_counts[200] == report.summary.total_requests
    assert all(response["ok"] for response in result.result["LinearLoadStrategy"])
