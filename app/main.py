"""DeltaGrid — Paris Agreement NDC vs energy trajectory gap analysis."""

import streamlit as st

from app.components.choropleth import render_choropleth
from app.components.sidebar import render_sidebar
from app.components.ui import render_footer, render_page_header
from src.data.owid import get_owid_year_range, load_owid_data
from src.models.scoring import compute_green_score


@st.cache_data(show_spinner=False, ttl=3600)
def _cached_score(energy_df, weights_key: tuple):
    """Compute green scores with memoization."""
    weights = dict(weights_key)
    return compute_green_score(energy_df, weights)


def inject_custom_css() -> None:
    """Inject custom CSS for visual improvements and accessibility."""
    st.markdown(
        """
        <style>
        /* Skip link for keyboard navigation */
        .skip-link {
            position: absolute;
            top: -40px;
            left: 0;
            background: #4CAF50;
            color: white;
            padding: 8px 16px;
            z-index: 10000;
            transition: top 0.2s;
            font-size: 14px;
            border-radius: 0 0 4px 0;
        }
        .skip-link:focus {
            top: 0;
        }

        /* Skeleton shimmer animation */
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        .skeleton {
            background: linear-gradient(90deg,
                #1A1F2E 25%, #252B3B 50%, #1A1F2E 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 6px;
            min-height: 200px;
        }

        /* Respect reduced motion preference */
        @media (prefers-reduced-motion: reduce) {
            .skeleton { animation: none; }
            * { transition-duration: 0.01ms !important; }
        }

        /* Card container for metrics */
        .metric-card {
            background: #1A1F2E;
            border: 1px solid #2D3548;
            border-radius: 8px;
            padding: 16px 20px;
        }
        .metric-card .stMetric {
            background: transparent;
        }

        /* Section container */
        .section-container {
            background: #1A1F2E;
            border: 1px solid #2D3548;
            border-radius: 8px;
            padding: 20px 24px;
            margin-bottom: 16px;
        }

        /* Status badge */
        .status-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            line-height: 1.6;
        }
        .badge-champion {
            background: rgba(0, 200, 83, 0.15);
            color: #00C853;
        }
        .badge-on-track {
            background: rgba(76, 175, 80, 0.15);
            color: #4CAF50;
        }
        .badge-behind {
            background: rgba(255, 193, 7, 0.15);
            color: #FFC107;
        }
        .badge-laggard {
            background: rgba(244, 67, 54, 0.15);
            color: #F44336;
        }
        .badge-no-data {
            background: rgba(158, 158, 158, 0.15);
            color: #9E9E9E;
        }

        /* Empty and error states */
        .empty-state, .error-state {
            text-align: center;
            padding: 48px 24px;
            border-radius: 8px;
            border: 1px dashed #2D3548;
        }
        .empty-state-icon, .error-state-icon {
            font-size: 36px;
            margin-bottom: 12px;
            opacity: 0.6;
        }
        .empty-state-title, .error-state-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #E0E0E0;
        }
        .empty-state-message, .error-state-message {
            font-size: 14px;
            color: #9E9E9E;
        }

        /* Footer */
        .app-footer {
            text-align: center;
            padding: 24px 0 8px;
            color: #6B7280;
            font-size: 13px;
            border-top: 1px solid #2D3548;
            margin-top: 32px;
        }
        .app-footer a {
            color: #4CAF50;
            text-decoration: none;
        }
        .app-footer a:hover {
            text-decoration: underline;
        }

        /* Improve sidebar section spacing */
        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Heading hierarchy fix */
        h1 { font-size: 28px !important; }
        h2 { font-size: 22px !important; }
        h3 { font-size: 18px !important; }
        </style>

        <a href="#main-content" class="skip-link">
            Skip to main content
        </a>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()

st.set_page_config(
    page_title="DeltaGrid",
    page_icon="⚡",
    layout="wide",
)

st.markdown('<div id="main-content"></div>', unsafe_allow_html=True)
render_page_header(
    "DeltaGrid",
    "Paris Agreement NDC pledges vs actual energy trajectory gap analysis",
)

with st.spinner("Loading energy data..."):
    energy_df = load_owid_data()

year_range = get_owid_year_range(energy_df)
weights, selected_year = render_sidebar(year_range)

weights_key = tuple(sorted(weights.items()))
scored_df = _cached_score(energy_df, weights_key)
year_df = scored_df[scored_df["year"] == selected_year].copy()

render_choropleth(
    year_df,
    "green_score",
    f"Green Score ({selected_year})",
    vmin=0,
    vmax=100,
)

# Metrics in card containers
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Countries", len(year_df))
with col2:
    avg_score = year_df["green_score"].mean()
    st.metric("Avg Green Score", f"{avg_score:.1f}")
with col3:
    st.metric("Year", selected_year)

render_footer()
