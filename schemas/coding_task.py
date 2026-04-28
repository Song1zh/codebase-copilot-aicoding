from __future__ import annotations

from pydantic import BaseModel, Field

class SuspectFile(BaseModel):
    path: str = Field(..., description="Path of the suspected relevant file")
    reason: str = Field(..., description="Why this file may be related to the issue")

class FixStep(BaseModel):
    order: int = Field(..., description="Step order, starting from 1")
    file_path: str = Field(..., description="File to modify or inspect")
    action: str = Field(..., description="Concrete action to take")
    detail: str = Field(..., description="Detailed explanation of the action")

class RootCauseHypothesis(BaseModel):
    hypothesis: str = Field(..., description="Hypothesis about the root cause")
    related_file: str = Field(..., description="File related to this hypothesis")

class FixPlan(BaseModel):
    issue_summary: str = Field(..., description="Summary of the issue")
    suspected_files: list[SuspectFile]
    root_cause_hypotheses: list[RootCauseHypothesis]
    fix_steps: list[FixStep]
    risks: list[str]
