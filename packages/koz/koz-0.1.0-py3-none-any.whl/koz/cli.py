"""Command-line interface for koz."""

from pathlib import Path
from typing import Optional

import click

from koz.analyzer import PatchAnalyzer
from koz.exporter import ReportExporter


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Koz - Python monkeypatch detection and analysis tool."""
    pass


@cli.command()
@click.argument(
    "project_path",
    type=click.Path(exists=True, file_okay=False, path_type=Path),  # type: ignore[type-var]
    default=".",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "toml"], case_sensitive=False),
    default="json",
    help="Output format (json or toml)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),  # type: ignore[type-var]
    default=None,
    help="Output file path (default: patches.<format>)",
)
@click.option(
    "--no-git",
    is_flag=True,
    default=False,
    help="Disable git metadata extraction",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress summary output",
)
def analyze(
    project_path: Path,
    format: str,
    output: Optional[Path],
    no_git: bool,
    quiet: bool,
) -> None:
    """Analyze a Python project for monkeypatches.

    PROJECT_PATH: Path to the Python project to analyze (default: current directory)
    """
    # Set default output path if not specified
    if output is None:
        output = Path(f"patches.{format}")

    # Run analysis
    click.echo(f"Analyzing project: {project_path.absolute()}")

    analyzer = PatchAnalyzer(project_path, use_git=not no_git)
    report = analyzer.analyze()

    # Export results
    exporter = ReportExporter()

    if format == "json":
        exporter.export_json(report, output)
    elif format == "toml":
        exporter.export_toml(report, output)

    click.echo(f"Report written to: {output.absolute()}")

    # Print summary unless quiet
    if not quiet:
        exporter.print_summary(report)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
