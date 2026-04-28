from __future__ import annotations

from pydantic import BaseModel, Field


class PatchSuggestion(BaseModel):
    target_file: str = Field(..., description="Target file path for the suggestion")
    change_summary: str = Field(..., description="Short summary of the suggested change")
    before_snippet: str = Field(..., description="Original code snippet from real code context")
    after_snippet: str = Field(..., description="Suggested replacement code snippet")
    explanation: str = Field(..., description="Why this change may address the issue")