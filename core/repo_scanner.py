from __future__ import annotations

import ast
from pathlib import Path

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
    ".mypy_cache",
    ".pytest_cache",
}


def find_python_files(repo_path: str) -> list[Path]:
    root = Path(repo_path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    py_files: list[Path] = []

    # 递归通配符查找，从根目录递归遍历所有子目录
    for path in root.rglob("*.py"):
        if any(part in DEFAULT_IGNORE_DIRS for part in path.parts):
            continue
        py_files.append(path)

    return sorted(py_files)


def _format_import(node: ast.AST) -> list[str]:
    imports: list[str] = []

    if isinstance(node, ast.Import):
        for alias in node.names:
            imports.append(alias.name)

    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        for alias in node.names:
            if module:
                imports.append(f"{module}.{alias.name}")
            else:
                imports.append(alias.name)

    return imports


def scan_python_file(py_file_path: str) -> dict:
    py_file = Path(py_file_path).resolve()

    if py_file.suffix != ".py":
        raise ValueError(f"Not a Python file: {py_file}")
    if not py_file.exists():
        raise FileNotFoundError(f"Python file does not exist: {py_file}")
    if not py_file.is_file():
        raise IsADirectoryError(f"Python file path is not a file: {py_file}")

    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source)

    functions: list[str] = []
    classes: list[str] = []
    imports: list[str] = []

    # 仅提取顶层定义，保持输出简单可复用
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.extend(_format_import(node))

    return {
        "path": str(py_file),
        "functions": functions,
        "classes": classes,
        "imports": sorted(set(imports)),
    }


def extract_file_summary(py_file: Path, root: Path) -> dict:
    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source)

    functions: list[str] = []
    classes: list[str] = []
    imports: list[str] = []

    # 只提取顶层定义，避免把类方法、嵌套函数混进来
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.extend(_format_import(node))

    return {
        "path": str(py_file.relative_to(root)),
        "functions": functions,
        "classes": classes,
        "imports": sorted(set(imports)),
    }


def scan_repo(repo_path: str) -> dict:
    root = Path(repo_path).resolve()
    py_files = find_python_files(repo_path)

    file_summaries = [extract_file_summary(py_file, root) for py_file in py_files]

    return {
        "repo_path": str(root),
        "total_python_files": len(py_files),
        "files": file_summaries,
    }