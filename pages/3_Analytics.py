"""
pages/3_📊_Analytics.py
-------------------------
Data insights & analytics dashboard over the Online Shoppers Purchasing
Intention dataset. Falls back to a file-uploader if the CSV hasn't been
placed in `data/online_shoppers_intention.csv` yet.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.session import init_session_state
from utils.styling import load_css, page_header, metric_card
from utils.icons import icon
from utils.data_utils import (
    load_default_dataset, load_uploaded_dataset, compute_kpis,
    purchase_rate_by_month, purchase_rate_by_visitor_type, numeric_correlation,
)

st.set_page_config(page_title="Purchase Intent AI | Analytics", page_icon="📊", layout="wide")
init_session_state()
load_css()

page_header(
    "Analytics Dashboard",
    "Explore purchase-intent trends and behavioural patterns across the shopper dataset.",
    icon("bar-chart", 34),
)

df = load_default_dataset()

if df is None:
    st.warning(
        "No bundled dataset found at `data/online_shoppers_intention.csv`. "
        "Upload it below to explore analytics (this won't be saved permanently)."
    )
    uploaded = st.file_uploader("Upload online_shoppers_intention.csv", type=["csv"])
    if uploaded is not None:
        df = load_uploaded_dataset(uploaded)

if df is None:
    st.stop()

# ------------------------------------------------------------------
# Shared chart styling — matches the palette used throughout this page
# ------------------------------------------------------------------
PLOT_LAYOUT = dict(
    height=360,
    margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#C3BCD6",
    xaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
)
LINE_COLOR, MARKER_COLOR = "#A78BFA", "#E879F9"
BAR_SCALE = ["#4C1D95", "#8B5CF6", "#E879F9"]


def _purchase_rate(frame: pd.DataFrame, group_col: str, min_n: int = 1, order=None) -> pd.DataFrame:
    """Sessions / ConversionRate(%) per level of group_col, matching the notebook's conversion_table."""
    g = frame.groupby(group_col, observed=True)
    out = g["Revenue"].agg(Sessions="size", Rate=lambda s: s.astype(int).mean() * 100)
    out = out.rename(columns={"Rate": "Purchase Rate (%)"})
    out = out[out["Sessions"] >= min_n]
    if order is not None:
        out = out.reindex([o for o in order if o in out.index])
    else:
        out = out.sort_values("Purchase Rate (%)", ascending=False)
    return out.reset_index()


# ------------------------------------------------------------------
# KPIs
# ------------------------------------------------------------------
kpis = compute_kpis(df)
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(metric_card("Total Sessions", f"{kpis['total_sessions']:,}", icon=icon("receipt"), accent="indigo"), unsafe_allow_html=True)
with k2:
    val = f"{kpis['purchase_rate']*100:.1f}%" if kpis["purchase_rate"] is not None else "N/A"
    st.markdown(metric_card("Purchase Rate", val, icon=icon("cart"), accent="emerald"), unsafe_allow_html=True)
with k3:
    val = f"{kpis['avg_page_values']:.2f}" if kpis["avg_page_values"] is not None else "N/A"
    st.markdown(metric_card("Avg Page Value", val, icon=icon("dollar"), accent="amber"), unsafe_allow_html=True)
with k4:
    val = f"{kpis['avg_bounce_rate']*100:.2f}%" if kpis["avg_bounce_rate"] is not None else "N/A"
    st.markdown(metric_card("Avg Bounce Rate", val, icon=icon("trending-down"), accent="rose"), unsafe_allow_html=True)
with k5:
    val = f"{kpis['avg_duration']:.0f}s" if kpis["avg_duration"] is not None else "N/A"
    st.markdown(metric_card("Avg Session Time", val, icon=icon("clock"), accent="cyan"), unsafe_allow_html=True)

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Trend charts
# ------------------------------------------------------------------
row1_left, row1_right = st.columns(2)

with row1_left:
    st.markdown(f'<div class="section-title">{icon("calendar")} Purchase Rate by Month</div>', unsafe_allow_html=True)
    month_df = purchase_rate_by_month(df)
    if not month_df.empty:
        fig = px.line(month_df, x="Month", y="Purchase Rate (%)", markers=True)
        fig.update_traces(line_color=LINE_COLOR, marker=dict(size=8, color=MARKER_COLOR), line_width=3)
        fig.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("`Month` or `Revenue` column not found in dataset.")

