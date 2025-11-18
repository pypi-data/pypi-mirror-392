"""Tests for the check_crontab CLI tool.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json
from typer.testing import CliRunner

from jps_crontab_utils.check_crontab import app

runner = CliRunner()


def test_check_crontab_file(
    tmp_crontab_file: Path,
    mock_executable: Path,
    mocker,
) -> None:
    """Test CLI audit with --file and valid crontab.

    Args:
        tmp_crontab_file: Temporary crontab file.
        mock_executable: Mock executable in PATH.
        mocker: Pytest-mock fixture.
    """
    # Mock file system checks — DO NOT mock stat.S_IXUSR
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.stat", return_value=mocker.Mock(st_size=100, st_mode=0o755))

    result = runner.invoke(app, ["--file", str(tmp_crontab_file)])
    assert result.exit_code == 0
    assert "Crontab Audit" in result.stdout
    assert "WARN" in result.stdout


def test_check_crontab_json(
    tmp_crontab_file: Path,
    mock_executable: Path,
    mocker,
) -> None:
    """Test JSON output mode.

    Args:
        tmp_crontab_file: Temporary crontab file.
        mock_executable: Mock executable.
        mocker: Pytest-mock fixture.
    """
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.stat", return_value=mocker.Mock(st_size=100, st_mode=0o755))

    result = runner.invoke(app, ["--file", str(tmp_crontab_file), "--json"])
    assert result.exit_code == 0

    data: list[dict[str, Any]] = json.loads(result.stdout)
    assert len(data) == 2
    assert data[0]["schedule"].startswith("0 2")
    assert "command" in data[0]


def test_check_crontab_missing_metadata(
    tmp_path: Path, mocker
) -> None:
    """Test detection of missing required metadata."""
    file_path = tmp_path / "bad.txt"
    file_path.write_text("0 1 * * * /bin/echo hi")

    # Mock real filesystem status
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.stat", return_value=mocker.Mock(st_size=100, st_mode=0o755))

    result = runner.invoke(app, ["--file", str(file_path)])
    assert result.exit_code == 1
    assert "missing" in result.stdout.lower()


def test_check_crontab_executable_not_found(
    tmp_crontab_file: Path,
    mocker,
) -> None:
    """Test audit failure when executable is not found.

    Args:
        tmp_crontab_file: Temporary crontab file.
        mocker: Pytest-mock fixture.
    """
    # Mock the resolver to return a non-existent path
    mocker.patch(
        "jps_crontab_utils.parser.CronParser._resolve_executable",
        return_value=Path("/nonexistent/backup.sh")
    )

    result = runner.invoke(app, ["--file", str(tmp_crontab_file)])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()
