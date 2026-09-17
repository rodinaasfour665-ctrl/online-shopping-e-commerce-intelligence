# 🛍️ Purchase Intent AI Platform

A production-style, multi-page Streamlit dashboard for the **Online Shoppers Purchasing
Intention** project: real-time purchase prediction, a grounded AI purchase-intelligence
assistant, an analytics dashboard, and an about/architecture page.

## 🧠 Architecture

```
Session Data (form input on the Prediction page)
        ↓
Preprocessing / feature engineering (utils/model_utils.py)
        ↓
Purchase Prediction Model (Gradient Boosting, models/best_model.pkl)
        ↓
Prediction + Probability + Feature Importance
        ↓
Grounded Session Context (utils/llm_utils.build_session_context)
        ↓
Gemini Purchase Intelligence Assistant
        ↓
Prediction Explanation + Behavior Analysis + Purchase Intent
        ↓
Key Conversion Barriers + Marketing Insights
        ↓
Prioritized, Evidence-Traced Conversion Action Plan
        ↓
Conversational follow-up Q&A about that same session
```

The AI Assistant is **not** a general-purpose chatbot and does **not** recommend
products. It only ever reasons over the real prediction, real probability, and real
session features produced by the ML model — it will not invent product IDs, product
names, customer purchase history, orders, transactions, or unsupported business/seasonal
claims. Its prompt explicitly separates **Model-Based Evidence** (the prediction,
probability, and actual feature values) from **Business Interpretation** (its reasonable
reading of what that behavior suggests), and it must not present the latter as if it
were a measured model fact.

## 📁 Folder structure

```
shopper_dashboard/
├── Home.py                      # Entry point — run this with `streamlit run`
├── pages/
│   ├── 1_🔮_Prediction.py       # Prediction form + results + history
│   ├── 2_🤖_AI_Assistant.py     # Grounded Purchase Intelligence Assistant (Gemini)
│   ├── 3_📊_Analytics.py        # KPIs & interactive charts
│   └── 4_ℹ️_About.py            # Project/team/tech/architecture
├── utils/
│   ├── session.py                 # session_state initialisation
│   ├── styling.py                 # CSS loader + reusable HTML components
│   ├── model_utils.py             # model load, feature engineering, prediction
│   ├── data_utils.py              # dataset loading + analytics helpers
│   └── llm_utils.py               # Gemini API wrapper + grounded insight pipeline
├── assets/
│   └── style.css                  # Global stylesheet
├── models/
│   ├── best_model.pkl              # trained sklearn Pipeline
│   └── feature_names.pkl           # 26-column feature name list
├── data/
│   └── online_shoppers_intention.csv   # optional, powers the Analytics page
└── requirements.txt
```

## ▶️ Running the app

```bash
cd shopper_dashboard
pip install -r requirements.txt
streamlit run Home.py
```

Streamlit will automatically detect everything inside `pages/` and add it to the sidebar
navigation — no manual routing code needed.

## 🤖 AI Assistant setup

The AI Assistant page calls the **Google Gemini API** via a server-side key — visitors
never see, enter, or store an API key. An administrator sets `GEMINI_API_KEY` (and
optionally `GEMINI_MODEL`, default `gemini-2.5-flash`) in `.streamlit/secrets.toml` or as
an environment variable before deploying.

**How it's used:**
1. Run a session through the **Prediction** page. This computes a real prediction and
   purchase probability and stores a grounded context (the session's feature values, the
   prediction, the probability, and the model's global feature importances — nothing
   else) in session state.
2. Open the **AI Assistant** page. It shows that prediction and probability, then
   generates a structured nine-section analysis strictly from that context:
   1. Prediction Summary
   2. Why This Prediction Happened
   3. Customer / Session Behavior
   4. Purchase Intent
   5. Key Conversion Barriers
   6. Marketing Insights
   7. Conversion Improvement Opportunities
   8. Prioritized Action Plan (High / Medium / Low priority, each action tied to a
      specific observed signal — never a generic, unconnected suggestion)
   9. Validation Recommendation (a reminder that recommended actions are hypotheses to
      be confirmed via A/B testing or future predictions, not guaranteed outcomes)

   The assistant never claims a specific probability an action will achieve (e.g. it
   will not say an action will raise the probability "from 20% to 70%") and never
   recommends specific products, product IDs, or cross-sell items — only prediction
   explanation and conversion-focused business actions.
3. Ask follow-up questions ("Why was the probability so low?", "What are the strongest
   signals here?") — answers stay grounded in the same session; running a new prediction
   starts a fresh insight and conversation.

## 🧠 Model details

- **Algorithm:** Gradient Boosting Classifier (selected from 6 candidates — Logistic
  Regression, Decision Tree, Random Forest, SVM, XGBoost, Gradient Boosting — by highest
  Test F1-Score).
- **Preprocessing:** `RobustScaler` on numeric features + `OneHotEncoder` on categorical
  features, both wrapped in the same `sklearn.Pipeline` that was pickled, so predictions
  reproduce training-time preprocessing exactly.
- **Engineered features:** `Total_Pages`, `Total_Duration`, `Product_Page_Ratio`,
  `Product_Duration_Ratio`, `Engagement_Score`, and `log1p` transforms of the four most
  skewed numeric columns — all recreated live in `utils/model_utils.engineer_features()`
  from the raw form inputs, exactly mirroring the training notebook's feature-engineering
  cell.
- **Test-set metrics** (captured from the training notebook, shown on the Prediction page):

  | Metric | Score |
  |---|---|
  | Accuracy | 90.5% |
  | Precision | 72.3% |
  | Recall | 64.1% |
  | F1-Score | 68.0% |
  | ROC-AUC | 0.936 |

## 🎨 Customising

- Colours, spacing, and card styles all live in `assets/style.css` — tweak the `:root`
  CSS variables at the top to re-theme the whole app in one place.
- Team names/roles and tech badges on the About page are placeholders — edit
  `pages/4_ℹ️_About.py` directly.
