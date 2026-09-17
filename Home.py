"""
Home.py
--------
Main entry point of the Streamlit multi-page app. Running
`streamlit run Home.py` launches this page and Streamlit automatically
picks up every script inside `pages/` as an additional sidebar page.
"""

import streamlit as st

from utils.session import init_session_state
from utils.styling import load_css, metric_card, feature_card, workflow_step
from utils.icons import icon
from utils.model_utils import load_model, load_feature_names, MODEL_METRICS, MODEL_NAME

# ------------------------------------------------------------------
# Page configuration — must be the first Streamlit command executed.
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Purchase Intent AI | Home",
    page_icon="🛍️",  # Streamlit tab icon only supports emoji/image, not inline SVG
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
load_css()

model = load_model()
feature_names = load_feature_names()

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown(f'## <span class="ui-icon" style="vertical-align:-4px;">{icon("bag", 26)}</span> Purchase Intent AI', unsafe_allow_html=True)
    st.caption("Online Shopper Behaviour Platform")
    st.markdown("---")
    st.markdown("**System status**")
    if model is not None:
        st.success(f"Model loaded — {MODEL_NAME}")
    else:
        st.error("Model not found. Place `best_model.pkl` in `models/`.")
    st.caption(f"{len(feature_names)} engineered features" if feature_names else "Feature list unavailable")
    st.markdown("---")
    st.markdown(f'<span style="font-size:12.5px;color:var(--text-on-dark-muted);">Navigate using the pages above {icon("arrow-up", 13)}</span>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Hero section
# ------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-orb hero-orb-1"></div>
        <div class="hero-orb hero-orb-2"></div>
        <div class="hero-orb hero-orb-3"></div>
        <div class="hero-particles">
            <span></span><span></span><span></span><span></span><span></span><span></span>
        </div>
        <div class="hero-content">
            <div class="hero-brand">
                <span class="hero-brand-icon">{icon("bag", 26)}</span>
                <span class="hero-brand-text">Online Shoppers Purchasing</span>
            </div>
            <div class="hero-title">Know a customer's<br/>next move before they do.</div>
            <div class="hero-meta">
                <div class="hero-eyebrow"><span class="hero-eyebrow-dot"></span>AI-POWERED E-COMMERCE ANALYTICS</div>
                <div class="hero-subtitle">
                    A production-style dashboard that predicts online shopper purchase intention in
                    real time, explains the "why" behind every prediction, and puts an AI analyst
                    on call to help you interpret the data.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Quick stats
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("trending-up")} Platform at a glance</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card("Model Accuracy", f"{MODEL_METRICS['Accuracy']*100:.1f}%", icon=icon("target"), accent="indigo"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("ROC-AUC Score", f"{MODEL_METRICS['ROC-AUC']:.3f}", icon=icon("ruler"), accent="cyan"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Engineered Features", f"{len(feature_names) if feature_names else 26}", icon=icon("layers"), accent="emerald"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Algorithm", "Gradient Boosting", icon=icon("tree"), accent="amber"), unsafe_allow_html=True)

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Key features
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("sparkle")} Key features</div>', unsafe_allow_html=True)
f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(feature_card(
        "Real-Time Prediction",
        "Fill in session behaviour data and get an instant purchase-intent prediction with a confidence score.",
        icon("orb"),
    ), unsafe_allow_html=True)
with f2:
    st.markdown(feature_card(
        "Explainable AI",
        "See exactly which features drove each prediction via model feature-importance rankings.",
        icon("brain"),
    ), unsafe_allow_html=True)
with f3:
    st.markdown(feature_card(
        "AI Assistant",
        "Chat with a Gemini-powered assistant that understands this model and dataset.",
        icon("bot"),
    ), unsafe_allow_html=True)
with f4:
    st.markdown(feature_card(
        "Live Analytics",
        "Explore KPIs, monthly trends, and correlations across the full shopper dataset.",
        icon("bar-chart"),
    ), unsafe_allow_html=True)

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# System workflow
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("settings")} How it works</div>', unsafe_allow_html=True)
w1, w2, w3, w4 = st.columns(4)
with w1:
    st.markdown(workflow_step(1, "Collect Session Data", "Behavioural signals are captured: pages viewed, time on site, bounce/exit rates, traffic source."), unsafe_allow_html=True)
with w2:
    st.markdown(workflow_step(2, "Feature Engineering", "Raw signals are enriched into 26 features — engagement scores, ratios, and log-transforms."), unsafe_allow_html=True)
with w3:
    st.markdown(workflow_step(3, "Model Inference", "A tuned Gradient Boosting pipeline scores the session's likelihood of ending in a purchase."), unsafe_allow_html=True)
with w4:
    st.markdown(workflow_step(4, "Actionable Insight", "Results, confidence scores, and AI-generated explanations are surfaced to the user."), unsafe_allow_html=True)

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Call to action
# ------------------------------------------------------------------
cta1, cta2 = st.columns([3, 1])
with cta1:
    st.markdown(
        """
        #### Ready to try it?
        Head to **Prediction** in the sidebar to score a session, or ask the
        **AI Assistant** anything about how the model works.
        """
    )
with cta2:
    st.page_link("pages/1_Prediction.py", label="Go to Prediction →")  # native page icon stays emoji (Streamlit limitation)

st.caption("Built with Streamlit · scikit-learn · Gemini API")