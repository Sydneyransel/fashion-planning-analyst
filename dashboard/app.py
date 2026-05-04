import os

import pandas as pd
import plotly.express as px
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SKIMS Product Performance Analytics",
    page_icon="◆",
    layout="wide",
)

SKIMS_PALETTE = [
    "#D4B896", "#C4A882", "#B49270",
    "#8B6F5E", "#6B5044", "#4A3728",
    "#2E2018", "#1A1008", "#000000",
]

CHART_LAYOUT = dict(
    plot_bgcolor="#FAFAF8",
    paper_bgcolor="#FAFAF8",
    font_color="#1A1A1A",
    legend_title_text="",
    hovermode="x unified",
    hoverdistance=-1,
    spikedistance=-1,
    margin=dict(l=0, r=0, t=24, b=0),
    xaxis=dict(showgrid=False, showline=True, linecolor="#D4B896",
               showspikes=True, spikecolor="#8B6F5E", spikethickness=1,
               spikedash="dot", spikemode="across"),
    yaxis=dict(showgrid=True, gridcolor="#F0EAE2", showline=False),
)


@st.cache_resource
def get_connection():
    try:
        creds = st.secrets
    except Exception:
        creds = os.environ
    return snowflake.connector.connect(
        account=creds["SNOWFLAKE_ACCOUNT"],
        user=creds["SNOWFLAKE_USER"],
        password=creds["SNOWFLAKE_PASSWORD"],
        database=creds["SNOWFLAKE_DATABASE"],
        warehouse=creds["SNOWFLAKE_WAREHOUSE"],
    )


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT
            dc.KEYWORD,
            dc.CATEGORY_GROUP,
            dd.WEEK_START,
            dd.MONTH,
            dd.QUARTER,
            dd.YEAR,
            dd.SEASON,
            f.INTEREST_SCORE
        FROM SKIMS_ANALYTICS.MART.FACT_WEEKLY_INTEREST f
        JOIN SKIMS_ANALYTICS.MART.DIM_CATEGORY dc ON f.CATEGORY_KEY = dc.CATEGORY_KEY
        JOIN SKIMS_ANALYTICS.MART.DIM_DATE dd ON f.DATE_KEY = dd.DATE_KEY
        ORDER BY dd.WEEK_START
    """
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cols = [desc[0].lower() for desc in cur.description]
    cur.close()
    df = pd.DataFrame(rows, columns=cols)
    df["week_start"] = pd.to_datetime(df["week_start"])
    return df


df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; padding:1.5rem 0 1rem 0;'>
        <h1 style='font-size:1.8rem; letter-spacing:0.18em; color:#1A1A1A; margin:0;'>
            SKIMS PRODUCT ANALYTICS
        </h1>
        <p style='color:#8B6F5E; letter-spacing:0.1em; margin:0.25rem 0 0 0; font-size:0.85rem;'>
            DEMAND INTELLIGENCE · GOOGLE TRENDS · 5-YEAR VIEW
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### FILTERS")
    all_groups = sorted(df["category_group"].unique())
    selected_groups = st.multiselect(
        "Category Group",
        options=all_groups,
        default=all_groups,
    )
    min_date = df["week_start"].min().date()
    max_date = df["week_start"].max().date()
    date_range = st.slider(
        "Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM",
    )
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.75rem; color:#8B6F5E;'>"
        "Data: Google Trends via pytrends<br>"
        "Updated: weekly via GitHub Actions</p>",
        unsafe_allow_html=True,
    )

filtered = df[
    (df["category_group"].isin(selected_groups))
    & (df["week_start"].dt.date >= date_range[0])
    & (df["week_start"].dt.date <= date_range[1])
].copy()

tab1, tab2 = st.tabs(
    ["◆  DESCRIPTIVE — What Happened?", "◆  DIAGNOSTIC — Why Did It Happen?"]
)

# ── Tab 1: Descriptive ────────────────────────────────────────────────────────
with tab1:
    latest_week = filtered["week_start"].max()
    latest_df = filtered[filtered["week_start"] == latest_week]
    avg_interest = latest_df["interest_score"].mean() if not latest_df.empty else 0
    peak_score = filtered["interest_score"].max() if not filtered.empty else 0
    top_keyword = (
        filtered.groupby("keyword")["interest_score"].mean().idxmax()
        if not filtered.empty
        else "—"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Interest (Latest Week)", f"{avg_interest:.0f} / 100")
    col2.metric("5-Year Peak Score", f"{peak_score} / 100")
    col3.metric("Top Keyword (Avg)", top_keyword.title())

    st.markdown("---")
    st.markdown("#### Weekly Interest Score by Keyword")

    keyword_order = (
        filtered.groupby("keyword")["interest_score"]
        .mean()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig1 = px.line(
        filtered.sort_values("week_start"),
        x="week_start",
        y="interest_score",
        color="keyword",
        color_discrete_sequence=SKIMS_PALETTE,
        category_orders={"keyword": keyword_order},
        labels={
            "week_start": "",
            "interest_score": "Interest Score (0–100)",
            "keyword": "Keyword",
        },
    )
    fig1.update_traces(hovertemplate="%{y:.0f}")
    fig1.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig1, use_container_width=True)

# ── Tab 2: Diagnostic ─────────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Average Interest by Season")
        season_order = ["Winter", "Spring", "Summer", "Fall"]
        season_df = (
            filtered.groupby(["season", "category_group"])["interest_score"]
            .mean()
            .reset_index()
        )
        fig2 = px.bar(
            season_df,
            x="season",
            y="interest_score",
            color="category_group",
            barmode="group",
            color_discrete_sequence=SKIMS_PALETTE,
            category_orders={"season": season_order},
            labels={
                "season": "",
                "interest_score": "Avg Interest Score",
                "category_group": "Category",
            },
        )
        fig2.update_traces(hovertemplate="%{fullData.name}: %{y:.0f}")
        fig2.update_layout(
            **{
                **CHART_LAYOUT,
                "hovermode": "x unified",
                "xaxis": dict(showgrid=False, showspikes=False),
            }
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown("#### Year-over-Year: Current vs. Prior Year")
        current_year = int(filtered["year"].max()) if not filtered.empty else 2025
        prior_year = current_year - 1
        yoy_df = filtered[filtered["year"].isin([current_year, prior_year])].copy()
        yoy_df["week_num"] = (
            yoy_df["week_start"].dt.isocalendar().week.astype(int)
        )
        yoy_avg = (
            yoy_df.groupby(["year", "week_num"])["interest_score"]
            .mean()
            .reset_index()
        )
        yoy_avg["year"] = yoy_avg["year"].astype(str)

        fig3 = px.line(
            yoy_avg.sort_values("week_num"),
            x="week_num",
            y="interest_score",
            color="year",
            color_discrete_sequence=["#000000", "#D4B896"],
            labels={
                "week_num": "Week of Year",
                "interest_score": "Avg Interest Score",
                "year": "Year",
            },
        )
        fig3.update_layout(
            **{**CHART_LAYOUT, "hovermode": "closest"}
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.info(
        "**Swim peaks sharply in Summer (66/100) — 74% above its Winter baseline of 38/100.** "
        "The seasonal swing repeats every year and is calendar-driven, not campaign-dependent, "
        "making it highly forecastable for inventory planning. "
        "**Dress is SKIMS' fastest-growing category**, rising from 32/100 in 2021 to 56/100 in 2026 "
        "— structural growth that warrants increasing open-to-buy allocation each year."
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<p style='text-align:center; color:#8B6F5E; font-size:0.72rem; "
    "letter-spacing:0.08em; padding-top:1rem;'>"
    "SKIMS PRODUCT PERFORMANCE ANALYTICS · ISBA 4715 · "
    "DATA: GOOGLE TRENDS VIA PYTRENDS</p>",
    unsafe_allow_html=True,
)
