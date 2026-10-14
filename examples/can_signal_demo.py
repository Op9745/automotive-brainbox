"""Run from repository root: python examples/can_signal_demo.py"""
from can_tools.signal_decoder import SignalDefinition, decode_frame

FRAME_DEFINITIONS = {
    0x180: [
        SignalDefinition("VehicleSpeed_kph", 0, 16, factor=0.1, maximum=300),
        SignalDefinition("EngineSpeed_rpm", 16, 16, maximum=9000),
    ]
}
# Synthetic bytes only; these are not captured vehicle/network data.
payload = bytes([0xFA, 0x00, 0xB8, 0x0B, 0, 0, 0, 0])
print(decode_frame(0x180, payload, FRAME_DEFINITIONS))
