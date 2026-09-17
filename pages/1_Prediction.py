"""
pages/1_Prediction.py
-------------------------
Interactive prediction page: user fills in a session-behaviour form,
the app engineers the same 26 features used in training, runs the
saved Gradient Boosting pipeline, and displays the result alongside
model performance metrics, feature importance, and prediction history.
"""

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.session import init_session_state
from utils.styling import load_css, page_header, metric_card, result_card
from utils.icons import icon
from utils.model_utils import (
    load_model, load_feature_names, engineer_features, validate_raw_inputs,
    predict, get_feature_importance, MODEL_METRICS, MODEL_NAME,
    MONTH_OPTIONS, VISITOR_TYPE_OPTIONS, OPERATING_SYSTEM_OPTIONS,
    BROWSER_OPTIONS, REGION_OPTIONS, TRAFFIC_TYPE_OPTIONS,
)
from utils.llm_utils import build_session_context

st.set_page_config(page_title="Purchase Intent AI | Prediction", page_icon="🔮", layout="wide")
init_session_state()
load_css()

model = load_model()
feature_names = load_feature_names()

page_header(
    "Purchase Intention Prediction",
    "Enter session behaviour details to predict whether the visit will end in a purchase.",
    "",
)

if model is None:
    st.error(
        "The trained model could not be loaded. Make sure `best_model.pkl` "
        "exists inside the `models/` folder, then refresh this page."
    )
    st.stop()

form_col, info_col = st.columns([2, 1], gap="large")

