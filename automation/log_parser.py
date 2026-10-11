"""Parse timestamped ECU/application logs into lightweight structured entries."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Iterable


_TIMESTAMP_RE = re.compile(
    r"^(?P<timestamp>\\d{4}-\\d{2}-\\d{2}[ T]\\d{2}:\\d{2}:\\d{2}(?:[.,]\\d+)?)"
)
_LEVEL_RE = re.compile(
    r"^\\s*\\[?(?P<level>DEBUG|INFO|WARN(?:ING)?|ERROR|CRITICAL|FATAL)\\]?"
    r"\\b\\s*[:|\\-]?\\s*(?P<message>.*)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LogEntry:
    """One parsed log line; unstructured lines are retained as UNKNOWN entries."""

    line_number: int
    timestamp: str | None
    level: str
    message: str
    raw: str

    def to_dict(self) -> dict[str, int | str | None]:
        """Return a JSON-friendly representation."""
        return asdict(self)


def parse_log_line(line: str, line_number: int = 1) -> LogEntry | None:
    """Parse a single line, returning None for blank lines.

    Supported timestamps begin with YYYY-MM-DD HH:MM:SS or use a T separator.
    A severity token may follow the timestamp or appear at the start of the line.
    """
    raw = line.rstrip("\\r\\n")
    if not raw.strip():
        return None

    remainder = raw.strip()
    timestamp = None
    timestamp_match = _TIMESTAMP_RE.match(remainder)
    if timestamp_match:
        timestamp = timestamp_match.group("timestamp")
        remainder = remainder[timestamp_match.end():].lstrip(" ]|:-")

    level = "UNKNOWN"
    level_match = _LEVEL_RE.match(remainder)
    if level_match:
        level = level_match.group("level").upper()
        if level == "WARN":
            level = "WARNING"
        remainder = level_match.group("message").strip()

    return LogEntry(
        line_number=line_number,
        timestamp=timestamp,
        level=level,
        message=remainder,
        raw=raw,
    )


def parse_log_file(path: str | Path) -> list[LogEntry]:
    """Read and parse a UTF-8 text log, preserving unstructured nonblank lines."""
    entries: list[LogEntry] = []
    with Path(path).open("r", encoding="utf-8", errors="replace") as log_file:
        for line_number, line in enumerate(log_file, start=1):
            entry = parse_log_line(line, line_number=line_number)
            if entry is not None:
                entries.append(entry)
    return entries


def summarize_logs(entries: Iterable[LogEntry]) -> dict[str, object]:
    """Summarize total entries and counts by normalized severity."""
    materialized = list(entries)
    counts = Counter(entry.level for entry in materialized)
    return {
        "total": len(materialized),
        "by_level": dict(sorted(counts.items())),
        "error_count": counts["ERROR"] + counts["CRITICAL"] + counts["FATAL"],
    }
