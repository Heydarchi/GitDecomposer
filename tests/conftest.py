"""Pytest configuration to ensure local package is importable.

Adds the repository root to sys.path so tests can import `gitdecomposer`
without requiring an installed wheel in the active environment.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


_ensure_repo_on_path()
