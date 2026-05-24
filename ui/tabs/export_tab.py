from __future__ import annotations

import streamlit as st

from providers.base import SEOProvider
from reports.generator import ReportGenerator


def render(domain: str, provider: SEOProvider, options: dict) -> None:
    st.header(f"Export Report — {domain}")
    st.markdown("Generate a self-contained HTML report with all available data.")

    if st.button("Generate HTML Report", type="primary"):
        with st.spinner("Collecting data and building report..."):
            try:
                generator = ReportGenerator(domain, provider, options)
                html_content = generator.build_html()
                st.download_button(
                    label="Download HTML Report",
                    data=html_content,
                    file_name=f"seo_report_{domain.replace('.', '_')}.html",
                    mime="text/html",
                )
                st.success("Report ready — click the button above to download.")
            except Exception as exc:
                st.error(f"Could not generate report: {exc}")

    st.markdown("---")
    st.markdown("**PDF export** requires WeasyPrint to be installed (`pip install weasyprint`).")
    if st.button("Generate PDF Report"):
        with st.spinner("Generating PDF..."):
            try:
                generator = ReportGenerator(domain, provider, options)
                pdf_bytes = generator.build_pdf()
                if pdf_bytes:
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"seo_report_{domain.replace('.', '_')}.pdf",
                        mime="application/pdf",
                    )
                    st.success("PDF ready.")
                else:
                    st.error("WeasyPrint is not installed. Run: pip install weasyprint")
            except Exception as exc:
                st.error(f"Could not generate PDF: {exc}")
