from __future__ import annotations

import re
from typing import Any


QUERY_ALIASES = {
    "命令行": ["cli", "command", "terminal"],
    "参数": ["arg", "args", "argument", "arguments"],
    "解析": ["parse", "parser", "argparse"],
    "错误": ["error", "bug", "fail"],
    "扫描": ["scan", "scanner"],
    "仓库": ["repo", "repository"],
    "文件": ["file", "files"],
    "检索": ["retrieve", "retriever", "search"],
    "函数": ["function", "functions"],
    "类": ["class", "classes"],
    "导入": ["import", "imports"],
}


def normalize_issue_text(issue_text: str) -> str:
    text = issue_text.lower()
    expanded_parts = [text]

    for zh_term, eng_terms in QUERY_ALIASES.items():
        if zh_term in issue_text:
            expanded_parts.extend(eng_terms)

    return " ".join(expanded_parts)


def tokenize_issue(issue_text: str) -> list[str]:
    text = normalize_issue_text(issue_text)

    tokens = re.findall(r"[a-zA-Z0-9_]+", text)

    stopwords = {
        "the", "a", "an", "to", "of", "for", "in", "on", "and", "or",
        "is", "are", "be", "with", "when", "from", "by", "how",
        "issue", "bug", "fix", "add", "need"
    }

    filtered_tokens = [token for token in tokens if token not in stopwords and len(token) > 2]
    return filtered_tokens


def _split_path_tokens(path: str) -> list[str]:
    parts = re.split(r"[\\/._\-]+", path.lower())
    return [p for p in parts if p]


def _split_symbol_tokens(symbols: list[str]) -> list[str]:
    result: list[str] = []
    for item in symbols:
        parts = re.split(r"[_\-.]+", item.lower())
        result.extend([p for p in parts if p])
        result.append(item.lower())
    return result


def score_file(issue_tokens: list[str], file_summary: dict[str, Any]) -> dict[str, Any]:
    path = file_summary["path"]
    functions = file_summary.get("functions", [])
    classes = file_summary.get("classes", [])
    imports = file_summary.get("imports", [])

    path_tokens = _split_path_tokens(path)
    function_tokens = _split_symbol_tokens(functions)
    class_tokens = _split_symbol_tokens(classes)
    import_tokens = _split_symbol_tokens(imports)

    score = 0
    matched_terms: list[str] = []

    for token in issue_tokens:
        token_score = 0

        # 路径命中通常很重要
        if token in path_tokens:
            token_score += 4

        # 函数名命中
        if token in function_tokens:
            token_score += 3

        # 类名命中
        if token in class_tokens:
            token_score += 3

        # import 命中
        if token in import_tokens:
            token_score += 2

        # 允许子串弱匹配，避免 retrieve vs retriever 完全错过
        if any(token in p or p in token for p in path_tokens):
            token_score += 1
        if any(token in f or f in token for f in function_tokens):
            token_score += 1
        if any(token in c or c in token for c in class_tokens):
            token_score += 1

        if token_score > 0:
            matched_terms.append(token)
            score += token_score

    return {
        "path": path,
        "score": score,
        "matched_terms": sorted(set(matched_terms)),
        "functions": functions,
        "classes": classes,
    }


def retrieve_relevant_files(
    issue_text: str,
    scan_result: dict[str, Any],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    issue_tokens = tokenize_issue(issue_text)
    files = scan_result.get("files", [])

    scored = [score_file(issue_tokens, file_summary) for file_summary in files]
    scored = [item for item in scored if item["score"] > 0]

    scored.sort(key=lambda x: (-x["score"], x["path"]))
    return scored[:top_k]