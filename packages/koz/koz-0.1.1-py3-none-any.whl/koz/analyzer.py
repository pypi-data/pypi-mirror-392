"""Main analyzer orchestrating patch detection."""

from pathlib import Path
from typing import Optional

from koz.config import KozConfig
from koz.detector import PatchDetector
from koz.git_integration import GitMetadataExtractor
from koz.parser import ASTWalker
from koz.schema import PatchReport


class PatchAnalyzer:
    """Orchestrates patch detection across a codebase."""

    def __init__(
        self,
        project_path: Path,
        use_git: bool = True,
        config: Optional[KozConfig] = None,
    ) -> None:
        """Initialize the patch analyzer.

        Args:
            project_path: Root path of the project to analyze
            use_git: Whether to extract git metadata
            config: Optional configuration for filtering files
        """
        self.project_path = project_path
        self.use_git = use_git
        self.config = config

        # Initialize walker with config patterns if provided
        include_patterns = config.include if config else None
        exclude_patterns = config.exclude if config else None
        self.walker = ASTWalker(project_path, include_patterns, exclude_patterns)

        self.detector = PatchDetector()
        self.git_extractor = GitMetadataExtractor(project_path) if use_git else None

    def analyze(self) -> PatchReport:
        """Analyze the project and generate a patch report.

        Returns:
            Complete patch report with all detected patches
        """
        report = PatchReport(project_path=str(self.project_path))

        # Walk through all Python files
        for file_path, tree in self.walker.walk_files():
            # Detect patches in this file
            patches = self.detector.detect_patches(file_path, tree)

            # Add git metadata if available
            if self.git_extractor and self.git_extractor.is_git_available():
                for patch in patches:
                    timestamp, author = self.git_extractor.get_file_metadata(
                        file_path, patch.line_start
                    )
                    patch.timestamp = timestamp
                    patch.author = author

            # Add patches to report
            for patch in patches:
                report.add_patch(patch)

        return report
