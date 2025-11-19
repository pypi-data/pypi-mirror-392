"""Tests for pysearchalgo core functions."""

from pylib-searchalgo import binary_search, linear_search, quick_sort, merge_sort


def test_binary_search():
    """Test binary_search."""
    arr = [1, 2, 3, 4, 5]
    assert binary_search(arr, 3) == 2
    assert binary_search(arr, 6) is None


def test_linear_search():
    """Test linear_search."""
    arr = [1, 2, 3, 4, 5]
    assert linear_search(arr, 3) == 2
    assert linear_search(arr, 6) is None


def test_quick_sort():
    """Test quick_sort."""
    arr = [3, 1, 4, 1, 5]
    assert quick_sort(arr) == [1, 1, 3, 4, 5]


def test_merge_sort():
    """Test merge_sort."""
    arr = [3, 1, 4, 1, 5]
    assert merge_sort(arr) == [1, 1, 3, 4, 5]
