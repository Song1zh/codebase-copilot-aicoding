from schemas.coding_task import FixPlan
from core.patch_generator import generate_patch_suggestion

issue = "命令行参数解析错误"

fix_plan = FixPlan.model_validate({
    "issue_summary": "The CLI has a command line argument parsing issue.",
    "suspected_files": [
        {
            "path": "app/cli.py",
            "reason": "This file defines CLI commands and argparse configuration."
        }
    ],
    "root_cause_hypotheses": [
        {
            "hypothesis": "The main function may not define required argparse arguments correctly.",
            "related_file": "app/cli.py"
        }
    ],
    "fix_steps": [
        {
            "order": 1,
            "file_path": "app/cli.py",
            "action": "Inspect main",
            "detail": "Check whether main defines the expected subcommands and required arguments."
        }
    ],
    "risks": [
        "The error may be caused by wrong command usage rather than implementation."
    ]
})

try:
    suggestion = generate_patch_suggestion(
        issue_text=issue,
        fix_plan=fix_plan,
        repo_path="."
    )
    print("Success! Generated patch suggestion:")
    print(suggestion.model_dump_json(indent=2))
except Exception as e:
    print(f"Error: {e}")
