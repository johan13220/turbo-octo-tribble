from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class DomainOverview(BaseModel):
    domain: str
    authority_score: int | None = None
    organic_traffic: int | None = None
    organic_keywords: int | None = None
    backlinks_total: int | None = None
    referring_domains: int | None = None
    fetched_at: datetime = Field(default_factory=datetime.now)


class Keyword(BaseModel):
    keyword: str
    position: int | None = None
    search_volume: int | None = None
    difficulty: float | None = None
    cpc: float | None = None
    url: str | None = None
    traffic: int | None = None


class ReferringDomain(BaseModel):
    domain: str
    backlinks: int | None = None
    authority_score: int | None = None


class BacklinkSummary(BaseModel):
    total_backlinks: int = 0
    referring_domains: int = 0
    new_backlinks: int = 0
    lost_backlinks: int = 0
    top_referring_domains: list[ReferringDomain] = Field(default_factory=list)


class AuditIssue(BaseModel):
    description: str
    count: int = 0
    category: str = ""


class PageSpeedResult(BaseModel):
    score: float | None = None
    lcp: float | None = None
    cls: float | None = None
    fcp: float | None = None


class AuditReport(BaseModel):
    health_score: float = 0.0
    errors: list[AuditIssue] = Field(default_factory=list)
    warnings: list[AuditIssue] = Field(default_factory=list)
    notices: list[AuditIssue] = Field(default_factory=list)
    pagespeed_desktop: PageSpeedResult | None = None
    pagespeed_mobile: PageSpeedResult | None = None


class CompetitorSnapshot(BaseModel):
    domain: str
    authority_score: int | None = None
    organic_traffic: int | None = None
    organic_keywords: int | None = None
    common_keywords: int | None = None
