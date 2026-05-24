"""SEMrush API provider — calls the SEMrush REST API directly."""
from __future__ import annotations

import httpx

from core.cache import cached
from core.config import get_settings
from core.models import (
    AuditIssue,
    AuditReport,
    BacklinkSummary,
    CompetitorSnapshot,
    DomainOverview,
    Keyword,
    PageSpeedResult,
    ReferringDomain,
)
from providers.base import SEOProvider

_SEMRUSH_BASE = "https://api.semrush.com"


def _fmt(domain: str) -> str:
    return domain.lower().strip().removeprefix("https://").removeprefix("http://").rstrip("/")


class SemrushProvider(SEOProvider):
    """Fetches data from the SEMrush API (requires a valid API key in .env)."""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.seo_api_key
        self.base_url = _SEMRUSH_BASE

    def _get(self, params: dict) -> str:
        params["key"] = self.api_key
        with httpx.Client(timeout=30) as client:
            resp = client.get(self.base_url, params=params)
            resp.raise_for_status()
            return resp.text

    def _parse_csv(self, text: str) -> list[dict]:
        lines = [l for l in text.strip().splitlines() if l]
        if len(lines) < 2:
            return []
        headers = lines[0].split(";")
        rows = []
        for line in lines[1:]:
            values = line.split(";")
            rows.append(dict(zip(headers, values)))
        return rows

    @cached()
    def get_domain_overview(self, domain: str, **kwargs) -> DomainOverview:
        domain = _fmt(domain)
        db = kwargs.get("database", "us")
        try:
            text = self._get({
                "type": "domain_rank",
                "domain": domain,
                "database": db,
                "export_columns": "Dn,Rk,Or,Ot,Oc,Ad,At,Ac,Sh,Sv,Sr,XN",
            })
            rows = self._parse_csv(text)
            if rows:
                r = rows[0]
                return DomainOverview(
                    domain=domain,
                    authority_score=_int(r.get("Rk")),
                    organic_traffic=_int(r.get("Ot")),
                    organic_keywords=_int(r.get("Or")),
                    backlinks_total=None,
                    referring_domains=None,
                )
        except Exception:
            pass
        return DomainOverview(domain=domain)

    @cached()
    def get_keywords(self, domain: str, limit: int = 50, **kwargs) -> list[Keyword]:
        domain = _fmt(domain)
        db = kwargs.get("database", "us")
        try:
            text = self._get({
                "type": "domain_organic",
                "domain": domain,
                "database": db,
                "display_limit": limit,
                "export_columns": "Ph,Po,Nq,Cp,Co,Tr,Ur",
            })
            rows = self._parse_csv(text)
            keywords = []
            for r in rows:
                keywords.append(Keyword(
                    keyword=r.get("Ph", ""),
                    position=_int(r.get("Po")),
                    search_volume=_int(r.get("Nq")),
                    cpc=_float(r.get("Cp")),
                    difficulty=_float(r.get("Co")),
                    traffic=_int(r.get("Tr")),
                    url=r.get("Ur"),
                ))
            return keywords
        except Exception:
            return []

    @cached()
    def get_backlinks(self, domain: str, **kwargs) -> BacklinkSummary:
        domain = _fmt(domain)
        try:
            text = self._get({
                "type": "backlinks_overview",
                "target": domain,
                "target_type": "root_domain",
                "export_columns": "ascore,total,domains_num,urls_num,ips_num,ipclassc_num,follows_num,nofollows_num",
            })
            rows = self._parse_csv(text)
            if rows:
                r = rows[0]
                return BacklinkSummary(
                    total_backlinks=_int(r.get("total")) or 0,
                    referring_domains=_int(r.get("domains_num")) or 0,
                )
        except Exception:
            pass
        return BacklinkSummary()

    @cached(ttl=3600)
    def get_audit(self, domain: str, **kwargs) -> AuditReport:
        # SEMrush site audit is project-based and async; return empty for now
        return AuditReport()

    @cached()
    def get_competitors(
        self, domain: str, competitors: list[str] | None = None, **kwargs
    ) -> list[CompetitorSnapshot]:
        domain = _fmt(domain)
        db = kwargs.get("database", "us")
        results = []
        targets = competitors or []
        if not targets:
            try:
                text = self._get({
                    "type": "domain_organic_organic",
                    "domain": domain,
                    "database": db,
                    "display_limit": 5,
                    "export_columns": "Dn,Co,Np,Or,Ot",
                })
                rows = self._parse_csv(text)
                targets = [r["Dn"] for r in rows if r.get("Dn")]
            except Exception:
                pass
        for comp in targets[:5]:
            overview = self.get_domain_overview(comp, **kwargs)
            results.append(CompetitorSnapshot(
                domain=comp,
                authority_score=overview.authority_score,
                organic_traffic=overview.organic_traffic,
                organic_keywords=overview.organic_keywords,
            ))
        return results


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _float(val) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
