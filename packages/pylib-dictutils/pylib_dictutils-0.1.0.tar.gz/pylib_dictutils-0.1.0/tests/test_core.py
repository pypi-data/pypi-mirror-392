"""Tests for pydictutils core functions."""

from pylib-dictutils import deep_merge, flatten_dict, pick


def test_deep_merge():
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"d": 3}, "e": 4}
    result = deep_merge(d1, d2)
    assert result["b"]["c"] == 2
    assert result["b"]["d"] == 3


def test_flatten_dict():
    d = {"a": 1, "b": {"c": 2}}
    result = flatten_dict(d)
    assert result["b.c"] == 2


def test_pick():
    d = {"a": 1, "b": 2, "c": 3}
    assert pick(d, ["a", "b"]) == {"a": 1, "b": 2}
