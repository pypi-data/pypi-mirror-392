"""Tests for pydateutils core functions."""

from datetime import datetime
from pylib-dateutils import days_between, add_days, format_date


def test_days_between():
    d1 = datetime(2023, 1, 1)
    d2 = datetime(2023, 1, 10)
    assert days_between(d1, d2) == 9


def test_add_days():
    d = datetime(2023, 1, 1)
    result = add_days(d, 5)
    assert result.day == 6
