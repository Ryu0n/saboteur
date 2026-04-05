import json
import pytest
from pathlib import Path

from saboteur.domain.mutation.contexts import MutationContext


@pytest.fixture
def mock_data():
    path = Path(__file__).parent / "resources" / "mock.json"
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# MutationContext.mutate()
# ---------------------------------------------------------------------------

def test_mutate_top_level_key(mock_data):
    ctx = MutationContext(key_paths=["age"], value=99, value_type=int)
    result = ctx.mutate(mock_data)
    assert result["age"] == 99
    assert mock_data["age"] != 99  # original is not modified (deepcopy)


def test_mutate_nested_key(mock_data):
    ctx = MutationContext(key_paths=["nested", "height"], value=200.0, value_type=float)
    result = ctx.mutate(mock_data)
    assert result["nested"]["height"] == 200.0
    assert mock_data["nested"]["height"] == 175.5  # original unchanged


def test_mutate_deeply_nested_key(mock_data):
    ctx = MutationContext(
        key_paths=["nested", "nested_level_2", "city"],
        value="Seoul",
        value_type=str,
    )
    result = ctx.mutate(mock_data)
    assert result["nested"]["nested_level_2"]["city"] == "Seoul"
    assert mock_data["nested"]["nested_level_2"]["city"] == "New York"


def test_mutate_injects_none(mock_data):
    ctx = MutationContext(key_paths=["name"], value=None, value_type=type(None))
    result = ctx.mutate(mock_data)
    assert result["name"] is None


def test_mutate_does_not_modify_original(mock_data):
    import copy
    original_copy = copy.deepcopy(mock_data)
    ctx = MutationContext(key_paths=["age"], value=0, value_type=int)
    ctx.mutate(mock_data)
    assert mock_data == original_copy


def test_mutate_invalid_path_raises_value_error(mock_data):
    # "age" is an int, not a dict, so descending further should raise.
    ctx = MutationContext(key_paths=["age", "nonexistent"], value=1, value_type=int)
    with pytest.raises((ValueError, TypeError, KeyError)):
        ctx.mutate(mock_data)
