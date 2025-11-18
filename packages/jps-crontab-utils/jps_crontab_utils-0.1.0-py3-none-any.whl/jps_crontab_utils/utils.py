"""Utility functions shared across CLI tools."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


def load_crontab(file: Optional[Path], user: Optional[str]) -> str:
    """Load crontab content from file or via `crontab -l`.

    Args:
        file: Path to a crontab file. If provided, reads from file.
        user: Username to read crontab for (uses `crontab -l -u user`).

    Returns:
        str: Full crontab content.

    Raises:
        RuntimeError: If `crontab -l` fails and no file is provided.
    """
    if file:
        return file.read_text(encoding="utf-8")

    cmd = ["crontab", "-l"]
    if user:
        cmd += ["-u", user]

    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Failed to read crontab for user '{user or 'current'}': {exc}") from exc