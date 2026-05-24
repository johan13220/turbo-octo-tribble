import streamlit as st

st.set_page_config(
    page_title="SEO Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.sidebar import render_sidebar
from ui.tabs import (
    backlinks_tab,
    competitors_tab,
    export_tab,
    keywords_tab,
    overview_tab,
    technical_tab,
)

domain, provider, options = render_sidebar()

if domain:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Domain Overview",
        "Keywords",
        "Backlinks",
        "Technical Audit",
        "Competitors",
        "Export Report",
    ])
    with tab1:
        overview_tab.render(domain, provider, options)
    with tab2:
        keywords_tab.render(domain, provider, options)
    with tab3:
        backlinks_tab.render(domain, provider, options)
    with tab4:
        technical_tab.render(domain, provider, options)
    with tab5:
        competitors_tab.render(domain, provider, options)
    with tab6:
        export_tab.render(domain, provider, options)
else:
    st.markdown(
        """
        <div style="text-align:center; padding:80px 20px;">
          <h1>🔍 SEO Dashboard</h1>
          <p style="font-size:1.2em; color:#555; margin-top:16px;">
            Enter a domain in the sidebar to start your analysis.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
