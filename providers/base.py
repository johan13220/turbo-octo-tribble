from abc import ABC, abstractmethod

from core.models import (
    AuditReport,
    BacklinkSummary,
    CompetitorSnapshot,
    DomainOverview,
    Keyword,
)


class SEOProvider(ABC):
    """Abstract interface every data provider must implement."""

    @abstractmethod
    def get_domain_overview(self, domain: str, **kwargs) -> DomainOverview: ...

    @abstractmethod
    def get_keywords(self, domain: str, limit: int = 50, **kwargs) -> list[Keyword]: ...

    @abstractmethod
    def get_backlinks(self, domain: str, **kwargs) -> BacklinkSummary: ...

    @abstractmethod
    def get_audit(self, domain: str, **kwargs) -> AuditReport: ...

    @abstractmethod
    def get_competitors(
        self, domain: str, competitors: list[str] | None = None, **kwargs
    ) -> list[CompetitorSnapshot]: ...
