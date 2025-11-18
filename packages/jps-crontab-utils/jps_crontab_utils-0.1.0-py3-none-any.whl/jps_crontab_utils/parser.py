"""Core parser for crontab files with metadata extraction and validation.

This module defines:
  - `CronJob`: a dataclass representing one crontab entry.
  - `CronParser`: parses raw crontab text into `CronJob` objects.

The parser supports:
  - Metadata comments immediately before a job
  - Multi-line commands with backslash continuation (POSIX-compliant)
  - Executable resolution via $PATH
  - Validation placeholders (populated by CLI tools)
"""

from __future__ import annotations

import os
import re
import shlex
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


# ----------------------------------------------------------------------
# Regex & constants
# ----------------------------------------------------------------------
# _COMMENT_REGEX = re.compile(
#     r"""^\s*#\s*   # leading # and optional spaces
#     (?P<key>[-\w]+)   # key (owner, owner-email, …)
#     \s*:\s*           # colon separator
#     (?P<value>.*?)    # value (trimmed later)
#     $""",
#     re.VERBOSE,
# )
_COMMENT_REGEX = re.compile(r'^\s*#\s*(?P<key>[-\w]+)\s*:\s*(?P<value>.*)$')

# Relaxed, whitespace-tolerant schedule parser
_SCHEDULE_REGEX = re.compile(
    r"""^\s*
    (?P<min>\S+)\s+
    (?P<hour>\S+)\s+
    (?P<dom>\S+)\s+
    (?P<month>\S+)\s+
    (?P<dow>\S+)\s+
    (?P<cmd>.+)$
    """,
    re.VERBOSE,
)

REQUIRED_KEYS: Set[str] = {
    "owner",
    "owner_email",
    "date_created",
    "reference",
    "code_repository",
}

RECOMMENDED_KEYS: Set[str] = {
    "labels",
    "description",
    "run_frequency",
    "notify_on_failure",
}


# ----------------------------------------------------------------------
@dataclass
class CronJob:
    """Represents a single crontab job with schedule, command, and metadata.

    Attributes:
        minute: Minute field (0-59, *, etc.)
        hour: Hour field (0-23, *, etc.)
        dom: Day of month (1-31, *, etc.)
        month: Month (1-12, *, etc.)
        dow: Day of week (0-7, *, etc.)
        command: Full command string (may include pipes, redirects, newlines)
        executable: Resolved absolute path of the first executable token
        metadata: Dictionary of key → value from comment block (keys normalised to underscores)

        # Validation results (populated by CLI tools)
        exists: Whether the executable file exists
        is_file: Whether the path is a regular file
        non_empty: Whether the file has size > 0
        executable_bit: Whether the file has +x bit set
        missing_required: Set of required metadata keys not present
        warnings: List of non-critical issues
    """

    minute: str
    hour: str
    dom: str
    month: str
    dow: str
    command: str
    executable: Path
    metadata: Dict[str, str]

    # Validation fields
    exists: bool = False
    is_file: bool = False
    non_empty: bool = False
    executable_bit: bool = False
    missing_required: Set[str] = field(default_factory=set)
    warnings: List[str] = field(default_factory=list)

    def first_token(self) -> str:
        """Return the first whitespace-separated token in the command.

        Returns:
            str: First token, or empty string if command is empty.
        """
        return shlex.split(self.command)[0] if self.command.strip() else ""

    def as_dict(self) -> Dict[str, object]:
        """Convert the job to a dictionary suitable for JSON output.

        Returns:
            Dict[str, object]: Serialized job with validation results.
        """
        return {
            "schedule": f"{self.minute} {self.hour} {self.dom} {self.month} {self.dow}",
            "command": self.command,
            "executable": str(self.executable),
            "metadata": self.metadata,
            "valid": self.exists and self.is_file and self.non_empty and self.executable_bit,
            "missing_required": list(self.missing_required),
            "warnings": self.warnings,
        }


