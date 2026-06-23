"""Shared UI components: empty states, error states, headers, footer."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st


def render_page_header(title: str, description: str | None = None) -> None:
    """Render a consistent page title without emoji."""
    st.title(title)
    if description:
        st.caption(description)


def render_empty_state(
    title: str = "No data available",
    message: str = "Try adjusting your filters or weights.",
) -> None:
    """Render a styled empty state."""
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-state-icon">&#9744;</div>
            <div class="empty-state-title">{title}</div>
            <div class="empty-state-message">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error_state(
    title: str = "Something went wrong",
    message: str = "An error occurred while loading data.",
    retry_fn: Callable[[], None] | None = None,
) -> None:
    """Render a styled error state with optional retry button."""
    st.markdown(
        f"""
        <div class="error-state">
            <div class="error-state-icon">&#9888;</div>
            <div class="error-state-title">{title}</div>
            <div class="error-state-message">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if retry_fn:
        if st.button("Retry", key=f"retry_{title}"):
            retry_fn()
            st.rerun()


def render_country_count(count: int) -> None:
    """Render a small country count indicator."""
    st.markdown(
        f'<p style="color:#9E9E9E;font-size:13px;margin:4px 0 0 0;">'
        f"{count} countries</p>",
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render the app footer with data attribution."""
    st.markdown(
        """
        <div class="app-footer">
            Data:
            <a href="https://github.com/owid/energy-data" target="_blank">
                OWID Energy
            </a>
            +
            <a href="https://www.climatewatchdata.org/" target="_blank">
                Climate Watch NDC
            </a>
            &middot; Built with Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )
