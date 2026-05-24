from __future__ import annotations

import pandas as pd
import streamlit as st

from providers.base import SEOProvider
from ui.charts import competitor_bar


def render(domain: str, provider: SEOProvider, options: dict) -> None:
    st.header(f"Competitor Analysis — {domain}")

    with st.expander("Add up to 3 competitors manually (optional)", expanded=False):
        c1, c2, c3 = st.columns(3)
        comp1 = c1.text_input("Competitor 1", key="comp1", placeholder="competitor1.com")
        comp2 = c2.text_input("Competitor 2", key="comp2", placeholder="competitor2.com")
        comp3 = c3.text_input("Competitor 3", key="comp3", placeholder="competitor3.com")

    manual = [c.strip() for c in [comp1, comp2, comp3] if c.strip()]
    cache_key = f"competitors_{domain}_{'_'.join(manual)}"

    if st.button("Analyse Competitors") or cache_key in st.session_state:
        if cache_key not in st.session_state:
            with st.spinner("Fetching competitor data..."):
                try:
                    st.session_state[cache_key] = provider.get_competitors(
                        domain, competitors=manual or None, **options
                    )
                except Exception as exc:
                    st.error(f"Could not fetch competitor data: {exc}")
                    return

        snapshots = st.session_state[cache_key]

        if not snapshots:
            st.info("No competitor data found. Try adding competitors manually above.")
            return

        metric = st.selectbox(
            "Compare by",
            ["organic_traffic", "organic_keywords", "authority_score"],
            format_func=lambda x: x.replace("_", " ").title(),
        )

        st.plotly_chart(competitor_bar(snapshots, metric=metric), use_container_width=True)

        df = pd.DataFrame([s.model_dump() for s in snapshots])
        df = df.rename(columns={
            "domain": "Domain",
            "authority_score": "Authority Score",
            "organic_traffic": "Organic Traffic",
            "organic_keywords": "Organic Keywords",
            "common_keywords": "Common Keywords",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
