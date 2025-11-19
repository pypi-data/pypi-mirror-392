"""Export functionality for patch reports."""

import json
from pathlib import Path
from typing import Any

try:
    import tomli_w

    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False

from koz.schema import PatchReport


class ReportExporter:
    """Exports patch reports to various formats."""

    @staticmethod
    def export_json(report: PatchReport, output_path: Path) -> None:
        """Export report to JSON format.

        Args:
            report: Patch report to export
            output_path: Path to write JSON file

        Raises:
            IOError: If file cannot be written
        """
        data = report.model_dump(mode="json")
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    @staticmethod
    def export_toml(report: PatchReport, output_path: Path) -> None:
        """Export report to TOML format.

        Args:
            report: Patch report to export
            output_path: Path to write TOML file

        Raises:
            ImportError: If tomli-w is not installed
            IOError: If file cannot be written
        """
        if not TOML_AVAILABLE:
            raise ImportError(
                "tomli-w is required for TOML export. "
                "Install with: pip install tomli-w"
            )

        data = report.model_dump(mode="json")
        # Convert to TOML-compatible format
        toml_data = ReportExporter._prepare_for_toml(data)

        with output_path.open("wb") as f:
            tomli_w.dump(toml_data, f)

    @staticmethod
    def _prepare_for_toml(data: dict[str, Any]) -> dict[str, Any]:
        """Prepare data for TOML serialization.

        TOML has limitations compared to JSON, so we need to convert
        certain data structures.

        Args:
            data: Data dictionary to prepare

        Returns:
            TOML-compatible data dictionary
        """
        # Convert datetime objects to ISO format strings
        result: dict[str, Any] = {}
        for key, value in data.items():
            if value is None:
                # TOML doesn't support null values, skip them
                continue
            elif isinstance(value, dict):
                result[key] = ReportExporter._prepare_for_toml(value)
            elif isinstance(value, list):
                result[key] = [
                    (
                        ReportExporter._prepare_for_toml(item)
                        if isinstance(item, dict)
                        else str(item) if hasattr(item, "isoformat") else item
                    )
                    for item in value
                ]
            elif hasattr(value, "isoformat"):
                result[key] = value.isoformat()
            else:
                result[key] = value

        return result

    @staticmethod
    def print_summary(report: PatchReport) -> None:
        """Print a summary of the patch report to stdout.

        Args:
            report: Patch report to summarize
        """
        print(f"\n{'='*60}")
        print("Patch Detection Report")
        print(f"{'='*60}")
        print(f"Project: {report.project_path}")
        print(f"Scan Time: {report.scan_time.isoformat()}")
        print(f"Total Patches Found: {report.total_patches}")
        print(f"{'='*60}\n")

        if report.patches:
            # Group patches by type
            by_type: dict[str, list] = {}
            for patch in report.patches:
                patch_type = patch.patch_type.value
                if patch_type not in by_type:
                    by_type[patch_type] = []
                by_type[patch_type].append(patch)

            for patch_type, patches in by_type.items():
                print(f"\n{patch_type.upper()} ({len(patches)} patches):")
                print("-" * 60)
                for patch in patches:
                    print(f"  {patch.target_class}.{patch.target_method}")
                    print(f"    File: {patch.file_path}:{patch.line_start}")
                    if patch.author:
                        print(f"    Author: {patch.author}")
                    if patch.timestamp:
                        print(f"    Modified: {patch.timestamp.isoformat()}")
                    print()
        else:
            print("No patches detected.")

        print(f"{'='*60}\n")
