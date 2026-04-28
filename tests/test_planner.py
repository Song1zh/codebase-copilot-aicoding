import pytest
from core.planner import create_fix_plan


def test_create_fix_plan_basic():
    issue = "argparse error"
    relevant_files = [
        {
            "path": "app/cli.py",
            "score": 8,
            "matched_terms": ["cli", "argparse"],
            "functions": ["main"],
            "classes": []
        }
    ]

    plan = create_fix_plan(issue, relevant_files)

    assert len(plan.suspected_files) >= 1
    assert len(plan.fix_steps) >= 1
    assert len(plan.risks) >= 1
    assert any("cli" in sf.path for sf in plan.suspected_files)


def test_create_fix_plan_structure():
    issue = "test issue"
    relevant_files = [
        {
            "path": "test.py",
            "score": 5,
            "matched_terms": ["test"],
            "functions": ["run"],
            "classes": []
        }
    ]

    plan = create_fix_plan(issue, relevant_files)

    assert hasattr(plan, "suspected_files")
    assert hasattr(plan, "fix_steps")
    assert hasattr(plan, "risks")
    assert plan.suspected_files[0].path == "test.py"
