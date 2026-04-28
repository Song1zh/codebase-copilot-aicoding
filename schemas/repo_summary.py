from __future__ import annotations

from pydantic import BaseModel, Field


class PythonFileSummary(BaseModel):
    path: str = Field(..., description="Relative path of the Python file")
    functions: list[str] = Field(default_factory=list)
    classes: list[str] = Field(default_factory=list)
    imports: list[str] = Field(default_factory=list)


class RepoSummary(BaseModel):
    repo_path: str = Field(..., description="Absolute path of the scanned repository")
    total_python_files: int
    total_functions: int
    total_classes: int
    total_imports: int
    python_files: list[str]
    files: list[PythonFileSummary]