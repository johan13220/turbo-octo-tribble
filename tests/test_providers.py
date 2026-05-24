from tests.conftest import MockProvider


def test_mock_overview(mock_provider, sample_domain):
    overview = mock_provider.get_domain_overview(sample_domain)
    assert overview.domain == sample_domain
    assert overview.authority_score == 72
    assert overview.organic_traffic == 45000


def test_mock_keywords(mock_provider, sample_domain):
    keywords = mock_provider.get_keywords(sample_domain)
    assert len(keywords) == 3
    assert all(kw.keyword for kw in keywords)
    assert keywords[0].position == 3


def test_mock_backlinks(mock_provider, sample_domain):
    bl = mock_provider.get_backlinks(sample_domain)
    assert bl.total_backlinks == 8500
    assert len(bl.top_referring_domains) == 2


def test_mock_audit(mock_provider, sample_domain):
    audit = mock_provider.get_audit(sample_domain)
    assert audit.health_score == 87.0
    assert len(audit.errors) == 1
    assert len(audit.warnings) == 1


def test_mock_competitors(mock_provider, sample_domain):
    comps = mock_provider.get_competitors(sample_domain)
    assert len(comps) == 2
    assert comps[0].domain == "competitor1.com"
