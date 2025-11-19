"""Tests for pyserializer core functions."""

from pylib-serializer import serialize, to_json


def test_serialize():
    obj = {"a": 1, "b": 2}
    result = serialize(obj)
    assert "a" in result
    assert "1" in result
