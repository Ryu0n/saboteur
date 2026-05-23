import asyncio
import logging

import pytest

from saboteur.application.facade import Saboteur
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.results import LoadRequestRecord
from saboteur.domain.load.runners import LoadRunner
from saboteur.domain.load.strategies import LoadStrategy
from saboteur.infrastructure.load.strategies.linear import LinearLoadStrategy
from saboteur.infrastructure.load.strategies.random import RandomLoadStrategy


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


def test_saboteur_random_loads(logger, monkeypatch):
    async def fake_single_request(self, session, context):
        return LoadRequestRecord(status=200, ok=True, latency_ms=8.0)

    monkeypatch.setattr(LoadStrategy, "_single_request", fake_single_request)
    results = asyncio.run(
        Saboteur(
            async_runners=[
                LoadRunner(
                    config=LoadConfig(
                        strategies=[RandomLoadStrategy()],
                        apply_all_strategies=False,
                        num_strategies_to_apply=1,
                        url="https://example.com",
                        method="GET",
                        duration_seconds=1,
                        interval_seconds=0.1,
                        random_interval=(0.0, 0.05),
                        concurrency=2,
                        seed=42,
                    )
                )
            ]
        ).run_async()
    )

    logger.debug(f"Results: {results}")

    result = next(iter(results.values()))
    report = result.strategy_reports[0]

    assert "RandomLoadStrategy" in result.result
    assert report.strategy == "RandomLoadStrategy"
    assert report.summary.total_requests >= 2
    assert report.summary.failure_count == 0
    assert report.summary.success_rate == 1.0
    assert report.summary.average_latency_ms == 8.0


def test_random_load_strategy_respects_interval_bounds(monkeypatch):
    import saboteur.infrastructure.load.strategies.random as strategy_module

    original_uniform = strategy_module.random.uniform
    sampled: list[float] = []

    def recording_uniform(a, b):
        v = original_uniform(a, b)
        sampled.append(v)
        return v

    monkeypatch.setattr(strategy_module.random, "uniform", recording_uniform)

    async def fake_single_request(self, session, context):
        return LoadRequestRecord(status=200, ok=True, latency_ms=1.0)

    monkeypatch.setattr(LoadStrategy, "_single_request", fake_single_request)

    asyncio.run(
        Saboteur(
            async_runners=[
                LoadRunner(
                    config=LoadConfig(
                        strategies=[RandomLoadStrategy()],
                        apply_all_strategies=False,
                        num_strategies_to_apply=1,
                        url="https://example.com",
                        method="GET",
                        duration_seconds=1,
                        interval_seconds=0.1,
                        random_interval=(0.01, 0.03),
                        concurrency=1,
                        seed=7,
                    )
                )
            ]
        ).run_async()
    )

    assert sampled, "expected at least one interval sample"
    for v in sampled:
        assert 0.01 <= v <= 0.03


def test_random_load_strategy_is_deterministic_with_seed(monkeypatch):
    import saboteur.infrastructure.load.strategies.random as strategy_module

    original_uniform = strategy_module.random.uniform
    recorded: list[float] = []

    def recording_uniform(a, b):
        v = original_uniform(a, b)
        recorded.append(v)
        return v

    monkeypatch.setattr(strategy_module.random, "uniform", recording_uniform)

    async def fake_single_request(self, session, context):
        return LoadRequestRecord(status=200, ok=True, latency_ms=1.0)

    monkeypatch.setattr(LoadStrategy, "_single_request", fake_single_request)

    def run_with_seed(seed: int) -> list[float]:
        recorded.clear()
        asyncio.run(
            Saboteur(
                async_runners=[
                    LoadRunner(
                        config=LoadConfig(
                            strategies=[RandomLoadStrategy()],
                            apply_all_strategies=False,
                            num_strategies_to_apply=1,
                            url="https://example.com",
                            method="GET",
                            duration_seconds=1,
                            interval_seconds=0.1,
                            random_interval=(0.0, 0.05),
                            concurrency=1,
                            seed=seed,
                        )
                    )
                ]
            ).run_async()
        )
        return list(recorded)

    run_a = run_with_seed(42)
    run_b = run_with_seed(42)
    run_c = run_with_seed(999)

    common_ab = min(len(run_a), len(run_b))
    common_ac = min(len(run_a), len(run_c))
    assert common_ab >= 3, "need enough samples to verify determinism"
    assert run_a[:common_ab] == run_b[:common_ab]
    assert run_a[:common_ac] != run_c[:common_ac]