# ==================================================================
# LEFT COLUMN — Input form
# ==================================================================
with form_col:
    with st.form("prediction_form", border=True):
        st.markdown(f'#### {icon("cursor", 18)} Session Activity', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        administrative = c1.number_input("Administrative pages", min_value=0, max_value=30, value=2, help="Number of administrative pages visited.")
        informational = c2.number_input("Informational pages", min_value=0, max_value=30, value=0, help="Number of informational pages visited.")
        product_related = c3.number_input("Product-related pages", min_value=0, max_value=800, value=18, help="Number of product-related pages visited.")

        c4, c5, c6 = st.columns(3)
        administrative_duration = c4.number_input("Admin duration (sec)", min_value=0.0, max_value=4000.0, value=60.0, step=1.0)
        informational_duration = c5.number_input("Info duration (sec)", min_value=0.0, max_value=3000.0, value=0.0, step=1.0)
        product_related_duration = c6.number_input("Product duration (sec)", min_value=0.0, max_value=65000.0, value=600.0, step=1.0)

        st.markdown(f'#### {icon("trending-down", 18)} Engagement Quality', unsafe_allow_html=True)
        c7, c8, c9 = st.columns(3)
        bounce_rates = c7.slider("Bounce rate", 0.0, 0.2, 0.02, step=0.001, format="%.3f", help="Average bounce rate of pages visited during the session.")
        exit_rates = c8.slider("Exit rate", 0.0, 0.2, 0.03, step=0.001, format="%.3f", help="Average exit rate of pages visited during the session.")
        page_values = c9.number_input("Page values", min_value=0.0, max_value=400.0, value=0.0, step=0.5, help="Average value of pages visited prior to a transaction.")

        special_day = st.slider(
            "Special-day closeness", 0.0, 1.0, 0.0, step=0.1,
            help="Closeness of the visit date to a special day (e.g. Mother's Day) — 0 = far, 1 = same day.",
        )

        st.markdown(f'#### {icon("user", 18)} Visitor & Technical Details', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        month = d1.selectbox("Month", MONTH_OPTIONS, index=MONTH_OPTIONS.index("May"))
        visitor_type = d2.selectbox("Visitor type", VISITOR_TYPE_OPTIONS)
        weekend = d3.selectbox("Weekend session?", ["No", "Yes"]) == "Yes"

        d4, d5, d6 = st.columns(3)
        operating_system = d4.selectbox("Operating system (code)", OPERATING_SYSTEM_OPTIONS, index=1)
        browser = d5.selectbox("Browser (code)", BROWSER_OPTIONS, index=1)
        region = d6.selectbox("Region (code)", REGION_OPTIONS, index=0)

        traffic_type = st.selectbox("Traffic type (code)", TRAFFIC_TYPE_OPTIONS, index=1)

        submitted = st.form_submit_button("Predict Purchase Intention", use_container_width=True, type="primary", icon=":material/bolt:")

    if submitted:
        raw = {
            "Administrative": administrative,
            "Administrative_Duration": administrative_duration,
            "Informational": informational,
            "Informational_Duration": informational_duration,
            "ProductRelated": product_related,
            "ProductRelated_Duration": product_related_duration,
            "BounceRates": bounce_rates,
            "ExitRates": exit_rates,
            "PageValues": page_values,
            "SpecialDay": special_day,
            "Month": month,
            "OperatingSystems": operating_system,
            "Browser": browser,
            "Region": region,
            "TrafficType": traffic_type,
            "VisitorType": visitor_type,
            "Weekend": weekend,
        }

        errors = validate_raw_inputs(raw)
        if errors:
            st.error("Please fix the following before predicting:\n\n" + "\n".join(f"- {e}" for e in errors))
        else:
            with st.spinner("Running inference through the Gradient Boosting pipeline..."):
                try:
                    X = engineer_features(raw)
                    pred_label, proba = predict(model, X)
                    is_purchase = pred_label == 1
                    result_text = "Likely to Purchase" if is_purchase else "Unlikely to Purchase"

                    st.session_state.last_prediction = {
                        "label": result_text,
                        "is_purchase": is_purchase,
                        "probability": proba,
                    }
                    st.session_state.prediction_history.insert(0, {
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Month": month,
                        "Visitor Type": visitor_type,
                        "Page Values": page_values,
                        "Product Pages": product_related,
                        "Prediction": result_text,
                        "Confidence": f"{proba*100:.1f}%" if proba is not None else "N/A",
                    })

                    # Build the grounded context the AI Assistant page will
                    # read — this is the ONLY data the LLM is ever allowed
                    # to see about this session.
                    importance_df = get_feature_importance(model, top_n=15)
                    st.session_state.prediction_context = build_session_context(
                        raw_features=raw,
                        engineered_features=X.iloc[0].to_dict(),
                        predicted_outcome="Purchase" if is_purchase else "No Purchase",
                        purchase_probability=proba if proba is not None else 0.0,
                        feature_importance_df=importance_df,
                        session_id=datetime.now().isoformat(),
                    )

                    st.success("Prediction complete.")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Prediction failed: {exc}")

    # Show the latest result banner (persists across reruns until a new one is made)
    if st.session_state.last_prediction:
        lp = st.session_state.last_prediction
        st.markdown(
            result_card(lp["label"], lp["probability"] or 0.0, lp["is_purchase"]),
            unsafe_allow_html=True,
        )
        st.caption("Open the **AI Assistant** page for a grounded explanation of this prediction.")

# ==================================================================
# RIGHT COLUMN — Model info
# ==================================================================
with info_col:
    st.markdown(f'#### {icon("clipboard", 18)} Model Performance', unsafe_allow_html=True)
    st.caption(f"Selected model: **{MODEL_NAME}** (best Test F1-Score during model comparison)")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(metric_card("Accuracy", f"{MODEL_METRICS['Accuracy']*100:.1f}%", icon=icon("target"), accent="indigo"), unsafe_allow_html=True)
        st.write("")
        st.markdown(metric_card("Recall", f"{MODEL_METRICS['Recall']*100:.1f}%", icon=icon("repeat"), accent="amber"), unsafe_allow_html=True)
    with m2:
        st.markdown(metric_card("Precision", f"{MODEL_METRICS['Precision']*100:.1f}%", icon=icon("check-circle"), accent="emerald"), unsafe_allow_html=True)
        st.write("")
        st.markdown(metric_card("ROC-AUC", f"{MODEL_METRICS['ROC-AUC']:.3f}", icon=icon("ruler"), accent="cyan"), unsafe_allow_html=True)
    st.write("")
    st.markdown(metric_card("F1-Score", f"{MODEL_METRICS['F1-Score']*100:.1f}%", icon=icon("scale"), accent="rose"), unsafe_allow_html=True)

    st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

    st.markdown(f'#### {icon("brain", 18)} Top Feature Importances', unsafe_allow_html=True)
    importance_df = get_feature_importance(model, top_n=12)
    if importance_df is not None and not importance_df.empty:
        fig = px.bar(
            importance_df.sort_values("Importance"),
            x="Importance", y="Feature", orientation="h",
            color="Importance", color_continuous_scale=["#4C1D95", "#8B5CF6", "#E879F9"],
        )
        fig.update_layout(
            height=420, showlegend=False, margin=dict(l=0, r=10, t=10, b=10),
            coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#C3BCD6",
            xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Feature importance isn't available for this model type.")

# ==================================================================
# Prediction history
# ==================================================================
st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)
hist_header, hist_clear = st.columns([5, 1])
with hist_header:
    st.markdown(f'<div class="section-title">{icon("clock")} Prediction History</div>', unsafe_allow_html=True)
with hist_clear:
    if st.button("Clear history", use_container_width=True, icon=":material/delete:"):
        st.session_state.prediction_history = []
        st.session_state.last_prediction = None
        st.rerun()

if st.session_state.prediction_history:
    hist_df = pd.DataFrame(st.session_state.prediction_history)
    st.dataframe(hist_df, use_container_width=True, hide_index=True)
else:
    st.info("No predictions made yet this session. Fill out the form above to get started.")