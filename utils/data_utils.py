from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "online_shoppers_intention.csv"

MONTH_ORDER = ["Feb", "Mar", "Apr", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@st.cache_data(show_spinner="Loading dataset...")
def load_default_dataset() -> pd.DataFrame | None:
    """Load the bundled CSV if present, else return None."""
    if DEFAULT_DATA_PATH.exists():
        return pd.read_csv(DEFAULT_DATA_PATH)
    return None


@st.cache_data(show_spinner="Reading uploaded file...")
def load_uploaded_dataset(uploaded_file) -> pd.DataFrame:
    """Parse a user-uploaded CSV into a DataFrame."""
    return pd.read_csv(uploaded_file)


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute the headline KPI numbers shown at the top of the Analytics page."""
    total_sessions = len(df)
    revenue_col = "Revenue" if "Revenue" in df.columns else None
    purchase_rate = float(df[revenue_col].astype(int).mean()) if revenue_col else None
    avg_page_values = float(df["PageValues"].mean()) if "PageValues" in df.columns else None
    avg_bounce_rate = float(df["BounceRates"].mean()) if "BounceRates" in df.columns else None
    avg_duration = None
    dur_cols = [c for c in ["Administrative_Duration", "Informational_Duration", "ProductRelated_Duration"] if c in df.columns]
    if dur_cols:
        avg_duration = float(df[dur_cols].sum(axis=1).mean())

    return {
        "total_sessions": total_sessions,
        "purchase_rate": purchase_rate,
        "avg_page_values": avg_page_values,
        "avg_bounce_rate": avg_bounce_rate,
        "avg_duration": avg_duration,
    }


def purchase_rate_by_month(df: pd.DataFrame) -> pd.DataFrame:
    if "Month" not in df.columns or "Revenue" not in df.columns:
        return pd.DataFrame()
    grouped = df.groupby("Month")["Revenue"].mean().reset_index()
    grouped["Month"] = pd.Categorical(grouped["Month"], categories=MONTH_ORDER, ordered=True)
    grouped = grouped.sort_values("Month")
    grouped["Revenue"] = grouped["Revenue"] * 100
    grouped.columns = ["Month", "Purchase Rate (%)"]
    return grouped


def purchase_rate_by_visitor_type(df: pd.DataFrame) -> pd.DataFrame:
    if "VisitorType" not in df.columns or "Revenue" not in df.columns:
        return pd.DataFrame()
    grouped = df.groupby("VisitorType")["Revenue"].mean().reset_index()
    grouped["Revenue"] = grouped["Revenue"] * 100
    grouped.columns = ["Visitor Type", "Purchase Rate (%)"]
    return grouped.sort_values("Purchase Rate (%)", ascending=False)


def numeric_correlation(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["int64", "float64", "bool"])
    if numeric_df.shape[1] < 2:
        return pd.DataFrame()
    return numeric_df.corr(numeric_only=True)
