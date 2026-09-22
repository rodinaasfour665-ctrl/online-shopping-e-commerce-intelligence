import os
import requests
import streamlit as st

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Default model used for chat generation. Can be overridden by setting
# GEMINI_MODEL in st.secrets or as an environment variable.
DEFAULT_MODEL = "gemini-3.6-flash"

SYSTEM_PROMPT = """You are the in-app AI Assistant for a "Purchase Intention Prediction" \
analytics platform built on the UCI Online Shoppers Purchasing Intention dataset. \
The platform trains a Gradient Boosting classifier (Accuracy ~90.5%, ROC-AUC ~0.94) \
to predict whether a website visitor session will end in a purchase (Revenue=True), \
based on session behaviour features (page counts/durations, bounce/exit rates, page \
values, month, visitor type, traffic source, etc.).

Help users understand:
- what the model predicts and how confident it is,
- what the input features mean and how they affect purchase likelihood,
- how to read the Analytics dashboard (KPIs, trends, correlations),
- general e-commerce / conversion-rate-optimisation best practices,
- and general data-science questions.

Be concise, clear, and use markdown (headers, bullet points, bold) where it improves
readability. If you don't know something specific about this particular deployment
(e.g. exact live data), say so honestly instead of guessing.
"""


def _get_config_value(key: str, default: str = "") -> str:
    """Read a server-side config value from st.secrets first, then env vars.
    Never sourced from user input."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:  # noqa: BLE001 - secrets.toml may not exist locally
        pass
    return os.environ.get(key, default)


def is_configured() -> bool:
    """True if the backend Gemini API key has been configured by the
    deployment (secrets.toml or environment variable)."""
    return bool(_get_config_value("GEMINI_API_KEY"))


def _build_contents(messages: list) -> list:
    """Convert [{'role': 'user'/'assistant', 'content': str}, ...] into
    Gemini's `contents` schema, mapping 'assistant' -> 'model'."""
    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    return contents


def call_gemini(
    messages: list,
    system_prompt: str = SYSTEM_PROMPT,
    temperature: float = 0.7,
    max_tokens: int = 1200,
) -> str:
    """
    Send the running conversation to the Gemini API and return the
    assistant's text reply. Raises RuntimeError on misconfiguration and
    requests.HTTPError on API failure.

    `system_prompt` defaults to the general project-awareness prompt above,
    but the grounded purchase-insight functions below pass a stricter,
    session-specific one instead.
    """
    api_key = _get_config_value("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "The AI Assistant isn't configured on this deployment yet. "
            "An administrator needs to set GEMINI_API_KEY in .streamlit/secrets.toml "
            "or as an environment variable."
        )
    model = _get_config_value("GEMINI_MODEL", DEFAULT_MODEL)

    url = f"{GEMINI_API_BASE}/{model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": _build_contents(messages),
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            # Gemini 2.5 models spend part of maxOutputTokens on invisible
            # "thinking" tokens before writing the visible answer. For a
            # long, multi-section instruction-following task like the
            # purchase-insight report, thinking can consume most of the
            # budget and truncate the actual output mid-way. Disabling it
            # reserves the full token budget for the visible response.
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    response = requests.post(
        url,
        headers={"content-type": "application/json", "x-goog-api-key": api_key},
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        return "*(The assistant returned an empty response.)*"

    finish_reason = candidates[0].get("finishReason")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts).strip()

    if not text:
        return "*(The assistant returned an empty response.)*"

    if finish_reason == "MAX_TOKENS":
        text += (
            "\n\n---\n_This response was cut off by the output token limit before it "
            "finished. Try asking again, or increase `max_tokens` in the calling code._"
        )

    return text


def extract_text_from_upload(uploaded_file) -> str:
    """
    Best-effort plain-text extraction from an uploaded file so its content
    can be added to the chat context. Supports .txt/.md/.csv natively and
    .pdf if `pypdf` is installed; anything else is skipped gracefully.
    """
    name = uploaded_file.name.lower()

    if name.endswith((".txt", ".md", ".csv")):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            st.warning("Install `pypdf` (`pip install pypdf`) to enable PDF text extraction.")
            return ""
        except Exception as exc:  # noqa: BLE001
            st.warning(f"Could not read PDF: {exc}")
            return ""

    st.info(f"File type for `{uploaded_file.name}` isn't supported for text extraction yet — "
            "supported: .txt, .md, .csv, .pdf")
    return ""


