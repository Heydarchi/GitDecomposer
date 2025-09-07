"""
Tests for global navbar injection in report HTML files.
"""

import os
from pathlib import Path
from unittest.mock import Mock

from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.services.report_generator import ReportGenerator


def test_navbar_injected_into_reports(tmp_path):
    mock_repo = Mock(spec=GitRepository)
    rg = ReportGenerator(mock_repo)

    # Create sample HTML files
    html_dir = tmp_path / "HTML"
    html_dir.mkdir(parents=True, exist_ok=True)
    files = ["commit_activity.html", "file_insights.html"]
    for f in files:
        (html_dir / f).write_text("<html><body><h1>Test</h1></body></html>", encoding="utf-8")

    # Run injector
    rg._inject_navbar_into_all_reports(str(tmp_path))

    # Validate injection
    for f in files:
        content = (html_dir / f).read_text(encoding="utf-8")
        assert "gd-global-nav" in content
        assert "Index" in content and "CSV" in content
        # The current file should be marked active in its own page
        # (best-effort check: the filename as link should exist)
        assert f in content
