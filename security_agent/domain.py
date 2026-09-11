from enum import StrEnum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Self, Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DomainModel(BaseModel):
    """Base contract for values crossing application boundaries."""
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

class CodeEvidence(DomainModel):
    file_path: str = Field(min_length=1)
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    explanation: str = Field(min_length=1)

    @field_validator("file_path")
    @classmethod
    def path_must_be_repository_relative(cls, value: str) -> str:
        # Normalize backslashes to forward slashes.
        # Reject POSIX absolute paths, Windows absolute paths, traversal (`..`),
        # and a path that normalizes to only `.`.
        # Return the normalized POSIX-style string.
        ...

    @model_validator(mode="after")
    def line_range_must_be_ordered(self) -> Self:
        # Reject line_end < line_start.
        # Return self when valid.
        ...

class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

Confidence = Annotated[
    float,
    Field(ge=0.0, le=1.0),
]

class FindingStatus(StrEnum):
    HYPOTHESIS = "hypothesis"
    SUPPORTED = "supported"
    VALIDATED = "validated"
    REJECTED = "rejected"
    ACCEPTED_RISK = "accepted_risk"


class Finding(DomainModel):
    finding_id: UUID = Field(default_factory=uuid4)
    summary: str = Field(min_length=1)
    severity: Severity
    confidence: Confidence
    status: FindingStatus = FindingStatus.HYPOTHESIS
    evidence: tuple[CodeEvidence, ...] = ()

    @model_validator(mode="after")
    def evidence_must_support_asserted_status(self) -> Self:
        if (
        self.status in {
            FindingStatus.SUPPORTED,
            FindingStatus.VALIDATED,
        }
        and not self.evidence
        ):
            raise ValueError(
                "Supported and validated findings require evidence"
            )

        return self

class Scope(DomainModel):
    root: Path
    include: tuple[str, ...] = ("**/*",)
    exclude: tuple[str, ...] = (
        ".git/**",
        "venv/**",
        ".venv/**",
        "__pycache__/**",
    )

    @field_validator("root")
    @classmethod
    def root_must_be_absolute(cls, value: Path) -> Path:
        # Reject a relative root with a clear ValueError.
        # Return value unchanged when valid; do not access the filesystem here.
        if not value.is_absolute():
            raise ValueError("Scope root must be an absolute path")
        return value

class FileRecord(DomainModel):
    path: str
    size: int

class RepositoryInventory(DomainModel):
    root: Path
    files: tuple[FileRecord, ...]
