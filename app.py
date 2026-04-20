import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="Sports Analytics & Performance Scout", layout="wide")
st.title("🏀 Sports Analytics & Performance Scout")
st.markdown("**Project ID:** DV-2026-GROUP-06 | **Authors:** Brent Gabriel De Castro & Mariella Janine Sola")
st.markdown("Exploring the evolution of physical archetypes and their correlation to NBA Clutch Performance (2012-2024).")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    return pd.read_csv("G6_Cleaned_NBA_Clutch_Data.csv")

df = load_data()

# --- PROFESSIONAL STYLING ---
sns.set_theme(style="white", palette="mako")

# ==========================================
# VISUALIZATION 1: STACKED AREA CHART (TRENDS)
# ==========================================
st.divider()
st.header("Key Question 1: The Pace-and-Space Evolution")
st.markdown("**Objective:** How has the share of late-game scoring efficiency shifted among different physical archetypes over the last decade?")

# Data Prep for Area Chart
area_data = df.groupby(['SEASON_START_YEAR', 'PHYSICAL_ARCHETYPE'])['PTS'].sum().reset_index()

# Plotly Stacked Area Chart
fig_area = px.area(
    area_data,
    x="SEASON_START_YEAR",
    y="PTS",
    color="PHYSICAL_ARCHETYPE",
    color_discrete_sequence=px.colors.qualitative.Set2,
    title="Trend Analysis: Total Clutch Points by Physical Archetype (2012-2023)",
    labels={"SEASON_START_YEAR": "Season Start Year", "PTS": "Total Clutch Points"}
)

# Force yearly ticks
fig_area.update_xaxes(dtick=1)

# Display chart
st.plotly_chart(fig_area, theme="streamlit", width='stretch')

st.markdown("> *Narrative Annotation:* Despite the league's heavy shift toward a faster, three-point heavy 'pace-and-space' style, heavier/power archetypes continue to account for a massive share of total clutch scoring, showing that size remains a highly durable asset in high-pressure, half-court game scenarios.")

# ==========================================
# VISUALIZATION 2 & 3: CORRELATIONS & REGRESSION
# ==========================================
st.divider()
st.header("Key Question 2: Physical Traits vs. Effectiveness")
st.markdown("**Objective:** To what extent do physical traits (BMI/Weight) correlate with a player's effectiveness in high-pressure situations?")

# --- SIDEBAR FILTER ---
st.sidebar.header("Filter by Era")
st.sidebar.markdown("Use this slider to facet the data by time period to see how correlations evolve over eras.")

min_year = int(df['SEASON_START_YEAR'].min())
max_year = int(df['SEASON_START_YEAR'].max())

selected_years = st.sidebar.slider(
    "Select Season Range:",
    min_year,
    max_year,
    (min_year, max_year)
)

# Filter dataframe
era_df = df[
    (df['SEASON_START_YEAR'] >= selected_years[0]) &
    (df['SEASON_START_YEAR'] <= selected_years[1])
]

col1, col2 = st.columns(2)

# --------------------------
# SCATTER + REGRESSION
# --------------------------
with col1:
    st.subheader("Scatter Plot with Regression")

    fig1, ax1 = plt.subplots(figsize=(8, 6))

    sns.regplot(
        x='BMI',
        y='PTS_PER_MIN',
        data=era_df,
        scatter_kws={'alpha': 0.4, 'color': '#2E86AB'},
        line_kws={'color': '#D64933', 'linewidth': 2},
        ax=ax1
    )

    sns.despine()
    ax1.set_xlabel("Body Mass Index (BMI)")
    ax1.set_ylabel("Clutch Points Per Minute")
    ax1.set_title(f"BMI vs Scoring Efficiency ({selected_years[0]}-{selected_years[1]})")

    st.pyplot(fig1)

    # Correlation narrative
    era_corr = era_df['BMI'].corr(era_df['PTS_PER_MIN'])

    if era_corr > 0.15:
        story = f"The regression line shows a **notable positive correlation ({era_corr:.2f})**. In this era, heavier players capitalized effectively on mismatches late in the game."
    elif era_corr > 0:
        story = f"The regression line is relatively flat **({era_corr:.2f})**. Size provided only a marginal advantage in this period."
    else:
        story = f"The trend flips **({era_corr:.2f})**. Higher BMI reduced efficiency, suggesting quicker players dominated clutch moments."

    st.markdown(f"> *Dynamic Narrative ({selected_years[0]}-{selected_years[1]}):* {story}")

# --------------------------
# HEATMAP
# --------------------------
with col2:
    st.subheader("Correlation Matrix (Heatmap)")

    fig2, ax2 = plt.subplots(figsize=(8, 6))

    matrix_cols = [
        'PLAYER_HEIGHT_INCHES',
        'PLAYER_WEIGHT',
        'BMI',
        'MIN',
        'PTS',
        'PTS_PER_MIN',
        'PLUS_MINUS'
    ]

    corr_data = era_df[matrix_cols].corr()

    sns.heatmap(
        corr_data,
        annot=True,
        cmap='coolwarm',
        fmt=".2f",
        vmin=-1,
        vmax=1,
        cbar_kws={"shrink": .8},
        ax=ax2
    )

    ax2.set_title(f"Metric Correlations ({selected_years[0]}-{selected_years[1]})")

    st.pyplot(fig2)

    # Heatmap narrative
    pm_weight_corr = corr_data.loc['PLUS_MINUS', 'PLAYER_WEIGHT']

    st.markdown(
        f"> *Dynamic Narrative ({selected_years[0]}-{selected_years[1]}):* "
        f"Weight vs Plus/Minus correlation is **{pm_weight_corr:.2f}**. "
        f"This helps identify when size contributes most to winning outcomes."
    )