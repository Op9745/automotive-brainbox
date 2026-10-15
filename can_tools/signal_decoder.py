"""Dependency-free decoder for synthetic Classical CAN frames."""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Mapping, Sequence


@dataclass(frozen=True)
class SignalDefinition:
    name: str
    start_bit: int
    length: int
    byte_order: str = "little"
    signed: bool = False
    factor: float = 1.0
    offset: float = 0.0
    minimum: float | None = None
    maximum: float | None = None

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("signal name cannot be empty")
        if isinstance(self.start_bit, bool) or not isinstance(self.start_bit, int) or self.start_bit < 0:
            raise ValueError("start_bit must be a non-negative integer")
        if isinstance(self.length, bool) or not isinstance(self.length, int) or not 1 <= self.length <= 64:
            raise ValueError("length must be an integer from 1 to 64")
        if self.byte_order not in {"little", "big"}:
            raise ValueError("byte_order must be 'little' or 'big'")
        if not math.isfinite(self.factor) or not math.isfinite(self.offset):
            raise ValueError("factor and offset must be finite")
        if self.minimum is not None and not math.isfinite(self.minimum):
            raise ValueError("minimum must be finite")
        if self.maximum is not None and not math.isfinite(self.maximum):
            raise ValueError("maximum must be finite")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("minimum cannot exceed maximum")


def _validate_payload(payload: bytes | bytearray | Sequence[int]) -> bytes:
    try:
        data = bytes(payload)
    except (TypeError, ValueError) as exc:
        raise TypeError("payload must be a sequence of byte values") from exc
    if len(data) > 8:
        raise ValueError("Classical CAN payload cannot exceed 8 bytes")
    return data


def extract_raw_value(payload: bytes | bytearray | Sequence[int], definition: SignalDefinition) -> int:
    """Extract a raw integer. Little-endian starts at LSB bit index; big-endian uses DBC sawtooth numbering."""
    data = _validate_payload(payload)
    if definition.byte_order == "little":
        if definition.start_bit + definition.length > len(data) * 8:
            raise ValueError("signal extends beyond payload")
        raw = (int.from_bytes(data, "little") >> definition.start_bit) & ((1 << definition.length) - 1)
    else:
        if definition.start_bit + definition.length > len(data) * 8:
            raise ValueError("signal extends beyond payload")
        # DBC Motorola start-bit numbering is sawtooth: bit 0 is the MSB
        # of byte 0 and bit 7 is its LSB. Consecutive positions therefore
        # move toward the LSB, then continue at the next byte's MSB.
        raw = 0
        for position in range(definition.start_bit, definition.start_bit + definition.length):
            byte_index, bit_in_byte = divmod(position, 8)
            raw = (raw << 1) | ((data[byte_index] >> (7 - bit_in_byte)) & 1)
    if definition.signed and raw & (1 << (definition.length - 1)):
        raw -= 1 << definition.length
    return raw


def decode_signal(payload: bytes | bytearray | Sequence[int], definition: SignalDefinition) -> float:
    """Convert raw value to physical units and enforce optional physical limits."""
    value = extract_raw_value(payload, definition) * definition.factor + definition.offset
    if definition.minimum is not None and value < definition.minimum:
        raise ValueError(f"{definition.name} value {value} below minimum {definition.minimum}")
    if definition.maximum is not None and value > definition.maximum:
        raise ValueError(f"{definition.name} value {value} above maximum {definition.maximum}")
    return value


def decode_frame(frame_id: int, payload: bytes | bytearray | Sequence[int],
                 definitions_by_frame: Mapping[int, Sequence[SignalDefinition]]) -> dict[str, float]:
    """Decode configured signals for a standard 11-bit CAN ID."""
    if isinstance(frame_id, bool) or not isinstance(frame_id, int) or not 0 <= frame_id <= 0x7FF:
        raise ValueError("frame_id must be a standard 11-bit CAN identifier (0..0x7FF)")
    data = _validate_payload(payload)
    if frame_id not in definitions_by_frame:
        raise KeyError(f"no signal definitions configured for CAN ID 0x{frame_id:X}")
    result = {}
    for definition in definitions_by_frame[frame_id]:
        if definition.name in result:
            raise ValueError(f"duplicate signal name in frame definition: {definition.name}")
        result[definition.name] = decode_signal(data, definition)
    return result
