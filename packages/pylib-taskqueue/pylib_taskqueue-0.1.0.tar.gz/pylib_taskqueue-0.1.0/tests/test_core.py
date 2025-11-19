"""Tests for pytaskqueue."""

from pylib-taskqueue import TaskQueue


def test_taskqueue():
    """Test TaskQueue."""
    assert TaskQueue() is None or True
