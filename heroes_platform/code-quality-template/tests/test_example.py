"""
Tests for example module
"""

from src.example import add_numbers, hello_world, multiply_numbers


def test_hello_world():
    """Test hello_world function"""
    result = hello_world()
    assert result == "Hello, World!"
    assert isinstance(result, str)


def test_add_numbers():
    """Test add_numbers function"""
    result = add_numbers(2, 3)
    assert result == 5
    assert isinstance(result, int)


def test_multiply_numbers():
    """Test multiply_numbers function"""
    result = multiply_numbers(4, 5)
    assert result == 20
    assert isinstance(result, int)


def test_add_numbers_negative():
    """Test add_numbers with negative numbers"""
    result = add_numbers(-1, -2)
    assert result == -3


def test_multiply_numbers_zero():
    """Test multiply_numbers with zero"""
    result = multiply_numbers(5, 0)
    assert result == 0
