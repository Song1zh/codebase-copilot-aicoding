import pytest
from pathlib import Path
import tempfile
import os

from core.repo_scanner import scan_repo


def test_scan_repo_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.py"
        test_file.write_text("""
def hello():
    pass

class MyClass:
    pass

import os
""")

        result = scan_repo(tmpdir)

        assert result["repo_path"] == tmpdir
        assert result["total_python_files"] == 1
        assert len(result["files"]) == 1
        assert result["files"][0]["functions"] == ["hello"]
        assert result["files"][0]["classes"] == ["MyClass"]
        assert "os" in result["files"][0]["imports"]


def test_scan_repo_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scan_repo(tmpdir)
        assert result["total_python_files"] == 0
        assert result["files"] == []
