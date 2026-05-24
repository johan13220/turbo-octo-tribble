"""Google Search Console provider — uses the Search Analytics API (OAuth2)."""
from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path

from core.cache import cached
from core.config import get_settings
from core.models import (
    AuditReport,
    BacklinkSummary,
    CompetitorSnapshot,
    DomainOverview,
    GSCDataPoint,
    GSCPage,
    Keyword,
)
from providers.base import SEOProvider

_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _build_service(credentials_path: str, token_path: str):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = None
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, _SCOPES)
            creds = flow.run_local_server(port=0)
        Path(token_path).parent.mkdir(parents=True, exist_ok=True)
        Path(token_path).write_text(creds.to_json())

    return build("searchconsole", "v1", credentials=creds)


def _resolve_property(service, domain: str) -> str:
    """Find the best matching GSC property for the given domain."""
    clean = domain.lower().removeprefix("https://").removeprefix("http://").rstrip("/")
    try:
        resp = service.sites().list().execute()
        sites = [s.get("siteUrl", "") for s in resp.get("siteEntry", [])]
        # Prefer sc-domain: (domain property — covers all protocols/subdomains)
        if f"sc-domain:{clean}" in sites:
            return f"sc-domain:{clean}"
        # Try URL prefix variants
        for prefix in [f"https://{clean}/", f"http://{clean}/",
                       f"https://www.{clean}/", f"http://www.{clean}/"]:
            if prefix in sites:
                return prefix
    except Exception:
        pass
    return f"sc-domain:{clean}"


class GSCProvider(SEOProvider):
    """
    Provides real click/impression/position data from Google Search Console.

    Setup:
      1. Run `python scripts/gsc_auth.py` to authenticate.
      2. Set GSC_CREDENTIALS_PATH and GSC_TOKEN_PATH in .env.
    """

    def __init__(self):
        settings = get_settings()
        self._credentials_path = os.path.expanduser(settings.gsc_credentials_path)
        self._token_path = os.path.expanduser(settings.gsc_token_path)
        self._service = None
        self._property_cache: dict[str, str] = {}

    def _svc(self):
        if self._service is None:
            self._service = _build_service(self._credentials_path, self._token_path)
        return self._service

    def _property(self, domain: str) -> str:
        if domain not in self._property_cache:
            self._property_cache[domain] = _resolve_property(self._svc(), domain)
        return self._property_cache[domain]

    def _query(
        self,
        domain: str,
        dimensions: list[str],
        days: int = 28,
        limit: int = 100,
        filters: list[dict] | None = None,
    ) -> list[dict]:
        # GSC has a ~3-day data lag
        end = date.today() - timedelta(days=3)
        start = end - timedelta(days=days - 1)
        body: dict = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "rowLimit": limit,
        }
        if dimensions:
            body["dimensions"] = dimensions
        if filters:
            body["dimensionFilterGroups"] = [{"filters": filters}]
        resp = self._svc().searchanalytics().query(
            siteUrl=self._property(domain), body=body
        ).execute()
        return resp.get("rows", [])

    @cached()
    def get_domain_overview(self, domain: str, **kwargs) -> DomainOverview:
        try:
            rows = self._query(domain, dimensions=[], days=28, limit=1)
            if rows:
                r = rows[0]
                return DomainOverview(
                    domain=domain,
                    total_clicks=int(r.get("clicks", 0)),
                    total_impressions=int(r.get("impressions", 0)),
                    avg_ctr=round(r.get("ctr", 0) * 100, 2),
                    avg_position=round(r.get("position", 0), 1),
                )
        except Exception:
            pass
        return DomainOverview(domain=domain)

    @cached()
    def get_keywords(self, domain: str, limit: int = 50, **kwargs) -> list[Keyword]:
        try:
            rows = self._query(domain, dimensions=["query"], days=28, limit=limit)
            result = []
            for r in rows:
                keys = r.get("keys", [])
                result.append(Keyword(
                    keyword=keys[0] if keys else "",
                    position=round(r.get("position", 0)),
                    clicks=int(r.get("clicks", 0)),
                    impressions=int(r.get("impressions", 0)),
                    ctr=round(r.get("ctr", 0) * 100, 2),
                ))
            return result
        except Exception:
            return []

    @cached()
    def get_backlinks(self, domain: str, **kwargs) -> BacklinkSummary:
        return BacklinkSummary()

    @cached(ttl=3600)
    def get_audit(self, domain: str, **kwargs) -> AuditReport:
        return AuditReport()

    @cached()
    def get_competitors(
        self, domain: str, competitors: list[str] | None = None, **kwargs
    ) -> list[CompetitorSnapshot]:
        return []

    @cached()
    def get_pages(self, domain: str, days: int = 28, limit: int = 50) -> list[GSCPage]:
        """Top pages by clicks."""
        try:
            rows = self._query(domain, dimensions=["page"], days=days, limit=limit)
            return [
                GSCPage(
                    url=r.get("keys", [""])[0],
                    clicks=int(r.get("clicks", 0)),
                    impressions=int(r.get("impressions", 0)),
                    ctr=round(r.get("ctr", 0) * 100, 2),
                    position=round(r.get("position", 0), 1),
                )
                for r in rows
            ]
        except Exception:
            return []

    @cached(ttl=3600)
    def get_performance_over_time(
        self, domain: str, days: int = 28
    ) -> list[GSCDataPoint]:
        """Daily clicks/impressions/position time series."""
        try:
            rows = self._query(domain, dimensions=["date"], days=days, limit=days)
            rows.sort(key=lambda r: r.get("keys", [""])[0])
            return [
                GSCDataPoint(
                    date=r.get("keys", [""])[0],
                    clicks=int(r.get("clicks", 0)),
                    impressions=int(r.get("impressions", 0)),
                    ctr=round(r.get("ctr", 0) * 100, 2),
                    position=round(r.get("position", 0), 1),
                )
                for r in rows
            ]
        except Exception:
            return []

    def list_properties(self) -> list[str]:
        """Return all GSC properties the authenticated user has access to."""
        try:
            resp = self._svc().sites().list().execute()
            return [s.get("siteUrl", "") for s in resp.get("siteEntry", [])]
        except Exception:
            return []
