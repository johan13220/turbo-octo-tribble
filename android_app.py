"""
Entry point for the Android (Kivy/KivyMD) version of SEO Dashboard.

On Android, this file:
  1. Sets CACHE_DIR and SEO_DASHBOARD_ENV_FILE to the app's writable storage.
  2. Injects android_compat.config into sys.modules so that core.config
     loads without pydantic-settings (not available as a p4a recipe).
  3. Builds the UI with MDBottomNavigation (4 tabs).
"""
from __future__ import annotations

import os
import sys
import threading

# ── Android path bootstrap (MUST run before any core.* import) ────────────
try:
    from kivy.utils import platform as _kv_platform  # noqa: E402
    if _kv_platform == "android":
        from android.storage import app_storage_path  # type: ignore[import]
        _data = app_storage_path()
        os.environ.setdefault("CACHE_DIR", os.path.join(_data, "seo_cache"))
        os.environ.setdefault("SEO_DASHBOARD_ENV_FILE", os.path.join(_data, ".env"))

        import android_compat.config as _compat_cfg
        sys.modules["core.config"] = _compat_cfg  # type: ignore[assignment]
except Exception:
    pass
# ──────────────────────────────────────────────────────────────────────────

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

from android_ui import state as app_state
from android_ui.screens.audit_screen import AuditContent
from android_ui.screens.competitors_screen import CompetitorsContent
from android_ui.screens.overview_screen import OverviewContent
from android_ui.screens.search_screen import SearchContent


def _nav_item(name: str, text: str, icon: str, content) -> MDBottomNavigationItem:
    item = MDBottomNavigationItem(name=name, text=text, icon=icon)
    item.add_widget(content)
    return item


class SEODashboardApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.theme_style = "Light"
        self.title = "SEO Dashboard"

        self.search_content = SearchContent(app=self)
        self.overview_content = OverviewContent()
        self.audit_content = AuditContent()
        self.competitors_content = CompetitorsContent()

        nav = MDBottomNavigation(panel_color=self.theme_cls.primary_color)
        nav.add_widget(_nav_item("search",      "Search",      "magnify",        self.search_content))
        nav.add_widget(_nav_item("overview",    "Overview",    "chart-bar",      self.overview_content))
        nav.add_widget(_nav_item("audit",       "Audit",       "shield-check",   self.audit_content))
        nav.add_widget(_nav_item("competitors", "Rivals",      "account-group",  self.competitors_content))

        app_state.state.app = self
        return nav

    def on_start(self):
        self._ensure_env_file()

    def _ensure_env_file(self):
        env_file = os.environ.get("SEO_DASHBOARD_ENV_FILE", ".env")
        if not os.path.exists(env_file):
            here = os.path.dirname(os.path.abspath(__file__))
            example = os.path.join(here, ".env.example")
            if os.path.exists(example):
                import shutil
                os.makedirs(os.path.dirname(env_file) or ".", exist_ok=True)
                shutil.copy(example, env_file)

    def run_analysis(self, domain: str, provider_name: str) -> None:
        """Fetch all data in a background thread then refresh the UI."""
        from providers.scraper import ScraperProvider
        from providers.semrush import SemrushProvider
        from core.config import get_settings

        domain = (
            domain.strip().lower()
            .removeprefix("https://")
            .removeprefix("http://")
            .rstrip("/")
        )
        if not domain:
            return

        app_state.state.domain = domain
        app_state.state.error = ""
        app_state.state.loading = True
        self.search_content.show_loading(True)

        settings = get_settings()
        provider = (
            SemrushProvider()
            if provider_name == "semrush" and settings.seo_api_key
            else ScraperProvider()
        )
        app_state.state.provider = provider

        def _work():
            try:
                app_state.state.overview = provider.get_domain_overview(domain)
                app_state.state.keywords = provider.get_keywords(domain, limit=50)
                app_state.state.audit = provider.get_audit(domain)
                app_state.state.competitors = provider.get_competitors(domain)
            except Exception as exc:
                app_state.state.error = str(exc)
            finally:
                app_state.state.loading = False
                Clock.schedule_once(self._refresh_ui, 0)

        threading.Thread(target=_work, daemon=True).start()

    def _refresh_ui(self, dt) -> None:
        self.search_content.show_loading(False)
        self.overview_content.refresh()
        self.audit_content.refresh()
        self.competitors_content.refresh()


if __name__ == "__main__":
    SEODashboardApp().run()
