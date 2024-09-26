import pytest
from unittest.mock import patch
import time
from read_sas.src._timer import timer


# Sample functions to use for testing
@timer
def sample_function():
    time.sleep(0.1)  # simulate some work
    return "result"


@timer
def sample_function_with_args(a, b):
    time.sleep(0.1)  # simulate some work
    return a + b


@pytest.mark.parametrize(
    "func, args, kwargs, expected_result, mocked_times",
    [
        (sample_function, (), {}, "result", [1.0, 2.0]),  # basic function with no args
        (sample_function_with_args, (3, 4), {}, 7, [1.0, 2.0]),  # function with args
    ],
)
@patch("time.time", side_effect=[1.0, 2.0])  # Mock time to control execution time
def test_timer(mock_time, func, args, kwargs, expected_result, mocked_times, capsys):
    """Test the `timer` decorator to check the execution time print output.

    The `time.time` function is mocked to simulate consistent time differences.
    """
    # Call the decorated function
    result = func(*args, **kwargs)

    # Check the function's return value
    assert result == expected_result, f"Expected: {expected_result}, Got: {result}"

    # Capture the printed output
    captured = capsys.readouterr()
    assert (
        f"Function:\t{func.__name__}\t\t | Execution time:\t1.0 seconds" in captured.out
    ), f"Expected: 1.0 seconds, Got: {captured.out}"

    # Ensure `time.time` was called twice (start and end times)
    assert (
        mock_time.call_count == 2
    ), f"Expected 2 calls to time.time, Got: {mock_time.call_count}"


@pytest.mark.parametrize(
    "mocked_times",
    [
        ([5.0, 5.1]),  # short execution time
        ([100.0, 102.0]),  # longer execution time
    ],
)
@patch("time.time")
def test_timer_varied_times(mock_time, mocked_times, capsys):
    """Test the `timer` decorator with varied time durations."""
    mock_time.side_effect = mocked_times

    # Call the decorated function
    result = sample_function()

    # Check the result
    assert result == "result", f"Expected: 'result', Got: {result}"

    # Capture the printed output
    captured = capsys.readouterr()
    expected_execution_time = mocked_times[1] - mocked_times[0]
    assert (
        f"Function:\tsample_function\t\t | Execution time:\t{expected_execution_time} seconds"
        in captured.out
    ), f"Expected: {expected_execution_time} seconds, Got: {captured.out}"

    # Ensure time.time was called twice (start and end times)
    assert (
        mock_time.call_count == 2
    ), f"Expected 2 calls to time.time, Got: {mock_time.call_count}"
