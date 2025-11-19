"""Tests for ATONEncoder."""
import pytest
from aton import ATONEncoder


def test_basic_encoding():
    encoder = ATONEncoder(optimize=True)
    data = {"users": [{"id": 1, "name": "John"}]}
    result = encoder.encode(data)
    assert "users(1):" in result
    assert '"John"' in result


def test_schema_generation():
    encoder = ATONEncoder(include_schema=True)
    data = {"products": [{"id": 1, "price": 99.99}]}
    result = encoder.encode(data)
    assert "@schema" in result
    assert "id:int" in result
    assert "price:float" in result


def test_defaults_generation():
    encoder = ATONEncoder(include_defaults=True)
    data = {
        "items": [
            {"id": 1, "status": "active"},
            {"id": 2, "status": "active"},
            {"id": 3, "status": "active"},
        ]
    }
    result = encoder.encode(data)
    assert "@defaults" in result
    assert 'status:"active"' in result
