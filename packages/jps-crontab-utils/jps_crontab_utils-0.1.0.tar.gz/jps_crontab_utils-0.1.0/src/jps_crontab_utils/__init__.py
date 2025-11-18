"""jps_crontab_utils – Crontab auditing and search tools.

This package provides two CLI tools:
- `check-crontab`: validate executables and metadata in crontab entries.
- `search-crontab`: query jobs by owner, repository, labels, etc.

Both tools use Typer for CLI and Rich for beautiful terminal output.
"""

from __future__ import annotations

from .check_crontab import app as check_app
from .search_crontab import app as search_app

__all__ = ["check_app", "search_app"]