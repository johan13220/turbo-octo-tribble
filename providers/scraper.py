"""Scraping-based provider — no API key required. Covers on-page metrics only."""
from __future__ import annotations

import re

import httpx
from bs4 import BeautifulSoup

from core.cache import cached
from core.models import (
    AuditIssue,
    AuditReport,
    BacklinkSummary,
    CompetitorSnapshot,
    DomainOverview,
    Keyword,
)
from providers.base import SEOProvider

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SEODashboard/1.0; +https://github.com/user/seo-dashboard)"
    )
}


def _ensure_scheme(domain: str) -> str:
    domain = domain.strip()
    if not domain.startswith(("http://", "https://")):
        return "https://" + domain
    return domain


class ScraperProvider(SEOProvider):
    """Provides on-page SEO analysis without an API key using BeautifulSoup."""

    @cached()
    def get_domain_overview(self, domain: str, **kwargs) -> DomainOverview:
        url = _ensure_scheme(domain)
        clean = domain.lower().removeprefix("https://").removeprefix("http://").rstrip("/")
        try:
            with httpx.Client(timeout=15, follow_redirects=True, headers=_HEADERS) as client:
                resp = client.get(url)
                resp.raise_for_status()
        except Exception:
            return DomainOverview(domain=clean)
        return DomainOverview(domain=clean)

    @cached()
    def get_keywords(self, domain: str, limit: int = 50, **kwargs) -> list[Keyword]:
        # Cannot determine keyword rankings without an API
        return []

    @cached()
    def get_backlinks(self, domain: str, **kwargs) -> BacklinkSummary:
        return BacklinkSummary()

    @cached(ttl=3600)
    def get_audit(self, domain: str, **kwargs) -> AuditReport:
        url = _ensure_scheme(domain)
        errors: list[AuditIssue] = []
        warnings: list[AuditIssue] = []
        notices: list[AuditIssue] = []
        score = 100.0

        try:
            with httpx.Client(timeout=15, follow_redirects=True, headers=_HEADERS) as client:
                resp = client.get(url)
                resp.raise_for_status()
                html = resp.text
        except Exception as exc:
            errors.append(AuditIssue(description=f"Could not fetch page: {exc}", count=1, category="crawl"))
            return AuditReport(health_score=0.0, errors=errors)

        soup = BeautifulSoup(html, "lxml")

        # Title
        title_tag = soup.find("title")
        if not title_tag or not title_tag.get_text(strip=True):
            errors.append(AuditIssue(description="Missing <title> tag", count=1, category="meta"))
            score -= 15
        elif len(title_tag.get_text(strip=True)) > 60:
            warnings.append(AuditIssue(description="Title tag too long (> 60 chars)", count=1, category="meta"))
            score -= 5

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
        if not meta_desc or not meta_desc.get("content", "").strip():
            warnings.append(AuditIssue(description="Missing meta description", count=1, category="meta"))
            score -= 10
        elif len(meta_desc.get("content", "")) > 160:
            notices.append(AuditIssue(description="Meta description too long (> 160 chars)", count=1, category="meta"))
            score -= 3

        # H1
        h1_tags = soup.find_all("h1")
        if not h1_tags:
            errors.append(AuditIssue(description="Missing H1 tag", count=1, category="content"))
            score -= 10
        elif len(h1_tags) > 1:
            warnings.append(AuditIssue(description=f"Multiple H1 tags ({len(h1_tags)})", count=len(h1_tags), category="content"))
            score -= 5

        # Images without alt
        images_no_alt = [img for img in soup.find_all("img") if not img.get("alt")]
        if images_no_alt:
            count = len(images_no_alt)
            warnings.append(AuditIssue(description=f"Images missing alt attribute", count=count, category="accessibility"))
            score -= min(10, count * 2)

        # Canonical
        canonical = soup.find("link", attrs={"rel": re.compile("^canonical$", re.I)})
        if not canonical:
            notices.append(AuditIssue(description="No canonical link tag found", count=1, category="meta"))
            score -= 3

        # Robots meta
        robots_meta = soup.find("meta", attrs={"name": re.compile("^robots$", re.I)})
        if robots_meta:
            content = robots_meta.get("content", "").lower()
            if "noindex" in content:
                errors.append(AuditIssue(description="Page has noindex directive", count=1, category="indexability"))
                score -= 20

        return AuditReport(
            health_score=max(0.0, score),
            errors=errors,
            warnings=warnings,
            notices=notices,
        )

    @cached()
    def get_competitors(
        self, domain: str, competitors: list[str] | None = None, **kwargs
    ) -> list[CompetitorSnapshot]:
        if not competitors:
            return []
        results = []
        for comp in competitors[:5]:
            clean = comp.lower().removeprefix("https://").removeprefix("http://").rstrip("/")
            results.append(CompetitorSnapshot(domain=clean))
        return results
