from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any


DEFAULT_IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
}


def _normalize_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def _should_ignore_path(path: Path) -> bool:
    return any(part in DEFAULT_IGNORE_DIRS for part in path.parts)


def read_file(path: str) -> str:
    file_path = Path(path).resolve()

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    return file_path.read_text(encoding="utf-8")

def read_lines(path: str, start: int, end: int) -> str:
    if start < 1:
        raise ValueError("start must be >= 1")

    if end < start:
        raise ValueError("end must be >= start")

    content = read_file(path)
    lines = content.splitlines()

    if start > len(lines):
        raise ValueError(
            f"start line {start} is greater than total lines {len(lines)}"
        )

    selected = lines[start - 1:end]
    return "\n".join(selected)

def find_symbol(path: str, symbol_name: str) -> list[dict[str, Any]]:
    if not symbol_name.strip():
        raise ValueError("symbol_name is empty")

    content = read_file(path)
    tree = ast.parse(content)
    lines = content.splitlines()

    matches: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        if node.name != symbol_name:
            continue

        start_line = node.lineno
        end_line = getattr(node, "end_lineno", node.lineno)
        code = "\n".join(lines[start_line - 1:end_line])

        if isinstance(node, ast.ClassDef):
            symbol_type = "class"
        elif isinstance(node, ast.AsyncFunctionDef):
            symbol_type = "async_function"
        else:
            symbol_type = "function"

        matches.append(
            {
                "path": _normalize_path(Path(path)),
                "symbol_name": symbol_name,
                "symbol_type": symbol_type,
                "start_line": start_line,
                "end_line": end_line,
                "code": code,
            }
        )

    matches.sort(key=lambda item: item["start_line"])
    return matches

def grep_code(repo_path: str, pattern: str) -> list[dict[str, Any]]:
    if not pattern.strip():
        raise ValueError("pattern is empty")

    root = Path(repo_path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern: {pattern}") from exc

    results: list[dict[str, Any]] = []

    for py_file in sorted(root.rglob("*.py")):
        if _should_ignore_path(py_file):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        relative_path = _normalize_path(py_file.relative_to(root))

        for line_number, line in enumerate(content.splitlines(), start=1):
            if regex.search(line):
                results.append(
                    {
                        "path": relative_path,
                        "line_number": line_number,
                        "line": line.strip(),
                    }
                )

    return results