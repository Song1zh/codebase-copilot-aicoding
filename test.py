from workflows.fix_workflow import run_fix_workflow

result = run_fix_workflow(
    repo_path=".",
    issue="命令行参数解析错误",
    top_k=3,
)

print(result["markdown_report"])