# ----------------------------------------------------------------------
class CronParser:
    """Parses raw crontab text into `CronJob` objects with metadata.

    Supports:
      - POSIX line continuation (`\\\n`)
      - Metadata in comment blocks
      - Executable resolution via $PATH

    Attributes:
        path_search: List of directories to search for executables (defaults to $PATH).
    """

    def __init__(self, path_search: Optional[List[Path]] = None) -> None:
        """Initialize parser with optional PATH for executable resolution.

        Args:
            path_search: List of directories to search. If None, uses $PATH.
        """
        self.path_search: List[Path] = [
            Path(p) for p in (path_search or os.getenv("PATH", "").split(os.pathsep))
        ]

    def _resolve_executable(self, token: str) -> Path:
        """Resolve the first token to an absolute path if it exists.

        Args:
            token: Command token (e.g., "backup.sh" or "/usr/bin/python").

        Returns:
            Path: Absolute path to executable, or resolved token if not found.
        """
        if os.pathsep in token or token.startswith("/"):
            return Path(token).expanduser().resolve()

        for directory in self.path_search:
            candidate = (directory / token).resolve()
            if candidate.exists():
                return candidate
        return Path(token).expanduser().resolve()

    def parse(self, crontab_text: str) -> List[CronJob]:
        """Parse raw crontab text into a list of `CronJob` objects.

        The parser expects metadata in comment lines immediately before a job:
        owner: Jane Doe
        owner-email: jane.doe@synthbio.edu
        ...
        0 2 * * * /opt/scripts/backup.sh
        textSupports multi-line commands with backslash continuation:
        0 0 * * * /bin/bash -c "echo start && \
        sleep 1 && \
        echo done"
        
        Args:
            crontab_text: Full crontab content as a string.

        Returns:
            List[CronJob]: Parsed jobs with metadata and resolved executables.
        """
        lines = [line.rstrip("\n") for line in crontab_text.splitlines()]
        jobs: List[CronJob] = []
        current_meta: Dict[str, str] = {}
        schedule_parts: List[str] = []
        command: str = ""

        for raw_line in lines:
            stripped = raw_line.strip()

            # Blank line indicates job boundary — finalize any open job
            if not stripped:
                if schedule_parts:
                    self._finalize_job(jobs, schedule_parts, command, current_meta)
                    schedule_parts = []
                    command = ""
                    current_meta.clear()
                continue

            if stripped.startswith("#"):
                match = _COMMENT_REGEX.match(raw_line)
                if match:
                    key = match.group("key").lower().replace("-", "_")
                    value = match.group("value").strip()
                    current_meta[key] = value
                continue

            # Try strict schedule parsing (must match exactly five fields + command)
            sched_match = _SCHEDULE_REGEX.fullmatch(raw_line)
            if sched_match:
                # New job begins — finalize previous if any
                if schedule_parts:
                    self._finalize_job(jobs, schedule_parts, command, current_meta)
                    current_meta.clear()

                schedule_parts = [
                    sched_match.group("min"),
                    sched_match.group("hour"),
                    sched_match.group("dom"),
                    sched_match.group("month"),
                    sched_match.group("dow"),
                ]
                command = sched_match.group("cmd")
                continue

            # Continuation line (job already started and no new schedule line)
            if schedule_parts and raw_line.endswith("\\"):
                command += "\n" + stripped.rstrip("\\").rstrip()
                continue
            elif schedule_parts:
                command += "\n" + stripped
                continue

            # Otherwise ignore
            continue

        # Don't forget the last job
        if schedule_parts:
            self._finalize_job(jobs, schedule_parts, command, current_meta)
            current_meta.clear()

        return jobs

    def _finalize_job(
        self,
        jobs: List[CronJob],
        schedule_parts: List[str],
        command: str,
        current_meta: Dict[str, str],
    ) -> None:
        """Build and append a CronJob from collected data.

        Args:
            jobs: List to append the new job to.
            schedule_parts: List of 5 schedule fields.
            command: Full command string (may span multiple lines).
            current_meta: Metadata dictionary for this job.
        """
        # Ensure schedule_parts has exactly 5 fields
        minute, hour, dom, month, dow = schedule_parts[:5]
        first_token = shlex.split(command)[0] if command.strip() else ""
        executable = self._resolve_executable(first_token)

        job = CronJob(
            minute=minute,
            hour=hour,
            dom=dom,
            month=month,
            dow=dow,
            command=command,
            executable=executable,
            metadata=current_meta.copy(),
        )
        jobs.append(job)
