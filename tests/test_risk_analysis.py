"""
Basic tests for RiskAnalysis service.
"""

from pathlib import Path
from unittest.mock import Mock

import plotly.graph_objects as go

from gitdecomposer.core.git_repository import GitRepository
from gitdecomposer.services.risk_analysis import RiskAnalysis


def test_create_file_insights_dashboard_writes_html(tmp_path):
    # Mock repo and analyzers
    mock_repo = Mock(spec=GitRepository)

    ra = RiskAnalysis(mock_repo)

    # Patch analyzers to return minimal valid shapes
    ra.file_analyzer.get_code_churn_analysis = Mock(
        return_value={
            "file_churn_rates": __import__("pandas").DataFrame(
                {
                    "file_path": ["a.py", "b.py"],
                    "churn_rate": [0.5, 0.2],
                    "total_changes": [10, 5],
                }
            )
        }
    )

    ra.critical_files_analyzer = Mock()
    ra.critical_files_analyzer.calculate.return_value = {
        "critical_files": [
            ("a.py", {"complexity": 10, "change_frequency": 5, "criticality_score": 0.8}),
            ("b.py", {"complexity": 5, "change_frequency": 3, "criticality_score": 0.4}),
        ]
    }

    ra.single_point_failure_analyzer = Mock()
    ra.single_point_failure_analyzer.calculate.return_value = {
        "spof_files": [
            {"file": "a.py", "dominant_author": "dev1", "dominance_ratio": 0.9},
            {"file": "b.py", "dominant_author": "dev2", "dominance_ratio": 0.7},
        ]
    }

    save_path = str(tmp_path / "file_insights.html")
    fig = ra.create_file_insights_dashboard(save_path)

    assert isinstance(fig, go.Figure)
    assert Path(save_path).exists()
