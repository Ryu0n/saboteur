import json
import random
from pathlib import Path

import pytest

from saboteur.utils.sampling import uniform_sample_from_dict, sample_unique_paths_from_dict


@pytest.fixture
def mock_data():
    path = Path(__file__).parent / "resources" / "mock.json"
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# uniform_sample_from_dict
# ---------------------------------------------------------------------------

def test_uniform_sample_returns_path_and_value(mock_data):
    key_paths, value = uniform_sample_from_dict(mock_data)
    assert isinstance(key_paths, list)
    assert len(key_paths) >= 1
    assert key_paths[0] in mock_data


def test_uniform_sample_stop_threshold_one_always_stops_at_top(mock_data):
    """threshold=1.0 means probability < 1.0 is always True, so always stops at depth 1."""
    for _ in range(20):
        key_paths, _ = uniform_sample_from_dict(mock_data, stop_threshold=1.0)
        assert len(key_paths) == 1


def test_uniform_sample_with_rng_is_reproducible(mock_data):
    rng1 = random.Random(99)
    rng2 = random.Random(99)
    result1 = uniform_sample_from_dict(mock_data, rng=rng1)
    result2 = uniform_sample_from_dict(mock_data, rng=rng2)
    assert result1 == result2


def test_uniform_sample_rng_does_not_advance_global_random(mock_data):
    """Passing an rng instance must not touch the global random state."""
    state_before = random.getstate()
    uniform_sample_from_dict(mock_data, rng=random.Random(7))
    assert random.getstate() == state_before


# ---------------------------------------------------------------------------
# sample_unique_paths_from_dict
# ---------------------------------------------------------------------------

def test_sample_unique_count_zero_returns_empty(mock_data):
    result = sample_unique_paths_from_dict(mock_data, count=0)
    assert result == []


def test_sample_unique_returns_requested_count(mock_data):
    result = sample_unique_paths_from_dict(mock_data, count=2)
    assert len(result) == 2


def test_sample_unique_paths_are_unique(mock_data):
    result = sample_unique_paths_from_dict(mock_data, count=3)
    paths = [tuple(key_paths) for key_paths, _ in result]
    assert len(paths) == len(set(paths))


def test_sample_unique_with_rng_is_reproducible(mock_data):
    rng1 = random.Random(42)
    rng2 = random.Random(42)
    result1 = sample_unique_paths_from_dict(mock_data, count=3, rng=rng1)
    result2 = sample_unique_paths_from_dict(mock_data, count=3, rng=rng2)
    assert result1 == result2


@pytest.mark.parametrize("threshold", [0.0, 0.3, 0.5, 0.7, 1.0])
def test_sample_unique_various_thresholds(mock_data, threshold):
    result = sample_unique_paths_from_dict(mock_data, count=2, stop_threshold=threshold)
    assert len(result) >= 1
    for key_paths, _ in result:
        assert isinstance(key_paths, list)
        assert len(key_paths) >= 1
