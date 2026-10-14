# CAN signal tooling (Phase 2)

A dependency-free starter decoder for synthetic Classical CAN frames. It demonstrates bit extraction, signed values, scaling/offset, signal bounds, and frame-ID-based decoding.

## Quick start

From the repository root, run:

    python examples/can_signal_demo.py
    pytest tests/practice_week_01/test_can_signal_decoder.py -q

## Supported behavior

- Little-endian signals: start_bit is the least-significant-bit index.
- Big-endian signals: start_bit uses DBC sawtooth numbering (bit 0 is the MSB of byte 0).
- Signed two's-complement decoding, factor and offset conversion, optional physical min/max validation.
- Standard 11-bit CAN IDs (0x000–0x7FF), payloads up to 8 bytes.
- Explicit errors for invalid definitions, signals outside payload, unknown frame IDs, and physical values outside configured limits.

## Limitations and safety

This is an educational decoder for synthetic frames, not a complete DBC parser or physical CAN adapter. It does not handle CAN FD, multiplexed signals, checksums, counters, or timing. Confirm bit positions, byte order, scaling, and valid ranges against the target network specification before using real data. Do not connect it to or transmit on a live vehicle bus as part of this demo.
