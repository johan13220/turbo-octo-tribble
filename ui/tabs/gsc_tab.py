from __future__ import annotations

import pandas as pd
import streamlit as st

from core.config import get_settings
from providers.base import SEOProvider
from providers.gsc import GSCProvider
from ui.charts import gsc_performance_chart


def _is_gsc_configured() -> bool:
    s = get_settings()
    return bool(s.gsc_credentials_path or s.gsc_token_path)


def _setup_instructions() -> None:
    st.info(
        "**Google Search Console n'est pas encore configuré.**\n\n"
        "Suivez ces étapes pour activer l'intégration :\n\n"
        "1. Allez sur [Google Cloud Console](https://console.cloud.google.com/) → "
        "créez un projet → activez l'API **Google Search Console**.\n"
        "2. Créez des identifiants OAuth2 (type : *Desktop app*) → téléchargez `credentials.json`.\n"
        "3. Lancez le script d'authentification :\n"
        "   ```\n   python scripts/gsc_auth.py\n   ```\n"
        "4. Ajoutez les lignes affichées dans votre fichier `.env`.\n"
        "5. Relancez le dashboard et sélectionnez **Google Search Console** comme provider.",
        icon="🔑",
    )


def render(domain: str, provider: SEOProvider, options: dict) -> None:
    st.header(f"Google Search Console — {domain}")

    if not isinstance(provider, GSCProvider):
        _setup_instructions() if not _is_gsc_configured() else st.info(
            "Sélectionnez **Google Search Console** comme provider dans la barre latérale pour voir ces données."
        )
        return

    days_options = {"7 jours": 7, "28 jours": 28, "90 jours": 90}
    days_label = st.radio(
        "Période",
        list(days_options.keys()),
        index=1,
        horizontal=True,
    )
    days = days_options[days_label]

    # --- Summary metrics ---
    perf_key = f"gsc_perf_{domain}_{days}"
    if perf_key not in st.session_state:
        with st.spinner("Chargement des données GSC..."):
            try:
                st.session_state[perf_key] = provider.get_performance_over_time(domain, days=days)
            except Exception as exc:
                st.error(f"Erreur GSC : {exc}")
                return

    data_points = st.session_state[perf_key]

    if data_points:
        total_clicks = sum(p.clicks for p in data_points)
        total_impressions = sum(p.impressions for p in data_points)
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
        avg_pos = sum(p.position for p in data_points) / len(data_points) if data_points else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Clicks", f"{total_clicks:,}")
        c2.metric("Total Impressions", f"{total_impressions:,}")
        c3.metric("Avg CTR", f"{avg_ctr:.2f}%")
        c4.metric("Avg Position", f"{avg_pos:.1f}")

        st.plotly_chart(gsc_performance_chart(data_points), use_container_width=True)
    else:
        st.warning("Aucune donnée de performance disponible pour cette période.")

    st.markdown("---")

    # --- Queries + Pages side by side ---
    col_q, col_p = st.columns(2)

    with col_q:
        st.subheader("Top Queries")
        kw_key = f"gsc_kw_{domain}_{days}"
        if kw_key not in st.session_state:
            with st.spinner("Chargement des requêtes..."):
                try:
                    st.session_state[kw_key] = provider.get_keywords(domain, limit=50)
                except Exception as exc:
                    st.error(str(exc))
                    st.session_state[kw_key] = []

        keywords = st.session_state[kw_key]
        if keywords:
            df = pd.DataFrame([
                {
                    "Query": k.keyword,
                    "Clicks": k.clicks,
                    "Impressions": k.impressions,
                    "CTR (%)": k.ctr,
                    "Position": k.position,
                }
                for k in keywords
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune requête disponible.")

    with col_p:
        st.subheader("Top Pages")
        pages_key = f"gsc_pages_{domain}_{days}"
        if pages_key not in st.session_state:
            with st.spinner("Chargement des pages..."):
                try:
                    st.session_state[pages_key] = provider.get_pages(domain, days=days)
                except Exception as exc:
                    st.error(str(exc))
                    st.session_state[pages_key] = []

        pages = st.session_state[pages_key]
        if pages:
            df = pd.DataFrame([
                {
                    "URL": p.url,
                    "Clicks": p.clicks,
                    "Impressions": p.impressions,
                    "CTR (%)": p.ctr,
                    "Position": p.position,
                }
                for p in pages
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune page disponible.")

    # --- List accessible properties ---
    with st.expander("Propriétés GSC accessibles"):
        props = provider.list_properties()
        if props:
            for p in props:
                st.code(p)
        else:
            st.caption("Impossible de récupérer la liste des propriétés.")
