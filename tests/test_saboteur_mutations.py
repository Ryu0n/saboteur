import json
import pytest
import logging
from pathlib import Path
from typing import List

from saboteur.application.facade import Saboteur
from saboteur.infrastructure.mutation.strategies.injections import NullInjectionStrategy
from saboteur.infrastructure.mutation.strategies.flippings import TypeFlipStrategy
from saboteur.infrastructure.mutation.strategies.randomizations import (
    IntegerRandomizationStrategy,
    FloatRandomizationStrategy,
    BooleanRandomizationStrategy,
    ListRandomizationStrategy,
    DictRandomizationStrategy,
)
from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.configs import MutationConfig
from saboteur.domain.mutation.contexts import MutationContext
from saboteur.domain.mutation.runners import MutationRunner
from saboteur.domain.mutation.results import MutationResult


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")


@pytest.fixture
def mock_data():
    path = Path(__file__).parent / "resources" / "mock.json"
    with open(path, "r") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "strategies, apply_all_strategies, num_strategies_to_apply",
    [
        ([NullInjectionStrategy()], True, None),
        ([TypeFlipStrategy(to_type=int)], True, None),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, None),
        ([NullInjectionStrategy()], True, None),
        ([TypeFlipStrategy()], True, None),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, None),
        ([NullInjectionStrategy()], False, 1),
        ([TypeFlipStrategy()], False, 1),
        ([NullInjectionStrategy(), TypeFlipStrategy()], False, 1),
        ([NullInjectionStrategy()], False, 1),
        ([TypeFlipStrategy()], False, 1),
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


# ---------------------------------------------------------------------------
# Saboteur runner management API
# ---------------------------------------------------------------------------

def test_saboteur_register_and_list_runners(mock_data):
    saboteur = Saboteur()
    assert saboteur.list_runners() == []

    runner = MutationRunner(
        config=MutationConfig(
            strategies=[NullInjectionStrategy()],
            original_data=mock_data,
        )
    )
    saboteur.register_runner(runner)
    assert runner in saboteur.list_runners()


def test_saboteur_unregister_runner(mock_data):
    runner = MutationRunner(
        config=MutationConfig(
            strategies=[NullInjectionStrategy()],
            original_data=mock_data,
        )
    )
    saboteur = Saboteur(runners=[runner])
    saboteur.unregister_runner(runner)
    assert saboteur.list_runners() == []


def test_saboteur_get_runner(mock_data):
    runner = MutationRunner(
        config=MutationConfig(
            strategies=[NullInjectionStrategy()],
            original_data=mock_data,
        )
    )
    saboteur = Saboteur(runners=[runner])
    assert saboteur.get_runner(id(runner)) is runner
    assert saboteur.get_runner(0) is None


# ---------------------------------------------------------------------------
# Strategy-level unit tests
# ---------------------------------------------------------------------------

def test_type_flip_strategy_picks_different_types_each_instantiation():
    """Each TypeFlipStrategy() call must independently sample a type."""
    types_seen = set()
    for _ in range(50):
        strategy = TypeFlipStrategy()
        ctx = MutationContext(key_paths=["x"], value=42, value_type=int)
        if strategy.is_applicable(ctx):
            mutated = strategy.apply(ctx)
            types_seen.add(type(mutated.value))
    # After 50 instantiations we expect more than one target type.
    assert len(types_seen) > 1


def test_list_randomization_strategy_skips_empty_list():
    from saboteur.infrastructure.mutation.strategies.randomizations import ListRandomizationStrategy
    strategy = ListRandomizationStrategy()
    ctx = MutationContext(key_paths=["x"], value=[], value_type=list)
    assert not strategy.is_applicable(ctx)


def test_list_randomization_strategy_applies_to_non_empty_list():
    from saboteur.infrastructure.mutation.strategies.randomizations import ListRandomizationStrategy
    strategy = ListRandomizationStrategy()
    ctx = MutationContext(key_paths=["x"], value=[1, 2, 3], value_type=list)
    assert strategy.is_applicable(ctx)
    result = strategy.apply(ctx)
    assert isinstance(result.value, list)
    assert len(result.value) == 3


def test_dict_randomization_strategy_shuffles_values():
    strategy = DictRandomizationStrategy()
    # Use a dict where all values are distinct so a shuffle is detectable.
    original = {"a": 1, "b": 2, "c": 3}
    ctx = MutationContext(key_paths=["x"], value=original, value_type=dict)
    assert strategy.is_applicable(ctx)

    found_difference = False
    for _ in range(30):
        result = strategy.apply(ctx)
        assert set(result.value.keys()) == set(original.keys())
        if result.value != original:
            found_difference = True
            break
    assert found_difference, "DictRandomizationStrategy never produced a different mapping"


def test_dict_randomization_strategy_not_applicable_for_single_key():
    strategy = DictRandomizationStrategy()
    ctx = MutationContext(key_paths=["x"], value={"a": 1}, value_type=dict)
    assert not strategy.is_applicable(ctx)


def test_boolean_randomization_strategy(mock_data):
    strategy = BooleanRandomizationStrategy()
    ctx = MutationContext(key_paths=["active"], value=True, value_type=bool)
    assert strategy.is_applicable(ctx)
    result = strategy.apply(ctx)
    assert isinstance(result.value, bool)


def test_float_randomization_strategy(mock_data):
    strategy = FloatRandomizationStrategy()
    ctx = MutationContext(key_paths=["nested", "height"], value=175.5, value_type=float)
    assert strategy.is_applicable(ctx)
    result = strategy.apply(ctx)
    assert isinstance(result.value, float)


def test_integer_randomization_strategy(mock_data):
    strategy = IntegerRandomizationStrategy()
    ctx = MutationContext(key_paths=["age"], value=25, value_type=int)
    assert strategy.is_applicable(ctx)
    result = strategy.apply(ctx)
    assert isinstance(result.value, int)
