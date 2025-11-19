"""Tests for pyvalidator core functions."""

from pylib-validator import Schema, validate


def test_validate():
    schema = Schema({"age": lambda x: isinstance(x, int) and x > 0})
    valid, errors = schema.validate({"age": 25})
    assert valid is True
    valid, errors = schema.validate({"age": -1})
    assert valid is False
