import pytest
from pathlib import Path
import tempfile

from core.repo_scanner import scan_repo
from core.code_retriever import retrieve_relevant_files


def test_retrieve_relevant_files_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        cli_file = Path(tmpdir) / "cli.py"
        cli_file.write_text("""
def main():
    import argparse
    pass
""")

        scanner_file = Path(tmpdir) / "scanner.py"
        scanner_file.write_text("""
def scan():
    pass
""")

        scan_result = scan_repo(tmpdir)

        results = retrieve_relevant_files("argparse", scan_result, top_k=3)

        assert len(results) >= 1
        assert any("cli" in r["path"].lower() for r in results)


def test_retrieve_with_chinese_issue():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def handle_cli():
    pass
""")

        scan_result = scan_repo(tmpdir)
        results = retrieve_relevant_files("命令行", scan_result, top_k=3)

        assert len(results) >= 1
