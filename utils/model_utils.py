"""
utils/model_utils.py
---------------------
Everything related to the trained ML pipeline:
 - loading the saved sklearn Pipeline (preprocessing + Gradient Boosting model)
 - turning raw form inputs into the exact 26-column engineered feature row
   the pipeline was trained on
 - running predictions
 - extracting feature importances
 - static evaluation metrics captured from the training notebook

The pipeline (`models/best_model.pkl`) already contains its own
ColumnTransformer (RobustScaler for numeric columns + OneHotEncoder for
categorical columns), so this module only has to reproduce the same
feature-engineering steps that were applied before the train/test split —
it must NOT re-scale or re-encode anything itself.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "feature_names.pkl"

# ------------------------------------------------------------------
# Reference values pulled directly from the training notebook so the
# UI offers realistic dropdown options / ranges instead of guesses.
# ------------------------------------------------------------------
MONTH_OPTIONS = ["Feb", "Mar", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
VISITOR_TYPE_OPTIONS = ["Returning_Visitor", "New_Visitor", "Other"]
OPERATING_SYSTEM_OPTIONS = list(range(1, 9))     # 1-8
BROWSER_OPTIONS = list(range(1, 14))             # 1-13
REGION_OPTIONS = list(range(1, 10))              # 1-9
TRAFFIC_TYPE_OPTIONS = list(range(1, 21))        # 1-20

# Metrics captured from the model-comparison step of the notebook
# (Gradient Boosting was selected as best_model by highest Test F1-Score).
MODEL_NAME = "Gradient Boosting Classifier"
MODEL_METRICS = {
    "Accuracy": 0.9054,
    "Precision": 0.7227,
    "Recall": 0.6414,
    "F1-Score": 0.6796,
    "ROC-AUC": 0.9363,
}


@st.cache_resource(show_spinner="Loading trained model...")
def load_model():
    """Load the trained sklearn Pipeline. Cached across reruns/sessions."""
    if not MODEL_PATH.exists():
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load model from `{MODEL_PATH.name}`: {exc}")
        return None


@st.cache_resource(show_spinner=False)
def load_feature_names():
    """Load the ordered list of 26 columns the pipeline expects."""
    if not FEATURES_PATH.exists():
        return []
    try:
        return joblib.load(FEATURES_PATH)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Failed to load feature names from `{FEATURES_PATH.name}`: {exc}")
        return []


def engineer_features(raw: dict) -> pd.DataFrame:
    """
    Convert raw form inputs into the full engineered single-row DataFrame
    the pipeline was trained on (mirrors the notebook's
    'FINAL PREPROCESSING - CELL 1' feature-engineering block exactly).
    """
    admin, admin_dur = float(raw["Administrative"]), float(raw["Administrative_Duration"])
    info, info_dur = float(raw["Informational"]), float(raw["Informational_Duration"])
    prod, prod_dur = float(raw["ProductRelated"]), float(raw["ProductRelated_Duration"])
    page_values = float(raw["PageValues"])

    total_pages = admin + info + prod
    total_duration = admin_dur + info_dur + prod_dur
    product_page_ratio = prod / (total_pages + 1)
    product_duration_ratio = prod_dur / (total_duration + 1)
    engagement_score = total_pages * (total_duration + 1)

    row = {
        "Administrative": admin,
        "Administrative_Duration": admin_dur,
        "Informational": info,
        "Informational_Duration": info_dur,
        "ProductRelated": prod,
        "ProductRelated_Duration": prod_dur,
        "BounceRates": float(raw["BounceRates"]),
        "ExitRates": float(raw["ExitRates"]),
        "PageValues": page_values,
        "SpecialDay": float(raw["SpecialDay"]),
        "Month": raw["Month"],
        "OperatingSystems": int(raw["OperatingSystems"]),
        "Browser": int(raw["Browser"]),
        "Region": int(raw["Region"]),
        "TrafficType": int(raw["TrafficType"]),
        "VisitorType": raw["VisitorType"],
        "Weekend": bool(raw["Weekend"]),
        "Total_Pages": total_pages,
        "Total_Duration": total_duration,
        "Product_Page_Ratio": product_page_ratio,
        "Product_Duration_Ratio": product_duration_ratio,
        "Engagement_Score": engagement_score,
        "Administrative_Duration_Log": np.log1p(admin_dur),
        "Informational_Duration_Log": np.log1p(info_dur),
        "ProductRelated_Duration_Log": np.log1p(prod_dur),
        "PageValues_Log": np.log1p(page_values),
    }
    return pd.DataFrame([row])


def validate_raw_inputs(raw: dict) -> list:
    """Return a list of human-readable validation error strings (empty = valid)."""
    errors = []
    non_negative_fields = [
        "Administrative", "Administrative_Duration", "Informational",
        "Informational_Duration", "ProductRelated", "ProductRelated_Duration",
        "PageValues",
    ]
    for field in non_negative_fields:
        if raw.get(field, 0) < 0:
            errors.append(f"**{field}** cannot be negative.")

    for field in ["BounceRates", "ExitRates", "SpecialDay"]:
        val = raw.get(field, 0)
        if not (0.0 <= val <= 1.0):
            errors.append(f"**{field}** must be between 0.0 and 1.0.")

    if raw.get("ExitRates", 0) < raw.get("BounceRates", 0):
        errors.append("**ExitRates** is typically greater than or equal to **BounceRates**.")

    return errors


def predict(model, X: pd.DataFrame):
    """Run the pipeline. Returns (predicted_label:int, purchase_probability:float|None)."""
    pred = int(model.predict(X)[0])
    proba = None
    if hasattr(model, "predict_proba"):
        proba = float(model.predict_proba(X)[0][1])
    return pred, proba


def get_feature_importance(model, top_n: int = 15) -> pd.DataFrame | None:
    """
    Extract feature importances from the fitted pipeline's final estimator,
    mapped back to the (one-hot expanded) column names from the preprocessor.
    Returns a DataFrame sorted descending, or None if unavailable.
    """
    try:
        preprocessor = model.named_steps.get("preprocessing")
        estimator = model.named_steps.get("model")
        if preprocessor is None or estimator is None:
            return None
        if not hasattr(estimator, "feature_importances_"):
            return None

        feature_names = preprocessor.get_feature_names_out()
        importances = estimator.feature_importances_

        df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
        df["Feature"] = df["Feature"].str.replace(r"^(num__|cat__)", "", regex=True)
        df = df.sort_values("Importance", ascending=False).head(top_n).reset_index(drop=True)
        return df
    except Exception:  # noqa: BLE001
        return None
