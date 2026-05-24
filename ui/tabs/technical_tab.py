from __future__ import annotations

import streamlit as st

from providers.base import SEOProvider
from ui.charts import audit_gauge


def _severity_icon(severity: str) -> str:
    return {"error": "🔴", "warning": "🟡", "notice": "🔵"}.get(severity, "⚪")


def render(domain: str, provider: SEOProvider, options: dict) -> None:
    st.header(f"Technical Audit — {domain}")

    cache_key = f"audit_{domain}"
    if cache_key not in st.session_state:
        with st.spinner("Running site audit (this may take a moment)..."):
            try:
                st.session_state[cache_key] = provider.get_audit(domain, **options)
            except Exception as exc:
                st.error(f"Could not complete audit: {exc}")
                return

    report = st.session_state[cache_key]

    col_gauge, col_summary = st.columns([1, 2])
    with col_gauge:
        st.plotly_chart(audit_gauge(report.health_score), use_container_width=True)
    with col_summary:
        st.metric("Errors", len(report.errors))
        st.metric("Warnings", len(report.warnings))
        st.metric("Notices", len(report.notices))

    for label, issues, sev in [
        ("Errors", report.errors, "error"),
        ("Warnings", report.warnings, "warning"),
        ("Notices", report.notices, "notice"),
    ]:
        if issues:
            icon = _severity_icon(sev)
            with st.expander(f"{icon} {label} ({len(issues)})", expanded=(sev == "error")):
                for issue in issues:
                    st.markdown(f"- **{issue.description}** — {issue.count} occurrence(s)")

    if not report.errors and not report.warnings and not report.notices:
        st.success("No issues detected. The page looks technically healthy!")
