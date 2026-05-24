"""Tests for GSC provider using a mock Google API service."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.models import GSCDataPoint, GSCPage, Keyword
from providers.gsc import GSCProvider, _resolve_property


@pytest.fixture
def mock_service():
    svc = MagicMock()
    svc.sites().list().execute.return_value = {
        "siteEntry": [
            {"siteUrl": "sc-domain:example.com"},
            {"siteUrl": "https://www.other.com/"},
        ]
    }
    return svc


@pytest.fixture
def gsc_provider(mock_service):
    provider = GSCProvider.__new__(GSCProvider)
    provider._service = mock_service
    provider._property_cache = {}
    return provider


def _make_rows(keys_list, clicks, impressions, ctr, position):
    return [
        {"keys": [k], "clicks": c, "impressions": i, "ctr": ct / 100, "position": p}
        for k, c, i, ct, p in zip(keys_list, clicks, impressions, ctr, position)
    ]


def test_resolve_property_domain(mock_service):
    prop = _resolve_property(mock_service, "example.com")
    assert prop == "sc-domain:example.com"


def test_resolve_property_fallback(mock_service):
    prop = _resolve_property(mock_service, "unknown.com")
    assert prop == "sc-domain:unknown.com"


def test_get_keywords(gsc_provider, mock_service):
    mock_service.searchanalytics().query().execute.return_value = {
        "rows": _make_rows(
            ["python seo", "seo tools"],
            [120, 85], [2000, 1500], [6.0, 5.67], [3.2, 5.1],
        )
    }
    keywords = gsc_provider.get_keywords("example.com")
    assert len(keywords) == 2
    assert keywords[0].keyword == "python seo"
    assert keywords[0].clicks == 120
    assert keywords[0].impressions == 2000
    assert keywords[0].ctr == 6.0


def test_get_pages(gsc_provider, mock_service):
    mock_service.searchanalytics().query().execute.return_value = {
        "rows": _make_rows(
            ["https://example.com/page1", "https://example.com/page2"],
            [200, 150], [3000, 2500], [6.67, 6.0], [2.1, 3.4],
        )
    }
    pages = gsc_provider.get_pages("example.com")
    assert len(pages) == 2
    assert pages[0].url == "https://example.com/page1"
    assert pages[0].clicks == 200


def test_get_performance_over_time(gsc_provider, mock_service):
    mock_service.searchanalytics().query().execute.return_value = {
        "rows": _make_rows(
            ["2024-01-01", "2024-01-02"],
            [100, 120], [1800, 2000], [5.56, 6.0], [4.2, 3.8],
        )
    }
    points = gsc_provider.get_performance_over_time("example.com", days=2)
    assert len(points) == 2
    assert points[0].date == "2024-01-01"
    assert points[0].clicks == 100


def test_get_domain_overview(gsc_provider, mock_service):
    mock_service.searchanalytics().query().execute.return_value = {
        "rows": [{"clicks": 5000, "impressions": 80000, "ctr": 0.0625, "position": 8.3}]
    }
    overview = gsc_provider.get_domain_overview("example.com")
    assert overview.total_clicks == 5000
    assert overview.total_impressions == 80000
    assert overview.avg_ctr == 6.25
    assert overview.avg_position == 8.3


def test_get_keywords_api_error(gsc_provider, mock_service):
    mock_service.searchanalytics().query().execute.side_effect = Exception("API error")
    # Use a unique domain so the disk cache from other tests doesn't interfere
    keywords = gsc_provider.get_keywords("api-error-test.com")
    assert keywords == []


def test_gsc_performance_chart():
    from ui.charts import gsc_performance_chart
    points = [
        GSCDataPoint(date="2024-01-01", clicks=100, impressions=2000, ctr=5.0, position=4.2),
        GSCDataPoint(date="2024-01-02", clicks=120, impressions=2200, ctr=5.45, position=3.9),
    ]
    fig = gsc_performance_chart(points)
    assert fig is not None
    assert len(fig.data) == 3  # clicks, impressions, position traces