with row1_right:
    st.markdown(f'<div class="section-title">{icon("users")} Purchase Rate by Visitor Type</div>', unsafe_allow_html=True)
    visitor_df = purchase_rate_by_visitor_type(df)
    if not visitor_df.empty:
        fig = px.bar(visitor_df, x="Visitor Type", y="Purchase Rate (%)", color="Purchase Rate (%)", color_continuous_scale=BAR_SCALE)
        fig.update_layout(showlegend=False, coloraxis_showscale=False, **PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("`VisitorType` or `Revenue` column not found in dataset.")

row2_left, row2_right = st.columns(2)

with row2_left:
    st.markdown(f'<div class="section-title">{icon("target")} Revenue Distribution</div>', unsafe_allow_html=True)
    if "Revenue" in df.columns:
        counts = df["Revenue"].astype(str).value_counts().reset_index()
        counts.columns = ["Purchased", "Count"]
        fig = px.pie(counts, names="Purchased", values="Count", hole=0.55, color_discrete_sequence=["#8B5CF6", "#2A2440"])
        fig.update_layout(
            height=360, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#C3BCD6",
            legend=dict(font=dict(color="#C3BCD6")),
        )
        fig.update_traces(marker=dict(line=dict(color="#0A0812", width=2)))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("`Revenue` column not found in dataset.")

with row2_right:
    st.markdown(f'<div class="section-title">{icon("link")} Bounce vs. Exit Rate</div>', unsafe_allow_html=True)
    if {"BounceRates", "ExitRates"}.issubset(df.columns):
        color_col = "Revenue" if "Revenue" in df.columns else None
        fig = px.scatter(
            df.sample(min(len(df), 2000), random_state=42),
            x="BounceRates", y="ExitRates", color=color_col,
            color_discrete_sequence=["#6D28D9", "#E879F9"], opacity=0.65,
        )
        fig.update_layout(legend=dict(font=dict(color="#C3BCD6")), **PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("`BounceRates`/`ExitRates` columns not found in dataset.")

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Business EDA highlights — curated from the notebook's 50-question
# Business EDA & Analytics section (strongest signal per theme only)
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("bar-chart")} Business Insight Highlights</div>', unsafe_allow_html=True)
st.caption("The handful of findings from the deep-dive notebook analysis with the clearest business signal.")

row3_left, row3_right = st.columns(2)

with row3_left:
    st.markdown(f'<div class="section-title">{icon("dollar")} Conversion Across PageValues Ranges</div>', unsafe_allow_html=True)
    if {"PageValues", "Revenue"}.issubset(df.columns):
        bins = [-0.01, 0, 5, 10, 20, 50, df["PageValues"].max() + 1]
        labels = ["0", "0-5", "5-10", "10-20", "20-50", "50+"]
        pv_df = df.copy()
        pv_df["PV_bin"] = pd.cut(pv_df["PageValues"], bins=bins, labels=labels)
        pv_table = _purchase_rate(pv_df, "PV_bin", order=labels)
        fig = px.bar(
            pv_table, x="PV_bin", y="Purchase Rate (%)", color="Purchase Rate (%)",
            color_continuous_scale=BAR_SCALE,
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title="PageValues range", **PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Conversion rises almost monotonically from ~4% at PageValues = 0 to 80%+ once it passes 50 — the single strongest purchase-intent signal in the dataset.")
    else:
        st.info("`PageValues`/`Revenue` columns not found in dataset.")

with row3_right:
    st.markdown(f'<div class="section-title">{icon("link")} Conversion by Traffic Type</div>', unsafe_allow_html=True)
    if {"TrafficType", "Revenue"}.issubset(df.columns):
        traffic_table = _purchase_rate(df, "TrafficType", min_n=30)
        fig = px.bar(
            traffic_table, x="TrafficType", y="Purchase Rate (%)", color="Purchase Rate (%)",
            color_continuous_scale=BAR_SCALE,
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, **PLOT_LAYOUT)
        fig.update_xaxes(type="category")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Channels with fewer than 30 sessions are excluded to avoid misleading small-sample rates. The largest channel by volume is also comfortably above-baseline — the single most valuable traffic source overall.")
    else:
        st.info("`TrafficType`/`Revenue` columns not found in dataset.")

row4_left, row4_right = st.columns(2)

with row4_left:
    st.markdown(f'<div class="section-title">{icon("receipt")} Administrative Activity vs. Conversion</div>', unsafe_allow_html=True)
    if {"Administrative", "Revenue"}.issubset(df.columns):
        adm_bins = [-1, 0, 2, 5, 10, df["Administrative"].max() + 1]
        adm_labels = ["0", "1-2", "3-5", "6-10", "10+"]
        adm_df = df.copy()
        adm_df["Admin_bin"] = pd.cut(adm_df["Administrative"], bins=adm_bins, labels=adm_labels)
        adm_table = _purchase_rate(adm_df, "Admin_bin", order=adm_labels)
        fig = px.bar(
            adm_table, x="Admin_bin", y="Purchase Rate (%)", color="Purchase Rate (%)",
            color_continuous_scale=BAR_SCALE,
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title="Administrative pages visited", **PLOT_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Conversion more than doubles the moment a session touches even 1–2 Administrative (account/checkout-adjacent) pages, then keeps climbing.")
    else:
        st.info("`Administrative`/`Revenue` columns not found in dataset.")

with row4_right:
    st.markdown(f'<div class="section-title">{icon("users")} Behavioral Segments</div>', unsafe_allow_html=True)
    seg_cols = {"PageValues", "ProductRelated", "ExitRates", "BounceRates", "Revenue"}
    if seg_cols.issubset(df.columns):
        seg_df = df.copy()
        med_pr = seg_df["ProductRelated"].median()
        med_er = seg_df["ExitRates"].median()
        q75_br = seg_df["BounceRates"].quantile(0.75)

        def _assign_segment(row):
            if row["PageValues"] > 0 and row["ProductRelated"] > med_pr:
                return "High-Intent Shopper"
            elif row["PageValues"] > 0:
                return "Value-Aware, Low-Browse"
            elif row["ExitRates"] < med_er and row["ProductRelated"] > med_pr:
                return "Engaged Explorer"
            elif row["BounceRates"] > q75_br:
                return "Bouncer"
            else:
                return "Low-Engagement Browser"

        seg_df["Segment"] = seg_df.apply(_assign_segment, axis=1)
        seg_table = _purchase_rate(seg_df, "Segment")
        fig = px.bar(
            seg_table, x="Segment", y="Purchase Rate (%)", color="Purchase Rate (%)",
            color_continuous_scale=BAR_SCALE,
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_title=None, **PLOT_LAYOUT)
        fig.update_xaxes(tickangle=20)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Rule-based segments built from PageValues, browsing depth and friction metrics. The two PageValues-positive segments convert at 50–80%+; everything else stays in single digits.")
    else:
        st.info("Not enough columns available to build behavioral segments.")

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

st.markdown(f'<div class="section-title">{icon("bar-chart")} Executive Comparison — Purchase vs. No-Purchase</div>', unsafe_allow_html=True)
compare_cols = [c for c in [
    "Administrative", "Administrative_Duration", "Informational", "Informational_Duration",
    "ProductRelated", "ProductRelated_Duration", "BounceRates", "ExitRates", "PageValues",
] if c in df.columns]
if compare_cols and "Revenue" in df.columns:
    exec_df = df.copy()
    exec_df["Revenue"] = exec_df["Revenue"].astype(int)
    final_compare = exec_df.groupby("Revenue")[compare_cols].mean().T
    final_compare.columns = ["No_Purchase_Mean", "Purchase_Mean"]
    final_compare["Relative_Diff_%"] = (
        (final_compare["Purchase_Mean"] - final_compare["No_Purchase_Mean"])
        / final_compare["No_Purchase_Mean"].replace(0, np.nan) * 100
    ).round(1)
    final_compare = final_compare.reindex(final_compare["Relative_Diff_%"].abs().sort_values(ascending=False).index)

    fig = go.Figure(go.Bar(
        x=final_compare["Relative_Diff_%"], y=final_compare.index, orientation="h",
        marker_color=[MARKER_COLOR if v >= 0 else "#4C1D95" for v in final_compare["Relative_Diff_%"]],
    ))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.25)")
    fig.update_layout(
        height=420, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#C3BCD6",
        xaxis=dict(title="Relative difference, Purchase vs No-Purchase (%)", gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("PageValues shows the largest gap by far between purchasing and non-purchasing sessions; BounceRates and ExitRates are lower for purchasers, everything else runs higher.")
else:
    st.info("Not enough columns available to build the executive comparison.")

st.markdown("<hr class='subtle-divider'/>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Correlation heatmap
# ------------------------------------------------------------------
st.markdown(f'<div class="section-title">{icon("grid")} Feature Correlation Heatmap</div>', unsafe_allow_html=True)
corr = numeric_correlation(df)
if not corr.empty:
    fig = px.imshow(
        corr.round(2),
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        aspect="auto",
        text_auto=".2f",
    )
    fig.update_traces(
        textfont_size=10.5,
        xgap=2, ygap=2,
        hovertemplate="%{x} vs %{y}: %{z:.2f}<extra></extra>",
    )
    fig.update_layout(
        height=620,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#C3BCD6", size=12),
        coloraxis_colorbar=dict(
            title=dict(text="corr", font=dict(color="#C3BCD6")),
            tickfont=dict(color="#C3BCD6"),
            outlinewidth=0,
        ),
        xaxis=dict(tickfont=dict(color="#E4DBFA")),
        yaxis=dict(tickfont=dict(color="#E4DBFA")),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough numeric columns to compute a correlation matrix.")

with st.expander("View raw data sample", icon=":material/search:"):
    st.dataframe(df.head(100), use_container_width=True)
