"""
pages/2_AI_Assistant.py
------------------------
Purchase Intelligence Assistant.

This page no longer runs a free-floating generic chatbot. It reads the
grounded context built by the Prediction page (utils.llm_utils.build_
session_context, stored in st.session_state.prediction_context), shows
the model's real prediction and probability, generates a structured AI
business analysis strictly from that data, and then lets the user ask
grounded follow-up questions about the same session.

If no prediction has been run yet, the assistant has nothing to ground
itself in and says so rather than falling back to free-form chat.
"""

import streamlit as st

from utils.session import init_session_state
from utils.styling import load_css, page_header, metric_card
from utils.icons import icon
from utils.llm_utils import generate_purchase_insight, ask_insight_assistant, is_configured

st.set_page_config(page_title="Purchase Intent AI | Assistant", page_icon="🤖", layout="wide")
init_session_state()
load_css()

page_header(
    "AI Assistant",
    "A grounded explanation and conversion action plan for your most recent prediction.",
    icon("bot", 34),
)

if not is_configured():
    st.error(
        "The AI Assistant isn't configured on this deployment yet. "
        "An administrator needs to set `GEMINI_API_KEY` in `.streamlit/secrets.toml` "
        "or as an environment variable — no action is needed from you."
    )

context = st.session_state.prediction_context

if context is None:
    st.info(
        "No prediction yet. Head over to the **Prediction** page, fill in a session, "
        "and come back here for a grounded explanation of the result."
    )
    st.stop()

# A new prediction since the last visit invalidates the cached insight
# and resets the follow-up conversation — they belong to the old session.
if (
    st.session_state.insight_result is None
    or st.session_state.insight_result.get("session_id") != context["session_id"]
):
    st.session_state.insight_result = None
    st.session_state.insight_conversation = []

# ------------------------------------------------------------------
# Headline: raw model output (Model-Based Evidence)
# ------------------------------------------------------------------
c1, c2 = st.columns(2)
with c1:
    st.markdown(
        metric_card("Prediction", context["predicted_outcome"], icon=icon("cart"), accent="indigo"),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        metric_card(
            "Purchase Probability",
            f"{context['purchase_probability'] * 100:.2f}%",
            icon=icon("target"),
            accent="emerald",
        ),
        unsafe_allow_html=True,
    )

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Generate (or show cached) grounded AI insight
# ------------------------------------------------------------------
if st.session_state.insight_result is None:
    st.markdown(
        f'#### {icon("brain", 18)} AI Purchase Intelligence Analysis',
        unsafe_allow_html=True,
    )
    st.caption("Generates a structured explanation plus a prioritized conversion action plan — grounded strictly in the prediction and features above.")
    if st.button("Generate AI Insight", type="primary", use_container_width=True, icon=":material/auto_awesome:"):
        with st.spinner("Analyzing this session's behavior signals..."):
            try:
                ai_text = generate_purchase_insight(context)
                st.session_state.insight_result = {"session_id": context["session_id"], "text": ai_text}
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
            except Exception as exc:  # noqa: BLE001
                st.error(f"Something went wrong generating the insight: {exc}")
else:
    st.markdown(st.session_state.insight_result["text"])

    st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

    # --------------------------------------------------------------
    # Follow-up Q&A, grounded in the same session context
    # --------------------------------------------------------------
    st.markdown(f'#### {icon("message", 18)} Ask about this session', unsafe_allow_html=True)
    st.caption("e.g. \"Why was the probability so low?\" or \"What are the strongest signals here?\"")

    for turn in st.session_state.insight_conversation:
        role = "user" if turn["role"] == "user" else "assistant"
        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🤖"):
            st.markdown(turn["text"])

    follow_up = st.chat_input("Ask a question about this prediction...")
    if follow_up:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(follow_up)
        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            placeholder.markdown(
                '<div class="typing-indicator"><span></span><span></span><span></span></div>',
                unsafe_allow_html=True,
            )
            try:
                ask_insight_assistant(context, st.session_state.insight_conversation, follow_up)
            except Exception as exc:  # noqa: BLE001
                error_text = f"Something went wrong reaching the assistant: {exc}"
                st.session_state.insight_conversation.append({"role": "user", "text": follow_up})
                st.session_state.insight_conversation.append({"role": "model", "text": error_text})
        st.rerun()

    st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)
    if st.button("Start a new insight for this session", icon=":material/refresh:"):
        st.session_state.insight_result = None
        st.session_state.insight_conversation = []
        st.rerun()
