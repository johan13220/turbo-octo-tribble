from __future__ import annotations
from datetime import datetime
import pytest

from core.models import (
    AuditIssue,
    AuditReport,
    BacklinkSummary,
    CompetitorSnapshot,
    DomainOverview,
    Keyword,
    ReferringDomain,
)
from providers.base import SEOProvider


class MockProvider(SEOProvider):
    def get_domain_overview(self, domain: str, **kwargs) -> DomainOverview:
        return DomainOverview(
            domain=domain,
            authority_score=72,
            organic_traffic=45000,
            organic_keywords=1200,
            backlinks_total=8500,
            referring_domains=320,
        )

    def get_keywords(self, domain: str, limit: int = 50, **kwargs) -> list[Keyword]:
        return [
            Keyword(keyword="python tutorial", position=3, search_volume=12000, difficulty=45.0, cpc=1.20),
            Keyword(keyword="learn python", position=7, search_volume=8500, difficulty=52.0, cpc=0.95),
            Keyword(keyword="python for beginners", position=12, search_volume=6200, difficulty=38.0, cpc=0.80),
        ]

    def get_backlinks(self, domain: str, **kwargs) -> BacklinkSummary:
        return BacklinkSummary(
            total_backlinks=8500,
            referring_domains=320,
            new_backlinks=42,
            lost_backlinks=15,
            top_referring_domains=[
                ReferringDomain(domain="github.com", backlinks=120, authority_score=94),
                ReferringDomain(domain="stackoverflow.com", backlinks=85, authority_score=91),
            ],
        )

    def get_audit(self, domain: str, **kwargs) -> AuditReport:
        return AuditReport(
            health_score=87.0,
            errors=[AuditIssue(description="Missing H1 tag", count=1, category="content")],
            warnings=[AuditIssue(description="Meta description too long", count=3, category="meta")],
            notices=[AuditIssue(description="No canonical link tag found", count=1, category="meta")],
        )

    def get_competitors(self, domain: str, competitors=None, **kwargs) -> list[CompetitorSnapshot]:
        return [
            CompetitorSnapshot(domain="competitor1.com", authority_score=65, organic_traffic=32000, organic_keywords=890),
            CompetitorSnapshot(domain="competitor2.com", authority_score=58, organic_traffic=21000, organic_keywords=610),
        ]


@pytest.fixture
def mock_provider():
    return MockProvider()


@pytest.fixture
def sample_domain():
    return "example.com"
