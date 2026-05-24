from __future__ import annotations

import pandas as pd
import streamlit as st

from providers.base import SEOProvider
from ui.charts import keyword_scatter, position_histogram


def render(domain: str, provider: SEOProvider, options: dict) -> None:
    st.header(f"Keywords — {domain}")

    cache_key = f"keywords_{domain}"
    if cache_key not in st.session_state:
        with st.spinner("Fetching keywords..."):
            try:
                st.session_state[cache_key] = provider.get_keywords(domain, limit=100, **options)
            except Exception as exc:
                st.error(f"Could not fetch keywords: {exc}")
                return

    keywords = st.session_state[cache_key]

    if not keywords:
        st.info(
            "No keyword data available. "
            "Keyword rankings require the SEMrush API provider."
        )
        return

    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(position_histogram(keywords), use_container_width=True)
    with col_right:
        st.plotly_chart(keyword_scatter(keywords), use_container_width=True)

    st.subheader(f"Top {len(keywords)} Keywords")

    df = pd.DataFrame([k.model_dump() for k in keywords])
    df = df.rename(columns={
        "keyword": "Keyword",
        "position": "Position",
        "search_volume": "Search Volume",
        "difficulty": "Difficulty",
        "cpc": "CPC ($)",
        "traffic": "Est. Traffic",
        "url": "URL",
    })
    st.dataframe(
        df[["Keyword", "Position", "Search Volume", "Difficulty", "CPC ($)", "Est. Traffic", "URL"]],
        use_container_width=True,
        hide_index=True,
    )