# ======================================================================
# GROUNDED PURCHASE-INTELLIGENCE PIPELINE
# ----------------------------------------------------------------------
# Ported from the validated Colab notebook (build_session_context ->
# create_business_insight_prompt -> generate_purchase_insight ->
# ask_insight_assistant). Adapted for this app's actual data flow:
# the notebook pulled a row out of a static X_test/y_test by position,
# but the Streamlit app has no labeled test set at runtime — it has a
# live session the user just submitted on the Prediction page. So
# `build_session_context()` below takes the prediction/probability that
# 1_Prediction.py already computed via model_utils, rather than
# re-deriving them from a dataset index.
# ======================================================================

INSIGHT_SYSTEM_PROMPT = (
    "You are an AI Purchase Intelligence Assistant embedded in a purchase-intention "
    "prediction dashboard. You explain the model's prediction AND provide a grounded, "
    "prioritized action plan for improving conversion. You must reason strictly from the "
    "model output and session data provided to you in the user message and never invent "
    "products, product IDs, orders, transactions, purchase history, or unsupported "
    "statistics. You never claim a specific numeric probability change from any "
    "recommended action — only that it may address an observed conversion barrier."
)


def build_session_context(
    raw_features: dict,
    engineered_features: dict,
    predicted_outcome: str,
    purchase_probability: float,
    feature_importance_df=None,
    actual_outcome: str = None,
    session_id: str = None,
) -> dict:
    """
    Build the grounded context dict for one real (live, user-submitted)
    session. This is the single source of truth for everything the LLM
    is allowed to know about the session — no product, order, or
    customer-history fields exist here because none exist in this app.

    `raw_features` is the human-readable form input (what a marketer
    would recognize); `engineered_features` is the full 26-column row
    actually fed to the model, kept alongside for completeness but not
    what's shown to the LLM by default (see create_business_insight_prompt).
    `actual_outcome` will normally be None here, since a live form
    submission has no ground-truth label the way a held-out test row does.
    """
    context = {
        "session_id": session_id,
        "purchase_probability": purchase_probability,
        "predicted_outcome": predicted_outcome,
        "session_features": raw_features,
        "engineered_features": engineered_features,
    }
    if actual_outcome is not None:
        context["actual_outcome"] = actual_outcome
    if feature_importance_df is not None and not feature_importance_df.empty:
        context["top_global_features"] = feature_importance_df.to_dict("records")
    return context


