from __future__ import annotations

from schemas.coding_task import FixPlan
from schemas.patch_suggestion import PatchSuggestion
from schemas.fix_report import TestSuggestion


def suggest_tests(
    issue_text: str,
    fix_plan: FixPlan,
    patch_suggestion: PatchSuggestion
) -> list[TestSuggestion]:
    tests: list[TestSuggestion] = []

    # 1. Syntax check test
    tests.append(
        TestSuggestion(
            name="Python Syntax Check",
            test_type="syntax",
            command="python -m py_compile <target_file>",
            expected_result="No syntax errors detected",
            reason="Verify the patched code has no syntax errors"
        )
    )

    # 2. Scan smoke test
    tests.append(
        TestSuggestion(
            name="Scan Smoke Test",
            test_type="cli",
            command="python app/cli.py scan --repo .",
            expected_result="Successfully scans the repository and outputs JSON",
            reason="Basic functionality test to ensure the CLI still works"
        )
    )

    # 3. Issue-specific test
    target_file = patch_suggestion.target_file
    tests.append(
        TestSuggestion(
            name="Issue-Specific Test",
            test_type="cli",
            command=f"python app/cli.py <relevant_command> --repo .",
            expected_result="Command executes without argument parsing errors",
            reason=f"Test the specific issue mentioned: {issue_text}"
        )
    )

    # 4. Manual patch review
    tests.append(
        TestSuggestion(
            name="Manual Patch Review",
            test_type="manual",
            command=f"Review changes in {target_file}",
            expected_result="Confirms the patch addresses the issue without breaking other functionality",
            reason="Human verification of the patch's correctness and impact"
        )
    )

    return tests
