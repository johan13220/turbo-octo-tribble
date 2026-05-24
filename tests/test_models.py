from core.models import AuditReport, BacklinkSummary, DomainOverview, Keyword


def test_domain_overview_defaults():
    d = DomainOverview(domain="example.com")
    assert d.authority_score is None
    assert d.organic_traffic is None
    assert d.domain == "example.com"


def test_keyword_model():
    kw = Keyword(keyword="seo tool", position=5, search_volume=1000, difficulty=40.0)
    assert kw.keyword == "seo tool"
    assert kw.position == 5


def test_audit_report_defaults():
    r = AuditReport()
    assert r.health_score == 0.0
    assert r.errors == []
    assert r.warnings == []


def test_backlink_summary_defaults():
    b = BacklinkSummary()
    assert b.total_backlinks == 0
    assert b.referring_domains == 0
