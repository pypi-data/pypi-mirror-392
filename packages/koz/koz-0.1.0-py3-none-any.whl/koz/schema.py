"""Schema definitions for patch detection output."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PatchType(str, Enum):
    """Types of monkeypatching detected by koz."""

    PATCH_TO = "patch_to"
    DIRECT_ASSIGNMENT = "direct_assignment"
    WRAPS_DECORATOR = "wraps_decorator"


class PatchInfo(BaseModel):
    """Information about a detected monkeypatch.

    Attributes:
        target_class: Name of the class being patched
        target_method: Name of the method being patched
        file_path: Path to the file containing the patch
        line_start: Starting line number of the patch
        line_end: Ending line number of the patch
        patch_type: Type of monkeypatching used
        timestamp: Modification time from git history (if available)
        author: Git author information (if available)
    """

    target_class: str = Field(..., description="Name of the class being patched")
    target_method: str = Field(..., description="Name of the method being patched")
    file_path: str = Field(..., description="Path to the file containing the patch")
    line_start: int = Field(..., ge=1, description="Starting line number")
    line_end: int = Field(..., ge=1, description="Ending line number")
    patch_type: PatchType = Field(..., description="Type of monkeypatching detected")
    timestamp: Optional[datetime] = Field(
        None, description="Modification time from git history"
    )
    author: Optional[str] = Field(None, description="Git author information")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class PatchReport(BaseModel):
    """Complete report of patches detected in a codebase.

    Attributes:
        project_path: Root path of the analyzed project
        scan_time: Timestamp when the scan was performed
        patches: List of detected patches
        total_patches: Total number of patches found
    """

    project_path: str = Field(..., description="Root path of the analyzed project")
    scan_time: datetime = Field(
        default_factory=datetime.now, description="Scan timestamp"
    )
    patches: list[PatchInfo] = Field(
        default_factory=list, description="List of detected patches"
    )
    total_patches: int = Field(default=0, description="Total number of patches found")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
    )

    def add_patch(self, patch: PatchInfo) -> None:
        """Add a patch to the report.

        Args:
            patch: Patch information to add
        """
        self.patches.append(patch)
        self.total_patches = len(self.patches)
