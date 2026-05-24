from __future__ import annotations

import pandas as pd
import streamlit as st

from providers.base import SEOProvider


def _fmt(val) -> str:
    if val is None:
        return "N/A"
    if isinstance(val, int) and val >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    if isinstance(val, int) and val >= 1_000:
        return f"{val / 1_000:.1f}K"
    return str(val)


def render(domain: str, provider: SEOProvider, options: dict) -> None:
    st.header(f"Backlinks — {domain}")

    cache_key = f"backlinks_{domain}"
    if cache_key not in st.session_state:
        with st.spinner("Fetching backlink data..."):
            try:
                st.session_state[cache_key] = provider.get_backlinks(domain, **options)
            except Exception as exc:
                st.error(f"Could not fetch backlinks: {exc}")
                return

    data = st.session_state[cache_key]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Backlinks", _fmt(data.total_backlinks))
    col2.metric("Referring Domains", _fmt(data.referring_domains))
    col3.metric("New Backlinks", _fmt(data.new_backlinks))
    col4.metric("Lost Backlinks", _fmt(data.lost_backlinks))

    if data.total_backlinks == 0:
        st.info("No backlink data available. Backlink analysis requires the SEMrush API provider.")
        return

    if data.top_referring_domains:
        st.subheader("Top Referring Domains")
        df = pd.DataFrame([r.model_dump() for r in data.top_referring_domains])
        df = df.rename(columns={"domain": "Domain", "backlinks": "Backlinks", "authority_score": "Authority Score"})
        st.dataframe(df, use_container_width=True, hide_index=True)
