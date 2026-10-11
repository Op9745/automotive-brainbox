from automation.log_parser import parse_log_line, parse_log_file, summarize_logs


def test_parse_timestamped_error_line():
    entry = parse_log_line("2026-10-11 12:34:56 ERROR ECU timeout", line_number=7)
    assert entry is not None
    assert entry.timestamp == "2026-10-11 12:34:56"
    assert entry.level == "ERROR"
    assert entry.message == "ECU timeout"
    assert entry.line_number == 7


def test_parse_bracketed_warning_and_normalize_level():
    entry = parse_log_line("2026-10-11T12:34:56.123 [WARN] bus load high")
    assert entry is not None
    assert entry.level == "WARNING"
    assert entry.message == "bus load high"


def test_preserve_unstructured_lines_and_ignore_blank_lines(tmp_path):
    assert parse_log_line("   ") is None
    entry = parse_log_line("unexpected diagnostic output")
    assert entry is not None
    assert entry.level == "UNKNOWN"
    assert entry.message == "unexpected diagnostic output"

    log_path = tmp_path / "ecu.log"
    log_path.write_text("INFO startup\n\nERROR timeout\n", encoding="utf-8")
    entries = parse_log_file(log_path)
    assert [item.line_number for item in entries] == [1, 3]
    assert summarize_logs(entries) == {
        "total": 2,
        "by_level": {"ERROR": 1, "INFO": 1},
        "error_count": 1,
    }
