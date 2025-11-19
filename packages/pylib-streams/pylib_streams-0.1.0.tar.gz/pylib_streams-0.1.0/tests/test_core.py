"""Tests for pystreams core functions."""

from pylib-streams import Stream, map, filter, reduce


def test_stream():
    """Test Stream."""
    result = Stream([1, 2, 3]).map(lambda x: x * 2).filter(lambda x: x > 3).to_list()
    assert result == [4, 6]


def test_map():
    """Test map."""
    assert map(lambda x: x * 2, [1, 2, 3]) == [2, 4, 6]


def test_filter():
    """Test filter."""
    assert filter(lambda x: x > 2, [1, 2, 3, 4]) == [3, 4]


def test_reduce():
    """Test reduce."""
    assert reduce(lambda a, b: a + b, [1, 2, 3]) == 6
