from __future__ import annotations

import streamlit as st

from core.models import DomainOverview
from providers.base import SEOProvider


def _fmt(val, suffix: str = "") -> str:
    if val is None:
        return "N/A"
    if isinstance(val, int) and val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M{suffix}"
    if isinstance(val, int) and val >= 1_000:
        return f"{val / 1_000:.1f}K{suffix}"
    return f"{val}{suffix}"


def render(domain: str, provider: SEOProvider, options: dict) -> None:
    st.header(f"Domain Overview — {domain}")

    cache_key = f"overview_{domain}"
    if cache_key not in st.session_state:
        with st.spinner("Fetching domain overview..."):
            try:
                st.session_state[cache_key] = provider.get_domain_overview(domain, **options)
            except Exception as exc:
                st.error(f"Could not fetch overview: {exc}")
                return

    data: DomainOverview = st.session_state[cache_key]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Authority Score", _fmt(data.authority_score))
    col2.metric("Organic Traffic", _fmt(data.organic_traffic, "/mo"))
    col3.metric("Organic Keywords", _fmt(data.organic_keywords))
    col4.metric("Backlinks", _fmt(data.backlinks_total))
    col5.metric("Referring Domains", _fmt(data.referring_domains))

    st.caption(f"Data fetched at: {data.fetched_at.strftime('%Y-%m-%d %H:%M')}")

    if all(v is None for v in [data.authority_score, data.organic_traffic, data.organic_keywords]):
        st.info(
            "No data available for this domain. "
            "If you're using the Scraper provider, switch to SEMrush API for richer metrics."
        )
