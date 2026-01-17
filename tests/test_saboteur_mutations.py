import logging
import pytest

from typing import List

from saboteur.application.facade import Saboteur
from saboteur.infrastructure.strategies.injections import NullInjectionStrategy
from saboteur.infrastructure.strategies.flippings import TypeFlipStrategy
from saboteur.domain.mutation.strategies import MutationStrategy
from saboteur.domain.mutation.configs import MutationConfig


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")

@pytest.fixture
def mock_data():
    return {
        "age": 25,
        "name": "John",
        "active": True,
        "score": None
    }

@pytest.mark.parametrize(
    "strategies, apply_all_strategies, apply_all_keys, num_strategies_to_apply, num_keys_to_apply",
    [
        ([NullInjectionStrategy(),], True, True, None, None),
        ([TypeFlipStrategy(from_type=str, to_type=int),], True, True, None, None),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, True, None, None),
        ([NullInjectionStrategy(),], True, False, None, 1),
        ([TypeFlipStrategy(),], True, False, None, 1),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, False, None, 1),
        ([NullInjectionStrategy(),], False, True, 1, None),
        ([TypeFlipStrategy(),], False, True, 1, None),
        ([NullInjectionStrategy(), TypeFlipStrategy()], False, True, 1, None),
        ([NullInjectionStrategy(),], False, False, 1, 1),
        ([TypeFlipStrategy(),], False, False, 1, 1),
        ([NullInjectionStrategy(), TypeFlipStrategy()], False, False, 1, 1),
    ]
)
def test_saboteur_mutations(
    strategies: List[MutationStrategy],
    apply_all_strategies: bool,
    apply_all_keys: bool,
    num_strategies_to_apply: int,
    num_keys_to_apply: int,
    mock_data,
    logger,
):
    logger.debug(f"Testing with strategies: {strategies}")
    
    config = MutationConfig(
        strategies=strategies,
        apply_all_strategies=apply_all_strategies,
        apply_all_keys=apply_all_keys,
        num_strategies_to_apply=num_strategies_to_apply,
        num_keys_to_apply=num_keys_to_apply,
    )
    
    saboteur = Saboteur(config=config)
    mutated_data = saboteur.attack(mock_data)
    
    logger.debug(f"Original data: {mock_data}")
    logger.debug(f"Mutated data: {mutated_data}")
    
    assert isinstance(mutated_data, dict)
    assert set(mutated_data.keys()) == set(mock_data.keys())
    # assert mock_data != mutated_data