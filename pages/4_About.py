"""
pages/4_ℹ️_About.py
---------------------
Project overview, team info, technology stack, and a lightweight
CSS-based architecture diagram (no external image dependency).
"""

import streamlit as st

from utils.session import init_session_state
from utils.styling import load_css, page_header, badge
from utils.icons import icon

st.set_page_config(page_title="Purchase Intent AI | About", page_icon="ℹ️", layout="wide")
init_session_state()
load_css()

page_header(
    "About This Project",
    "Purchase-intent prediction platform for the UCI Online Shoppers dataset.",
    icon("info", 34),
)

# ------------------------------------------------------------------
# Project description
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("book")} Project Overview</div>', unsafe_allow_html=True)
st.markdown(
    """
This platform predicts whether an online shopping session will end in a purchase, using the
**Online Shoppers Purchasing Intention** dataset (12,330 sessions, UCI Machine Learning
Repository). A full data-science pipeline — cleaning, feature engineering, model comparison,
and hyperparameter-tuned Gradient Boosting — powers the prediction engine behind this
dashboard, wrapped in a production-style Streamlit interface with an integrated AI assistant
for interpretation and Q&A.

**Problem statement:** e-commerce teams want to identify, in real time, which sessions are
likely to convert — so they can trigger interventions (discounts, live chat, retargeting)
for at-risk sessions and understand which behavioural signals matter most.
"""
)

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Technologies used
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("wrench")} Technologies Used</div>', unsafe_allow_html=True)
tech_badges = [
    ("Python", "info"), ("Streamlit", "info"), ("scikit-learn", "success"),
    ("Pandas / NumPy", "success"), ("Plotly", "warning"), ("Gradient Boosting", "warning"),
    ("Google Gemini API", "neutral"), ("Joblib", "neutral"),
]
st.markdown(
    " ".join(badge(name, kind) for name, kind in tech_badges),
    unsafe_allow_html=True,
)

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Architecture diagram (pure CSS/HTML — no external image needed)
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("layout")} System Architecture</div>', unsafe_allow_html=True)

database_icon = icon("database", 24)
layers_icon = icon("layers", 24)
settings_icon = icon("settings", 24)
tree_icon = icon("tree", 24)
monitor_icon = icon("monitor", 24)
bot_icon = icon("bot", 24)
user_icon = icon("user", 24)
arrow_icon = icon("arrow-right", 18)

st.markdown(
    f"""
    <style>
    .arch-flow {{ display: flex; align-items: center; justify-content: space-between; gap: 6px; flex-wrap: wrap; margin: 10px 0 24px; }}
    .arch-box {{
        flex: 1; min-width: 150px; background: var(--glass-fill); border: 1px solid var(--glass-border);
        border-radius: 14px; padding: 16px 12px; text-align: center; box-shadow: var(--shadow-soft);
        backdrop-filter: var(--blur-glass); -webkit-backdrop-filter: var(--blur-glass);
    }}
    .arch-box-icon {{ margin-bottom: 6px; }}
    .arch-box-title {{ font-weight: 700; font-size: 13.5px; color: var(--text-primary); }}
    .arch-box-desc {{ font-size: 11.5px; color: var(--text-secondary); margin-top: 4px; }}
    .arch-arrow {{ font-size: 20px; color: var(--color-primary-hover); }}
    </style>

    <div class="arch-flow">
        <div class="arch-box">
            <div class="arch-box-icon">{database_icon}</div>
            <div class="arch-box-title">Raw Session Data</div>
            <div class="arch-box-desc">UCI Online Shoppers CSV</div>
        </div>
        <div class="arch-arrow">{arrow_icon}</div>
        <div class="arch-box">
            <div class="arch-box-icon">{layers_icon}</div>
            <div class="arch-box-title">Feature Engineering</div>
            <div class="arch-box-desc">Ratios, logs, engagement score</div>
        </div>
        <div class="arch-arrow">{arrow_icon}</div>
        <div class="arch-box">
            <div class="arch-box-icon">{settings_icon}</div>
            <div class="arch-box-title">Preprocessing Pipeline</div>
            <div class="arch-box-desc">RobustScaler + OneHotEncoder</div>
        </div>
        <div class="arch-arrow">{arrow_icon}</div>
        <div class="arch-box">
            <div class="arch-box-icon">{tree_icon}</div>
            <div class="arch-box-title">Gradient Boosting Model</div>
            <div class="arch-box-desc">Best of 6 evaluated models</div>
        </div>
        <div class="arch-arrow">{arrow_icon}</div>
        <div class="arch-box">
            <div class="arch-box-icon">{monitor_icon}</div>
            <div class="arch-box-title">Streamlit Dashboard</div>
            <div class="arch-box-desc">Prediction · Analytics · Chat</div>
        </div>
    </div>

    <div class="arch-flow" style="justify-content:center; gap: 40px;">
        <div class="arch-box" style="max-width:220px;">
            <div class="arch-box-icon">{bot_icon}</div>
            <div class="arch-box-title">Gemini API</div>
            <div class="arch-box-desc">Powers the AI Assistant page for natural-language Q&amp;A</div>
        </div>
        <div class="arch-box" style="max-width:220px;">
            <div class="arch-box-icon">{user_icon}</div>
            <div class="arch-box-title">End User</div>
            <div class="arch-box-desc">Analyst / merchandiser using the dashboard</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Purchase Intent AI Platform · Built with Streamlit, scikit-learn, and the Gemini API.")