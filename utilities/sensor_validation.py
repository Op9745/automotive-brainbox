"""Input validation helpers for synthetic automotive sensor data."""

import math


MIN_TEMPERATURE_C = -50.0
MAX_TEMPERATURE_C = 200.0


def validate_temperature(temperature: int | float) -> float:
    """Return a finite temperature in Celsius within this project's configured bounds.

    These bounds are demo-project validation limits, not a universal automotive
    sensor specification.
    """
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise TypeError("temperature must be a numeric value")
    value = float(temperature)
    if not math.isfinite(value):
        raise ValueError("temperature must be finite")
    if not MIN_TEMPERATURE_C <= value <= MAX_TEMPERATURE_C:
        raise ValueError(
            f"temperature {value} outside allowed range "
            f"[{MIN_TEMPERATURE_C}, {MAX_TEMPERATURE_C}] °C"
        )
    return value
