from __future__ import annotations

import streamlit as st

from core.cache import cache_info, clear_domain_cache
from core.config import get_settings
from providers.base import SEOProvider
from providers.gsc import GSCProvider
from providers.scraper import ScraperProvider
from providers.semrush import SemrushProvider

_DATABASES = {
    "United States": "us",
    "United Kingdom": "uk",
    "France": "fr",
    "Germany": "de",
    "Spain": "es",
    "Canada": "ca",
    "Australia": "au",
}


def render_sidebar() -> tuple[str, SEOProvider, dict]:
    """Render the sidebar and return (domain, provider, options)."""
    settings = get_settings()

    with st.sidebar:
        st.title("SEO Dashboard")
        st.markdown("---")

        domain = st.text_input(
            "Domain to analyse",
            placeholder="example.com",
            help="Enter a domain without http:// — e.g. wikipedia.org",
        ).strip()

        database = st.selectbox("Market / Database", list(_DATABASES.keys()), index=0)

        st.markdown("---")
        st.subheader("Data Provider")

        has_semrush = bool(settings.seo_api_key)
        has_gsc = bool(settings.gsc_credentials_path or settings.gsc_token_path)

        provider_options = ["SEMrush API", "Google Search Console", "Scraper (no API key)"]
        if has_gsc:
            default_idx = 1
        elif has_semrush:
            default_idx = 0
        else:
            default_idx = 2

        provider_choice = st.radio(
            "Provider",
            provider_options,
            index=default_idx,
            help=(
                "SEMrush: clé API requise (SEO_API_KEY)\n"
                "GSC: OAuth2 requis — lancez `python scripts/gsc_auth.py`\n"
                "Scraper: aucune clé requise (métriques on-page uniquement)"
            ),
        )

        if provider_choice == "SEMrush API" and not has_semrush:
            st.warning("SEO_API_KEY absent du .env — passage au Scraper.")
            provider_choice = "Scraper (no API key)"

        if provider_choice == "Google Search Console" and not has_gsc:
            st.warning(
                "GSC non configuré. Lancez `python scripts/gsc_auth.py` pour l'activer.\n"
                "Passage au Scraper pour l'instant."
            )
            provider_choice = "Scraper (no API key)"

        provider: SEOProvider
        if provider_choice == "SEMrush API":
            provider = SemrushProvider()
        elif provider_choice == "Google Search Console":
            provider = GSCProvider()
        else:
            provider = ScraperProvider()

        st.markdown("---")
        st.subheader("Cache")
        info = cache_info()
        st.caption(f"{info['size']} cached entries")
        if domain and st.button("Clear cache for this domain"):
            n = clear_domain_cache(domain)
            st.success(f"Removed {n} entries for {domain}")
            st.rerun()

    options = {"database": _DATABASES[database]}
    return domain, provider, options
