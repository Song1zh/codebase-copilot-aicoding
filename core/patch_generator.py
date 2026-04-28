from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.code_reader import find_symbol, read_file
from core.llm_client import LLMClient
from schemas.coding_task import FixPlan
from schemas.patch_suggestion import PatchSuggestion


PROMPT_PATH = Path("prompts/patch_system.txt")


def load_patch_system_prompt(prompt_path: Path = PROMPT_PATH) -> str:
    if not prompt_path.exists():
        raise FileNotFoundError(f"Patch system prompt not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8").strip()


def choose_target_file(fix_plan: FixPlan) -> str:
    if fix_plan.fix_steps:
        return fix_plan.fix_steps[0].file_path

    if fix_plan.suspected_files:
        return fix_plan.suspected_files[0].path

    raise ValueError("FixPlan does not contain any target file.")


def _repo_file_path(repo_path: str, target_file: str) -> Path:
    root = Path(repo_path).resolve()
    file_path = (root / target_file).resolve()

    if root != file_path and root not in file_path.parents:
        raise ValueError(f"Unsafe target file path: {target_file}")

    if not file_path.exists():
        raise FileNotFoundError(f"Target file does not exist: {target_file}")

    if not file_path.is_file():
        raise ValueError(f"Target path is not a file: {target_file}")

    return file_path


def _extract_candidate_symbols(fix_plan: FixPlan) -> list[str]:
    text_parts: list[str] = []

    text_parts.append(fix_plan.issue_summary)

    for item in fix_plan.root_cause_hypotheses:
        text_parts.append(item.hypothesis)

    for step in fix_plan.fix_steps:
        text_parts.append(step.action)
        text_parts.append(step.detail)

    text = "\n".join(text_parts)

    candidates = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]{2,}\b", text)

    stopwords = {
        "the", "and", "for", "with", "from", "this", "that",
        "check", "inspect", "verify", "update", "modify",
        "file", "function", "class", "issue", "error",
        "argument", "command", "required"
    }

    result: list[str] = []
    for item in candidates:
        lowered = item.lower()
        if lowered in stopwords:
            continue
        if item not in result:
            result.append(item)

    return result


def select_before_snippet(
    repo_path: str,
    target_file: str,
    fix_plan: FixPlan,
    max_chars: int = 3000,
) -> str:
    file_path = _repo_file_path(repo_path, target_file)

    candidate_symbols = _extract_candidate_symbols(fix_plan)

    for symbol in candidate_symbols:
        matches = find_symbol(str(file_path), symbol)
        if matches:
            code = matches[0]["code"]
            if code.strip():
                return code[:max_chars]

    content = read_file(str(file_path))

    if not content.strip():
        raise ValueError(f"Target file is empty: {target_file}")

    return content[:max_chars]


def build_patch_user_prompt(
    issue_text: str,
    fix_plan: FixPlan,
    target_file: str,
    before_snippet: str,
) -> str:
    fix_plan_json = fix_plan.model_dump_json(indent=2)

    return f"""
Issue:
{issue_text}

FixPlan:
{fix_plan_json}

Target file:
{target_file}

Real before_snippet from target file:
```python
{before_snippet}

Generate one minimal PatchSuggestion JSON.
The before_snippet in your JSON must exactly match the real before_snippet above.
""".strip()

def generate_patch_suggestion(
    issue_text: str,
    fix_plan: FixPlan,
    repo_path: str,
    llm_client: LLMClient | None = None,
) -> PatchSuggestion:
    if not issue_text.strip():
        raise ValueError("issue_text is empty.")

    target_file = choose_target_file(fix_plan)
    before_snippet = select_before_snippet(
        repo_path=repo_path,
        target_file=target_file,
        fix_plan=fix_plan,
    )

    system_prompt = load_patch_system_prompt()
    user_prompt = build_patch_user_prompt(
        issue_text=issue_text,
        fix_plan=fix_plan,
        target_file=target_file,
        before_snippet=before_snippet,
    )

    client = llm_client or LLMClient()
    raw_output = client.generate_json(system_prompt, user_prompt)

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM output is not valid JSON: {raw_output}") from exc

    # 强制保证 target_file 和 before_snippet 来自本地真实上下文
    data["target_file"] = target_file
    data["before_snippet"] = before_snippet

    suggestion = PatchSuggestion.model_validate(data)

    if not suggestion.after_snippet.strip():
        raise ValueError("after_snippet is empty.")

    if not suggestion.change_summary.strip():
        raise ValueError("change_summary is empty.")

    if not suggestion.explanation.strip():
        raise ValueError("explanation is empty.")

    if suggestion.before_snippet not in read_file(str(_repo_file_path(repo_path, target_file))):
        raise ValueError("before_snippet is not from the real target file.")

    return suggestion
