"""Unit tests for the crontab parser in jps_crontab_utils.parser.

Tests:
  - Parsing of valid crontab with normalised metadata
  - Executable resolution via PATH and absolute paths
  - Handling of missing metadata and continuation lines
"""

from __future__ import annotations

from pathlib import Path

from jps_crontab_utils.parser import CronJob, CronParser


def test_parse_sample_crontab(sample_crontab: str, mock_executable: Path) -> None:
    """Test parsing of a full-featured crontab with two jobs.

    Args:
        sample_crontab: Valid crontab content.
        mock_executable: Mock executable in PATH.
    """
    parser = CronParser()
    jobs: list[CronJob] = parser.parse(sample_crontab)

    assert len(jobs) == 2

    # First job
    job1 = jobs[0]
    assert job1.minute == "0"
    assert job1.hour == "2"
    assert job1.command == "/opt/scripts/backup.sh --all"
    assert job1.executable == Path("/opt/scripts/backup.sh")
    assert job1.metadata["owner"] == "Jane Doe"
    assert job1.metadata["owner_email"] == "jane.doe@synthbio.edu"
    assert job1.metadata["labels"] == "nightly, backup"
    assert "code_repository" in job1.metadata

    # Second job
    job2 = jobs[1]
    assert job2.minute == "15"
    assert "prod" in job2.metadata["labels"]


def test_resolve_executable_in_path(mock_executable: Path) -> None:
    """Test resolution of executable present in mocked PATH.

    Args:
        mock_executable: Path to executable in temp dir.
    """
    parser = CronParser()
    resolved: Path = parser._resolve_executable("backup.sh")
    assert resolved == mock_executable
    assert resolved.exists()


def test_resolve_absolute_path() -> None:
    """Test that absolute paths are preserved without PATH lookup."""
    parser = CronParser()
    resolved: Path = parser._resolve_executable("/bin/ls")
    assert resolved == Path("/bin/ls").resolve()


def test_missing_metadata() -> None:
    """Test parsing of a job with no metadata comments."""
    crontab = "30 3 * * * /bin/echo hello > /dev/null"
    parser = CronParser()
    jobs: list[CronJob] = parser.parse(crontab)
    assert len(jobs) == 1
    assert jobs[0].metadata == {}


def test_continuation_lines() -> None:
    """Test parsing of multi-line command with backslash continuation."""
    crontab = """
# owner: Test User
# owner-email: test@example.com
0 0 * * * /bin/bash -c \\
    "echo start && \\
     sleep 1 && \\
     echo done"
""".strip()
    parser = CronParser()
    jobs: list[CronJob] = parser.parse(crontab)
    assert len(jobs) == 1
    assert "sleep 1" in jobs[0].command
    assert jobs[0].metadata["owner"] == "Test User"
    assert jobs[0].metadata["owner_email"] == "test@example.com"