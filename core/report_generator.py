from __future__ import annotations

from typing import Any

from schemas.coding_task import FixPlan
from schemas.fix_report import FixReport, TestSuggestion
from schemas.patch_suggestion import PatchSuggestion
from schemas.repo_summary import RepoSummary


def _to_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"Unsupported object type: {type(obj)}")


def _escape_table_text(value: Any) -> str:
    text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def build_fix_report(
    issue_text: str,
    repo_summary: RepoSummary | dict[str, Any],
    candidate_files: list[dict[str, Any]],
    fix_plan: FixPlan,
    patch_suggestion: PatchSuggestion,
    test_suggestions: list[TestSuggestion],
) -> FixReport:
    fix_plan_dict = fix_plan.model_dump()

    risks: list[str] = []
    risks.extend(fix_plan_dict.get("risks", []))
    risks.append("PatchSuggestion is not automatically applied; manual review is required.")

    repo_summary_dict = _to_dict(repo_summary)

    return FixReport(
        issue=issue_text,
        repo_summary=repo_summary_dict,
        candidate_files=candidate_files,
        fix_plan=fix_plan_dict,
        patch_suggestion=patch_suggestion.model_dump(),
        test_suggestions=test_suggestions,
        risks=risks,
    )


def render_markdown_report(report: FixReport) -> str:
    repo = report.repo_summary
    fix_plan = report.fix_plan
    patch = report.patch_suggestion

    lines: list[str] = []

    lines.append("# Codebase Copilot Fix Report")
    lines.append("")

    lines.append("## 1. Issue")
    lines.append("")
    lines.append(report.issue)
    lines.append("")

    lines.append("## 2. Repository Summary")
    lines.append("")
    lines.append(f"- Repo path: `{repo.get('repo_path', '')}`")
    lines.append(f"- Total Python files: `{repo.get('total_python_files', '')}`")
    lines.append(f"- Total functions: `{repo.get('total_functions', '')}`")
    lines.append(f"- Total classes: `{repo.get('total_classes', '')}`")
    lines.append(f"- Total imports: `{repo.get('total_imports', '')}`")
    lines.append("")

    lines.append("## 3. Candidate Files")
    lines.append("")

    if report.candidate_files:
        lines.append("| Rank | Path | Score | Matched terms |")
        lines.append("|---:|---|---:|---|")
        for idx, item in enumerate(report.candidate_files, start=1):
            path = _escape_table_text(item.get("path", ""))
            score = _escape_table_text(item.get("score", ""))
            matched_terms = ", ".join(item.get("matched_terms", []))
            matched_terms = _escape_table_text(matched_terms)
            lines.append(f"| {idx} | `{path}` | {score} | {matched_terms} |")
    else:
        lines.append("No candidate files were provided.")

    lines.append("")

    lines.append("## 4. Fix Plan")
    lines.append("")
    lines.append(f"### Issue summary")
    lines.append("")
    lines.append(fix_plan.get("issue_summary", ""))
    lines.append("")

    lines.append("### Suspected files")
    lines.append("")
    suspected_files = fix_plan.get("suspected_files", [])
    if suspected_files:
        for item in suspected_files:
            lines.append(f"- `{item.get('path', '')}`: {item.get('reason', '')}")
    else:
        lines.append("- No suspected files.")
    lines.append("")

    lines.append("### Root cause hypotheses")
    lines.append("")
    hypotheses = fix_plan.get("root_cause_hypotheses", [])
    if hypotheses:
        for item in hypotheses:
            lines.append(
                f"- `{item.get('related_file', '')}`: {item.get('hypothesis', '')}"
            )
    else:
        lines.append("- No root cause hypotheses.")
    lines.append("")

    lines.append("### Fix steps")
    lines.append("")
    steps = fix_plan.get("fix_steps", [])
    if steps:
        for item in steps:
            lines.append(
                f"{item.get('order', '-')}. `{item.get('file_path', '')}` - "
                f"{item.get('action', '')}: {item.get('detail', '')}"
            )
    else:
        lines.append("- No fix steps.")
    lines.append("")

    lines.append("## 5. Patch Suggestion")
    lines.append("")
    lines.append(f"- Target file: `{patch.get('target_file', '')}`")
    lines.append(f"- Change summary: {patch.get('change_summary', '')}")
    lines.append("")
    lines.append("### Before snippet")
    lines.append("")
    lines.append("```python")
    lines.append(patch.get("before_snippet", ""))
    lines.append("```")
    lines.append("")
    lines.append("### After snippet")
    lines.append("")
    lines.append("```python")
    lines.append(patch.get("after_snippet", ""))
    lines.append("```")
    lines.append("")
    lines.append("### Explanation")
    lines.append("")
    lines.append(patch.get("explanation", ""))
    lines.append("")

    lines.append("## 6. Test Suggestions")
    lines.append("")
    if report.test_suggestions:
        lines.append("| Name | Type | Command / Action | Expected result | Reason |")
        lines.append("|---|---|---|---|---|")
        for item in report.test_suggestions:
            lines.append(
                f"| {_escape_table_text(item.name)} "
                f"| {_escape_table_text(item.test_type)} "
                f"| `{_escape_table_text(item.command)}` "
                f"| {_escape_table_text(item.expected_result)} "
                f"| {_escape_table_text(item.reason)} |"
            )
    else:
        lines.append("No test suggestions.")
    lines.append("")

    lines.append("## 7. Risks")
    lines.append("")
    if report.risks:
        for risk in report.risks:
            lines.append(f"- {risk}")
    else:
        lines.append("- No risks provided.")
    lines.append("")

    return "\n".join(lines)