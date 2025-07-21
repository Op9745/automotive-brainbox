import pytest

class Vehicle:
    def __init__(self):
        self.mode = "idle"

    def switch_mode(self, new_mode):
        valid_modes = ["idle", "drive", "park"]
        if new_mode in valid_modes:
            self.mode = new_mode
        else:
            raise ValueError("Invalid mode")

@pytest.fixture
def vehicle():
    return Vehicle()

@pytest.mark.parametrize("input_mode,expected", [
    ("drive", "drive"),
    ("park", "park"),
    ("fly", "ValueError"),
])
def test_mode_switch(vehicle, input_mode, expected):
    if expected == "ValueError":
        with pytest.raises(ValueError):
            vehicle.switch_mode(input_mode)
    else:
        vehicle.switch_mode(input_mode)
        assert vehicle.mode == expected