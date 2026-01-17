import json
import copy
import pytest
import logging


@pytest.fixture
def logger():
    return logging.getLogger("saboteur")

@pytest.fixture
def mock_data():
    with open("tests/resources/mock.json", "r") as json_file:
        return json.load(json_file)


@pytest.mark.parametrize(
    "key_paths, original_value",
    [
        (["age"], "Alice"),
        (["name"], 30),
        (["nested", "height"], "dark"),
        (["nested", "nested_level_2", "city"], True),
    ]
)
def test_muate_with_references(mock_data, logger, key_paths, original_value):
    copied = copy.deepcopy(mock_data)
    t = copied
    
    for k in key_paths[:-1]:
        t = t[k]
        if not isinstance(t, dict):
            raise ValueError(f"Invalid key path: {key_paths}")
    
    t[key_paths[-1]] = original_value
    logger.debug(f"Mutated data: {copied}")