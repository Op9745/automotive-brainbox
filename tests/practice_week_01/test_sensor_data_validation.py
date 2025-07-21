import pytest

@pytest.mark.parametrize("temperature", [-40.0, 0.0, 150.0, None, 9999.9])

def test_temperature_bounds(temperature):
    if temperature is None:
        pytest.skip("Temperature is None")
    assert -50.0 <= temperature <= 200.0, f"Temperature {temperature} out of bounds"