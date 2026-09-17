"""
utils/session.py
-----------------
Centralised Streamlit session_state initialisation.

Every page calls `init_session_state()` at the top of its script so that
keys are always guaranteed to exist, no matter which page the user lands
on first (Streamlit multi-page apps run every page as an independent
script, so state must be defensively initialised everywhere).
"""

import streamlit as st


def init_session_state() -> None:
    """Create every session_state key used across the app if it is missing."""

    defaults = {
        # ---- Prediction page ----
        "prediction_history": [],   # list[dict] of past predictions
        "last_prediction": None,    # dict with the most recent result

        # ---- AI Assistant page ----
        "prediction_context": None,   # grounded context dict for the most recent prediction
                                       # (built by llm_utils.build_session_context in 1_Prediction.py)
        "insight_result": None,       # {"session_id": str, "text": str} — cached AI insight so we
                                       # don't re-call Gemini on every page revisit
        "insight_conversation": [],   # list[{"role": "user"/"model", "text": str}] follow-up Q&A
                                       # about the current prediction_context

        # ---- Global ----
        "app_theme_loaded": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
