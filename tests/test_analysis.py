from ui.charts import keyword_scatter, position_histogram, audit_gauge, competitor_bar


def test_keyword_scatter_empty():
    fig = keyword_scatter([])
    assert fig is not None


def test_position_histogram(mock_provider, sample_domain):
    keywords = mock_provider.get_keywords(sample_domain)
    fig = position_histogram(keywords)
    assert fig is not None


def test_audit_gauge():
    fig = audit_gauge(87.5)
    assert fig is not None


def test_competitor_bar(mock_provider, sample_domain):
    comps = mock_provider.get_competitors(sample_domain)
    fig = competitor_bar(comps, metric="organic_traffic")
    assert fig is not None
