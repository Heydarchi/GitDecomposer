"""
Smoke tests for AdvancedAnalytics dashboards to ensure methods execute and write HTML.
"""

from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import plotly.graph_objects as go

from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.services.advanced_analytics import AdvancedAnalytics


def _df(data: dict) -> pd.DataFrame:
    return pd.DataFrame(data)


def test_repository_health_dashboard_smoke(tmp_path):
    mock_repo = Mock(spec=GitRepository)
    aa = AdvancedAnalytics(mock_repo)

    aa.commit_analyzer.get_commit_velocity_analysis = Mock(
        return_value={"weekly_velocity": _df({"week": ["2024-01"], "commits": [10]})}
    )
    aa.commit_analyzer.get_bug_fix_ratio_analysis = Mock(return_value={"bug_fix_ratio": 12})
    aa.file_analyzer.get_documentation_coverage_analysis = Mock(return_value={"documentation_ratio": 30})

    path = str(tmp_path / "repository_health.html")
    fig = aa.create_repository_health_dashboard(path)

    assert isinstance(fig, go.Figure)
    assert Path(path).exists()
