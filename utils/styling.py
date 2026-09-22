from pathlib import Path
import streamlit as st

from utils.icons import icon as _icon

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def load_css() -> None:
    """Inject the shared stylesheet. Safe to call on every page."""
    css_path = ASSETS_DIR / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Stylesheet not found at assets/style.css — using default Streamlit theme.")


def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Render a consistent gradient page header used at the top of every page."""
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-icon">{icon}</div>
            <div>
                <div class="page-header-title">{title}</div>
                <div class="page-header-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: str = "", icon: str = None, accent: str = "indigo") -> str:
    """Return HTML for one KPI / metric card. Use inside st.markdown(..., unsafe_allow_html=True)."""
    icon = icon if icon is not None else _icon("bar-chart")
    delta_html = f'<div class="metric-card-delta">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card accent-{accent}">
        <div class="metric-card-icon">{icon}</div>
        <div class="metric-card-value">{value}</div>
        <div class="metric-card-label">{label}</div>
        {delta_html}
    </div>
    """


def feature_card(title: str, description: str, icon: str = None) -> str:
    """Return HTML for a feature / capability card (Home page)."""
    icon = icon if icon is not None else _icon("sparkle")
    return f"""
    <div class="feature-card">
        <div class="feature-card-icon">{icon}</div>
        <div class="feature-card-title">{title}</div>
        <div class="feature-card-desc">{description}</div>
    </div>
    """


def workflow_step(number: int, title: str, description: str) -> str:
    """Return HTML for one step in the 'system workflow' section."""
    return f"""
    <div class="workflow-step">
        <div class="workflow-step-number">{number}</div>
        <div class="workflow-step-title">{title}</div>
        <div class="workflow-step-desc">{description}</div>
    </div>
    """


def badge(text: str, kind: str = "neutral") -> str:
    """Small pill badge. kind: success | danger | neutral | info | warning."""
    return f'<span class="badge badge-{kind}">{text}</span>'


def result_card(prediction_label: str, probability: float, is_purchase: bool) -> str:
    """Big result banner shown after a prediction on the Prediction page."""
    state = "purchase" if is_purchase else "no-purchase"
    result_icon = _icon("cart", 40) if is_purchase else _icon("door", 40)
    pct = f"{probability * 100:.1f}%"
    return f"""
    <div class="result-card result-{state}">
        <div class="result-card-icon">{result_icon}</div>
        <div class="result-card-body">
            <div class="result-card-label">Prediction</div>
            <div class="result-card-value">{prediction_label}</div>
            <div class="result-card-confidence">Confidence: <b>{pct}</b></div>
        </div>
    </div>
    """