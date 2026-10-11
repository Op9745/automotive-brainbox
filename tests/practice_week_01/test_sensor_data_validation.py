import pytest

from utilities.sensor_validation import validate_temperature


@pytest.mark.parametrize("temperature", [-50.0, -40.0, 0.0, 150.0, 200.0])
def test_temperature_within_bounds_is_accepted(temperature):
    assert validate_temperature(temperature) == float(temperature)


@pytest.mark.parametrize("temperature", [-50.1, 200.1, 9999.9])
def test_temperature_outside_bounds_is_rejected(temperature):
    with pytest.raises(ValueError, match="outside allowed range"):
        validate_temperature(temperature)


@pytest.mark.parametrize("temperature", [None, "25", True, float("nan"), float("inf")])
def test_non_numeric_or_non_finite_temperature_is_rejected(temperature):
    with pytest.raises((TypeError, ValueError)):
        validate_temperature(temperature)
