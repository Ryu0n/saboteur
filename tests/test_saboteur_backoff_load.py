import pytest
import asyncio
import logging
from saboteur.application.facade import Saboteur
from saboteur.infrastructure.load.strategies.backoff import ExponentialBackoffLoadStrategy
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.runners import LoadRunner

@pytest.fixture
def logger():
    return logging.getLogger("saboteur")

@pytest.mark.asyncio
async def test_exponential_backoff_load(logger):
    strategies = [
        ExponentialBackoffLoadStrategy(
            initial_interval=0.1,
            multiplier=2.0,
            max_interval=1.0
        ),
    ]

    runners = [
        LoadRunner(
            config=LoadConfig(
                strategies=strategies,
                url="https://www.google.com",
                method="GET",
                duration_seconds=3,
                concurrency=2,
            )
        ),
    ]

    saboteur = Saboteur(async_runners=runners)
    results = await saboteur.run_async()
    
    logger.debug(f"Results: {results}")
    
    # Check if we have results
    assert len(results) > 0
    for runner_id, result in results.items():
        assert result.result is not None
        # We expect at least one batch to have run
        for strategy_responses in result.result.values():
            assert len(strategy_responses) >= 2