def create_business_insight_prompt(session_context: dict) -> str:
    """
    Builds a strictly grounded prompt covering both the prediction
    explanation AND a prioritized conversion action plan. Only facts
    present in `session_context` may be used; recommendations must trace
    back to an observed signal in that context, never to invented
    customer/product/business facts.
    """
    features_text = "\n".join(
        f"- {key}: {value}" for key, value in session_context["session_features"].items()
    )

    top_features_text = "Not available for this model type."
    if session_context.get("top_global_features"):
        top_features_text = "\n".join(
            f"- {row['Feature']}: importance={row['Importance']:.4f}"
            for row in session_context["top_global_features"][:10]
        )

    actual_line = ""
    if session_context.get("actual_outcome"):
        actual_line = f"Actual outcome (ground truth): {session_context['actual_outcome']}\n"

    prompt = f"""You are an AI Purchase Intelligence Assistant embedded in a purchase-intention
prediction dashboard. You analyze ONE real website session, explain the model's
prediction in plain, business-friendly language, and provide a grounded,
prioritized action plan for improving the customer's likelihood of converting.

=== MODEL OUTPUT (real, from the trained classifier) ===
Predicted outcome: {session_context['predicted_outcome']}
Purchase probability: {session_context['purchase_probability']:.2%}
{actual_line}
=== SESSION FEATURES (real, from the current session — the ONLY facts about this session) ===
{features_text}

=== GLOBALLY IMPORTANT FEATURES FOR THIS MODEL ===
{top_features_text}

Using ONLY the information above, write a structured analysis with EXACTLY
these nine section headers (markdown, numbered):

1. Prediction Summary
   - State the predicted outcome, purchase probability, and actual outcome
     when available.

2. Why This Prediction Happened
   - Explain the strongest evidence from the actual model/session context
     above (e.g. which feature values and, if available, which globally
     important features align with this session).

3. Customer / Session Behavior
   - Explain what the session's actual feature values indicate about how
     this visitor behaved.

4. Purchase Intent
   - Classify the observed intent (e.g. low/moderate/high) and explain why,
     using only the session features and prediction above.

5. Key Conversion Barriers
   - Identify the actual signals in the session features above that may be
     preventing conversion. If the prediction is Purchase with a high
     probability, say plainly that no significant barriers are evident
     rather than inventing some.

6. Marketing Insights
   - Translate the model evidence into business-relevant observations.
     Clearly distinguish Model-Based Evidence (the prediction, probability,
     and actual feature values above) from Business Interpretation (your
     reasonable reading of what that behavior suggests) — never present
     interpretation as if it were a measured model fact.

7. Conversion Improvement Opportunities
   - Explain what could plausibly be changed in the customer's journey to
     improve conversion likelihood, each one tied to a specific barrier or
     signal identified above. Valid recommendation categories include:
     improving CTA visibility, reducing checkout friction, clarifying
     navigation or product information, strengthening trust signals,
     providing shipping/delivery information, reducing funnel steps,
     offering incentives when justified by the evidence, improving
     engagement with relevant content, targeted retargeting, offering
     assistance when the session shows signs of hesitation, and improving
     the transition from browsing to conversion-oriented action.

8. Prioritized Action Plan
   - For each recommended action, use exactly this structure:
     **Action:** <short action name>
     **Why:** <the specific observed session evidence motivating it>
     **Expected Goal:** <what behavior change this aims to encourage>
     **Priority:** High / Medium / Low
     **Evidence:** <restate the specific feature(s)/signal(s) this traces to>
   - Prioritize based on: (a) strength of the observed signal, (b) relevance
     to this specific prediction, (c) potential conversion impact, and
     (d) practicality of implementation. Group actions under "High Priority",
     "Medium Priority", and "Low Priority / Optional" subheadings.
   - Follow this reasoning chain for every action, implicitly or explicitly:
     Observed Evidence -> Interpretation -> Conversion Barrier/Opportunity ->
     Recommended Action.

9. Validation Recommendation
   - Close with a short note that these actions are recommendations, not
     guaranteed outcomes, and should be validated via A/B testing,
     conversion-rate monitoring, future model predictions, or controlled
     experiments before being treated as confirmed improvements.

Strict rules:
- Do NOT invent, assume, or mention any specific product, product ID,
  product name, order, or purchase history — none exists in the data above.
- Do NOT claim the customer purchased anything unless "Predicted outcome" or
  "Actual outcome" explicitly says so.
- Do NOT state or imply a specific numeric probability the actions will
  achieve (e.g. never say something like "this will raise the probability
  from 20% to 70%"). Only say an action may reduce an observed barrier or
  represents a potential opportunity to improve conversion likelihood —
  actual impact must be validated separately, as noted in section 9.
- Base every statement strictly on the session features and model output
  given above; do not fabricate additional customer facts, conversion
  statistics, or seasonal claims that aren't supported by the data shown.
- Do NOT recommend specific products, product IDs, cross-sell items, or
  reorder suggestions — this assistant analyzes purchase intent and
  business/conversion actions, not product recommendations.
- Every recommendation in sections 7 and 8 must be traceable to a specific
  signal named in sections 2-5; do not give generic advice unconnected to
  this session's actual features.
- Write for a marketing/analytics stakeholder, not a data scientist —
  clear, concise, and actionable.
"""
    return prompt


def generate_purchase_insight(session_context: dict) -> str:
    """
    The "grounded prompt -> Gemini" half of the notebook's
    generate_purchase_insight(). The ML-prediction half already happened
    on the Prediction page (model_utils.predict() + build_session_context()
    above) before this is ever called.
    """
    prompt = create_business_insight_prompt(session_context)
    return call_gemini(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=INSIGHT_SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=3000,
    )


def ask_insight_assistant(session_context: dict, conversation_history: list, user_question: str) -> str:
    """
    Ported from the notebook. Continues a conversation about one specific
    session's prediction, re-sending the grounding facts on every turn
    (the Gemini REST call has no memory between requests). Mutates
    `conversation_history` in place with the new question + answer.
    """
    history_text = "\n".join(
        f"{turn['role'].upper()}: {turn['text']}" for turn in conversation_history
    ) or "(this is the first question)"

    grounding = create_business_insight_prompt(session_context)

    prompt = f"""{grounding}

=== CONVERSATION SO FAR ===
{history_text}

=== NEW USER QUESTION ===
{user_question}

Answer the user's question conversationally in a few sentences, staying
strictly grounded in the session features and model output above. If the
question asks about something not covered by the data (e.g. a specific
product or past order), say plainly that this information isn't available
in the current session data rather than inventing an answer.
"""
    reply = call_gemini(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=INSIGHT_SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=600,
    )
    conversation_history.append({"role": "user", "text": user_question})
    conversation_history.append({"role": "model", "text": reply})
    return reply
