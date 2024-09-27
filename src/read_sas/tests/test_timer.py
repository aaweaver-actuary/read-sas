import pytest
from unittest.mock import patch
import time
from read_sas.src._timer import timer


def func(x: float) -> str:
    time.sleep(x)
    return "done"


def test_timer_seconds():
    @timer
    def dummy_function() -> str:
        return func(1)

    with patch("builtins.print") as mock_print:
        result = dummy_function()
        assert result == "done"
        mock_print.assert_called_once()
        assert "Execution time:" in mock_print.call_args[0][0]
        assert "seconds" in mock_print.call_args[0][0]


def test_timer_milliseconds():
    @timer
    def dummy_function() -> str:
        return func(0.002)

    with patch("builtins.print") as mock_print:
        result = dummy_function()
        assert result == "done"
        mock_print.assert_called_once()
        assert "Execution time:" in mock_print.call_args[0][0]
        assert "milliseconds" in mock_print.call_args[0][0]


def test_timer_microseconds():
    @timer
    def dummy_function() -> str:
        return func(0.000002)

    with patch("builtins.print") as mock_print:
        result = dummy_function()
        assert result == "done"
        mock_print.assert_called_once()
        assert "Execution time:" in mock_print.call_args[0][0]
        assert "microseconds" in mock_print.call_args[0][0]


def test_timer_nanoseconds():
    @timer
    def dummy_function() -> str:
        return func(0.00000000002)

    with patch("builtins.print") as mock_print:
        result = dummy_function()
        assert result == "done"
        mock_print.assert_called_once()
        assert "Execution time:" in mock_print.call_args[0][0]
        assert "microseconds" in mock_print.call_args[0][0]
