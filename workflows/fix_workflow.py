from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from core.repo_scanner import scan_repo as scan_repo_core
from core.code_retriever import retrieve_relevant_files
from core.planner import create_fix_plan
from core.patch_generator import (
    choose_target_file,
    generate_patch_suggestion,
    select_before_snippet,
)
from core.test_suggester import suggest_tests
from core.report_generator import build_fix_report, render_markdown_report


MIN_RETRIEVAL_SCORE = 3


class FixWorkflowState(TypedDict, total=False):
    repo_path: str
    issue: str
    top_k: int

    repo_summary: Any
    candidate_files: list[dict[str, Any]]
    refined_issue: str
    retrieval_refined: bool

    fix_plan: Any
    target_file: str
    before_snippet: str
    patch_suggestion: Any
    test_suggestions: list[Any]

    fix_report: Any
    markdown_report: str


def scan_repo_node(state: FixWorkflowState) -> dict[str, Any]:
    repo_path = state["repo_path"]
    repo_summary = scan_repo_core(repo_path)
    return {"repo_summary": repo_summary}


def retrieve_files_node(state: FixWorkflowState) -> dict[str, Any]:
    issue = state.get("refined_issue") or state["issue"]
    top_k = state.get("top_k", 3)

    repo_summary = state["repo_summary"]

    if hasattr(repo_summary, "model_dump"):
        scan_result = repo_summary.model_dump()
    else:
        scan_result = repo_summary

    candidate_files = retrieve_relevant_files(
        issue_text=issue,
        scan_result=scan_result,
        top_k=top_k,
    )

    return {"candidate_files": candidate_files}


def is_retrieval_weak(candidate_files: list[dict[str, Any]]) -> bool:
    if not candidate_files:
        return True

    best_score = candidate_files[0].get("score", 0)
    if best_score < MIN_RETRIEVAL_SCORE:
        return True

    return False


def route_after_retrieve(state: FixWorkflowState) -> str:
    candidate_files = state.get("candidate_files", [])
    already_refined = state.get("retrieval_refined", False)

    if is_retrieval_weak(candidate_files) and not already_refined:
        return "refine_retrieval"

    return "plan_fix"


def refine_retrieval_node(state: FixWorkflowState) -> dict[str, Any]:
    issue = state["issue"]

    # MVP 级 query expansion：不引入 embedding，不调用 LLM。
    # 目的只是让中文/模糊 issue 更容易命中英文代码符号。
    extra_terms = [
        "cli",
        "argparse",
        "parser",
        "repo",
        "scan",
        "retrieve",
        "planner",
        "patch",
        "error",
        "empty",
        "upload",
        "file",
    ]

    refined_issue = issue + " " + " ".join(extra_terms)

    repo_summary = state["repo_summary"]
    if hasattr(repo_summary, "model_dump"):
        scan_result = repo_summary.model_dump()
    else:
        scan_result = repo_summary

    candidate_files = retrieve_relevant_files(
        issue_text=refined_issue,
        scan_result=scan_result,
        top_k=state.get("top_k", 3),
    )

    return {
        "refined_issue": refined_issue,
        "retrieval_refined": True,
        "candidate_files": candidate_files,
    }


def plan_fix_node(state: FixWorkflowState) -> dict[str, Any]:
    candidate_files = state.get("candidate_files", [])

    if not candidate_files:
        raise ValueError(
            "No candidate files found. Retrieval is too weak for planning."
        )

    fix_plan = create_fix_plan(
        issue_text=state["issue"],
        relevant_files=candidate_files,
    )

    return {"fix_plan": fix_plan}


def inspect_code_node(state: FixWorkflowState) -> dict[str, Any]:
    fix_plan = state["fix_plan"]
    repo_path = state["repo_path"]

    target_file = choose_target_file(fix_plan)
    before_snippet = select_before_snippet(
        repo_path=repo_path,
        target_file=target_file,
        fix_plan=fix_plan,
    )

    return {
        "target_file": target_file,
        "before_snippet": before_snippet,
    }


def suggest_patch_node(state: FixWorkflowState) -> dict[str, Any]:
    patch_suggestion = generate_patch_suggestion(
        issue_text=state["issue"],
        fix_plan=state["fix_plan"],
        repo_path=state["repo_path"],
    )

    # 保底校验：PatchSuggestion 的 before_snippet 必须来自 inspect_code 阶段读到的上下文。
    expected_before = state.get("before_snippet", "")
    if expected_before and patch_suggestion.before_snippet != expected_before:
        raise ValueError(
            "PatchSuggestion before_snippet does not match inspected code context."
        )

    return {"patch_suggestion": patch_suggestion}


def suggest_tests_node(state: FixWorkflowState) -> dict[str, Any]:
    test_suggestions = suggest_tests(
        issue_text=state["issue"],
        fix_plan=state["fix_plan"],
        patch_suggestion=state["patch_suggestion"],
    )

    return {"test_suggestions": test_suggestions}


def generate_report_node(state: FixWorkflowState) -> dict[str, Any]:
    fix_report = build_fix_report(
        issue_text=state["issue"],
        repo_summary=state["repo_summary"],
        candidate_files=state["candidate_files"],
        fix_plan=state["fix_plan"],
        patch_suggestion=state["patch_suggestion"],
        test_suggestions=state["test_suggestions"],
    )

    markdown_report = render_markdown_report(fix_report)

    return {
        "fix_report": fix_report,
        "markdown_report": markdown_report,
    }


def build_fix_workflow():
    workflow = StateGraph(FixWorkflowState)

    workflow.add_node("scan_repo", scan_repo_node)
    workflow.add_node("retrieve_files", retrieve_files_node)
    workflow.add_node("refine_retrieval", refine_retrieval_node)
    workflow.add_node("plan_fix", plan_fix_node)
    workflow.add_node("inspect_code", inspect_code_node)
    workflow.add_node("suggest_patch", suggest_patch_node)
    workflow.add_node("suggest_tests", suggest_tests_node)
    workflow.add_node("generate_report", generate_report_node)

    workflow.add_edge(START, "scan_repo")
    workflow.add_edge("scan_repo", "retrieve_files")

    workflow.add_conditional_edges(
        "retrieve_files",
        route_after_retrieve,
        {
            "refine_retrieval": "refine_retrieval",
            "plan_fix": "plan_fix",
        },
    )

    workflow.add_edge("refine_retrieval", "plan_fix")
    workflow.add_edge("plan_fix", "inspect_code")
    workflow.add_edge("inspect_code", "suggest_patch")
    workflow.add_edge("suggest_patch", "suggest_tests")
    workflow.add_edge("suggest_tests", "generate_report")
    workflow.add_edge("generate_report", END)

    return workflow.compile()


def run_fix_workflow(
    repo_path: str,
    issue: str,
    top_k: int = 3,
) -> FixWorkflowState:
    app = build_fix_workflow()

    initial_state: FixWorkflowState = {
        "repo_path": repo_path,
        "issue": issue,
        "top_k": top_k,
        "retrieval_refined": False,
    }

    result = app.invoke(initial_state)
    return result