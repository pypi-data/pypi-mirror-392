#!/usr/bin/env python3
"""Parse a crontab file into structured job objects with normalized metadata.

Usage:
    jps-crontab-parse --file PATH [--json]

Options:
    --file PATH     Path to a crontab file to parse.
    --json          Output parsed jobs as JSON instead of table output.
    --help          Show this message and exit.

Description:
    This tool reads a crontab file and extracts all cron jobs,
    resolving metadata blocks, handling POSIX multiline commands,
    and locating the executable using the system PATH.

Metadata format:
    Metadata must be placed directly above a job, each line beginning with `#`.
    Example:
        # owner: Jane Doe
        # owner-email: jane@org.com
        0 1 * * * /path/to/script.sh

Examples:
    Parse a file and show table output:
        jps-crontab-parse --file crontab.txt

    Output JSON:
        jps-crontab-parse --file crontab.txt --json
"""

from __future__ import annotations

import json
from pathlib import Path
import stat
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .parser import CronJob, CronParser, REQUIRED_KEYS, RECOMMENDED_KEYS
from .utils import load_crontab


app = typer.Typer(
    name="check-crontab",
    help="Audit a crontab for executables and required metadata.",
    add_completion=False,
)

console = Console()


def validate_job(job: CronJob) -> None:
    """Populate validation fields on a `CronJob`.

    Args:
        job: The job to validate. Mutates in place.
    """
    exe = job.executable

    job.exists = exe.exists()
    job.is_file = exe.is_file()
    job.non_empty = exe.stat().st_size > 0 if job.is_file else False
    job.executable_bit = bool(exe.stat().st_mode & stat.S_IXUSR) if job.is_file else False

    # Required metadata
    missing = REQUIRED_KEYS - job.metadata.keys()
    job.missing_required.update(missing)

    # Warnings
    if not job.executable_bit and job.is_file:
        job.warnings.append("missing +x")
    if "labels" in job.metadata and not job.metadata["labels"].strip():
        job.warnings.append("empty labels")
    for rec in RECOMMENDED_KEYS - job.metadata.keys():
        job.warnings.append(f"missing recommended: {rec}")


@app.command()
def main(
    file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="Path to a crontab file"
    ),
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Read another user's crontab"
    ),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON instead of table"),
    fail_on_warnings: bool = typer.Option(
        False, "--fail-on-warnings", help="Exit with code 2 if only warnings exist"
    ),
) -> None:
    """Audit the specified crontab.

    Args:
        file: Path to crontab file (mutually exclusive with --user).
        user: Username to read crontab from.
        json_out: Output in JSON format.
        fail_on_warnings: Treat warnings as failure (exit code 2).

    Raises:
        typer.Exit: With appropriate exit code based on results.
    """
    if file and user:
        typer.echo("Error: Cannot specify both --file and --user.", err=True)
        raise typer.Exit(code=1)

    raw_crontab = load_crontab(file, user)
    parser = CronParser()
    jobs: List[CronJob] = parser.parse(raw_crontab)

    errors = 0
    warnings = 0

    for job in jobs:
        validate_job(job)
        if job.missing_required or not (
            job.exists and job.is_file and job.non_empty and job.executable_bit
        ):
            errors += 1
        if job.warnings:
            warnings += 1

    # JSON output
    if json_out:
        console.print(json.dumps([j.as_dict() for j in jobs], indent=2, default=str))
    else:
        table = Table(
            title=f"Crontab Audit – {len(jobs)} job(s)",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Schedule", style="dim")
        table.add_column("Executable", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Issues", style="yellow")

        for job in jobs:
            schedule = f"{job.minute} {job.hour} {job.dom} {job.month} {job.dow}"
            exe_name = job.executable.name

            if job.missing_required or not job.exists:
                status = "[red]ERROR[/red]"
            elif job.warnings:
                status = "[yellow]WARN[/yellow]"
            else:
                status = "[green]OK[/green]"

            issues: List[str] = []
            if job.missing_required:
                issues.append(f"missing: {', '.join(job.missing_required)}")
            if not job.exists:
                issues.append("not found")
            elif not job.is_file:
                issues.append("not a file")
            elif not job.non_empty:
                issues.append("empty")
            elif not job.executable_bit:
                issues.append("no +x")
            issues.extend(job.warnings)

            table.add_row(
                schedule,
                exe_name,
                status,
                "; ".join(issues) if issues else "—",
            )

        console.print(table)

    # Exit code
    exit_code = 0
    if errors:
        exit_code = 1
    elif warnings and fail_on_warnings:
        exit_code = 2
    raise typer.Exit(code=exit_code)


if __name__ == "__main__":
    app()