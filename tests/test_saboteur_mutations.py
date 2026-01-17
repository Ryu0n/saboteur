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
    "strategies, apply_all_strategies, num_strategies_to_apply",
    [
        ([NullInjectionStrategy(),], True, None),
        ([TypeFlipStrategy(from_type=str, to_type=int),], True, None),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, None),
        ([NullInjectionStrategy(),], True, None),
        ([TypeFlipStrategy(),], True, None),
        ([NullInjectionStrategy(), TypeFlipStrategy()], True, None),
        ([NullInjectionStrategy(),], False, 1),
        ([TypeFlipStrategy(),], False, 1),
        ([NullInjectionStrategy(), TypeFlipStrategy()], False, 1),
        ([NullInjectionStrategy(),], False, 1),
        ([TypeFlipStrategy(),], False, 1),
        ([NullInjectionStrategy(), TypeFlipStrategy()], False, 1),
    ]
)
def test_saboteur_mutations(
    strategies: List[MutationStrategy],
    apply_all_strategies: bool,
    num_strategies_to_apply: int,
    mock_data,
    logger,
):
    logger.debug(f"Testing with strategies: {strategies}")
    
    config = MutationConfig(
        strategies=strategies,
        apply_all_strategies=apply_all_strategies,
        num_strategies_to_apply=num_strategies_to_apply,
    )
    
    saboteur = Saboteur(config=config)
    mutated_data = saboteur.attack(mock_data)
    
    logger.debug(f"Original data: {mock_data}")
    logger.debug(f"Mutated data: {mutated_data}")
    
    assert isinstance(mutated_data, dict)
    assert set(mutated_data.keys()) == set(mock_data.keys())
    # assert mock_data != mutated_data