"""Tests for ATONDecoder."""
import pytest
from aton import ATONDecoder


def test_basic_decoding():
    decoder = ATONDecoder()
    aton = """
    @schema[id:int, name:str]
    
    users(1):
      1, "John"
    """
    result = decoder.decode(aton)
    assert "users" in result
    assert len(result["users"]) == 1
    assert result["users"][0]["id"] == 1
    assert result["users"][0]["name"] == "John"


def test_with_defaults():
    decoder = ATONDecoder()
    aton = """
    @schema[id:int, status:str]
    @defaults[status:"active"]
    
    items(2):
      1
      2
    """
    result = decoder.decode(aton)
    assert result["items"][0]["status"] == "active"
    assert result["items"][1]["status"] == "active"
