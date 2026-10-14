import pytest

from can_tools.signal_decoder import SignalDefinition, decode_frame, decode_signal, extract_raw_value


def test_decode_little_endian_scaled_speed():
    definition = SignalDefinition("VehicleSpeed", 0, 16, factor=0.5, maximum=250)
    assert decode_signal(bytes([123, 0]), definition) == 61.5


def test_decode_big_endian_dbc_sawtooth_nibble():
    definition = SignalDefinition("Nibble", 0, 4, byte_order="big")
    assert extract_raw_value(bytes([0xA0]), definition) == 10


def test_decode_signed_twos_complement():
    assert extract_raw_value(bytes([0xFE]), SignalDefinition("Offset", 0, 8, signed=True)) == -2


def test_decode_frame_by_id():
    definitions = {0x123: [
        SignalDefinition("Speed", 0, 8, factor=0.5),
        SignalDefinition("RPM", 8, 8, factor=100),
    ]}
    assert decode_frame(0x123, bytes([100, 30]), definitions) == {"Speed": 50.0, "RPM": 3000.0}


@pytest.mark.parametrize("kwargs", [
    {"name": "bad", "start_bit": -1, "length": 1},
    {"name": "bad", "start_bit": 0, "length": 0},
    {"name": "bad", "start_bit": 0, "length": 65},
    {"name": "bad", "start_bit": 0, "length": 1, "byte_order": "middle"},
])
def test_invalid_definition_rejected(kwargs):
    with pytest.raises(ValueError):
        SignalDefinition(**kwargs)


def test_signal_outside_payload_rejected():
    with pytest.raises(ValueError, match="extends beyond payload"):
        decode_signal(bytes([0]), SignalDefinition("Bad", 7, 2))


def test_physical_limit_enforced():
    with pytest.raises(ValueError, match="above maximum"):
        decode_signal(bytes([101]), SignalDefinition("Speed", 0, 8, maximum=100))


def test_unknown_frame_id_rejected():
    with pytest.raises(KeyError, match="no signal definitions"):
        decode_frame(0x321, bytes([0]), {0x123: []})


def test_classical_can_payload_maximum_eight_bytes():
    with pytest.raises(ValueError, match="cannot exceed 8 bytes"):
        decode_frame(0x123, bytes(9), {0x123: []})
