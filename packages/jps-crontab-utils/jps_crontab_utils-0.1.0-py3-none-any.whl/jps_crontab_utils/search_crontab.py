#!/usr/bin/env python3
"""Search metadata fields in a crontab file.

Usage:
    jps-crontab-search --file PATH [--label LBL] [--repo URL]
                       [--email EMAIL] [--json]

Options:
    --file PATH     Path to crontab file to search.
    --label LBL     Match jobs that contain ALL specified labels.
                    Multiple --label flags may be provided.
    --repo URL      Match exact code-repository value.
    --email EMAIL   Match owner-email (substring match).
    --json          Output matching jobs as JSON.
    --help          Show this message and exit.

Search Behavior:
    - Label search uses AND logic.
      Example: --label nightly --label backup
      matches jobs whose label list includes BOTH.

    - Owner-email uses substring match
      Example: --email smith

    - Code-repository must match exactly.

Examples:
    Search by label:
        jps-crontab-search --file crontab.txt --label nightly

    Search by owner email:
        jps-crontab-search --file crontab.txt --email jane.doe

    JSON output for automation:
        jps-crontab-search --file crontab.txt --label prod --json

"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .parser import CronJob, CronParser
from .utils import load_crontab


app = typer.Typer(
    name="search-crontab",
    help="Search crontab jobs by owner, repository, labels, etc.",
    add_completion=False,
)

console = Console()


def build_predicate(
    repo: Optional[str],
    label: Optional[str],
    owner: Optional[str],
    email: Optional[str],
    reference: Optional[str],
) -> Callable[[CronJob], bool]:
    """Build a combined predicate from search criteria.

    All non-None criteria are AND-ed together.

    Args:
        repo: Exact code-repository match.
        label: Comma-separated labels (all must be present).
        owner: Substring in owner field.
        email: Substring in owner-email.
        reference: Substring in reference URL.

    Returns:
        Callable[[CronJob], bool]: Predicate function.
    """
    predicates: List[Callable[[CronJob], bool]] = []

    if repo:
        repo_lower = repo.lower()
        predicates.append(
            lambda j: j.metadata.get("code_repository", "").lower() == repo_lower
        )

    if label:
        wanted = {l.strip().lower() for l in label.split(",") if l.strip()}
        predicates.append(
            lambda j: wanted.issubset(
                {l.strip().lower() for l in j.metadata.get("labels", "").split(",") if l.strip()}
            )
        )

    if owner:
        owner_lower = owner.lower()
        predicates.append(lambda j: owner_lower in j.metadata.get("owner", "").lower())

    if email:
        email_lower = email.lower()
        predicates.append(lambda j: email_lower in j.metadata.get("owner_email", "").lower())

    if reference:
        ref_lower = reference.lower()
        predicates.append(lambda j: ref_lower in j.metadata.get("reference", "").lower())

    def combined(job: CronJob) -> bool:
        return all(p(job) for p in predicates)

    return combined


@app.command()
def main(
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Crontab file"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Another user"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Exact code-repository URL"),
    label: Optional[str] = typer.Option(None, "--label", help="Comma-separated labels (AND)"),
    owner: Optional[str] = typer.Option(None, "--owner", help="Substring of owner"),
    email: Optional[str] = typer.Option(None, "--email", help="Substring of owner-email"),
    reference: Optional[str] = typer.Option(None, "--reference", help="Substring of reference URL"),
    json_out: bool = typer.Option(False, "--json", help="Emit JSON"),
) -> None:
    """Search crontab jobs using metadata filters.

    Args:
        file: Path to crontab file.
        user: User to read crontab from.
        repo, label, owner, email, reference: Search criteria.
        json_out: Output in JSON format.

    Raises:
        typer.Exit: 1 if no criteria or no matches.
    """
    if file and user:
        typer.echo("Error: Cannot use both --file and --user.", err=True)
        raise typer.Exit(1)

    if not any((repo, label, owner, email, reference)):
        typer.echo("Error: At least one search criterion is required.", err=True)
        raise typer.Exit(1)

    raw = load_crontab(file, user)
    parser = CronParser()
    jobs: List[CronJob] = parser.parse(raw)

    predicate = build_predicate(repo, label, owner, email, reference)
    matches = [j for j in jobs if predicate(j)]

    if json_out:
        console.print(json.dumps([j.as_dict() for j in matches], indent=2, default=str))
        return

    if not matches:
        console.print("[bold red]No matches found.[/bold red]")
        raise typer.Exit(1)

    table = Table(title=f"{len(matches)} match(es)", show_header=True, header_style="bold cyan")
    table.add_column("Schedule")
    table.add_column("Command", overflow="fold")
    table.add_column("Metadata", overflow="fold")

    for job in matches:
        sched = f"{job.minute} {job.hour} {job.dom} {job.month} {job.dow}"
        meta_lines = "\n".join(f"{k}: {v}" for k, v in job.metadata.items())
        table.add_row(sched, job.command.strip(), meta_lines)

    console.print(table)


if __name__ == "__main__":
    app()