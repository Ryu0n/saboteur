import json
import pytest
import logging

from typing import List

from saboteur.application.facade import Saboteur
from saboteur.infrastructure.mutation.strategies.injections import NullInjectionStrategy
from saboteur.infrastructure.mutation.strategies.flippings import TypeFlipStrategy
from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.configs import MutationConfig
from saboteur.domain.mutation.runners import MutationRunner
from saboteur.domain.mutation.results import MutationResult


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")


@pytest.fixture
def mock_data():
    with open("tests/resources/mock.json", "r") as json_file:
        return json.load(json_file)


@pytest.mark.parametrize(
    "strategies, apply_all_strategies, num_strategies_to_apply",
    [
        (
            [
                NullInjectionStrategy(),
            ],
            True,
            None,
        ),
        (
            [
                TypeFlipStrategy(to_type=int),
            ],
            True,
            None,
        ),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, None),
        (
            [
                NullInjectionStrategy(),
            ],
            True,
            None,
        ),
        (
            [
                TypeFlipStrategy(),
            ],
            True,
            None,
        ),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, None),
        (
            [
                NullInjectionStrategy(),
            ],
            False,
            1,
        ),
        (
            [
                TypeFlipStrategy(),
            ],
            False,
            1,
        ),
        ([NullInjectionStrategy(), TypeFlipStrategy()], False, 1),
        (
            [
                NullInjectionStrategy(),
            ],
            False,
            1,
        ),
        (
            [
                TypeFlipStrategy(),
            ],
            False,
            1,
        ),
        ([NullInjectionStrategy(), TypeFlipStrategy()], False, 1),
    ],
)
def test_saboteur_mutations(
    strategies: List[MutationStrategy],
    apply_all_strategies: bool,
    num_strategies_to_apply: int,
    mock_data,
    logger,
):
    logger.debug(f"Testing with strategies: {strategies}")

    runners = [
        MutationRunner(
            config=MutationConfig(
                strategies=strategies,
                apply_all_strategies=apply_all_strategies,
                num_strategies_to_apply=num_strategies_to_apply,
                original_data=mock_data,
            )
        ),
    ]

    saboteur = Saboteur(runners=runners)
    results = saboteur.run()
    result = next(iter(results.values()))

    logger.debug(f"Original data: {mock_data}")
    logger.debug(f"Mutated data: {results}")

    assert isinstance(result, MutationResult)
    assert isinstance(result.result, dict)
    assert set(result.result.keys()) == set(mock_data.keys())
    assert len(result.applied_mutations) <= max(1, len(strategies))


def test_mutation_result_includes_trace_for_multiple_targets(mock_data):
    runner = MutationRunner(
        config=MutationConfig(
            strategies=[
                NullInjectionStrategy(),
                TypeFlipStrategy(to_type=str),
            ],
            apply_all_strategies=False,
            num_strategies_to_apply=1,
            original_data=mock_data,
            max_targets=2,
            seed=42,
        )
    )

    result = runner.run()

    assert len(result.applied_mutations) == 2
    assert [trace.key_path for trace in result.applied_mutations] == [
        ["age"],
        ["name"],
    ]
    assert [trace.strategy for trace in result.applied_mutations] == [
        "NullInjectionStrategy",
        "NullInjectionStrategy",
    ]
    assert result.result["age"] is None
    assert result.result["name"] is None


def test_mutation_seed_produces_reproducible_result(mock_data):
    config = MutationConfig(
        strategies=[
            NullInjectionStrategy(),
            TypeFlipStrategy(to_type=str),
        ],
        apply_all_strategies=False,
        num_strategies_to_apply=1,
        original_data=mock_data,
        max_targets=2,
        seed=5,
    )

    first_result = MutationRunner(config=config).run()
    second_result = MutationRunner(config=config).run()

    assert first_result.result == second_result.result
    assert first_result.applied_mutations == second_result.applied_mutations
