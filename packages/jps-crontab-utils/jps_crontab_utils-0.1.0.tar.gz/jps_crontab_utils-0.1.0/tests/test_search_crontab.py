"""Integration tests for the search-crontab CLI tool.

Tests metadata-based search with normalised keys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from jps_crontab_utils.search_crontab import app

runner = CliRunner()


def test_search_by_label(tmp_crontab_file: Path, mock_executable: Path) -> None:
    """Test search by label (AND logic).

    Args:
        tmp_crontab_file: Temporary crontab file.
        mock_executable: Mock executable in PATH.
    """
    result = runner.invoke(app, [
        "--file", str(tmp_crontab_file),
        "--label", "nightly"
    ])
    assert result.exit_code == 0
    assert "backup.sh" in result.stdout
    assert "Jane Doe" in result.stdout


def test_search_by_repo(tmp_crontab_file: Path) -> None:
    """Test exact match search by code-repository.

    Args:
        tmp_crontab_file: Temporary crontab file.
    """
    result = runner.invoke(app, [
        "--file", str(tmp_crontab_file),
        "--repo", "git@gitlab.com:synthbio/pipeline.git"
    ])
    assert result.exit_code == 0
    assert "backup.sh" in result.stdout


def test_search_by_owner_email(tmp_crontab_file: Path) -> None:
    """Test substring search in owner-email field.

    Args:
        tmp_crontab_file: Temporary crontab file.
    """
    result = runner.invoke(app, [
        "--file", str(tmp_crontab_file),
        "--email", "john.smith"
    ])
    assert result.exit_code == 0
    assert "etl" in result.stdout


def test_search_no_matches(tmp_crontab_file: Path) -> None:
    """Test that no matches returns exit code 1.

    Args:
        tmp_crontab_file: Temporary crontab file.
    """
    result = runner.invoke(app, [
        "--file", str(tmp_crontab_file),
        "--label", "nonexistent"
    ])
    assert result.exit_code == 1
    assert "No matches found" in result.stdout


def test_search_json_output(tmp_crontab_file: Path) -> None:
    """Test JSON output for search results.

    Args:
        tmp_crontab_file: Temporary crontab file.
    """
    result = runner.invoke(app, [
        "--file", str(tmp_crontab_file),
        "--label", "prod",
        "--json"
    ])
    assert result.exit_code == 0

    import json
    data: list[dict[str, Any]] = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["metadata"]["labels"] == "prod, hourly"