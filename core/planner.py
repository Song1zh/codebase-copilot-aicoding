from __future__ import annotations

import json
from typing import Any

from core.llm_client import LLMClient
from schemas.coding_task import FixPlan


SYSTEM_PROMPT = """You are a code analysis planner. Your task is to analyze the user's issue and suspected files, then generate a structured fix plan in JSON format.

## Output Rules
- Output JSON only, no Markdown code blocks
- Do not claim the bug is fixed
- Only use file paths provided in suspected_files

## Output Structure
{
  "issue_summary": "Brief summary of the issue",
  "suspected_files": [
    {"path": "file/path.py", "reason": "why this file is related"}
  ],
  "root_cause_hypotheses": [
    {"hypothesis": "Possible root cause explanation", "related_file": "file/path.py"}
  ],
  "fix_steps": [
    {"order": 1, "file_path": "file/path.py", "action": "concrete action", "detail": "specific detail"}
  ],
  "risks": ["potential risk or limitation"]
}

## Guidelines
- Be specific and actionable, avoid generic suggestions
- Each fix_step should have concrete action and detail
- Risks should reflect real concerns (e.g., edge cases, dependencies, potential side effects)
- Focus on investigation and modification steps, not code implementation
"""

SYSTEM_PROMPT = SYSTEM_PROMPT.strip()


def build_user_prompt(issue_text: str, relevant_files: list[dict[str, Any]]) -> str:
    files_json = json.dumps(relevant_files, ensure_ascii=False, indent=2)

    return f"""
Issue:
{issue_text}

Suspected files from retriever:
{files_json}

Please generate a minimal FixPlan JSON.
""".strip()


def create_fix_plan(
    issue_text: str,
    relevant_files: list[dict[str, Any]],
    llm_client: LLMClient | None = None,
) -> FixPlan:
    if not relevant_files:
        raise ValueError("No relevant files provided.")
    client = llm_client or LLMClient()

    user_prompt = build_user_prompt(issue_text, relevant_files)
    raw_output = client.generate_json(SYSTEM_PROMPT, user_prompt)

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM output is not valid JSON: {raw_output}") from exc

    plan = FixPlan.model_validate(data)

    allowed_paths = {item["path"] for item in relevant_files}

    for suspected_file in plan.suspected_files:
        if suspected_file.path not in allowed_paths:
            raise ValueError(
                f"LLM used a file outside retriever results: {suspected_file.path}"
            )

    for step in plan.fix_steps:
        if step.file_path not in allowed_paths:
            raise ValueError(
                f"LLM generated a fix step for an unknown file: {step.file_path}"
            )

    return plan   