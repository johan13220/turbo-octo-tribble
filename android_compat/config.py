"""
Android-compatible config module — replaces core.config on Android.
Uses python-dotenv directly instead of pydantic-settings (no binary deps).
Injected into sys.modules['core.config'] by android_app.py at startup.
"""
from __future__ import annotations

import os
from pathlib import Path


def _load_env(env_file: str) -> dict:
    try:
        from dotenv import dotenv_values
        return dict(dotenv_values(env_file))
    except Exception:
        return {}


class Settings:
    def __init__(self) -> None:
        env_file = os.environ.get("SEO_DASHBOARD_ENV_FILE", ".env")
        v = _load_env(env_file)

        def _get(key: str, default: str = "") -> str:
            return os.environ.get(key, v.get(key, default))

        self.seo_api_key = _get("SEO_API_KEY")
        self.seo_api_base_url = _get("SEO_API_BASE_URL", "https://api.semrush.com")
        self.cache_dir = _get("CACHE_DIR", "~/.seo_dashboard/cache")
        self.cache_ttl_hours = int(_get("CACHE_TTL_HOURS", "24"))
        self.default_language = _get("DEFAULT_LANGUAGE", "en")
        self.default_location_id = int(_get("DEFAULT_LOCATION_ID", "2840"))
        self.max_keywords = int(_get("MAX_KEYWORDS", "100"))
        self.report_output_dir = _get("REPORT_OUTPUT_DIR", "./reports_output")
        self.gsc_credentials_path = _get("GSC_CREDENTIALS_PATH")
        self.gsc_token_path = _get("GSC_TOKEN_PATH", "~/.seo_dashboard/gsc_token.json")


_instance: Settings | None = None


def get_settings() -> Settings:
    global _instance
    if _instance is None:
        _instance = Settings()
    return _instance
