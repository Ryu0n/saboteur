import asyncio
import logging

import pytest

from saboteur.application.facade import Saboteur
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.results import LoadRequestRecord
from saboteur.domain.load.runners import LoadRunner
from saboteur.domain.load.strategies import LoadStrategy
from saboteur.infrastructure.load.strategies.backoff import ExponentialBackoffLoadStrategy


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")


def test_exponential_backoff_load(logger, monkeypatch):
    responses = [
        LoadRequestRecord(status=200, ok=True, latency_ms=10.0),
        LoadRequestRecord(status=503, ok=False, latency_ms=25.0, error="upstream unavailable"),
    ]
    call_count = {"count": 0}

    async def fake_single_request(self, session, context):
        index = call_count["count"] % len(responses)
        call_count["count"] += 1
        return responses[index]

    monkeypatch.setattr(LoadStrategy, "_single_request", fake_single_request)
    results = asyncio.run(
        Saboteur(
            async_runners=[
                LoadRunner(
                    config=LoadConfig(
                        strategies=[
                            ExponentialBackoffLoadStrategy(
                                initial_interval=0.05,
                                multiplier=2.0,
                                max_interval=0.1,
                                jitter=False,
                            )
                        ],
                        url="https://example.com",
                        method="GET",
                        duration_seconds=1,
                        concurrency=2,
                    )
                )
            ]
        ).run_async()
    )

    logger.debug(f"Results: {results}")

    result = next(iter(results.values()))
    report = result.strategy_reports[0]

    assert report.strategy == "ExponentialBackoffLoadStrategy"
    assert report.summary.total_requests >= 2
    assert report.summary.success_count * 2 == report.summary.total_requests
    assert report.summary.failure_count == report.summary.success_count
    assert report.summary.status_code_counts[200] == report.summary.success_count
    assert report.summary.status_code_counts[503] == report.summary.failure_count
    assert any(response.error for response in report.responses)
