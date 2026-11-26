"""Small parser for DUTPilot markers and simulator diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
import re


ERROR_RE = re.compile(r"\b(?:syntax error|error|fatal)\b", re.IGNORECASE)
WARNING_RE = re.compile(r"\bwarning\b", re.IGNORECASE)

# Zero-valued tallies such as "0 errors", "errors: 0" or "no warnings" are run
# summaries, not diagnostics. Counting them would turn a clean run into a false
# failure.
ZERO_ERROR_RE = re.compile(
    r"\b(?:0|zero|no)\s+errors?\b|\berrors?\s*[:=]\s*(?:0|none)\b",
    re.IGNORECASE,
)
ZERO_WARNING_RE = re.compile(
    r"\b(?:0|zero|no)\s+warnings?\b|\bwarnings?\s*[:=]\s*(?:0|none)\b",
    re.IGNORECASE,
)

MARKER_TOKENS = ("DUTPILOT_PASS", "DUTPILOT_FAIL")


@dataclass(frozen=True)
class ParsedLog:
    markers: dict[str, list[str]]
    errors: list[str]
    warnings: list[str]


def parse_logs(*logs: str) -> ParsedLog:
    """Split simulator output into markers, errors and warnings.

    Marker lines are recorded only in ``markers``. They are never classified as
    diagnostics, because the failure reason they carry is already surfaced
    through ``markers`` and ``primary_error``.
    """

    markers: dict[str, list[str]] = {"pass": [], "fail": []}
    errors: list[str] = []
    warnings: list[str] = []

    for log in logs:
        for raw_line in log.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if "DUTPILOT_PASS" in line:
                markers["pass"].append(line)
            if "DUTPILOT_FAIL" in line:
                markers["fail"].append(line)
            if any(token in line for token in MARKER_TOKENS):
                continue

            if ERROR_RE.search(line) and not ZERO_ERROR_RE.search(line):
                errors.append(line)
            if WARNING_RE.search(line) and not ZERO_WARNING_RE.search(line):
                warnings.append(line)

    return ParsedLog(markers=markers, errors=errors, warnings=warnings)
