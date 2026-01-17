import json
import pytest
import random
import logging


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")


@pytest.fixture
def mock_data():
    with open("tests/resources/mock.json", "r") as json_file:
        return json.load(json_file)


def travel(data: dict, logger: logging.Logger, threshold=0.5):
    key_paths: list[str] = []
    probability = random.uniform(0, 1)

    def _travel(d: dict):
        key_list = list(d.keys())
        random_key = random.choice(key_list)
        key_paths.append(random_key)
        random_value = d[random_key]
        if probability < threshold or not isinstance(random_value, dict):
            logger.debug(f"Traveling to key: {random_key} and value: {random_value}")
            return random_value
        else:
            _travel(d[random_key])

    random_value = _travel(data)
    return key_paths, random_value


@pytest.mark.parametrize("threshold", [0.0, 0.3, 0.5, 0.7, 1.0])
def test_select_random_key(logger, mock_data, threshold):
    key_paths, value = travel(mock_data, logger, threshold=threshold)
    assert isinstance(key_paths, list)
    assert len(key_paths) >= 1
    logger.debug(f"Selected key paths: {key_paths}")
    logger.debug(f"Selected value: {value}")
