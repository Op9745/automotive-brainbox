import pytest

def parse_signal(signal):
    required_keys = {"speed", "rpm", "latency"}
    if not all(key in signal for key in required_keys):
        raise ValueError("Invalid signal data")
    return signal

def assert_data_freshness(signal):
    assert signal["latency"] < 100, "Signal latency too high"

def test_valid_signal_parsing():
    signal = {"speed": 80, "rpm": 3000, "latency": 50}
    parsed = parse_signal(signal)
    assert parsed["speed"] == 80
    assert_data_freshness(parsed)

def test_invalid_signal_missing_field():
    signal = {"speed": 80, "latency": 20}
    with pytest.raises(ValueError):
        parse_signal(signal)