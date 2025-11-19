"""Tests for pycompare core functions."""

from pylib-compare import deep_diff, patch, compare


def test_deep_diff():
    d1 = {"a": 1}
    d2 = {"a": 2}
    diff = deep_diff(d1, d2)
    assert diff["a"]["op"] == "replace"


def test_compare():
    assert compare({"a": 1}, {"a": 1}) is True
    assert compare({"a": 1}, {"a": 2}) is False
