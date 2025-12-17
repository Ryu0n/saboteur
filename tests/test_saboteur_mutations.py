import logging
import pytest
from saboteur.application.facade import Saboteur
from saboteur.infrastructure.strategies.injections import NullInjectionStrategy
from saboteur.infrastructure.strategies.flippings import TypeFlipStrategy


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
    "strategies",
    [
        [NullInjectionStrategy(),],
        [TypeFlipStrategy(),],
        [NullInjectionStrategy(), TypeFlipStrategy()],
    ]
)
def test_saboteur_mutations(strategies, mock_data, logger):
    logger.debug(f"Testing with strategies: {strategies}")
    
    saboteur = Saboteur(strategies=strategies)
    mutated_data = saboteur.attack(mock_data)
    
    logger.debug(f"Original data: {mock_data}")
    logger.debug(f"Mutated data: {mutated_data}")
    
    assert isinstance(mutated_data, dict)
    assert set(mutated_data.keys()) == set(mock_data.keys())
    assert mock_data != mutated_data