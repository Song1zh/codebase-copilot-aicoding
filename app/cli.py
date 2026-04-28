from __future__ import annotations

import argparse
import json

from core.repo_scanner import scan_repo
from core.code_retriever import retrieve_relevant_files
from core.planner import create_fix_plan
from core.patch_generator import generate_patch_suggestion
from core.test_suggester import suggest_tests
from core.report_generator import build_fix_report, render_markdown_report
from workflows.fix_workflow import run_fix_workflow


def main() -> None:
    parser = argparse.ArgumentParser(prog="Codebase Copilot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("--repo", required=True)

    retrieve_parser = subparsers.add_parser("retrieve")
    retrieve_parser.add_argument("--repo", required=True)
    retrieve_parser.add_argument("--issue", required=True)
    retrieve_parser.add_argument("--top-k", type=int, default=3)

    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--repo", required=True)
    plan_parser.add_argument("--issue", required=True)
    plan_parser.add_argument("--top-k", type=int, default=3)

    suggest_parser = subparsers.add_parser("suggest")
    suggest_parser.add_argument("--repo", required=True)
    suggest_parser.add_argument("--issue", required=True)
    suggest_parser.add_argument("--top-k", type=int, default=3)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--repo", required=True)
    report_parser.add_argument("--issue", required=True)
    report_parser.add_argument("--top-k", type=int, default=3)

    fix_parser = subparsers.add_parser("fix")
    fix_parser.add_argument("--repo", required=True)
    fix_parser.add_argument("--issue", required=True)
    fix_parser.add_argument("--top-k", type=int, default=3)

    args = parser.parse_args()

    if args.command == "scan":
        repo_summary = scan_repo(args.repo)
        print(json.dumps(repo_summary, ensure_ascii=False, indent=2))
        return

    if args.command == "retrieve":
        repo_summary = scan_repo(args.repo)
        candidate_files = retrieve_relevant_files(
            issue_text=args.issue,
            scan_result=repo_summary.model_dump(),
            top_k=args.top_k,
        )
        print(json.dumps(candidate_files, ensure_ascii=False, indent=2))
        return

    if args.command == "plan":
        repo_summary = scan_repo(args.repo)
        candidate_files = retrieve_relevant_files(
            issue_text=args.issue,
            scan_result=repo_summary.model_dump(),
            top_k=args.top_k,
        )
        fix_plan = create_fix_plan(args.issue, candidate_files)
        print(fix_plan.model_dump_json(indent=2))
        return

    if args.command == "suggest":
        repo_summary = scan_repo(args.repo)
        candidate_files = retrieve_relevant_files(
            issue_text=args.issue,
            scan_result=repo_summary.model_dump(),
            top_k=args.top_k,
        )
        fix_plan = create_fix_plan(args.issue, candidate_files)
        patch_suggestion = generate_patch_suggestion(
            issue_text=args.issue,
            fix_plan=fix_plan,
            repo_path=args.repo,
        )
        print(patch_suggestion.model_dump_json(indent=2))
        return

    if args.command == "report":
        repo_summary = scan_repo(args.repo)
        candidate_files = retrieve_relevant_files(
            issue_text=args.issue,
            scan_result=repo_summary.model_dump(),
            top_k=args.top_k,
        )
        fix_plan = create_fix_plan(args.issue, candidate_files)
        patch_suggestion = generate_patch_suggestion(
            issue_text=args.issue,
            fix_plan=fix_plan,
            repo_path=args.repo,
        )
        test_suggestions = suggest_tests(
            issue_text=args.issue,
            fix_plan=fix_plan,
            patch_suggestion=patch_suggestion,
        )
        fix_report = build_fix_report(
            issue_text=args.issue,
            repo_summary=repo_summary,
            candidate_files=candidate_files,
            fix_plan=fix_plan,
            patch_suggestion=patch_suggestion,
            test_suggestions=test_suggestions,
        )
        markdown_report = render_markdown_report(fix_report)
        print(markdown_report)
        return

    if args.command == "fix":
        result = run_fix_workflow(
            repo_path=args.repo,
            issue=args.issue,
            top_k=args.top_k,
        )
        print(result["markdown_report"])
        return


if __name__ == "__main__":
    main()