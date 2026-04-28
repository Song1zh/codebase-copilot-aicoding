from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TestSuggestion(BaseModel):
    name: str = Field(..., description="Name of the suggested test")
    test_type: str = Field(..., description="Type of test, such as cli/manual/syntax")
    command: str = Field(..., description="Command or manual action to run")
    expected_result: str = Field(..., description="Expected result after running the test")
    reason: str = Field(..., description="Why this test is suggested")


class FixReport(BaseModel):
    issue: str = Field(..., description="Original issue text")
    repo_summary: dict[str, Any] = Field(..., description="Repository summary from Repo Scanner")
    candidate_files: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Top-k candidate files from Code Retriever",
    )
    fix_plan: dict[str, Any] = Field(..., description="Structured FixPlan")
    patch_suggestion: dict[str, Any] = Field(..., description="Structured PatchSuggestion")
    test_suggestions: list[TestSuggestion] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)