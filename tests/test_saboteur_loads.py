import json
import pytest
import logging
import asyncio

from typing import List

from saboteur.application.facade import Saboteur
from saboteur.infrastructure.load.strategies.linear import LinearLoadStrategy
from saboteur.domain.load.strategies import LoadStrategy
from saboteur.domain.load.configs import LoadConfig
from saboteur.domain.load.runners import LoadRunner


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")


@pytest.mark.parametrize(
    "strategies, apply_all_strategies, num_strategies_to_apply",
    [
        (
            [
                LinearLoadStrategy(),
            ],
            False,
            1,
        ),
    ],
)
def test_saboteur_loads(
    strategies: List[LoadStrategy],
    apply_all_strategies: bool,
    num_strategies_to_apply: int,
    logger,
):
    logger.debug(f"Testing with strategies: {strategies}")

    runners = [
        LoadRunner(
            config=LoadConfig(
                strategies=strategies,
                apply_all_strategies=apply_all_strategies,
                num_strategies_to_apply=num_strategies_to_apply,
                url="https://www.google.com",
                method="GET",
                # headers={},
                # body={},
                duration_seconds=10,
                interval_seconds=0.5,
                concurrency=10,
            )
        ),
    ]

    saboteur = Saboteur(async_runners=runners)
    results = asyncio.run(saboteur.run_async())
    logger.debug(f"Results: {results}")
