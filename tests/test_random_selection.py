import json
import pytest
import random


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")


@pytest.fixture
def mock_data():
    with open("tests/resources/mock.json", "r") as json_file:
        return json.load(json_file)


def travel(data: dict, logger: logging.Logger, threshold=0.5):
    probability = random.uniform(0, 1)

    def _travel(d, path=""):
        key_list = list(d.keys())
        random_key = random.choice(key_list)
        random_value = d[random_key]
        if probability < threshold or not isinstance(random_value, dict):
            logger.debug(f"Traveling to key: {random_key} and value: {random_value}")
            return
        else:
            _travel(d[random_key])

    _travel(data)


@pytest.mark.parametrize("threshold", [0.0, 0.3, 0.5, 0.7, 1.0])
def test_select_random_key(logger, mock_data, threshold):
    travel(mock_data, logger, threshold=threshold)
