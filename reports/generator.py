from __future__ import annotations

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from core.models import AuditReport, BacklinkSummary, DomainOverview, Keyword
from providers.base import SEOProvider
from ui.charts import audit_gauge, competitor_bar, keyword_scatter, position_histogram

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class ReportGenerator:
    def __init__(self, domain: str, provider: SEOProvider, options: dict):
        self.domain = domain
        self.provider = provider
        self.options = options
        self._env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), autoescape=True)

    def _collect(self) -> dict:
        overview = self.provider.get_domain_overview(self.domain, **self.options)
        keywords = self.provider.get_keywords(self.domain, limit=50, **self.options)
        backlinks = self.provider.get_backlinks(self.domain, **self.options)
        audit = self.provider.get_audit(self.domain, **self.options)
        competitors = self.provider.get_competitors(self.domain, **self.options)
        return {
            "domain": self.domain,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "overview": overview,
            "keywords": keywords,
            "backlinks": backlinks,
            "audit": audit,
            "competitors": competitors,
        }

    def _chart_html(self, data: dict) -> dict:
        charts = {}
        kw = data["keywords"]
        if kw:
            charts["keyword_scatter"] = keyword_scatter(kw).to_html(full_html=False, include_plotlyjs="cdn")
            charts["position_hist"] = position_histogram(kw).to_html(full_html=False, include_plotlyjs=False)
        charts["audit_gauge"] = audit_gauge(data["audit"].health_score).to_html(full_html=False, include_plotlyjs=False)
        if data["competitors"]:
            charts["competitor_bar"] = competitor_bar(data["competitors"]).to_html(full_html=False, include_plotlyjs=False)
        return charts

    def build_html(self) -> str:
        data = self._collect()
        charts = self._chart_html(data)
        template = self._env.get_template("report.html.j2")
        return template.render(**data, charts=charts)

    def build_pdf(self) -> bytes | None:
        try:
            from weasyprint import HTML
        except ImportError:
            return None
        html_content = self.build_html()
        return HTML(string=html_content, base_url=".").write_pdf()
