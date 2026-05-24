"""Shared application state for the Android UI."""
from __future__ import annotations
from typing import Any


class AppState:
    domain: str = ""
    provider: Any = None
    overview: Any = None
    keywords: list = []
    audit: Any = None
    competitors: list = []
    loading: bool = False
    error: str = ""
    app: Any = None


state = AppState()
