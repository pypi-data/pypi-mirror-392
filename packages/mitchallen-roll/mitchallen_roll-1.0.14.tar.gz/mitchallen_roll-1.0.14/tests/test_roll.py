"""Tests for mitchallen.roll package."""

import pytest

from mitchallen.roll import d6, d20, roll


def test_roll_default():
    """Test roll() with default 6 sides."""
    result = roll()
    assert isinstance(result, int)
    assert 1 <= result <= 6


def test_roll_custom_sides():
    """Test roll() with custom number of sides."""
    result = roll(20)
    assert isinstance(result, int)
    assert 1 <= result <= 20


def test_roll_single_side():
    """Test roll() with 1 side."""
    result = roll(1)
    assert result == 1


def test_roll_invalid_sides():
    """Test roll() raises ValueError for invalid sides."""
    with pytest.raises(ValueError, match="Number of sides must be at least 1"):
        roll(0)

    with pytest.raises(ValueError, match="Number of sides must be at least 1"):
        roll(-1)


def test_d6():
    """Test d6() returns value in correct range."""
    result = d6()
    assert isinstance(result, int)
    assert 1 <= result <= 6


def test_d20():
    """Test d20() returns value in correct range."""
    result = d20()
    assert isinstance(result, int)
    assert 1 <= result <= 20


def test_roll_distribution():
    """Test that roll() produces varied results."""
    results = [roll(6) for _ in range(100)]
    # Check we get at least 3 different values in 100 rolls
    assert len(set(results)) >= 3
    # Check all results are in valid range
    assert all(1 <= r <= 6 for r in results)
